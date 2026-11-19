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

# How this file fits the project
# ------------------------------
# I.D. is a design-stage repository for a desktop creative suite (a script editor plus a step-sequencer
# "DAW", see docs/IDE_VISION_SPEC.md and project.ideas). This script is the only executable piece: it
# builds a small royalty-free starter library so the suite has sounds to play without shipping or
# downloading any recordings. Every sound is computed from formulas, so the output is reproducible
# except for the two noise-based sounds (snare, hi-hat), which draw fresh random numbers each run.
#
# Inputs : none (no arguments, no network, no existing audio).
# Outputs: id_app/samples/{drums,bass,synths}/*.wav next to this file, 16-bit mono PCM at 44.1 kHz:
#          drums/kick.wav, snare.wav, hihat.wav; bass/wub.wav, sub.wav; synths/pluck.wav, pad.wav.
#          Existing files with the same names are overwritten.
# Run    : python3 generate_samples.py       (needs numpy and scipy)
# Limits : there are no automated tests. Waveforms are mathematically simple (for example the square
#          wave in generate_pluck is not band-limited, so it aliases at high pitch) and the "pad" is a
#          bare sine with no fade, which can click at its start and end. These are demo sounds.

import os
import numpy as np
from scipy.io import wavfile

# Sample rate in Hz: 44.1 kHz is the CD standard and covers the audible range (Nyquist limit 22.05 kHz).
# Every duration below is converted to a sample count by multiplying by this value.
SAMPLE_RATE = 44100

# Output root, anchored to this file so the result does not depend on the caller's working directory.
# "id_app" is the folder name the creative-suite app expects to load its starter samples from.
BASE_DIR = os.path.join(os.path.dirname(__file__), "id_app", "samples")


def create_dir(name):
    """Creates a sample category directory if it does not already exist.

    Args:
        name: Category folder name below BASE_DIR, e.g. "drums".

    Returns:
        The full path of the (now existing) directory.

    Side effects:
        Creates BASE_DIR and the category folder on disk; safe to call repeatedly.
    """
    path = os.path.join(BASE_DIR, name)

    # exist_ok makes re-running the script idempotent instead of raising FileExistsError.
    os.makedirs(path, exist_ok=True)
    return path


def save_wav(folder, filename, data):
    """
    Normalizes floating-point audio data to 16-bit signed integer PCM and writes to disk.

    Digital Audio Invariants:
      1. Clamps audio array to [-1.0, 1.0] headroom ceiling to prevent wraparound distortion.
      2. Quantizes normalized floating-point samples to 16-bit signed two's complement integers
         (the scale factor 32767 keeps the result inside [-32767, 32767]).
      3. Serializes header chunks (RIFF, fmt , data) conforming to the Microsoft WAV specification.

    Args:
        folder: Existing directory to write into (normally from create_dir).
        filename: File name including the .wav extension.
        data: 1-D float array of samples, nominally in [-1.0, 1.0]; louder values are clipped.

    Side effects:
        Writes (or overwrites) one mono WAV file at SAMPLE_RATE.
    """
    path = os.path.join(folder, filename)

    # Clip first: a float above 1.0 would overflow int16 and wrap to a loud negative value (a harsh
    # click). Clipping instead causes only mild distortion on rare peaks.
    data = np.clip(data, -1.0, 1.0)

    # Scale by 32767 (not 32768) so +1.0 maps to the largest positive int16 and nothing overflows;
    # the one-step asymmetry at -32768 is inaudible.
    data = np.int16(data * 32767)
    wavfile.write(path, SAMPLE_RATE, data)


def generate_kick():
    """
    Synthesizes an electronic kick drum with rapid exponential pitch drop.

    Mathematical Synthesis Model:
      - Time domain: t in [0, 0.4] seconds sampled at 44.1 kHz.
      - Instantaneous frequency f(t) = 110 * exp(-20t) + 40 Hz, sweeping from 150 Hz to 40 Hz sub.
      - Phase accumulator: phi(t) = integral(2 * pi * f(tau) dtau) approximated by discrete cumulative sum.
      - Amplitude envelope: A(t) = exp(-15t) modelling exponential acoustic energy dissipation.

    Returns:
        1-D float array of int(0.4 * SAMPLE_RATE) samples, peak amplitude <= 1.0.
    """
    # endpoint=False keeps the sample spacing exactly 1/SAMPLE_RATE (no duplicated end point).
    t = np.linspace(0, 0.4, int(SAMPLE_RATE * 0.4), endpoint=False)

    # The "thump" of a kick is a sine that starts around 150 Hz (the beater hit) and falls fast to a
    # 40 Hz body tone. exp(-20t) has a time constant of 50 ms, so the sweep is almost finished after
    # about 150 ms; the +40 is the floor the pitch settles on.
    freqs = np.exp(-t * 20) * 110 + 40

    # Phase is the running sum of frequency. Computing sin(2*pi*f(t)*t) directly would be wrong for a
    # changing f(t): it would jump in pitch instead of gliding. Dividing by SAMPLE_RATE converts
    # "radians per second" into "radians per sample".
    phase = np.cumsum(freqs * 2 * np.pi / SAMPLE_RATE)

    # Amplitude fades with a 67 ms time constant, so the 0.4 s buffer ends near silence
    # (exp(-6) is about 0.25 percent), avoiding a click at the end of the file.
    env = np.exp(-t * 15)
    audio = np.sin(phase) * env
    return audio


def generate_snare():
    """Synthesizes a snare drum combining a tonal fundamental body with filtered noise burst.

    Returns:
        1-D float array of int(0.3 * SAMPLE_RATE) samples. The sum of tone and noise can exceed 1.0
        briefly, which save_wav clips. Uses np.random, so each run differs slightly.
    """
    t = np.linspace(0, 0.3, int(SAMPLE_RATE * 0.3), endpoint=False)

    # Tonal "drum head" part: pitch glides from 250 Hz down to 150 Hz, and fades quickly (time
    # constant 50 ms), giving the short "crack" body.
    freqs = np.exp(-t * 15) * 100 + 150
    phase = np.cumsum(freqs * 2 * np.pi / SAMPLE_RATE)
    tone = np.sin(phase) * np.exp(-t * 20)

    # The snare wires are modelled as white noise (uniform random samples, equal energy at all
    # frequencies). It decays more slowly (83 ms) than the tone so the rattle trails the hit, and is
    # halved so the noise does not mask the body.
    noise = np.random.uniform(-1, 1, len(t))
    noise_env = np.exp(-t * 12)
    noise = noise * noise_env * 0.5
    return tone + noise


def generate_hihat():
    """Synthesizes a closed metallic hi-hat using high-pass filtered white noise.

    Returns:
        1-D float array of int(0.1 * SAMPLE_RATE) samples, amplitude at most 0.5 before clipping.
        Uses np.random, so each run differs slightly.
    """
    t = np.linspace(0, 0.1, int(SAMPLE_RATE * 0.1), endpoint=False)
    noise = np.random.uniform(-1, 1, len(t))

    # Cheap high-pass filter: subtracting 0.9 of the previous sample removes slow (low-frequency)
    # movement and keeps rapid change, so what is left sounds bright and metallic. NumPy evaluates the
    # right-hand side before assigning, so each pass uses the unmodified previous values. Repeating it
    # 5 times makes the cut steeper; the amplitude grows with each pass, which is why the final gain of
    # 0.5 (and the clipping in save_wav) matters.
    for _ in range(5):
        noise[1:] = noise[1:] - 0.9 * noise[:-1]

    # Very fast decay (20 ms time constant) makes the hat "closed" (a short tick) instead of open.
    env = np.exp(-t * 50)
    return noise * env * 0.5


def generate_wub():
    """Synthesizes a dubstep-style wub bassline using saw wave modulated by a 5Hz LFO.

    Returns:
        1-D float array of int(0.5 * SAMPLE_RATE) samples in [-1, 1].
    """
    t = np.linspace(0, 0.5, int(SAMPLE_RATE * 0.5), endpoint=False)

    # The "wub" is a slow loudness wobble. This low-frequency oscillator (LFO) is a 5 Hz sine shifted
    # and scaled from [-1, 1] to [0, 1], so it only ever reduces the volume and never inverts the wave.
    lfo = (np.sin(2 * np.pi * 5 * t) + 1) / 2

    # Carrier: a sawtooth at 55 Hz (the note A1). The expression 2*(x - floor(x + 0.5)) with
    # x = cycles elapsed produces a ramp from -1 to +1 that restarts every cycle. It is rich in
    # harmonics, which is what makes bass sounds buzz.
    freq = 55
    phase = t * freq * 2 * np.pi
    saw = 2 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))

    # Multiplying by the LFO gives an amplitude wobble (a true filter sweep would change the harmonics,
    # which this shortcut does not do). The exp(-3t) fade lets the note die away over half a second.
    audio = saw * lfo * np.exp(-t * 3)
    return audio


def generate_pluck():
    """Synthesizes a sharp melodic synth pluck using 440Hz square wave with rapid decay.

    Returns:
        1-D float array of SAMPLE_RATE samples (1 second), peak amplitude 0.3.
    """
    t = np.linspace(0, 1.0, int(SAMPLE_RATE * 1.0), endpoint=False)

    # 440 Hz is concert pitch A4, the usual tuning reference (project.ideas also stores tuning_hz 440).
    freq = 440
    phase = t * freq * 2 * np.pi

    # A square wave is the sign of a sine: it jumps between -1 and +1. It has only odd harmonics, giving
    # the hollow "chiptune" colour. It is not band-limited, so some harmonics fold back as aliasing.
    square = np.sign(np.sin(phase))

    # Exponential decay (125 ms time constant) turns the held tone into a plucked note; the 0.3 gain
    # leaves headroom because a square wave is perceived as much louder than a sine at the same peak.
    env = np.exp(-t * 8)
    return square * env * 0.3


def main():
    """Coordinates batch generation of complete drum, bass, and synth audio sample library.

    Side effects:
        Creates the id_app/samples folder tree and writes seven WAV files; prints progress.
    """
    print("Synthesizing audio library...")
    drums = create_dir("drums")
    bass = create_dir("bass")
    synths = create_dir("synths")

    # Drums come straight from the generator functions above.
    save_wav(drums, "kick.wav", generate_kick())
    save_wav(drums, "snare.wav", generate_snare())
    save_wav(drums, "hihat.wav", generate_hihat())

    save_wav(bass, "wub.wav", generate_wub())

    # Sub bass is built inline: a 40 Hz sine lasting 1 s whose loudness falls as exp(-5 * seconds).
    # linspace(0, 5, SAMPLE_RATE) is the exponent axis: it runs 0 to 5 across the one second of samples.
    save_wav(bass, "sub.wav", np.sin(2 * np.pi * 40 * np.linspace(0, 1, SAMPLE_RATE)) * np.exp(-np.linspace(0, 5, SAMPLE_RATE)))

    save_wav(synths, "pluck.wav", generate_pluck())

    # Pad: a steady 440 Hz sine for 2 s at low gain (0.2). It is the simplest possible sustained tone and
    # has no fade-in or fade-out, so it can click where it starts and stops.
    save_wav(synths, "pad.wav", np.sin(2 * np.pi * 440 * np.linspace(0, 2, SAMPLE_RATE * 2)) * 0.2)
    print("Audio library generated at", BASE_DIR)


# Only run when executed as a script, so importing the module (for example to reuse generate_kick) has
# no side effects on disk.
if __name__ == "__main__":
    main()
