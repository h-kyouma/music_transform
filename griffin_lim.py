from utils.audio import inv_cqt_spectrogram, inv_spectrogram, save_wav
from utils.images import load_image
import os
        
def invert_spectrogram(path, CQT=False):
    if not os.path.exists('output'): os.makedirs('output')
    
    img = load_image(path)
    output_path = 'output/' + path.split('/')[-1][:-4]
    if CQT==True:
        save_wav(inv_cqt_spectrogram(img), output_path + '_CQT.wav')
    else:
        save_wav(inv_spectrogram(img), output_path + '.wav')
