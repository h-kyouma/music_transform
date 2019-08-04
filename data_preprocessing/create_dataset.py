import h5py
import pandas as pd
import numpy as np
import shutil
import os
from sklearn.model_selection import train_test_split
from utils.images import load_image


def move_files(files):
    directories = ['data/low_res/CQT_spectrograms/train', 'data/low_res/CQT_spectrograms/validation', 'data/low_res/CQT_spectrograms/test',
                   'data/high_res/CQT_spectrograms/train', 'data/high_res/CQT_spectrograms/validation', 'data/high_res/CQT_spectrograms/test',
                   'data/low_res/spectrograms/train', 'data/low_res/spectrograms/validation', 'data/low_res/spectrograms/test',
                   'data/high_res/spectrograms/train', 'data/high_res/spectrograms/validation', 'data/high_res/spectrograms/test']

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

    train = files[0]
    validation = files[1]
    test = files[2]

    for train_file in train:
        shutil.move('data/low_res/CQT_spectrograms/' + train_file[2:-4] + '.tif', 'data/low_res/CQT_spectrograms/train/' + train_file[2:-4] + '.tif')
        shutil.move('data/high_res/CQT_spectrograms/' + train_file[2:-4] + '.tif', 'data/high_res/CQT_spectrograms/train/' + train_file[2:-4] + '.tif')
        shutil.move('data/low_res/spectrograms/' + train_file[2:-4] + '.tif', 'data/low_res/spectrograms/train/' + train_file[2:-4] + '.tif')
        shutil.move('data/high_res/spectrograms/' + train_file[2:-4] + '.tif', 'data/high_res/spectrograms/train/' + train_file[2:-4] + '.tif')

    for validation_file in validation:
        shutil.move('data/low_res/CQT_spectrograms/' + validation_file[2:-4] + '.tif', 'data/low_res/CQT_spectrograms/validation/' + validation_file[2:-4] + '.tif')
        shutil.move('data/high_res/CQT_spectrograms/' + validation_file[2:-4] + '.tif', 'data/high_res/CQT_spectrograms/validation/' + validation_file[2:-4] + '.tif')
        shutil.move('data/low_res/spectrograms/' + validation_file[2:-4] + '.tif', 'data/low_res/spectrograms/validation/' + validation_file[2:-4] + '.tif')
        shutil.move('data/high_res/spectrograms/' + validation_file[2:-4] + '.tif', 'data/high_res/spectrograms/validation/' + validation_file[2:-4] + '.tif')

    for test_file in test:
        shutil.move('data/low_res/CQT_spectrograms/' + test_file[2:-4] + '.tif', 'data/low_res/CQT_spectrograms/test/' + test_file[2:-4] + '.tif')
        shutil.move('data/high_res/CQT_spectrograms/' + test_file[2:-4] + '.tif', 'data/high_res/CQT_spectrograms/test/' + test_file[2:-4] + '.tif')
        shutil.move('data/low_res/spectrograms/' + test_file[2:-4] + '.tif', 'data/low_res/spectrograms/test/' + test_file[2:-4] + '.tif')
        shutil.move('data/high_res/spectrograms/' + test_file[2:-4] + '.tif', 'data/high_res/spectrograms/test/' + test_file[2:-4] + '.tif')


def get_metadata():
    metadata = pd.read_csv('data/metadata_processed.csv')
    return metadata[['rock', 'classical', 'electronic', 'mp3_path']].to_numpy(dtype=str)


def split_data(data):
    train, test = train_test_split(data, random_state=42)
    train, validation = train_test_split(train, random_state=42)
    return train, validation, test


def get_labels(metadata):
    labels = []
    for row in metadata:
        labels.append(row[:3])
    return np.stack(labels).astype(int)


def get_data(metadata):
    train, validation, test = split_data(metadata)
    return [train[:, -1], get_labels(train)], [validation[:, -1], get_labels(validation)], [test[:, -1],
                                                                                            get_labels(test)]


def new_dataset(data_file, filename, num_samples, size=3):
    if size != 3:
        x, y, z = size
        dataset = data_file.create_dataset(filename, [num_samples, x, y, z], compression='gzip')
    else:
        dataset = data_file.create_dataset(filename, [num_samples, size], compression='gzip')
    return dataset


def fill_dataset(dataset, files, size, step=100):
    x, y, z = size
    temp = np.zeros((step, x, y, z))

    curr_index = 0
    while len(files) - curr_index > step:
        for i in range(curr_index, curr_index + step):
            print('\r %s' % str(i + 1) + ' of ' + str(len(files)), end="   ")
            temp[i - curr_index, :, :, :] = np.expand_dims(load_image(files[i]), axis=-1)
        dataset[curr_index:curr_index + step, :, :, :] = temp
        curr_index = curr_index + step

    for j in range(curr_index, len(files)):
        print('\r%s' % str(j + 1) + ' of ' + str(len(files)), end="   ")
        dataset[j, :, :, :] = np.expand_dims(load_image(files[j]), axis=-1)


def create_dataset():
    print('\n>>> CREATING DATASET<<<')

    metadata = get_metadata()
    train, validation, test = get_data(metadata)
    labels = [train[1], validation[1], test[1]]
    files = [train[0], validation[0], test[0]]

    datasets = [['CQT_train', 'CQT_validation', 'CQT_test'],
                ['Log_train', 'Log_validation', 'Log_test'],
                ['labels_train', 'labels_validation', 'labels_test']]

    img_size = (600, 628, 1)
    dataset_file = h5py.File('data/dataset.hdf5', 'a')

    for category in datasets:
        for ds_name, label_cat, file_cat in zip(category, labels, files):
            print('Filling dataset:', ds_name)
            if 'CQT' in ds_name:
                CQT_dataset = new_dataset(dataset_file, ds_name, len(file_cat), img_size)
                CQT_files = ['data/low_res/CQT_spectrograms/' + file[2:-4] + '.tif' for file in file_cat]
                fill_dataset(CQT_dataset, CQT_files, img_size)
            elif 'Log' in ds_name:
                Log_dataset = new_dataset(dataset_file, ds_name, len(file_cat), img_size)
                Log_files = ['data/low_res/spectrograms/' + file[2:-4] + '.tif' for file in file_cat]
                fill_dataset(Log_dataset, Log_files, img_size)
            elif 'labels' in ds_name:
                Labels_dataset = new_dataset(dataset_file, ds_name, len(label_cat))
                Labels_dataset[:, :] = label_cat
            print('\n')

    dataset_file.close()

    move_files(files)

    print('>>> DONE <<<\n')
