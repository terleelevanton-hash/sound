"""Vol.2 voices: amapiano log drum, orchestral/cinematic percussion,
world instruments, acid/wobble bass, fills, scratches, shouts."""
import numpy as np
from .dsp import *
from .drums import _metallic


# ------------------------------------------------------------------ bass / log drum
def log_drum(rng, freq, dur=0.75, bend=1.6, drive=1.6, tone=2400, attack=0.004):
    """Amapiano log drum: soft mallet attack, pitch drop, hollow tube body."""
    n = n_of(dur)
    t = np.arange(n) / FS
    f = freq * (1 + (bend - 1) * np.exp(-t / 0.045))
    ph = 2 * np.pi * np.cumsum(f) / FS
    body = np.sin(ph) + 0.45 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
    env = (1 - np.exp(-t / attack)) * np.exp(-t / (dur * 0.42))
    hollow = bp(noise(n, rng), 200, 1800) * np.exp(-t / 0.02) * 0.35
    sig = body * env + hollow
    sig = sat(sig, drive, 'tanh')
    sig = lp(sig, tone, 2)
    sig = peaking(sig, freq * 2, 3.0, 1.2)
    return sig


def wobble(rng, freq, dur=1.2, bpm=140, rate=1.0, depth=1400, drive=2.0):
    n = n_of(dur)
    t = np.arange(n) / FS
    pitch_env = 1 + 0.02 * np.sin(2 * np.pi * 0.3 * t)
    osc_ = saw_ph(2 * np.pi * np.cumsum(freq * pitch_env) / FS)
    osc_ += 0.5 * sqr_ph(2 * np.pi * np.cumsum(freq * 0.5 * pitch_env) / FS)
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * rate * (bpm / 60) * t - np.pi / 2)
    cut = freq * 1.5 + depth * lfo
    sig = tv_lp(osc_, cut, block=64)
    env = (1 - np.exp(-t / 0.005)) * (0.75 + 0.25 * np.exp(-t / (dur * 1.5)))
    sig = sat(sig * env, drive, 'tanh')
    return sig


def acid(rng, freq, dur=1.0, cutoff=2500, env_amt=4500, res=6.0, drive=2.2, slide=0.0):
    n = n_of(dur)
    t = np.arange(n) / FS
    f = freq * (1 + slide * np.exp(-t / 0.06))
    osc_ = saw_ph(2 * np.pi * np.cumsum(f) / FS)
    cut = cutoff + env_amt * np.exp(-t / 0.11)
    sig = tv_lp(osc_, cut, block=64)
    # pseudo resonance via narrow peaking at the moving cutoff
    sig = peaking(sig, float(np.mean(cut[:200])), 3 + res * 1.2, 3.0)
    env = (1 - np.exp(-t / 0.002)) * np.exp(-t / (dur * 0.45))
    sig = sat(sig * env, drive, 'tanh')
    return sig


# ------------------------------------------------------------------ cinematic / tonal perc
def timpani(rng, freq, dur=2.2, mallet=0.5, drive=1.2):
    n = n_of(dur)
    t = np.arange(n) / FS
    f = freq * (1 + 0.10 * np.exp(-t / 0.05))
    sig = np.zeros(n)
    for r, a, d in [(1.0, 1.0, 1.0), (1.5, 0.5, 0.6), (2.0, 0.35, 0.45), (2.9, 0.18, 0.3), (4.1, 0.1, 0.2)]:
        sig += a * np.sin(2 * np.pi * np.cumsum(f * r) / FS) * np.exp(-t / (dur * d * 0.55))
    sig += bp(noise(n, rng), 150, 4000) * np.exp(-t / 0.03) * mallet
    sig *= (1 - np.exp(-t / 0.004))
    sig = reverb(sig, wet=0.18, decay=1.2, tone=4000, rng=rng)[:n]
    return sat(lp(sig, 6000), drive, 'tanh')


def gong(rng, freq=90, dur=4.0, swell=0.35):
    n = n_of(dur)
    t = np.arange(n) / FS
    sig = np.zeros(n)
    for k in range(9):
        r = rng.uniform(1.0, 6.5)
        sig += (1 / (k + 1.4)) * np.sin(2 * np.pi * freq * r * t + rng.uniform(0, 6)) \
            * np.exp(-t / (dur * rng.uniform(0.35, 0.9)))
    sig += 0.25 * bp(noise(n, rng), 200, 6000) * np.exp(-t / (dur * 0.25))
    env = (1 - np.exp(-t / swell))
    sig *= env
    sig = reverb(sig, wet=0.4, decay=dur * 0.5, tone=5000, rng=rng)[:n]
    return sat(lp(sig, 9000), 1.1, 'tanh')


def singing_bowl(rng, freq=220, dur=3.5):
    n = n_of(dur)
    t = np.arange(n) / FS
    sig = np.zeros(n)
    for r, g, d in [(1.0, 1.0, 1.0), (2.71, 0.55, 0.7), (5.15, 0.3, 0.45), (8.6, 0.14, 0.28)]:
        sig += g * np.sin(2 * np.pi * freq * r * t) * np.exp(-t / (dur * d * 0.6))
    # beating between two near-identical modes
    sig += 0.6 * np.sin(2 * np.pi * freq * 1.002 * t) * np.exp(-t / (dur * 0.6))
    sig *= (1 - np.exp(-t / 0.02))
    sig += 0.15 * bp(noise(n, rng), 2000, 9000) * np.exp(-t / 0.01)
    return sat(lp(sig, 8000), 1.05, 'tanh')


def tubular_bells(rng, freq, dur=3.0):
    n = n_of(dur)
    t = np.arange(n) / FS
    sig = np.zeros(n)
    for r, g, d in [(1.0, 1.0, 1.0), (2.0, 0.65, 0.7), (2.41, 0.4, 0.5), (3.03, 0.28, 0.4),
                    (4.16, 0.16, 0.3), (5.43, 0.1, 0.22)]:
        sig += g * np.sin(2 * np.pi * freq * r * t) * np.exp(-t / (dur * d * 0.55))
    sig += 0.2 * bp(noise(n, rng), 3000, 12000) * np.exp(-t / 0.006)
    sig *= (1 - np.exp(-t / 0.003))
    sig = reverb(sig, wet=0.3, decay=dur * 0.5, tone=7000, rng=rng)[:n]
    return sat(sig, 1.05, 'tanh')


def chimes(rng, base=1400, count=6, dur=2.4):
    n = n_of(dur)
    sig = np.zeros(n)
    for i in range(count):
        off = n_of(i * rng.uniform(0.05, 0.16))
        if off >= n:
            break
        f = base * rng.uniform(0.7, 1.9)
        m = n - off
        tt = np.arange(m) / FS
        h = np.zeros(m)
        for r, g in [(1, 1), (2.76, 0.4), (5.4, 0.18)]:
            h += g * np.sin(2 * np.pi * f * r * tt) * np.exp(-tt / (dur * rng.uniform(0.2, 0.5)))
        sig[off:] += h * rng.uniform(0.3, 0.8)
    return sat(hp(sig, 600), 1.05, 'tanh')


def cymbal_swell(rng, dur=2.5, rise=0.9):
    """Reverse-cymbal style swell that crescendos into a hit."""
    base = D_crash = None
    from . import drums as D
    x = D.crash(rng, decay=dur * 0.9, hp_f=3000)
    x = x[:n_of(dur)]
    env = np.linspace(0, 1, len(x)) ** 2.2
    x = x * env
    x[-n_of(0.02):] *= np.linspace(1, 0.4, n_of(0.02))
    return sat(x, 1.1, 'tanh')


def wood_plank(rng, tone=520, decay=0.09):
    n = n_of(decay * 6 + 0.03)
    t = np.arange(n) / FS
    sig = np.sin(2 * np.pi * tone * t) * np.exp(-t / decay)
    sig += 0.6 * np.sin(2 * np.pi * tone * 2.72 * t) * np.exp(-t / (decay * 0.5))
    sig += 0.35 * bp(noise(n, rng), 600, 6000) * np.exp(-t / 0.004)
    return sat(sig, 1.25, 'tanh')


def timbales(rng, f0=330, decay=0.3, shell=0.45):
    n = n_of(decay * 3.4 + 0.05)
    t = np.arange(n) / FS
    f = f0 * (1 + 0.28 * np.exp(-t / 0.02))
    body = np.sin(2 * np.pi * np.cumsum(f) / FS) * np.exp(-t / decay)
    body += 0.45 * np.sin(2 * np.pi * np.cumsum(f * 1.62) / FS) * np.exp(-t / (decay * 0.45))
    nz = bp(noise(n, rng), 900, 7000) * np.exp(-t / 0.012) * shell
    return sat(hp(body + nz, 180), 1.25, 'tanh')


def agogo(rng, f1=720, f2=1080, decay=0.22):
    n = n_of(decay * 4 + 0.05)
    t = np.arange(n) / FS
    sig = np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * f2 * t) * 0.7
    sig += 0.4 * np.sin(2 * np.pi * f1 * 2.9 * t)
    sig *= np.exp(-t / decay) * (1 - np.exp(-t / 0.001))
    sig += 0.3 * bp(noise(n, rng), 1500, 8000) * np.exp(-t / 0.004)
    return sat(sig, 1.3, 'tanh')


def surdo(rng, f0=70, decay=0.5):
    n = n_of(decay * 3)
    t = np.arange(n) / FS
    f = f0 * (1 + 0.35 * np.exp(-t / 0.04))
    body = np.sin(2 * np.pi * np.cumsum(f) / FS) * np.exp(-t / decay)
    nz = bp(noise(n, rng), 100, 3000) * np.exp(-t / 0.04) * 0.6
    return lp(sat(body + nz, 1.3, 'tanh'), 4000)


# ------------------------------------------------------------------ world / reeds
def didgeridoo(rng, freq=70, dur=1.8):
    n = n_of(dur)
    t = np.arange(n) / FS
    vib = 1 + 0.01 * np.sin(2 * np.pi * 3.2 * t)
    ph = 2 * np.pi * np.cumsum(freq * vib) / FS
    sig = saw_ph(ph) * 0.6 + np.sin(ph) * 0.5
    sig = formant(sig, [320, 780, 1400], [4, 5, 6], [1.0, 0.6, 0.35])
    drone = 1 + 0.3 * np.sin(2 * np.pi * 24 * t)
    noise_ = bp(noise(n, rng), 300, 3000) * 0.25
    env = (1 - np.exp(-t / 0.08)) * (0.8 + 0.2 * np.exp(-t / 0.6))
    return sat(lp((sig + noise_) * env * drone, 5000), 1.4, 'tanh')


def accordion(rng, freq, dur=1.6):
    n = n_of(dur)
    t = np.arange(n) / FS
    vib = 1 + 0.005 * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.2) / 0.4, 0, 1)
    osc_ = np.zeros(n)
    for d in (-0.006, 0, 0.006):
        osc_ += saw_ph(2 * np.pi * np.cumsum(freq * (1 + d) * vib) / FS) / 3
    env = (1 - np.exp(-t / 0.03)) * (0.75 + 0.25 * np.exp(-t / 0.4))
    sig = osc_ * env
    sig += 0.06 * bp(noise(n, rng), 1500, 6000) * np.exp(-t / 0.05)
    return sat(lp(hp(sig, 120), 6000), 1.25, 'tanh')


def harmonica(rng, freq, dur=1.5):
    n = n_of(dur)
    t = np.arange(n) / FS
    vib = 1 + 0.006 * np.sin(2 * np.pi * 6 * t) * np.clip((t - 0.15) / 0.4, 0, 1)
    ph = 2 * np.pi * np.cumsum(freq * vib) / FS
    sig = np.sin(ph) + 0.55 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph) + 0.15 * np.sin(4 * ph)
    env = (1 - np.exp(-t / 0.02)) * (0.8 + 0.2 * np.exp(-t / 0.5))
    breath = bp(noise(n, rng), 1200, 7000) * 0.12
    sig = (sig + breath) * env
    return sat(lp(sig, 7000), 1.3, 'tanh')


def guzheng(rng, freq, dur=1.8, bend=0.02):
    sig = ks_pluck(freq, dur, bright=0.85, damp=0.35, rng=rng)
    n = len(sig)
    t = np.arange(n) / FS
    # characteristic pitch bend on attack
    bend_env = 1 + bend * np.exp(-t / 0.05)
    idx = np.cumsum(bend_env)
    idx = idx / idx[-1] * (n - 1)
    sig = np.interp(idx, np.arange(n), sig)
    sig = peaking(sig, 1800, 4.0, 1.2)
    sig = hp(sig, 130)
    return sat(sig, 1.2, 'tanh')


# ------------------------------------------------------------------ fx / voice
def scratch(rng, dur=0.35, rev=1.0):
    n = n_of(dur)
    t = np.arange(n) / FS
    # sample-scratch emulation: noise through fast pitch-modulated bandpass + gating
    lfo = np.sin(2 * np.pi * 6 * rev * t) * 600 + 1800
    sig = tv_bp(noise(n, rng), lfo * 0.6, lfo * 1.5, block=64)
    gate = (np.sin(2 * np.pi * 3.2 * rev * t) > 0).astype(float)
    sig = sig * (0.4 + 0.6 * gate)
    sig += 0.3 * bp(noise(n, rng), 200, 2500)
    env = (1 - np.exp(-t / 0.004)) * np.exp(-t / (dur * 0.9))
    return sat(sig * env, 1.5, 'tanh')


def shout(rng, freq=180, dur=0.55, vowel='e'):
    n = n_of(dur)
    t = np.arange(n) / FS
    f = freq * (1 - 0.18 * (t / dur) ** 0.8)     # falling pitch like a shout
    ph = 2 * np.pi * np.cumsum(f) / FS
    glottal = saw_ph(ph) + 0.5 * sqr_ph(ph * 1.0) + 0.15 * noise(n, rng)
    F = {'e': ([700, 1800, 2600], [7, 9, 11]), 'a': ([800, 1250, 2700], [6, 8, 10]),
         'o': ([520, 900, 2500], [5, 7, 9])}[vowel]
    sig = 0.2 * glottal + 1.8 * formant(glottal, F[0], F[1], [1, 0.7, 0.4])
    env = (1 - np.exp(-t / 0.006)) * np.exp(-t / (dur * 0.5))
    sig = lp(hp(sig * env, 200), 6500)
    sig = reverb(sig, wet=0.18, decay=0.35, tone=6000, rng=rng)[:n]
    return sat(sig, 1.4, 'tanh')


def air_horn(rng, dur=1.6, f=220):
    n = n_of(dur)
    t = np.arange(n) / FS
    sig = np.zeros(n)
    for r in (1, 1.5, 2, 2.5, 3, 4, 5):
        sig += (1 / r) * saw_ph(2 * np.pi * f * r * t + rng.uniform(0, 6))
    env = (1 - np.exp(-t / 0.02)) * (1 - np.exp(-(dur - t) / 0.15))
    sig = sat(sig * env / 3, 2.5, 'tanh')
    sig = formant(sig, [600, 1400, 2600], [3, 4, 5], [1, 0.7, 0.4])
    sig = lp(sig, 7000)
    return sig
