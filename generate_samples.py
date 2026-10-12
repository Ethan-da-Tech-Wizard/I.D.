import os
import numpy as np
from scipy.io import wavfile

SAMPLE_RATE = 44100
BASE_DIR = os.path.join(os.path.dirname(__file__), "id_app", "samples")

def create_dir(name):
    path = os.path.join(BASE_DIR, name)
    os.makedirs(path, exist_ok=True)
    return path

def save_wav(folder, filename, data):
    path = os.path.join(folder, filename)
    # Normalize to 16-bit PCM
    data = np.clip(data, -1.0, 1.0)
    data = np.int16(data * 32767)
    wavfile.write(path, SAMPLE_RATE, data)

def generate_kick():
    t = np.linspace(0, 0.4, int(SAMPLE_RATE * 0.4), endpoint=False)
    # Pitch envelope: starts high (150Hz), drops quickly to 40Hz
    freqs = np.exp(-t * 20) * 110 + 40
    phase = np.cumsum(freqs * 2 * np.pi / SAMPLE_RATE)
    # Amp envelope
    env = np.exp(-t * 15)
    audio = np.sin(phase) * env
    return audio

def generate_snare():
    t = np.linspace(0, 0.3, int(SAMPLE_RATE * 0.3), endpoint=False)
    # Tone
    freqs = np.exp(-t * 15) * 100 + 150
    phase = np.cumsum(freqs * 2 * np.pi / SAMPLE_RATE)
    tone = np.sin(phase) * np.exp(-t * 20)
    # Noise
    noise = np.random.uniform(-1, 1, len(t))
    noise_env = np.exp(-t * 12)
    noise = noise * noise_env * 0.5
    return tone + noise

def generate_hihat():
    t = np.linspace(0, 0.1, int(SAMPLE_RATE * 0.1), endpoint=False)
    noise = np.random.uniform(-1, 1, len(t))
    # High pass filter approximation
    for _ in range(5):
        noise[1:] = noise[1:] - 0.9 * noise[:-1]
    env = np.exp(-t * 50)
    return noise * env * 0.5

def generate_wub():
    t = np.linspace(0, 0.5, int(SAMPLE_RATE * 0.5), endpoint=False)
    # LFO for wub (Low pass filter simulation)
    lfo = (np.sin(2 * np.pi * 5 * t) + 1) / 2
    # Base saw wave at 55Hz
    freq = 55
    phase = t * freq * 2 * np.pi
    saw = 2 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))
    # Simple low pass approximation using LFO amplitude
    audio = saw * lfo * np.exp(-t * 3)
    return audio

def generate_pluck():
    t = np.linspace(0, 1.0, int(SAMPLE_RATE * 1.0), endpoint=False)
    freq = 440
    phase = t * freq * 2 * np.pi
    square = np.sign(np.sin(phase))
    env = np.exp(-t * 8)
    return square * env * 0.3

def main():
    print("Synthesizing audio library...")
    drums = create_dir("drums")
    bass = create_dir("bass")
    synths = create_dir("synths")
    
    save_wav(drums, "kick.wav", generate_kick())
    save_wav(drums, "snare.wav", generate_snare())
    save_wav(drums, "hihat.wav", generate_hihat())
    
    save_wav(bass, "wub.wav", generate_wub())
    save_wav(bass, "sub.wav", np.sin(2 * np.pi * 40 * np.linspace(0, 1, SAMPLE_RATE)) * np.exp(-np.linspace(0, 5, SAMPLE_RATE)))
    
    save_wav(synths, "pluck.wav", generate_pluck())
    save_wav(synths, "pad.wav", np.sin(2 * np.pi * 440 * np.linspace(0, 2, SAMPLE_RATE * 2)) * 0.2)
    print("Audio library generated at", BASE_DIR)

if __name__ == "__main__":
    main()
