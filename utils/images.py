import cv2
import numpy as np


def save_img(name, image):
    cv2.imwrite(name, image)


def load_image(name):
    return cv2.imread(name, -1)


def average_pool(img, scale_factor=2):
    new_img = []
    x = 0
    y = 0

    for i in range(0, img.shape[0], scale_factor):
        for j in range(0, img.shape[1], scale_factor):
            new_img.append(np.average(img[i:i + scale_factor, j:j + scale_factor]))
            y += 1
        x += 1

    return np.reshape(np.asarray(new_img), (x, int(y / x)))


def multiply_channels(img, out_channels=3):
    multiple_channel_img = np.zeros((img.shape[0], img.shape[1], out_channels))
    for i in range(out_channels):
        multiple_channel_img[:, :, i] = img
    return multiple_channel_img


def normalize_to_PNGlike(tif_like_image):
    png_like_image = tif_like_image
    png_like_image += 1.0
    png_like_image *= 255.0 / png_like_image.max()
    return png_like_image.astype(np.float32)


def denormalize_from_PNGlike(png_like_image):
    tif_like_image = png_like_image.astype(np.float32)
    img_max = tif_like_image.max()
    img_min = tif_like_image.min()
    tif_like_image -= img_min
    tif_like_image /= (img_max - img_min)
    tif_like_image *= 2
    tif_like_image -= 1
    return tif_like_image


def bilinear_interpolation(image, fx=2, fy=2):
    return cv2.resize(image,None, fx=fx, fy=fy, interpolation=cv2.INTER_LINEAR)
