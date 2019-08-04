from utils.audio import inv_cqt_spectrogram, inv_spectrogram, save_wav
from utils.images import load_image, bilinear_interpolation
import os


def invert_spectrogram(path, upsampling_method=None, CQT=False):
    if not os.path.exists('inverted_audio'):
        os.makedirs('inverted_audio')

    img = load_image(path)
    if upsampling_method is not None:
        if upsampling_method == 'bilinear_interpolation':
            img = bilinear_interpolation(img)

    output_path = 'inverted_audio/' + path.split('/')[-1][:-4]
    if CQT is True:
        save_wav(inv_cqt_spectrogram(img), output_path + '_CQT.wav')
    else:
        save_wav(inv_spectrogram(img), output_path + '.wav')
