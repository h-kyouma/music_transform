import requests
import os
from zipfile import ZipFile

def download_file(url, filename):
    print('>>> DOWNLOADING : %s <<<' %filename) 
    temp = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(temp.content)
        
def unpack_files(parts):
    print('>>> UNPACKING <<<')
    with open('mp3.zip','ab') as result:
        for file in parts:
            with open(file, 'rb') as temp:
                result.write(temp.read())
                
    with ZipFile('mp3.zip', 'r') as zip_ref:
        zip_ref.extractall()
        
    os.remove('mp3.zip')

def download_database():
    url = 'http://mi.soi.city.ac.uk/datasets/magnatagatune/'
    metadata = 'annotations_final.csv'
    parts = ['mp3.zip.001', 'mp3.zip.002', 'mp3.zip.003'] 
    
    download_file(url+metadata, metadata)
    [download_file(url+part, part) for part in parts]
    
    unpack_files(parts)
    [os.remove(part) for part in parts]
    
    print('>>> DONE <<<')
