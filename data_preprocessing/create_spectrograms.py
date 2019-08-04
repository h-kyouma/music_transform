from utils.audio import load_audio, spectrogram, cqt_spectrogram
from utils.images import save_img
import os
import pandas as pd
import numpy as np


def get_mp3_paths():
    metadata = pd.read_csv('data/metadata_processed.csv')
    mp3_paths = metadata['mp3_path']
    return ['data/mp3_files/' + mp3_path for mp3_path in mp3_paths]


def save_spectrograms():
    if not os.path.exists('data/high_res/spectrograms'):
        os.makedirs('data/high_res/spectrograms')
    if not os.path.exists('data/high_res/CQT_spectrograms'):
        os.makedirs('data/high_res/CQT_spectrograms')

    mp3_paths = get_mp3_paths()
    outputs_img = ['data/high_res/spectrograms/' + file.split('/')[-1][:-4] + '.tif' for file in mp3_paths]
    CQT_outputs_img = ['data/high_res/CQT_spectrograms/' + file.split('/')[-1][:-4] + '.tif' for file in mp3_paths]

    print('>>> SAVING SPECTROGRAMS <<<')
    for index, (spec_path, CQT_spec_path, mp3_path) in enumerate(zip(outputs_img, CQT_outputs_img, mp3_paths)):
        print('\r{}'.format(index) + ' out of ' + str(len(mp3_paths)), end='     ')
        mp3_file = load_audio(mp3_path)
        spec = spectrogram(mp3_file).astype(np.float32)
        CQT_spec = cqt_spectrogram(mp3_file).astype(np.float32)
        save_img(spec_path, spec)
        save_img(CQT_spec_path, CQT_spec)

    print('\n>>> DONE <<<\n')
