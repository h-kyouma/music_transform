import requests
import os
from zipfile import ZipFile


def download_file(url, filename):
    print('>>> DOWNLOADING : %s <<<' % filename)
    temp = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(temp.content)


def unpack_files(parts):
    if not os.path.exists('data'):
        os.makedirs('data')
    print('>>> UNPACKING <<<')
    with open('mp3.zip', 'ab') as result:
        for file in parts:
            with open(file, 'rb') as temp:
                result.write(temp.read())

    with ZipFile('mp3.zip', 'r') as zip_ref:
        zip_ref.extractall('data/mp3_files')

    os.remove('mp3.zip')


def download_database():
    url = 'http://mi.soi.city.ac.uk/datasets/magnatagatune/'
    metadata = 'annotations_final.csv'
    parts = ['mp3.zip.001', 'mp3.zip.002', 'mp3.zip.003']

    download_file(url + metadata, metadata)
    [download_file(url + part, part) for part in parts]

    unpack_files(parts)
    [os.remove(part) for part in parts]

    # remove corrupted files
    os.remove('data/mp3_files/9/american_baroque-dances_and_suites_of_rameau_and_couperin-25-le_petit_rien_xiveme_ordre_couperin-88-117.mp3')
    os.remove('data/mp3_files/8/jacob_heringman-josquin_des_prez_lute_settings-19-gintzler__pater_noster-204-233.mp3')

    print('>>> DONE <<<\n')
