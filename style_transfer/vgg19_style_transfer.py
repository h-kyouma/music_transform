import numpy as np
import os
import time
from keras.applications import vgg19
from keras import backend as K
from scipy.optimize import fmin_l_bfgs_b
from utils.images import load_image, save_img, normalize_to_PNGlike, denormalize_from_PNGlike, multiply_channels
from utils.griffin_lim import invert_spectrogram


def preprocess_image(image_path):
    img = load_image(image_path)
    img = normalize_to_PNGlike(img)
    img = multiply_channels(img)
    img = np.expand_dims(img, axis=0)
    img = vgg19.preprocess_input(img)
    return img


def deprocess_image(x, i, img_nrows, img_ncols):
    if K.image_data_format() == 'channels_first':
        x = x.reshape((3, img_nrows, img_ncols))
        x = x.transpose((1, 2, 0))
    else:
        x = x.reshape((img_nrows, img_ncols, 3))

    img = denormalize_from_PNGlike(x)
    return img


def gram_matrix(x):
    assert K.ndim(x) == 3
    if K.image_data_format() == 'channels_first':
        features = K.batch_flatten(x)
    else:
        features = K.batch_flatten(K.permute_dimensions(x, (2, 0, 1)))
    gram = K.dot(features, K.transpose(features))
    return gram


def style_loss(style, combination, img_nrows, img_ncols):
    assert K.ndim(style) == 3
    assert K.ndim(combination) == 3
    S = gram_matrix(style)
    C = gram_matrix(combination)
    channels = 3
    size = img_nrows * img_ncols
    return K.sum(K.square(S - C)) / (4.0 * (channels ** 2) * (size ** 2))


def content_loss(base, combination):
    return K.sum(K.square(combination - base))


def total_variation_loss(x, img_nrows, img_ncols):
    assert K.ndim(x) == 4
    if K.image_data_format() == 'channels_first':
        a = K.square(
            x[:, :, :img_nrows - 1, :img_ncols - 1] - x[:, :, 1:, :img_ncols - 1])
        b = K.square(
            x[:, :, :img_nrows - 1, :img_ncols - 1] - x[:, :, :img_nrows - 1, 1:])
    else:
        a = K.square(
            x[:, :img_nrows - 1, :img_ncols - 1, :] - x[:, 1:, :img_ncols - 1, :])
        b = K.square(
            x[:, :img_nrows - 1, :img_ncols - 1, :] - x[:, :img_nrows - 1, 1:, :])
    return K.sum(K.pow(a + b, 1.25))


def eval_loss_and_grads(x, img_nrows, img_ncols, f_outputs):
    if K.image_data_format() == 'channels_first':
        x = x.reshape((1, 3, img_nrows, img_ncols))
    else:
        x = x.reshape((1, img_nrows, img_ncols, 3))
    outs = f_outputs([x])
    loss_value = outs[0]
    if len(outs[1:]) == 1:
        grad_values = outs[1].flatten().astype('float64')
    else:
        grad_values = np.array(outs[1:]).flatten().astype('float64')
    return loss_value, grad_values


def run_style_transfer(base_image_path, style_reference_image_path, result_prefix, img_nrows, img_ncols,
                       iterations=10, total_variation_weight=1.0, style_weight=1.0, content_weight=0.025):
    if not os.path.exists('output'):
        os.makedirs('output')

    # get tensor representations of our images
    base_image = K.variable(preprocess_image(base_image_path))
    style_reference_image = K.variable(preprocess_image(style_reference_image_path))

    # this will contain our generated image
    if K.image_data_format() == 'channels_first':
        combination_image = K.placeholder((1, 3, img_nrows, img_ncols))
    else:
        combination_image = K.placeholder((1, img_nrows, img_ncols, 3))

    # combine the 3 images into a single Keras tensor
    input_tensor = K.concatenate([base_image, style_reference_image, combination_image], axis=0)

    # build the VGG19 network with our 3 images as input
    # the model will be loaded with pre-trained ImageNet weights
    model = vgg19.VGG19(input_tensor=input_tensor, weights='imagenet', include_top=False)
    print('Model loaded.')

    # get the symbolic outputs of each "key" layer (we gave them unique names).
    outputs_dict = dict([(layer.name, layer.output) for layer in model.layers])

    # combine these loss functions into a single scalar
    loss = K.variable(0.0)
    layer_features = outputs_dict['block5_conv2']
    base_image_features = layer_features[0, :, :, :]
    combination_features = layer_features[2, :, :, :]
    loss += content_weight * content_loss(base_image_features, combination_features)

    feature_layers = ['block1_conv1', 'block2_conv1', 'block3_conv1', 'block4_conv1', 'block5_conv1']
    for layer_name in feature_layers:
        layer_features = outputs_dict[layer_name]
        style_reference_features = layer_features[1, :, :, :]
        combination_features = layer_features[2, :, :, :]
        sl = style_loss(style_reference_features, combination_features, img_nrows, img_ncols)
        loss += (style_weight / len(feature_layers)) * sl
    loss += total_variation_weight * total_variation_loss(combination_image, img_nrows, img_ncols)

    # get the gradients of the generated image wrt the loss
    grads = K.gradients(loss, combination_image)

    outputs = [loss]
    if isinstance(grads, (list, tuple)):
        outputs += grads
    else:
        outputs.append(grads)

    f_outputs = K.function([combination_image], outputs)

    class Evaluator(object):

        def __init__(self):
            self.loss_value = None
            self.grads_values = None

        def loss(self, x):
            assert self.loss_value is None
            loss_value, grad_values = eval_loss_and_grads(x, img_nrows, img_ncols, f_outputs)
            self.loss_value = loss_value
            self.grad_values = grad_values
            return self.loss_value

        def grads(self, x):
            assert self.loss_value is not None
            grad_values = np.copy(self.grad_values)
            self.loss_value = None
            self.grad_values = None
            return grad_values

    evaluator = Evaluator()

    # run scipy-based optimization (L-BFGS) over the pixels of the generated image
    # so as to minimize the neural style loss
    x = preprocess_image(base_image_path)

    for i in range(iterations):
        print('Start of iteration', i)
        start_time = time.time()
        x, min_val, info = fmin_l_bfgs_b(evaluator.loss, x.flatten(), fprime=evaluator.grads, maxfun=20)
        print('Current loss value:', min_val)

        # save current generated image
        img = deprocess_image(x.copy(), i, img_nrows, img_ncols)
        fname = result_prefix + '_at_iteration_%d' % i
        save_img('output/' + fname + '_channel0.tif', img[:, :, 0])
        save_img('output/' + fname + '_channel1.tif', img[:, :, 1])
        save_img('output/' + fname + '_channel2.tif', img[:, :, 2])
        end_time = time.time()
        print('Image saved as', fname)
        print('Iteration %d completed in %ds' % (i, end_time - start_time))


def main():
    base_img_path = 'input/american_baroque-the_four_seasons_by_vivaldi-01-concerto_no_1_in_d_major_rv_269_spring__allegro-0-29.tif'
    style_reference_image_path = 'input/brad_sucks-i_dont_know_what_im_doing-07-i_think_i_started_a_trend-88-117.tif'
    result_prefix = 'test1'
    img_nrows = 600
    img_ncols = 628

    run_style_transfer(base_img_path, style_reference_image_path, result_prefix, img_nrows, img_ncols)

    img_paths = os.listdir('output')
    for img_path in img_paths:
        invert_spectrogram('output/' + img_path, 'bilinear_interpolation')


if __name__ == "__main__":
    main()
