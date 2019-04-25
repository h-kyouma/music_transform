import gc
import os
import librosa
import librosa.display
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def create_dirs():
    paths = ['CQT spectrograms/test', 'CQT spectrograms/train',
             'Log-power spectrograms/test', 'Log-power spectrograms/train']
    
    [os.makedirs(path) for path in paths if not os.path.exists(path)]

def save_CQT(y, sr, filename, randomizer):
    C = np.abs(librosa.cqt(y, sr=sr))
    
    fig = plt.figure(frameon=False)
    ax = plt.axes()
    ax.set_axis_off()
    librosa.display.specshow(librosa.amplitude_to_db(C))
    plt.set_cmap('magma')
    
    if(randomizer > 1 or randomizer < -1):
        plt.savefig('CQT spectrograms/test/'+filename+'.png', 
                    bbox_inches='tight',  
                    pad_inches=0, 
                    dpi=100)
    else:
        plt.savefig('CQT spectrograms/train/'+filename+'.png', 
                    bbox_inches='tight',
                    pad_inches=0, 
                    dpi=100)
        
    #to avoid leaking RAM
    #-------------------------
    fig.clf()
    plt.close(fig)
    del C
    gc.collect()
    #-------------------------
    
def save_log_power(y, sr, filename, randomizer):
    S = np.abs(librosa.stft(y))
    
    fig = plt.figure()
    ax = plt.axes()
    ax.set_axis_off()
    librosa.display.specshow(librosa.power_to_db(S**2, ref=np.max),
                             sr=sr)
    plt.set_cmap('magma')
    
    if(randomizer > 1 or randomizer < -1):
        plt.savefig('Log-power spectrograms/test/'+filename+'.png', 
                    bbox_inches='tight', 
                    pad_inches=0, 
                    dpi=100)
    else:
        plt.savefig('Log-power spectrograms/train/'+filename+'.png', 
                    bbox_inches='tight',  
                    pad_inches=0, 
                    dpi=100)
        
    #to avoid leaking RAM
    #-------------------------
    fig.clf()
    plt.close(fig)
    del S
    gc.collect()
    #-------------------------

def create_spectrograms():
    print('\n>>> CREATING SPECTROGRAMS <<<')
    
    create_dirs()
    
    metadata = pd.read_csv('metadata_processed.csv')
    mp3_paths = metadata['mp3_path'].to_numpy(dtype=str)
    
    for counter, mp3_path in enumerate(mp3_paths, start=1):
        print('\rSpectrogram %s' %counter + ' of ' + str(len(mp3_paths)), end="   ")
        filename = mp3_path.split('/')[-1][:-4]
        y, sr = librosa.load(mp3_path)
        randomizer = np.random.normal()
        save_CQT(y, sr, filename, randomizer)
        save_log_power(y, sr, filename, randomizer)
        
    print('>>> DONE <<<')
