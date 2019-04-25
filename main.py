from download_database import download_database
from metadata_processing import metadata_processing
from create_spectrograms import create_spectrograms

def preprocessing():
    #download_database()
    #metadata_processing()
    create_spectrograms()
        
if __name__ == "__main__":
    preprocessing()
