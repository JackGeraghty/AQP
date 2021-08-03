from pesq import pesq
import numpy as np
import librosa

class Pypesq:
    def __init__(self, ref_file, deg_file):
        self.ref_path = ref_file
        self.deg_path = deg_file

    def load_files(self, freq:int):
        if freq >= 16000:
            freq = 16000
            self.ref = librosa.load(self.ref_path, sr=freq, mono=True) # mono true because it only takes single array
            self.deg = librosa.load(self.deg_path, sr=freq, mono=True)
            self.freq = freq
        elif freq == 8000:
            freq = 8000
            self.ref = librosa.load(self.ref_path, sr=freq, mono=True)
            self.deg = librosa.load(self.deg_path, sr=freq, mono=True)
            self.freq = freq
        else:
            print("fs (sampling frequency) should be either 8000 or 16000")

    def alignment(self):
        ref_length = len(self.ref[0])
        deg_length = len(self.deg[0])
        if ref_length > deg_length:
            return np.array(self.ref[0].tolist()[:deg_length]), self.deg[0]
        elif deg_length > ref_length:
            return self.ref[0], np.array(self.deg[0].tolist()[:ref_length])

    def comparision(self, mode:str='wb'):
        ref_sig, deg_sig = self.alignment()
        return pesq(self.freq, ref_sig, deg_sig, mode)

pypesq = Pypesq('./boz48_stereo.wav', './boz48_stereo_24kbps_aac.wav')
pypesq.load_files(16000)
pypesq.comparision('wb')
