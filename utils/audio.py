import librosa
import librosa.filters
import numpy as np
from utils.hparams import hparams
from scipy import signal
from scipy.io import wavfile


def load_audio(path):
    return librosa.core.load(path, sr=hparams['sample_rate'])[0]


def save_wav(wav, path):
    wav *= 32767 / max(0.01, np.max(np.abs(wav)))
    wavfile.write(path, hparams['sample_rate'], wav.astype(np.int16))


def spectrogram(y):
    D = _stft(_preemphasis(y))
    S = _amp_to_db(np.abs(D)) - hparams['ref_level_db']
    return _normalize(S)


def inv_spectrogram(spectrogram):
    S = _db_to_amp(_denormalize(spectrogram) + hparams['ref_level_db'])  # Convert back to linear
    return _inv_preemphasis(_griffin_lim(S ** hparams['power']))  # Reconstruct phase


def cqt_spectrogram(y):
    D = _cqt(_preemphasis(y))
    S = _amp_to_db(np.abs(D)) - hparams['ref_level_db']
    return _normalize(S)


def inv_cqt_spectrogram(cqt_spectrogram):
    S = _db_to_amp(_denormalize(cqt_spectrogram) + hparams['ref_level_db'])  # Convert back to linear
    return _inv_preemphasis(_cqt_griffin_lim(S))  # Reconstruct phase


# Based on https://github.com/librosa/librosa/issues/434
def _griffin_lim(S):
    angles = np.exp(2j * np.pi * np.random.rand(*S.shape))
    S_complex = np.abs(S).astype(np.complex)
    for i in range(hparams['griffin_lim_iters']):
        if i > 0:
            angles = np.exp(1j * np.angle(_stft(y)))
        y = _istft(S_complex * angles)
    return y


def _cqt_griffin_lim(S):
    angles = np.exp(2j * np.pi * np.random.rand(*S.shape))
    S_complex = np.abs(S).astype(np.complex)
    for i in range(hparams['griffin_lim_iters']):
        print("\rIter: "+str(i)+' out of '+str(hparams['griffin_lim_iters']), end="   ")
        if i > 0:
            angles = np.exp(1j * np.angle(_cqt(y)))
        y = _icqt(S_complex * angles)
    return y


def _stft(y):
    return librosa.stft(y=y, n_fft=hparams['fft_size'], hop_length=get_hop_size())


def _istft(y):
    return librosa.istft(y, hop_length=get_hop_size())


def _cqt(y):
    return librosa.cqt(y, hop_length=get_hop_size(), n_bins=hparams['n_bins'], 
                       bins_per_octave=hparams['bins_per_octave'])


def _icqt(y):
    return librosa.icqt(y, hop_length=get_hop_size(), bins_per_octave=hparams['bins_per_octave'])


# Conversions:
def _amp_to_db(x):
    return 20 * np.log10(np.maximum(1e-5, x))


def _db_to_amp(x):
    return np.power(10.0, x * 0.05)


def _preemphasis(x):
    return signal.lfilter([1, -hparams['preemphasis']], [1], x)


def _inv_preemphasis(x):
    return signal.lfilter([1], [1, -hparams['preemphasis']], x)


def _normalize(S):
    return np.clip(
        (2 * hparams['max_abs_value']) * ((S - hparams['min_level_db']) / 
         (-hparams['min_level_db'])) - hparams['max_abs_value'],
         -hparams['max_abs_value'], hparams['max_abs_value'])


def _denormalize(D):
    return (((np.clip(D, -hparams['max_abs_value'], hparams['max_abs_value'])
              + hparams['max_abs_value']) * -hparams['min_level_db'] / 
            (2 * hparams['max_abs_value'])) + hparams['min_level_db'])


def get_hop_size():
    hop_size = hparams['hop_size']
    if hop_size is None:
        assert hparams['frame_shift_ms'] is not None
        hop_size = int(hparams['frame_shift_ms'] / 1000 * hparams['sample_rate'])
    return hop_size
