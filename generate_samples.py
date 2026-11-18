# ==============================================================================
# Program: generate_samples.py
# Programmer: Ethan-da-Tech-Wizard
# Last Modified: November 18, 2026
# Purpose: Procedural audio synthesis tool for the I.D. creative suite.
#          Generates 16-bit PCM WAV audio samples (kick, snare, hi-hat, wub bass,
#          sub-bass, pluck synth, and ambient pad) using NumPy mathematical
#          functions (sine, saw, square waves, exponential decay envelopes,
#          and filtered white noise) and saves them via scipy.io.wavfile.
# ==============================================================================
import os
import numpy as np
from scipy.io import wavfile

# Audio standard parameters: CD-quality 44.1kHz sample rate
SAMPLE_RATE = 44100
BASE_DIR = os.path.join(os.path.dirname(__file__), "id_app", "samples")

def create_dir(name):
    """Creates a sample category directory if it does not already exist."""
    path = os.path.join(BASE_DIR, name)
    os.makedirs(path, exist_ok=True)
    return path

def save_wav(folder, filename, data):
    """Normalizes floating-point audio data to 16-bit signed integer PCM and writes to disk."""
    path = os.path.join(folder, filename)
    # Clip signal between -1.0 and 1.0 to avoid harsh digital clipping/overflow
    data = np.clip(data, -1.0, 1.0)
    # Scale normalized float [-1.0, 1.0] to 16-bit integer range [-32767, 32767]
    data = np.int16(data * 32767)
    wavfile.write(path, SAMPLE_RATE, data)

def generate_kick():
    """Synthesizes an electronic kick drum with rapid exponential pitch drop."""
    t = np.linspace(0, 0.4, int(SAMPLE_RATE * 0.4), endpoint=False)
    # Step 1: Pitch envelope: starts high (150Hz), drops quickly to 40Hz
    freqs = np.exp(-t * 20) * 110 + 40
    # Step 2: Integrate instantaneous frequency over time to compute cumulative phase
    phase = np.cumsum(freqs * 2 * np.pi / SAMPLE_RATE)
    # Step 3: Apply exponential decay amplitude envelope
    env = np.exp(-t * 15)
    audio = np.sin(phase) * env
    return audio

def generate_snare():
    """Synthesizes a snare drum combining a tonal fundamental body with filtered noise burst."""
    t = np.linspace(0, 0.3, int(SAMPLE_RATE * 0.3), endpoint=False)
    # Step 1: Synthesize tonal body with rapid frequency drop
    freqs = np.exp(-t * 15) * 100 + 150
    phase = np.cumsum(freqs * 2 * np.pi / SAMPLE_RATE)
    tone = np.sin(phase) * np.exp(-t * 20)
    # Step 2: Generate white noise burst for the snare wire rattle
    noise = np.random.uniform(-1, 1, len(t))
    noise_env = np.exp(-t * 12)
    noise = noise * noise_env * 0.5
    return tone + noise

def generate_hihat():
    """Synthesizes a closed metallic hi-hat using high-pass filtered white noise."""
    t = np.linspace(0, 0.1, int(SAMPLE_RATE * 0.1), endpoint=False)
    noise = np.random.uniform(-1, 1, len(t))
    # Approximate high-pass difference filter over 5 iterative passes
    for _ in range(5):
        noise[1:] = noise[1:] - 0.9 * noise[:-1]
    # Fast decaying amplitude envelope
    env = np.exp(-t * 50)
    return noise * env * 0.5

def generate_wub():
    """Synthesizes a dubstep-style wub bassline using saw wave modulated by a 5Hz LFO."""
    t = np.linspace(0, 0.5, int(SAMPLE_RATE * 0.5), endpoint=False)
    # Step 1: Low-Frequency Oscillator (LFO) oscillating at 5 Hz
    lfo = (np.sin(2 * np.pi * 5 * t) + 1) / 2
    # Step 2: Base sawtooth oscillator at 55Hz (A1 musical note)
    freq = 55
    phase = t * freq * 2 * np.pi
    saw = 2 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))
    # Step 3: Modulate saw wave amplitude with LFO to simulate filter cutoff sweep
    audio = saw * lfo * np.exp(-t * 3)
    return audio

def generate_pluck():
    """Synthesizes a sharp melodic synth pluck using 440Hz square wave with rapid decay."""
    t = np.linspace(0, 1.0, int(SAMPLE_RATE * 1.0), endpoint=False)
    freq = 440
    phase = t * freq * 2 * np.pi
    # Square wave via sign of sine wave
    square = np.sign(np.sin(phase))
    env = np.exp(-t * 8)
    return square * env * 0.3

def main():
    """Coordinates batch generation of complete drum, bass, and synth audio sample library."""
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
