from utils.images import load_image, save_img, average_pool
import os


def resize_images_in_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_paths = os.listdir(directory.split('/')[0] + '/high_res/' + directory.split('/')[2])

    for index, spectrogram in enumerate(file_paths):
        print('\rSpectrogram {}'.format(index + 1) + ' out of ' + str(len(file_paths)), end="      ")
        if os.path.isfile(directory + '/' + spectrogram):
            continue
        img = load_image(directory.split('/')[0] + '/high_res/' + directory.split('/')[2] + '/' + spectrogram)
        save_img(directory + '/' + spectrogram, average_pool(img))


def downsample_images():
    print('>>> DOWNSAMPLING IMAGES <<<')

    directories = ['data/low_res/spectrograms', 'data/low_res/CQT_spectrograms']
    for directory in directories:
        resize_images_in_directory(directory)

    print('\n>>> DONE <<<\n')
