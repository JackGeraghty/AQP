import numpy as np
import scipy.signal as signal

def nsim_map(deg_specgram: np.ndarray, ref_specgram: np.ndarray, 
             L: int) -> np.ndarray:
    window = np.array([[0.0113, 0.0838, 0.0113], [0.0838, 0.6193, 0.0838], [0.0113, 0.0838, 0.0113]])
    #window = [w/sum(window) for w in window]
        
    # C1 and C2 constant
    K = [0.01, 0.03]
    C1 = pow(K[0] * L, 2)
    C2 = pow(K[1] * L, 2)

    mode = 'same'
    mu_d = signal.convolve2d(deg_specgram, np.rot90(window, 2), mode=mode)
    mu_r = signal.convolve2d(ref_specgram, np.rot90(window, 2), mode=mode)
        
    mu_d_sq = mu_d * mu_d
    mu_r_sq = mu_r * mu_r
    mu_r_mu_d = mu_r * mu_d

    sigma_d_sq = signal.convolve2d(deg_specgram * deg_specgram, np.rot90(window, 2), mode=mode) - mu_d_sq
    sigma_r_sq = signal.convolve2d(ref_specgram * ref_specgram, np.rot90(window, 2), mode=mode) - mu_r_sq
    sigma_r_d = signal.convolve2d(ref_specgram * deg_specgram, np.rot90(window, 2), mode=mode) - mu_r_mu_d

    sigma_r = np.sign(sigma_r_sq) * np.sqrt(np.abs(sigma_r_sq))
    sigma_d = np.sign(sigma_d_sq) * np.sqrt(np.abs(sigma_d_sq))

    L_r_d = (2 * mu_r * mu_d + C1) / (mu_r_sq + mu_d_sq + C1)
    S_r_d = (sigma_r_d + C2) / (sigma_r * sigma_d + C2)

    return np.sign(L_r_d) * np.abs(L_r_d) * np.sign(S_r_d) * np.abs(S_r_d)

