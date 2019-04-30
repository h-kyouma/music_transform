import gc
import os
import librosa
import librosa.display
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def create_dirs():
    paths = ['CQT spectrograms','Log-power spectrograms']
    
    [os.makedirs(path) for path in paths if not os.path.exists(path)]

def save_CQT(y, sr, filename):
    C = np.abs(librosa.cqt(y, sr=sr))
    
    fig = plt.figure(frameon=False)
    ax = plt.axes()
    ax.set_axis_off()
    librosa.display.specshow(librosa.amplitude_to_db(C))
    plt.set_cmap('magma')
    
    plt.savefig('CQT spectrograms/'+filename+'.png', 
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
    
def save_log_power(y, sr, filename):
    S = np.abs(librosa.stft(y))
    
    fig = plt.figure()
    ax = plt.axes()
    ax.set_axis_off()
    librosa.display.specshow(librosa.power_to_db(S**2, ref=np.max),
                             sr=sr)
    plt.set_cmap('magma')
    
    plt.savefig('Log-power spectrograms/'+filename+'.png', 
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
        save_CQT(y, sr, filename)
        save_log_power(y, sr, filename)
        
    print('\n>>> DONE <<<')
