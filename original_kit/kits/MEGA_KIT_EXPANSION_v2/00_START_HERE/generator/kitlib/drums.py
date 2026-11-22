"""Synthesized drum / percussion voices."""
import numpy as np
from .dsp import *


def _metallic(n, rng, base=205.3, ratios=(1, 1.48, 1.8, 2.55, 2.63, 3.9), jitter=0.004, shape='square'):
    t = np.arange(n) / FS
    out = np.zeros(n)
    for i, r in enumerate(ratios):
        f = base * r * (1 + rng.uniform(-jitter, jitter))
        ph = 2 * np.pi * f * t + rng.uniform(0, 6.28)
        out += (sqr_ph(ph) if shape == 'square' else np.sin(ph)) / (i + 1.3)
    return out / len(ratios) ** 0.5


# --------------------------------------------------------------------------- KICK
def kick(rng, f_start=140, f_end=48, pitch_tau=0.028, decay=0.30, click=0.35,
         drive=1.4, tone=9000, sub=0.35, punch=0.25, dur=None, beater=0.0):
    dur = dur or decay * 2.05 + 0.04
    n = n_of(dur)
    t = np.arange(n) / FS
    f = f_end + (f_start - f_end) * np.exp(-t / max(pitch_tau, 1e-4))
    body = np.sin(2 * np.pi * np.cumsum(f) / FS)
    env = np.exp(-t / max(decay, 1e-4))
    env *= (1 - np.exp(-t / 0.0008))
    sig = body * env
    # sub reinforcement
    sig += sub * np.sin(2 * np.pi * np.cumsum(f * 0.985) / FS) * env ** 1.6
    # punch: 1.5 - 4k transient
    if punch:
        pn = noise(n, rng)
        pn = bp(pn, 900, 4500)
        sig += punch * pn * np.exp(-t / 0.006) * 0.6
    # click / beater
    if click:
        cn = noise(n, rng)
        cn = bp(cn, 2500, min(14000, FS * 0.45))
        sig += click * cn * np.exp(-t / 0.0035)
    if beater:
        sig += beater * np.sin(2 * np.pi * 2100 * t) * np.exp(-t / 0.004)
    sig = sat(sig, drive, 'tanh')
    sig = lp(sig, tone, 2)
    sig = peaking(sig, 60, 4.0, 0.9)
    sig = dc_block(sig)
    return sig


# --------------------------------------------------------------------------- SNARE
def snare(rng, tone=190, noise_amt=1.0, decay=0.14, bright=6000, lp_f=None,
          second=1.62, pink=0.0, clap_layer=0.0, drive=1.2, buzz=0.0, rattle=0.5):
    n = n_of(decay * 3.2 + 0.06)
    t = np.arange(n) / FS
    f = tone * (1 + 0.55 * np.exp(-t / 0.012))
    t1 = np.sin(2 * np.pi * np.cumsum(f) / FS)
    t2 = np.sin(2 * np.pi * np.cumsum(f * second) / FS) * 0.6
    body = (t1 + t2) * np.exp(-t / (decay * 0.55)) * (1 - np.exp(-t / 0.0006))
    nz = noise(n, rng)
    nz = bp(nz, 900, bright)
    if pink:
        nz = nz + pink * bp(noise(n, rng), 200, 1800)
    nenv = np.exp(-t / decay) * (1 - np.exp(-t / 0.001))
    # rattle: amplitude modulation noise for snare wires
    if rattle:
        mod = 1 + rattle * 0.5 * np.sin(2 * np.pi * 78 * t + rng.uniform(0, 6))
        nz = nz * mod
    sig = body + noise_amt * nz * nenv
    if buzz:
        sig += buzz * np.sin(2 * np.pi * 4000 * t) * np.exp(-t / 0.02)
    if clap_layer:
        c = clap(rng, decay=decay * 1.2)
        c = np.pad(c, (n_of(0.004), 0))[:n]
        sig += clap_layer * c
    if lp_f:
        sig = lp(sig, lp_f, 2)
    sig = hp(sig, 160, 2)
    sig = sat(sig, drive, 'tanh')
    return sig


# --------------------------------------------------------------------------- CLAP
def clap(rng, decay=0.16, spacing=0.011, bursts=4, lo=900, hi=3600, drive=1.1,
         room=0.25, tail_lp=9000, spread=1.0):
    dur = decay * 2.8 + bursts * spacing + 0.05
    n = n_of(dur)
    t = np.arange(n) / FS
    sig = np.zeros(n)
    for k in range(bursts):
        off = n_of(spacing * k * rng.uniform(0.85, 1.25) * spread)
        if off >= n:
            break
        m = n - off
        tt = np.arange(m) / FS
        b = bp(noise(m, rng), lo, hi) * np.exp(-tt / (0.006 + 0.002 * k))
        sig[off:] += b * (1.0 - 0.12 * k)
    # main body tail
    tt = t
    tail = bp(noise(n, rng), lo * 0.7, hi * 1.2) * np.exp(-tt / decay) * (1 - np.exp(-tt / 0.02))
    sig = sig + tail * 0.9
    sig = hp(sig, 300, 2)
    sig = lp(sig, tail_lp, 2)
    sig = sat(sig, drive, 'tanh')
    if room:
        sig = reverb(sig, wet=room, decay=0.25, tone=7000, predelay=0.004, rng=rng)
    return sig


# --------------------------------------------------------------------------- SNAP / RIM / STICK
def snap(rng, decay=0.07, lo=1500, hi=6500, layers=3):
    n = n_of(decay * 4)
    sig = np.zeros(n)
    for k in range(layers):
        off = n_of(0.004 * k * rng.uniform(0.7, 1.4))
        m = n - off
        tt = np.arange(m) / FS
        sig[off:] += bp(noise(m, rng), lo, hi) * np.exp(-tt / (decay * (1 - 0.22 * k)))
    sig = hp(sig, 700)
    return sat(sig, 1.2, 'tanh')


def rim(rng, tone=780, decay=0.05, click=0.7, body=0.6):
    n = n_of(decay * 5 + 0.02)
    t = np.arange(n) / FS
    ping = np.sin(2 * np.pi * tone * t) * np.exp(-t / decay)
    ping += 0.5 * np.sin(2 * np.pi * tone * 2.71 * t) * np.exp(-t / (decay * 0.6))
    nz = bp(noise(n, rng), 1800, 9000) * np.exp(-t / 0.004) * click
    sig = body * ping + nz
    return sat(sig, 1.1, 'tanh')


def stick(rng, tone=1200, decay=0.03):
    n = n_of(decay * 6 + 0.01)
    t = np.arange(n) / FS
    sig = np.sin(2 * np.pi * tone * t) * np.exp(-t / decay)
    sig += bp(noise(n, rng), 2000, 11000) * np.exp(-t / 0.0035)
    return sat(sig, 1.05, 'tanh')


# --------------------------------------------------------------------------- HATS / CYMBALS
def hat_closed(rng, decay=0.045, base=205.3, metal=1.0, noise_amt=0.45, tone=8500,
               drive=1.0, digital=0.0, jitter=0.004):
    n = n_of(max(decay * 4, 0.09))
    t = np.arange(n) / FS
    src = _metallic(n, rng, base, jitter=jitter)
    src = metal * src + noise_amt * noise(n, rng)
    if digital:
        src = bitcrush(src, bits=int(6 + 6 * (1 - digital)), downsample=max(1, int(1 + digital * 3)))
    env = np.exp(-t / decay) * (1 - np.exp(-t / 0.0006))
    sig = hp(src * env, 6500, 2)
    sig = peaking(sig, 10500, 3.0, 1.2)
    sig = lp(sig, tone * 2.2)
    return sat(sig, drive, 'tanh')


def hat_open(rng, decay=0.35, base=205.3, metal=1.0, noise_amt=0.4, tone=9000, drive=1.0):
    n = n_of(decay * 2.45 + 0.05)
    t = np.arange(n) / FS
    src = metal * _metallic(n, rng, base) + noise_amt * noise(n, rng)
    env = (1 - np.exp(-t / 0.002)) * np.exp(-t / decay)
    env = env * (1 + 0.15 * np.sin(2 * np.pi * 9 * t))
    sig = hp(src * env, 6000, 2)
    sig = lp(sig, tone * 2)
    return sat(sig, drive, 'tanh')


def crash(rng, decay=1.6, base=180, noise_amt=1.0, metal=0.8, hp_f=3500, tone=16000, shimmer=0.15):
    n = n_of(decay * 1.75 + 0.08)
    t = np.arange(n) / FS
    src = metal * _metallic(n, rng, base, ratios=(1, 1.41, 1.73, 2.11, 2.63, 3.11, 4.3)) + noise_amt * noise(n, rng)
    env = np.exp(-t / decay) * (1 - np.exp(-t / 0.002))
    env *= (1 + shimmer * np.sin(2 * np.pi * 5.5 * t))
    sig = hp(src * env, hp_f, 2)
    sig = lp(sig, tone, 1)
    sig = sat(sig, 1.1, 'tanh')
    return sig


def ride(rng, decay=1.1, base=300, bell=0.35):
    n = n_of(decay * 1.95 + 0.08)
    t = np.arange(n) / FS
    src = _metallic(n, rng, base, ratios=(1, 1.63, 2.13, 2.71, 3.37, 4.09)) * 0.7 + 0.5 * noise(n, rng)
    env = np.exp(-t / decay) * (1 - np.exp(-t / 0.0015))
    sig = hp(src * env, 4200, 2)
    if bell:
        b = (np.sin(2 * np.pi * 2650 * t) + 0.4 * np.sin(2 * np.pi * 3970 * t)) * np.exp(-t / 0.12)
        sig += bell * b
    return sat(sig, 1.05, 'tanh')


def china(rng, decay=1.3):
    sig = crash(rng, decay=decay, base=250, hp_f=2200, shimmer=0.3)
    sig = bitcrush(sig, bits=7, downsample=2)
    sig = bp(sig, 1200, 12000)
    return sat(sig, 1.5, 'tanh')


def splash(rng, decay=0.55):
    return crash(rng, decay=decay, base=420, hp_f=4500, shimmer=0.25)


# --------------------------------------------------------------------------- TOMS
def tom(rng, f0=150, decay=0.35, skin=0.35, drop=1.5, drive=1.1):
    n = n_of(decay * 3 + 0.05)
    t = np.arange(n) / FS
    f = f0 * (1 + (drop - 1) * np.exp(-t / 0.09))
    body = np.sin(2 * np.pi * np.cumsum(f) / FS) * np.exp(-t / decay)
    body += 0.35 * np.sin(2 * np.pi * np.cumsum(f * 1.58) / FS) * np.exp(-t / (decay * 0.5))
    nz = bp(noise(n, rng), 400, 4200) * np.exp(-t / (decay * 0.22)) * skin
    sig = sat(body + nz, drive, 'tanh')
    return lp(sig, 8000)


# --------------------------------------------------------------------------- PERCUSSION
def shaker(rng, decay=0.07, lo=4500, hi=12000, grains=2, drive=1.0):
    n = n_of(decay * 5 + 0.03)
    sig = np.zeros(n)
    for k in range(grains):
        off = n_of(0.008 * k * rng.uniform(0.6, 1.6))
        m = n - off
        tt = np.arange(m) / FS
        sig[off:] += bp(noise(m, rng), lo, hi) * np.exp(-tt / (decay * (1 - 0.25 * k))) * (1 - 0.3 * k)
    sig = hp(sig, 2500)
    return sat(sig, drive, 'tanh')


def tambourine(rng, decay=0.35):
    n = n_of(decay * 3 + 0.05)
    t = np.arange(n) / FS
    jingle = bp(noise(n, rng), 5000, 14000) * np.exp(-t / decay)
    ring = _metallic(n, rng, 620, ratios=(1, 1.9, 2.7, 3.6)) * 0.4 * np.exp(-t / (decay * 0.7))
    sig = hp(jingle + ring, 3800)
    sig += bp(noise(n, rng), 2000, 6000) * np.exp(-t / 0.01) * 0.3
    return sat(sig, 1.1, 'tanh')


def cowbell(rng, f1=560, f2=845, decay=0.28, drive=1.3):
    n = n_of(decay * 3.5 + 0.05)
    t = np.arange(n) / FS
    a = sqr_ph(2 * np.pi * f1 * t) + sqr_ph(2 * np.pi * f2 * t) + 0.5 * sqr_ph(2 * np.pi * f2 * 1.51 * t)
    env = np.exp(-t / decay) * (1 - np.exp(-t / 0.001))
    sig = bp(a * env, 400, 5200)
    sig += 0.3 * np.sin(2 * np.pi * f2 * 2 * t) * np.exp(-t / (decay * 0.4))
    return sat(sig, drive, 'tanh')


def clave(rng, tone=2500, decay=0.05):
    n = n_of(decay * 6 + 0.03)
    t = np.arange(n) / FS
    sig = np.sin(2 * np.pi * tone * t) * np.exp(-t / decay)
    sig += 0.4 * np.sin(2 * np.pi * tone * 2.42 * t) * np.exp(-t / (decay * 0.5))
    sig += bp(noise(n, rng), 1800, 9000) * np.exp(-t / 0.0025) * 0.7
    return sat(sig, 1.05, 'tanh')


def woodblock(rng, tone=1050, decay=0.055):
    n = n_of(decay * 6 + 0.03)
    t = np.arange(n) / FS
    sig = np.sin(2 * np.pi * tone * t) * np.exp(-t / decay)
    sig += 0.5 * np.sin(2 * np.pi * tone * 2.9 * t) * np.exp(-t / (decay * 0.4))
    sig += bp(noise(n, rng), 800, 5000) * np.exp(-t / 0.003) * 0.5
    return sat(sig, 1.2, 'tanh')


def triangle_ring(rng, tone=3400, decay=0.9):
    n = n_of(decay * 3)
    t = np.arange(n) / FS
    sig = np.zeros(n)
    for r, g in [(1, 1), (2.74, .5), (5.4, .28), (8.9, .14)]:
        sig += g * np.sin(2 * np.pi * tone * r * t + rng.uniform(0, 3)) * np.exp(-t / (decay / (1 + r * 0.2)))
    sig += bp(noise(n, rng), 4000, 14000) * np.exp(-t / 0.003) * 0.3
    return sat(sig, 1.0, 'tanh')


def conga(rng, f0=200, decay=0.3, slap=0.4):
    n = n_of(decay * 3 + 0.05)
    t = np.arange(n) / FS
    f = f0 * (1 + 0.35 * np.exp(-t / 0.03))
    body = np.sin(2 * np.pi * np.cumsum(f) / FS) * np.exp(-t / decay)
    body += 0.3 * np.sin(2 * np.pi * np.cumsum(f * 1.9) / FS) * np.exp(-t / (decay * 0.4))
    nz = bp(noise(n, rng), 700, 5000) * np.exp(-t / 0.012) * slap
    return sat(body + nz, 1.15, 'tanh')


def djembe(rng, f0=110, decay=0.25, slap=0.6):
    n = n_of(decay * 3.5 + 0.05)
    t = np.arange(n) / FS
    f = f0 * (1 + 0.6 * np.exp(-t / 0.02))
    body = np.sin(2 * np.pi * np.cumsum(f) / FS) * np.exp(-t / decay)
    nz = bp(noise(n, rng), 600, 7000) * np.exp(-t / 0.02) * slap
    sig = sat(body + nz, 1.3, 'tanh')
    return lp(sig, 7000)


def tabla(rng, f0=280, decay=0.18, ring=0.3):
    n = n_of(decay * 4 + 0.05)
    t = np.arange(n) / FS
    f = f0 * (1 + 0.25 * np.exp(-t / 0.02))
    body = np.sin(2 * np.pi * np.cumsum(f) / FS) * np.exp(-t / decay)
    body += ring * np.sin(2 * np.pi * f0 * 3.1 * t) * np.exp(-t / (decay * 0.8))
    nz = bp(noise(n, rng), 1500, 8000) * np.exp(-t / 0.008) * 0.4
    return sat(body + nz, 1.1, 'tanh')


def frame_drum(rng, f0=95, decay=0.3):
    n = n_of(decay * 3.2 + 0.05)
    t = np.arange(n) / FS
    f = f0 * (1 + 0.3 * np.exp(-t / 0.04))
    body = np.sin(2 * np.pi * np.cumsum(f) / FS) * np.exp(-t / decay)
    nz = bp(noise(n, rng), 300, 6000) * np.exp(-t / 0.03) * 0.5
    sig = body + nz
    return lp(sat(sig, 1.2, 'tanh'), 6000)


def cajon(rng, f0=85, decay=0.15, slap=0.8):
    n = n_of(decay * 4 + 0.05)
    t = np.arange(n) / FS
    body = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.4 * np.exp(-t / 0.02))) / FS) * np.exp(-t / decay)
    nz = bp(noise(n, rng), 1200, 6500) * np.exp(-t / 0.01) * slap
    return lp(sat(body + nz, 1.2, 'tanh'), 9000)


def cabasa(rng, decay=0.12, grains=14):
    n = n_of(decay * 3 + 0.05)
    sig = np.zeros(n)
    for k in range(grains):
        off = n_of(decay * 2 * k / grains * rng.uniform(0.8, 1.2))
        if off >= n:
            break
        m = n - off
        tt = np.arange(m) / FS
        sig[off:] += bp(noise(m, rng), 4000, 13000) * np.exp(-tt / 0.006) * (1 - k / grains)
    return hp(sig, 3000)


def guiro(rng, decay=0.2, grains=9):
    n = n_of(decay * 3 + 0.05)
    sig = np.zeros(n)
    for k in range(grains):
        off = n_of(decay * 2.2 * k / grains)
        if off >= n:
            break
        m = n - off
        tt = np.arange(m) / FS
        sig[off:] += bp(noise(m, rng), 1800, 7000) * np.exp(-tt / 0.012) * (0.6 + 0.4 * np.sin(k))
    return hp(sig, 1200)


def anvil(rng, base=520, decay=0.9):
    n = n_of(decay * 3)
    t = np.arange(n) / FS
    sig = np.zeros(n)
    for r, g, d in [(1, 1, 1.0), (2.32, .6, .6), (3.91, .4, .35), (6.2, .25, .2), (9.1, .15, .12)]:
        sig += g * np.sin(2 * np.pi * base * r * t + rng.uniform(0, 6)) * np.exp(-t / (decay * d))
    sig += bp(noise(n, rng), 2000, 12000) * np.exp(-t / 0.004) * 0.6
    return sat(sig, 1.2, 'tanh')


def glass(rng, base=2200, decay=0.5):
    n = n_of(decay * 3)
    t = np.arange(n) / FS
    sig = np.zeros(n)
    for k in range(6):
        f = base * rng.uniform(0.6, 3.0)
        sig += np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * np.exp(-t / (decay * rng.uniform(0.3, 1.0))) / (k + 1)
    sig += bp(noise(n, rng), 3000, 15000) * np.exp(-t / 0.003) * 0.5
    return sat(sig, 1.1, 'tanh')


def bottle(rng, base=900, decay=0.25):
    n = n_of(decay * 3)
    t = np.arange(n) / FS
    f = base * (1 + 0.8 * np.exp(-t / 0.012))
    sig = np.sin(2 * np.pi * np.cumsum(f) / FS) * np.exp(-t / decay)
    sig += 0.3 * bp(noise(n, rng), 1500, 9000) * np.exp(-t / 0.006)
    return sat(sig, 1.1, 'tanh')


def coins(rng, decay=0.3):
    n = n_of(decay * 3)
    t = np.arange(n) / FS
    sig = np.zeros(n)
    for k in range(5):
        off = n_of(rng.uniform(0, 0.05))
        m = n - off
        tt = np.arange(m) / FS
        f = rng.uniform(3000, 8000)
        sig[off:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt / rng.uniform(0.03, 0.12)) * 0.3
    sig += bp(noise(n, rng), 4000, 15000) * np.exp(-t / 0.004) * 0.3
    return sat(sig, 1.1, 'tanh')


def vibraslap(rng, decay=0.35):
    n = n_of(decay * 3)
    t = np.arange(n) / FS
    sig = bp(noise(n, rng), 2500, 9000) * np.exp(-t / decay)
    sig *= (1 + 0.8 * np.sin(2 * np.pi * 42 * t))
    return sat(sig, 1.2, 'tanh')


def stomp(rng, decay=0.12, f0=70, thud=0.8, room=0.2):
    n = n_of(decay * 3.5 + 0.05)
    t = np.arange(n) / FS
    low = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.5 * np.exp(-t / 0.02))) / FS) * np.exp(-t / decay)
    nz = bp(noise(n, rng), 120, 3000) * np.exp(-t / (decay * 0.5)) * thud
    sig = sat(low + nz, 1.3, 'tanh')
    sig = lp(sig, 4000)
    if room:
        sig = reverb(sig, wet=room, decay=0.35, tone=4000, rng=rng)
    return sig


# --------------------------------------------------------------------------- ELECTRONIC PERC
def blip(rng, f0=1200, f1=300, decay=0.07, drive=1.0):
    n = n_of(decay * 4 + 0.03)
    t = np.arange(n) / FS
    f = f1 + (f0 - f1) * np.exp(-t / 0.02)
    sig = np.sin(2 * np.pi * np.cumsum(f) / FS) * np.exp(-t / decay)
    sig += 0.2 * np.sin(2 * np.pi * np.cumsum(f * 2) / FS) * np.exp(-t / (decay * 0.4))
    return sat(sig, drive, 'tanh')


def laser(rng, f0=6000, f1=200, decay=0.18):
    n = n_of(decay * 3)
    t = np.arange(n) / FS
    f = f1 + (f0 - f1) * np.exp(-t / 0.045)
    sig = saw_ph(2 * np.pi * np.cumsum(f) / FS) * np.exp(-t / decay)
    sig = lp(sig, 9000)
    return sat(sig, 1.3, 'tanh')


def glitch_perc(rng, decay=0.12, bits=6):
    n = n_of(decay * 3 + 0.03)
    t = np.arange(n) / FS
    src = noise(n, rng) * np.exp(-t / decay)
    sig = bitcrush(src, bits=bits, downsample=rng.integers(2, 6))
    sig = bp(sig, 400, 12000)
    return sat(sig, 1.4, 'tanh')


def metal_stab(rng, base=460, decay=0.35):
    n = n_of(decay * 3)
    t = np.arange(n) / FS
    sig = _metallic(n, rng, base, ratios=(1, 1.71, 2.44, 3.62, 5.1)) * np.exp(-t / decay)
    sig += 0.5 * np.sin(2 * np.pi * base * 0.5 * t) * np.exp(-t / (decay * 0.5))
    sig = bp(sig, 150, 9000)
    return sat(sig, 1.4, 'tanh')


# --------------------------------------------------------------------------- 808 / BASS
def sub808(rng, freq, dur=2.0, glide_from=None, glide_time=0.06, drive=1.6,
           harmonic=0.25, decay_tau=None, click=0.0, lp_f=3200, style='clean'):
    n = n_of(dur)
    t = np.arange(n) / FS
    if glide_from:
        f = freq + (glide_from - freq) * np.exp(-t / glide_time)
    else:
        f = np.full(n, freq)
    ph = 2 * np.pi * np.cumsum(f) / FS
    sig = np.sin(ph)
    if harmonic:
        sig += harmonic * np.sin(2 * ph) * 0.6 + harmonic * 0.3 * np.sin(3 * ph)
    tau = decay_tau or dur / 1.6
    env = (1 - np.exp(-t / 0.004)) * np.exp(-t / tau)
    sig *= env
    if click:
        sig += click * bp(noise(n, rng), 1500, 8000) * np.exp(-t / 0.004)
    if style == 'distorted':
        sig = sat(sig, drive * 4, 'tanh')
        sig = bitcrush(sig, bits=10, downsample=1)
    elif style == 'soft':
        sig = sat(sig, drive * 0.6, 'tanh')
    elif style == 'reese':
        sig = np.sin(ph) + 0.5 * np.sin(2 * np.pi * np.cumsum(f * 1.006) / FS)
        sig = sat(sig, drive * 2, 'tanh')
    else:
        sig = sat(sig, drive, 'tanh')
    sig = lp(sig, lp_f, 2)
    sig = dc_block(sig)
    # long fade at end to avoid clicks
    tail = n_of(0.02)
    if n > tail:
        sig[-tail:] *= np.linspace(1, 0, tail)
    return sig


def bass_synth(rng, freq, dur=1.2, style='saw', cutoff=600, env_amt=2200, drive=1.3, sub=0.5):
    n = n_of(dur)
    t = np.arange(n) / FS
    if style == 'saw':
        osc_ = saw_ph(2 * np.pi * freq * t) + 0.5 * saw_ph(2 * np.pi * freq * 1.005 * t)
    elif style == 'square':
        osc_ = sqr_ph(2 * np.pi * freq * t) * 0.7 + saw_ph(2 * np.pi * freq * 0.5 * t) * 0.3
    elif style == 'pluck':
        osc_ = saw_ph(2 * np.pi * freq * t)
    else:
        osc_ = np.sin(2 * np.pi * freq * t)
    env = (1 - np.exp(-t / 0.003)) * np.exp(-t / (dur / 2.2))
    cut = cutoff + env_amt * np.exp(-t / 0.12)
    sig = tv_lp(osc_, cut, block=64)
    sig *= env
    sig += sub * np.sin(2 * np.pi * freq * t) * env
    sig = sat(sig, drive, 'tanh')
    return dc_block(sig)


def bass_guitar(rng, freq, dur=1.4, bright=0.45, damp=0.55, drive=1.2):
    sig = ks_pluck(freq, dur, bright=bright, damp=damp, rng=rng)
    sig = peaking(sig, freq * 2, 3.0, 1.0)
    sig = lp(sig, 3200, 2)
    sig = hp(sig, 40, 1)
    return sat(sig, drive, 'tanh')
