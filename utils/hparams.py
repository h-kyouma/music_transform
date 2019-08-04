hparams = {
    # Audio:
    'sample_rate': 22050,
    'frame_shift_ms': 12.5,
    'preemphasis': 0.97,
    'min_level_db': -100,
    'ref_level_db': 20,
    'max_abs_value': 1,
    'power': 1.5,
    'fft_size': 2398, #so the output resolution of botth types of spectrograms is 1255x1200
    'hop_size': 512,
    'n_bins': 60 * 20,
    'bins_per_octave': 12 * 20,

    # Eval:
    'griffin_lim_iters': 60
}
