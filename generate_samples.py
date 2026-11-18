# Program: I.D. - generate_samples.py
# Programmer: Ethan-da-Tech-Wizard (written with Claude, an AI assistant)
# Last Modified: 2026-11-18
# Purpose: Synthesizes a small library of drum, bass and synth sounds with math (NumPy) and saves them as WAV files in the id_app/samples folders.
"""Generate a starter library of synthesized audio samples (drums, bass, synths) as WAV files."""

# ===== Imports =====
import os                          # for building file paths and making folders
import numpy as np                 # for the math that makes the sound waves
from scipy.io import wavfile       # for writing the finished numbers out as a .wav file

# ===== Settings =====
# How many sound measurements (samples) make up one second of audio (CD quality).
SAMPLE_RATE = 44100
# Folder where the WAV files go: an "id_app/samples" folder next to this script.
BASE_DIR = os.path.join(os.path.dirname(__file__), "id_app", "samples")

def create_dir(name):
    """Make (if needed) a sub-folder called `name` inside BASE_DIR and return its path."""
    path = os.path.join(BASE_DIR, name)
    # exist_ok=True means it is fine if the folder already exists.
    os.makedirs(path, exist_ok=True)
    return path

def save_wav(folder, filename, data):
    """Write the sound `data` (numbers from -1.0 to 1.0) to folder/filename as a 16-bit WAV file."""
    path = os.path.join(folder, filename)
    # Normalize to 16-bit PCM
    # Clamp every value into the allowed range so it cannot distort past full volume.
    data = np.clip(data, -1.0, 1.0)
    # Scale -1..1 up to the 16-bit whole-number range and convert the type.
    data = np.int16(data * 32767)
    # Save the file using our sample rate.
    wavfile.write(path, SAMPLE_RATE, data)

def generate_kick():
    """Build a kick drum: a low sine wave whose pitch drops quickly while it fades out."""
    # t is a list of time stamps covering 0.4 seconds, one per audio sample.
    t = np.linspace(0, 0.4, int(SAMPLE_RATE * 0.4), endpoint=False)
    # Pitch envelope: starts high (150Hz), drops quickly to 40Hz
    freqs = np.exp(-t * 20) * 110 + 40
    # Adding up the frequency over time gives the wave's phase (where it is in its cycle).
    phase = np.cumsum(freqs * 2 * np.pi / SAMPLE_RATE)
    # Amp envelope
    # Volume starts at full and fades away exponentially.
    env = np.exp(-t * 15)
    # The sine of the phase is the sound; multiply by the volume curve.
    audio = np.sin(phase) * env
    return audio

def generate_snare():
    """Build a snare drum: a short falling-pitch tone mixed with a burst of random noise."""
    # 0.3 seconds of time stamps.
    t = np.linspace(0, 0.3, int(SAMPLE_RATE * 0.3), endpoint=False)
    # Tone
    # Pitch starts near 250Hz and falls toward 150Hz.
    freqs = np.exp(-t * 15) * 100 + 150
    phase = np.cumsum(freqs * 2 * np.pi / SAMPLE_RATE)
    # The tone fades out fast.
    tone = np.sin(phase) * np.exp(-t * 20)
    # Noise
    # Random values between -1 and 1 make the "rattle" of the snare wires.
    noise = np.random.uniform(-1, 1, len(t))
    # The noise fades more slowly than the tone, and is cut to half volume.
    noise_env = np.exp(-t * 12)
    noise = noise * noise_env * 0.5
    # Mix the tone and the noise together.
    return tone + noise

def generate_hihat():
    """Build a hi-hat: a very short burst of noise with the low frequencies filtered out."""
    # 0.1 seconds of time stamps.
    t = np.linspace(0, 0.1, int(SAMPLE_RATE * 0.1), endpoint=False)
    noise = np.random.uniform(-1, 1, len(t))
    # High pass filter approximation
    # Subtracting the previous value from each value removes slow changes (low pitch),
    # leaving the bright, hissy part. Repeating it 5 times strengthens the effect.
    for _ in range(5):
        noise[1:] = noise[1:] - 0.9 * noise[:-1]
    # Very fast fade-out, then half volume.
    env = np.exp(-t * 50)
    return noise * env * 0.5

def generate_wub():
    """Build a wobbly bass ("wub"): a low sawtooth wave whose volume pulses 5 times a second."""
    # 0.5 seconds of time stamps.
    t = np.linspace(0, 0.5, int(SAMPLE_RATE * 0.5), endpoint=False)
    # LFO for wub (Low pass filter simulation)
    # A slow sine wave (5 times a second) shifted to run between 0 and 1; it controls the wobble.
    lfo = (np.sin(2 * np.pi * 5 * t) + 1) / 2
    # Base saw wave at 55Hz
    freq = 55
    phase = t * freq * 2 * np.pi
    # This formula turns the phase into a sawtooth wave (a ramp that jumps back down).
    saw = 2 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))
    # Simple low pass approximation using LFO amplitude
    # Multiply by the wobble and by a slow fade-out.
    audio = saw * lfo * np.exp(-t * 3)
    return audio

def generate_pluck():
    """Build a plucked synth note: a 440Hz square wave that fades out over one second."""
    # 1 second of time stamps.
    t = np.linspace(0, 1.0, int(SAMPLE_RATE * 1.0), endpoint=False)
    # 440Hz is the musical note A.
    freq = 440
    phase = t * freq * 2 * np.pi
    # The sign of a sine wave is +1 or -1, which makes a square wave.
    square = np.sign(np.sin(phase))
    env = np.exp(-t * 8)
    # Fade it out and keep the volume low (0.3).
    return square * env * 0.3

def main():
    """Create the folders, build each sound and save it as a WAV file."""
    print("Synthesizing audio library...")
    # Make the three category folders.
    drums = create_dir("drums")
    bass = create_dir("bass")
    synths = create_dir("synths")
    
    # Drum sounds.
    save_wav(drums, "kick.wav", generate_kick())
    save_wav(drums, "snare.wav", generate_snare())
    save_wav(drums, "hihat.wav", generate_hihat())
    
    # Bass sounds: the wobble bass, and a plain 40Hz sine "sub" that fades out over 1 second.
    save_wav(bass, "wub.wav", generate_wub())
    save_wav(bass, "sub.wav", np.sin(2 * np.pi * 40 * np.linspace(0, 1, SAMPLE_RATE)) * np.exp(-np.linspace(0, 5, SAMPLE_RATE)))
    
    # Synth sounds: the pluck, and a soft 440Hz sine "pad" lasting 2 seconds.
    save_wav(synths, "pluck.wav", generate_pluck())
    save_wav(synths, "pad.wav", np.sin(2 * np.pi * 440 * np.linspace(0, 2, SAMPLE_RATE * 2)) * 0.2)
    print("Audio library generated at", BASE_DIR)

# Only run main() when this file is run directly (not when imported by another file).
if __name__ == "__main__":
    main()
