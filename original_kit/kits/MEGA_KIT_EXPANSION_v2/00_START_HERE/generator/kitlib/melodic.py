"""Synthesized melodic instruments (tuned to MIDI notes)."""
import numpy as np
from .dsp import *
from .drums import _metallic


def _partials(freq, dur, parts, rng=None, attack=0.002, noise_amt=0.0,
              noise_lo=1500, noise_hi=9000, inharm=0.0, beat=0.0, rng_seed=None):
    rng = rng or np.random.default_rng(rng_seed)
    n = n_of(dur)
    t = np.arange(n) / FS
    sig = np.zeros(n)
    for (ratio, amp, dec) in parts:
        f = freq * ratio * np.sqrt(1 + inharm * ratio ** 2)
        ph = 2 * np.pi * f * t
        if beat:
            s = (np.sin(ph) + np.sin(ph * (1 + beat))) * 0.5
        else:
            s = np.sin(ph)
        sig += amp * s * np.exp(-t / max(dec, 1e-3))
    if noise_amt:
        nz = bp(noise(n, rng), noise_lo, min(noise_hi, FS * 0.45))
        sig += noise_amt * nz * np.exp(-t / 0.004)
    sig *= (1 - np.exp(-t / max(attack, 1e-4)))
    return sig


# ------------------------------------------------------------------ KEYS
def piano(freq, dur=2.2, bright=0.5, rng=None):
    rng = rng or np.random.default_rng()
    n = n_of(dur)
    t = np.arange(n) / FS
    B = 0.00035 * (1.0 + 0.4 * bright)
    parts = []
    for k in range(1, 22):
        amp = (1.0 / k ** (1.15 + 0.5 * (1 - bright))) * (0.6 + 0.8 * bright if k > 1 else 1.0)
        f = freq * k * np.sqrt(1 + B * k ** 2)
        if f > FS * 0.45:
            break
        dec = (dur * 0.9) / (1 + 0.55 * (k - 1)) * (0.8 + 0.5 * bright)
        parts.append((k, amp, dec))
    sig = np.zeros(n)
    for k, amp, dec in parts:
        f = freq * k * np.sqrt(1 + B * k ** 2)
        # two slightly detuned strings
        s = np.sin(2 * np.pi * f * t) + np.sin(2 * np.pi * f * 1.0006 * t) * 0.7
        s += 0.35 * np.sin(2 * np.pi * f * 1.0013 * t)
        sig += amp * s * np.exp(-t / dec)
    # hammer noise + felt thump
    nz = bp(noise(n, rng), 800, 6000) * np.exp(-t / 0.006) * (0.25 + 0.3 * bright)
    sig += nz
    sig += 0.25 * np.sin(2 * np.pi * freq * 0.5 * t) * np.exp(-t / 0.5)
    sig *= (1 - np.exp(-t / 0.0015))
    sig = lp(sig, 4000 + 9000 * bright)
    tail = n_of(0.03)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sig


def rhodes(freq, dur=2.4, bark=1.0, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    idx = (2.2 * bark) * np.exp(-t / 0.18) + 0.35
    mod = np.sin(2 * np.pi * freq * t + 0.6 * np.sin(2 * np.pi * freq * 1.0 * t))
    carrier = np.sin(2 * np.pi * freq * t + idx * mod)
    carrier += 0.4 * np.sin(2 * np.pi * freq * 2.0 * t + (idx * 0.5) * mod)
    env = (1 - np.exp(-t / 0.002)) * (0.55 * np.exp(-t / (dur * 0.55)) + 0.45 * np.exp(-t / 0.25))
    sig = carrier * env
    sig += 0.2 * np.sin(2 * np.pi * freq * 8 * t) * np.exp(-t / 0.03) * bark  # tine ping
    sig = lp(sig, 6500, 2)
    tail = n_of(0.04)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sat(sig, 1.1, 'tanh')


def fm_ep(freq, dur=2.0, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    idx = 3.0 * np.exp(-t / 0.25) + 0.2
    mod = np.sin(2 * np.pi * freq * 2.0 * t)
    sig = np.sin(2 * np.pi * freq * t + idx * mod) * np.exp(-t / 0.7)
    sig += 0.15 * np.sin(2 * np.pi * freq * 4 * t) * np.exp(-t / 0.15)
    sig *= (1 - np.exp(-t / 0.002))
    return sat(lp(sig, 6000), 1.2, 'tanh')


def organ(freq, dur=2.2, drawbars=(1.0, 0.6, 0.4, 0.25, 0.12), rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    ratios = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
    sig = np.zeros(n)
    for r, g in zip(ratios, list(drawbars) + [0.08] * 3):
        sig += g * np.sin(2 * np.pi * freq * r * t + rng.uniform(0, 6))
    env = (1 - np.exp(-t / 0.012)) * (0.75 + 0.25 * np.exp(-t / 0.4))
    sig *= env
    sig += 0.06 * noise(n, rng) * np.exp(-t / 0.05)  # key click
    sig += 0.12 * np.sin(2 * np.pi * freq * 0.25 * t) * env  # leakage
    tail = n_of(0.05)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sat(lp(sig, 7000), 1.1, 'tanh')


def music_box(freq, dur=1.8, rng=None):
    parts = [(1.0, 1.0, dur * 0.9), (2.76, 0.45, dur * 0.45), (5.40, 0.22, dur * 0.25),
             (8.93, 0.1, dur * 0.15), (13.3, 0.05, dur * 0.08)]
    sig = _partials(freq, dur, parts, rng, attack=0.001, noise_amt=0.25, noise_lo=3000, noise_hi=14000)
    return hp(sig, 400)


def celesta(freq, dur=1.8, rng=None):
    parts = [(1.0, 1.0, dur * 0.8), (2.0, 0.35, dur * 0.4), (4.02, 0.12, dur * 0.2)]
    sig = _partials(freq, dur, parts, rng, attack=0.002, noise_amt=0.15, noise_lo=2000)
    return lp(sig, 9000)


def harpsichord(freq, dur=1.6, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    sig = np.zeros(n)
    for k, a, d in [(1, 1, 0.9), (2, 0.5, 0.5), (3, 0.3, 0.35), (4, 0.2, 0.25), (5, 0.14, 0.2), (7, 0.08, 0.15)]:
        sig += a * saw_ph(2 * np.pi * freq * k * t * (1 + 0.0004 * k)) * np.exp(-t / (dur * d))
    sig += 0.3 * bp(noise(n, rng), 3000, 12000) * np.exp(-t / 0.004)
    sig *= (1 - np.exp(-t / 0.0008))
    tail = n_of(0.02)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sat(lp(hp(sig, 150), 11000), 1.2, 'tanh')


# ------------------------------------------------------------------ MALLETS / BARS
def marimba(freq, dur=1.2, rng=None):
    parts = [(1.0, 1.0, dur * 0.7), (3.93, 0.35, dur * 0.16), (9.2, 0.1, dur * 0.06)]
    sig = _partials(freq, dur, parts, rng, attack=0.0015, noise_amt=0.35, noise_lo=800, noise_hi=5000)
    sig = lp(sig, 6000)
    tail = n_of(0.03)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sig


def vibraphone(freq, dur=2.2, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    sig = np.zeros(n)
    for r, a, d in [(1, 1, 1), (4.0, 0.4, 0.5), (10.0, 0.15, 0.25)]:
        sig += a * np.sin(2 * np.pi * freq * r * t) * np.exp(-t / (dur * d * 0.7))
    trem = 1 - 0.35 * (0.5 + 0.5 * np.sin(2 * np.pi * 5.2 * t))
    sig *= trem * (1 - np.exp(-t / 0.004))
    sig += 0.2 * bp(noise(n, rng), 2000, 8000) * np.exp(-t / 0.003)
    tail = n_of(0.05)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sat(lp(sig, 8000), 1.05, 'tanh')


def glockenspiel(freq, dur=1.6, rng=None):
    parts = [(1.0, 1.0, dur * 0.9), (2.76, 0.6, dur * 0.5), (5.4, 0.35, dur * 0.3), (8.9, 0.2, dur * 0.18)]
    sig = _partials(freq, dur, parts, rng, attack=0.001, noise_amt=0.2, noise_lo=4000)
    return hp(sig, 300)


def kalimba(freq, dur=1.6, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    sig = np.sin(2 * np.pi * freq * t) * np.exp(-t / (dur * 0.55))
    sig += 0.35 * np.sin(2 * np.pi * freq * 5.4 * t) * np.exp(-t / (dur * 0.12))
    sig += 0.15 * np.sin(2 * np.pi * freq * 2.0 * t) * np.exp(-t / (dur * 0.3))
    sig += 0.4 * bp(noise(n, rng), 1500, 6000) * np.exp(-t / 0.003)
    sig *= (1 - np.exp(-t / 0.001))
    tail = n_of(0.04)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sat(lp(sig, 7000), 1.1, 'tanh')


def steel_drum(freq, dur=1.5, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    f = freq * (1 + 0.02 * np.exp(-t / 0.03))
    ph = 2 * np.pi * np.cumsum(f) / FS
    sig = np.sin(ph) * np.exp(-t / (dur * 0.6))
    sig += 0.5 * np.sin(2 * ph * 1.01) * np.exp(-t / (dur * 0.35))
    sig += 0.28 * np.sin(3 * ph * 1.02) * np.exp(-t / (dur * 0.22))
    sig += 0.15 * np.sin(4.2 * ph) * np.exp(-t / (dur * 0.15))
    sig += 0.35 * bp(noise(n, rng), 1200, 7000) * np.exp(-t / 0.008)
    sig *= (1 - np.exp(-t / 0.0015))
    tail = n_of(0.03)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sat(lp(sig, 9000), 1.2, 'tanh')


def handpan(freq, dur=2.2, rng=None):
    return _partials(freq, dur, [(1, 1, dur * 0.8), (2.0, 0.4, dur * 0.5), (2.94, 0.25, dur * 0.35),
                                 (4.1, 0.12, dur * 0.2)], rng, attack=0.002, beat=0.0022,
                    noise_amt=0.2, noise_lo=600, noise_hi=4000)


# ------------------------------------------------------------------ SYNTHS
def pluck(freq, dur=1.3, cutoff=2600, q=0.9, drive=1.2, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    osc_ = saw_ph(2 * np.pi * freq * t) + 0.6 * sqr_ph(2 * np.pi * freq * 1.003 * t)
    env = (1 - np.exp(-t / 0.002)) * np.exp(-t / (dur * 0.42))
    cut = freq * 1.2 + cutoff * np.exp(-t / 0.1)
    sig = tv_lp(osc_, cut, block=64)
    sig *= env
    tail = n_of(0.04)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sat(sig, drive, 'tanh')


def saw_lead(freq, dur=1.5, detune=0.008, cutoff=5200, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    osc_ = np.zeros(n)
    for d, g in [(-detune, 0.8), (0, 1.0), (detune, 0.8), (detune * 2.1, 0.4)]:
        osc_ += g * saw_ph(2 * np.pi * freq * (1 + d) * t + rng.uniform(0, 6))
    env = (1 - np.exp(-t / 0.006)) * (0.7 + 0.3 * np.exp(-t / 0.3))
    cut = 900 + cutoff * (0.4 + 0.6 * np.exp(-t / 0.25))
    sig = tv_lp(osc_, cut, block=96) * env
    sig = sat(sig, 1.3, 'tanh')
    tail = n_of(0.05)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sig


def supersaw(freq, dur=2.0, voices=7, spread=0.02, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    osc_ = np.zeros(n)
    for i in range(voices):
        d = (i - (voices - 1) / 2) / ((voices - 1) / 2) * spread
        osc_ += saw_ph(2 * np.pi * freq * (1 + d) * t + rng.uniform(0, 6)) / voices
    osc_ = lp(osc_, 9000)
    env = (1 - np.exp(-t / 0.02)) * (0.65 + 0.35 * np.exp(-t / 0.6))
    sig = osc_ * env
    tail = n_of(0.08)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sat(sig, 1.15, 'tanh')


def pulse_lead(freq, dur=1.0, duty=0.25, crush=0, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    ph = (freq * t) % 1.0
    sig = np.where(ph < duty, 1.0, -1.0) * 0.7 + np.where(ph < duty * 0.5, 1.0, -1.0) * 0.3
    env = (1 - np.exp(-t / 0.003)) * np.exp(-t / (dur * 0.5))
    sig *= env
    if crush:
        sig = bitcrush(sig, bits=crush, downsample=3)
    tail = n_of(0.02)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sat(lp(sig, 12000), 1.1, 'tanh')


def square_lead(freq, dur=1.2, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    sig = sqr_ph(2 * np.pi * freq * t) * 0.7 + saw_ph(2 * np.pi * freq * 1.005 * t) * 0.3
    env = (1 - np.exp(-t / 0.01)) * (0.6 + 0.4 * np.exp(-t / 0.5))
    sig = tv_lp(sig * env, 1500 + 3500 * np.exp(-np.arange(n) / FS / 0.4), block=96)
    tail = n_of(0.04)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sat(sig, 1.2, 'tanh')


def pad_warm(freq, dur=3.0, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    osc_ = np.zeros(n)
    for d, g in [(-0.006, 1), (0.006, 1), (-0.011, 0.6), (0.011, 0.6), (0.017, 0.35)]:
        osc_ += g * saw_ph(2 * np.pi * freq * (1 + d) * t + rng.uniform(0, 6))
    osc_ = tv_lp(osc_, 700 + 1800 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.15 * t)), block=128)
    env = adsr(n, a=0.45, d=0.5, s=0.75, r=0.7)
    sig = osc_ * env / 3.0
    sig = chorus(sig, depth_ms=6, rate=0.35, mix=0.35)
    sig = reverb(sig, wet=0.3, decay=1.8, tone=5000, rng=rng)
    return sat(sig, 1.1, 'tanh')


def pad_choir(freq, dur=3.0, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    osc_ = np.zeros(n)
    for d, g in [(-0.004, 1), (0.004, 1), (0.009, 0.6)]:
        osc_ += g * saw_ph(2 * np.pi * freq * (1 + d) * t + rng.uniform(0, 6))
    src = osc_ / 2.6 + 0.12 * noise(n, rng)
    f = formant(src, [620, 1150, 2500, 3400], [5, 6, 8, 10], [1.0, 0.6, 0.35, 0.2])
    env = adsr(n, a=0.55, d=0.6, s=0.8, r=0.8)
    sig = f * env
    sig = chorus(sig, depth_ms=7, rate=0.5, mix=0.4)
    sig = reverb(sig, wet=0.35, decay=2.0, tone=5000, rng=rng)
    return sat(sig, 1.2, 'tanh')


def fm_bell(freq, dur=2.2, ratio=3.51, index=3.5, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    idx = index * np.exp(-t / 0.35) + 0.15
    sig = np.sin(2 * np.pi * freq * t + idx * np.sin(2 * np.pi * freq * ratio * t))
    sig *= (1 - np.exp(-t / 0.001)) * np.exp(-t / (dur * 0.5))
    tail = n_of(0.05)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sat(lp(sig, 12000), 1.05, 'tanh')


# ------------------------------------------------------------------ GUITARS / STRINGS
def guitar_clean(freq, dur=1.8, bright=0.55, rng=None):
    sig = ks_pluck(freq, dur, bright=bright, damp=0.35, rng=rng)
    sig = peaking(sig, 105, 4.0, 1.1)
    sig = peaking(sig, 210, 2.5, 1.2)
    sig = peaking(sig, 2400, 2.0, 1.0)
    sig = lp(sig, 5200, 2)
    tail = n_of(0.05)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sat(sig, 1.15, 'tanh')


def guitar_muted(freq, dur=0.9, rng=None):
    sig = ks_pluck(freq, dur, bright=0.75, damp=0.92, rng=rng)
    sig = peaking(sig, 180, 3.0, 1.0)
    sig = lp(sig, 2400, 2)
    sig = hp(sig, 90, 1)
    sig *= np.exp(-np.arange(len(sig)) / FS / 0.22)
    return sat(sig, 1.4, 'tanh')


def guitar_dist(freq, dur=1.6, fifth=0.45, drive=6.0, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    base = saw_ph(2 * np.pi * freq * t) + 0.5 * sqr_ph(2 * np.pi * freq * 1.004 * t)
    if fifth:
        base += fifth * (saw_ph(2 * np.pi * freq * 1.4983 * t) + 0.4 * sqr_ph(2 * np.pi * freq * 1.4983 * 1.003 * t))
    env = (1 - np.exp(-t / 0.003)) * np.exp(-t / (dur * 0.55))
    sig = base * env
    sig = peaking(sig, 120, 4.0, 1.0)
    sig = sat(sig, drive, 'tanh')
    sig = peaking(sig, 900, 3.0, 1.4)
    sig = lp(sig, 4500, 2)
    sig = hp(sig, 90, 2)
    tail = n_of(0.05)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sig


def sitar(freq, dur=2.0, rng=None):
    sig = ks_pluck(freq, dur, bright=0.9, damp=0.25, rng=rng)
    n = len(sig)
    t = np.arange(n) / FS
    # jawari buzz
    buzz = sat(sig, 4.0, 'fold')
    sig = 0.6 * sig + 0.4 * buzz
    sig = peaking(sig, 3200, 4.0, 1.2)
    sig += 0.15 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-t / (dur * 0.4))
    return sat(hp(sig, 120), 1.3, 'tanh')


def koto(freq, dur=1.6, rng=None):
    sig = ks_pluck(freq, dur, bright=0.85, damp=0.45, rng=rng)
    n = len(sig)
    t = np.arange(n) / FS
    vibr = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.exp(-t / 0.6)
    sig = sig * vibr
    sig = peaking(sig, 1800, 3.0, 1.2)
    return sat(hp(sig, 110), 1.2, 'tanh')


def banjo(freq, dur=1.2, rng=None):
    sig = ks_pluck(freq, dur, bright=1.0, damp=0.55, rng=rng)
    sig = peaking(sig, 2800, 5.0, 1.0)
    sig = peaking(sig, 800, 2.0, 1.0)
    return sat(hp(sig, 180), 1.3, 'tanh')


def oud(freq, dur=1.4, rng=None):
    sig = ks_pluck(freq, dur, bright=0.6, damp=0.7, rng=rng)
    sig = peaking(sig, 1400, 4.0, 1.2)
    sig = lp(sig, 4000)
    return sat(hp(sig, 100), 1.2, 'tanh')


def harp(freq, dur=2.4, rng=None):
    sig = ks_pluck(freq, dur, bright=0.7, damp=0.2, rng=rng)
    sig = peaking(sig, 400, 2.0, 1.0)
    tail = n_of(0.1)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sat(lp(sig, 8000), 1.05, 'tanh')


def _bowed(freq, dur, bright=0.5, vib=0.004, vib_rate=5.2, attack=0.09, formants=None, breath=0.03, rng=None):
    rng = rng or np.random.default_rng()
    n = n_of(dur)
    t = np.arange(n) / FS
    det = 1 + vib * np.sin(2 * np.pi * vib_rate * t) * np.clip(t / 0.35, 0, 1)
    osc_ = np.zeros(n)
    for d in (-0.004, 0.0, 0.005):
        osc_ += saw_ph(2 * np.pi * freq * (1 + d) * det * t) / 3
    if formants:
        osc_ = 0.6 * osc_ + 0.7 * formant(osc_, *formants)
    env = (1 - np.exp(-t / attack)) * (0.8 + 0.2 * np.exp(-t / 0.6))
    noise_env = (1 - np.exp(-t / 0.02)) * np.exp(-t / 0.5)
    sig = osc_ * env * (1 - breath) + breath * 4 * np.abs(noise(n, rng)) * noise_env
    tail = n_of(0.12)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sat(lp(sig, 5000 + 5000 * bright), 1.15, 'tanh')


def strings_ensemble(freq, dur=3.0, rng=None):
    sig = _bowed(freq, dur, bright=0.6, vib=0.0035, attack=0.13, rng=rng,
                 formants=([420, 900, 2100], [4, 5, 6], [1.0, 0.55, 0.3]))
    sig = chorus(sig, depth_ms=8, rate=0.3, mix=0.4)
    sig = reverb(sig, wet=0.22, decay=1.5, tone=4500, rng=rng)
    return sat(sig, 1.1, 'tanh')


def solo_violin(freq, dur=2.6, rng=None):
    return _bowed(freq, dur, bright=0.75, vib=0.006, attack=0.06, rng=rng,
                  formants=([480, 1100, 2600], [5, 6, 7], [1.0, 0.6, 0.35]), breath=0.02)


def cello(freq, dur=2.8, rng=None):
    return _bowed(freq, dur, bright=0.4, vib=0.005, attack=0.1, rng=rng,
                  formants=([300, 700, 1600], [4, 5, 6], [1.0, 0.6, 0.3]), breath=0.015)


def erhu(freq, dur=2.4, rng=None):
    sig = _bowed(freq, dur, bright=0.8, vib=0.009, vib_rate=6.5, attack=0.05, rng=rng,
                 formants=([700, 1400, 3000], [6, 7, 8], [1.0, 0.7, 0.4]), breath=0.05)
    return sig


def pizz(freq, dur=1.0, rng=None):
    sig = ks_pluck(freq, dur, bright=0.7, damp=0.55, rng=rng)
    sig *= (1 - np.exp(-np.arange(len(sig)) / FS / 0.002))
    return sat(hp(sig, 120), 1.2, 'tanh')


# ------------------------------------------------------------------ WINDS / BRASS
def flute(freq, dur=1.8, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5 * t) * np.clip(t / 0.4, 0, 1)
    ph = 2 * np.pi * np.cumsum(freq * vib) / FS
    sig = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.06 * np.sin(3 * ph)
    env = (1 - np.exp(-t / 0.05)) * (0.8 + 0.2 * np.exp(-t / 0.5))
    breath = bp(noise(n, rng), 2000, 8000) * (0.12 + 0.1 * np.exp(-t / 0.06))
    sig = sig * env + breath * env
    tail = n_of(0.1)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sat(lp(sig, 9000), 1.1, 'tanh')


def pan_flute(freq, dur=1.6, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    ph = 2 * np.pi * freq * t
    sig = np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.08 * np.sin(4 * ph)
    env = (1 - np.exp(-t / 0.02)) * np.exp(-t / (dur * 0.7))
    chiff = bp(noise(n, rng), 1500, 7000) * np.exp(-t / 0.05) * 0.5
    return sat(lp(sig * env + chiff, 8000), 1.1, 'tanh')


def ocarina(freq, dur=1.6, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    sig = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 2.01 * t) + 0.1 * np.sin(2 * np.pi * freq * 3 * t)
    env = (1 - np.exp(-t / 0.06)) * (0.85 + 0.15 * np.exp(-t / 0.5))
    sig = sig * env + 0.08 * bp(noise(n, rng), 800, 4000) * env
    tail = n_of(0.08)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sat(lp(sig, 6000), 1.15, 'tanh')


def clarinet(freq, dur=2.0, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    vib = 1 + 0.003 * np.sin(2 * np.pi * 4.6 * t) * np.clip(t / 0.5, 0, 1)
    ph = 2 * np.pi * np.cumsum(freq * vib) / FS
    sig = np.zeros(n)
    for k in range(1, 12, 2):
        sig += np.sin(k * ph) / k ** 1.1
    env = (1 - np.exp(-t / 0.04)) * (0.8 + 0.2 * np.exp(-t / 0.6))
    sig = sig * env + 0.05 * bp(noise(n, rng), 1200, 5000) * env
    tail = n_of(0.1)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sat(lp(sig, 5000), 1.1, 'tanh')


def shakuhachi(freq, dur=2.0, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    vib = 1 + 0.012 * np.sin(2 * np.pi * 6 * t) * np.clip(t / 0.5, 0, 1)
    ph = 2 * np.pi * np.cumsum(freq * vib) / FS
    sig = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
    env = (1 - np.exp(-t / 0.06)) * (0.8 + 0.2 * np.exp(-t / 0.7))
    breath = bp(noise(n, rng), 900, 6000) * (0.35 + 0.25 * np.exp(-t / 0.08))
    sig = (sig + breath) * env
    tail = n_of(0.12)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sat(lp(sig, 7000), 1.2, 'tanh')


def trumpet(freq, dur=1.8, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.3) / 0.4, 0, 1)
    osc_ = np.zeros(n)
    for d in (-0.003, 0.003):
        osc_ += saw_ph(2 * np.pi * np.cumsum(freq * (1 + d) * vib) / FS) / 2
    cut = 600 + 4200 * (1 - np.exp(-t / 0.09))
    sig = tv_lp(osc_, cut, block=64)
    env = (1 - np.exp(-t / 0.03)) * (0.75 + 0.25 * np.exp(-t / 0.5))
    sig = sig * env
    sig = peaking(sig, 1200, 3.0, 1.2)
    sig += 0.04 * bp(noise(n, rng), 800, 4000) * env
    tail = n_of(0.1)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sat(sig, 1.4, 'tanh')


def synth_brass(freq, dur=1.8, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    osc_ = np.zeros(n)
    for d, g in [(-0.007, 1), (0, 1), (0.007, 1)]:
        osc_ += g * saw_ph(2 * np.pi * freq * (1 + d) * t) / 3
    cut = 500 + 3500 * (1 - np.exp(-t / 0.15))
    sig = tv_lp(osc_, cut, block=96) * (1 - np.exp(-t / 0.04)) * (0.7 + 0.3 * np.exp(-t / 0.4))
    tail = n_of(0.08)
    sig[-tail:] *= np.linspace(1, 0, tail)
    return sat(sig, 1.3, 'tanh')


# ------------------------------------------------------------------ VOX
def vocal_aah(freq, dur=2.4, vowel='a', rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.4 * t) * np.clip(t / 0.5, 0, 1)
    ph = 2 * np.pi * np.cumsum(freq * vib) / FS
    glottal = saw_ph(ph) + 0.35 * saw_ph(2 * ph)
    glottal += 0.12 * noise(n, rng)
    F = {'a': ([700, 1220, 2600, 3400], [6, 8, 10, 12]),
         'o': ([450, 800, 2830, 3400], [5, 6, 8, 10]),
         'e': ([530, 1840, 2480, 3500], [6, 8, 10, 12]),
         'u': ([325, 700, 2530, 3300], [5, 6, 8, 10])}[vowel]
    sig = 0.12 * glottal + 1.6 * formant(glottal, F[0], F[1], [1, 0.7, 0.4, 0.2])
    env = (1 - np.exp(-t / 0.12)) * (0.8 + 0.2 * np.exp(-t / 0.6))
    sig = lp(hp(sig * env, 120), 5500)
    sig = chorus(sig, depth_ms=5, rate=0.6, mix=0.3)
    sig = reverb(sig, wet=0.3, decay=1.6, tone=6000, rng=rng)
    return sat(sig, 1.15, 'tanh')


def vocal_chop(freq, dur=1.1, rng=None):
    n = n_of(dur)
    t = np.arange(n) / FS
    ph = 2 * np.pi * freq * t
    glottal = saw_ph(ph) + 0.3 * saw_ph(2 * ph)
    sig = np.zeros(n)
    # formant morph a->o
    for k in range(4):
        f0 = 700 - 250 * min(1, k / 3)
        f = [f0, 1220 - 300 * min(1, k / 3), 2600]
        seg = n // 4
        a, b = k * seg, min(n, (k + 1) * seg)
        if a >= n:
            break
        sig[a:b] = formant(glottal[a:b], f, [6, 8, 10], [1, 0.6, 0.3])
    sig *= (1 - np.exp(-t / 0.01)) * np.exp(-t / (dur * 0.6))
    sig = hp(sig, 150)
    sig = chorus(sig, depth_ms=4, rate=1.2, mix=0.25)
    return sat(sig, 1.2, 'tanh')
