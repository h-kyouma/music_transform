from data_preprocessing.download_database import download_database
from data_preprocessing.metadata_processing import metadata_processing
from data_preprocessing.create_spectrograms import save_spectrograms
from data_preprocessing.downsample_images import downsample_images
from data_preprocessing.create_dataset import create_dataset


def preprocessing():
    download_database()
    metadata_processing()
    save_spectrograms()
    downsample_images()
    create_dataset()
