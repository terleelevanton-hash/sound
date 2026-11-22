"""Sound-design FX: risers, impacts, textures, foley, transitions."""
import numpy as np
from .dsp import *
from . import drums as D


def riser(rng, dur=3.0, lo=300, hi=9000, tone=True, noise_amt=1.0, drive=1.2):
    n = n_of(dur)
    t = np.arange(n) / FS
    prog = (t / dur) ** 1.6
    srcc = lo * (hi / lo) ** prog
    nz = tv_bp(noise(n, rng), srcc * 0.6, srcc * 1.6, block=64)
    amp = (t / dur) ** 2.2
    sig = noise_amt * nz * amp
    if tone:
        f = 110 * 2 ** (prog * 5.5)
        sig += 0.35 * saw_ph(2 * np.pi * np.cumsum(f) / FS) * amp
    sig = sat(sig, drive, 'tanh')
    sig = reverb(sig, wet=0.25, decay=0.9, tone=8000, rng=rng)[:n]
    return sig


def downlifter(rng, dur=2.5, lo=200, hi=7000, rng2=None):
    x = riser(rng, dur, lo, hi)
    return reverse(x)


def impact(rng, decay=1.6, f0=55, boom=1.0, noise_amt=0.8):
    n = n_of(decay * 1.6)
    t = np.arange(n) / FS
    f = f0 * (1 + 1.4 * np.exp(-t / 0.06))
    body = np.sin(2 * np.pi * np.cumsum(f) / FS) * np.exp(-t / (decay * 0.55))
    nz = bp(noise(n, rng), 120, 6000) * np.exp(-t / 0.09) * noise_amt
    crack = bp(noise(n, rng), 2000, 12000) * np.exp(-t / 0.01) * 0.5
    sig = sat(boom * body + nz + crack, 1.8, 'tanh')
    sig = reverb(sig, wet=0.35, decay=decay, tone=4000, rng=rng)[:n]
    return sig


def sweep(rng, dur=1.2, f_from=400, f_to=8000, rise=True):
    n = n_of(dur)
    t = np.arange(n) / FS
    prog = (t / dur) ** 1.4 if rise else 1 - (t / dur) ** 1.4
    cen = f_from * (f_to / f_from) ** prog
    sig = tv_bp(noise(n, rng), cen * 0.5, cen * 1.8, block=64)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.2
    return sat(sig * env, 1.2, 'tanh')


def reverse_reverb(rng, dur=2.0, src='pluck'):
    if src == 'pluck':
        x = D.blip(rng, f0=1200, f1=400, decay=0.1)
    elif src == 'cymbal':
        x = D.crash(rng, decay=0.8)
    else:
        x = D.snare(rng, decay=0.15)
    w = reverb(x, wet=0.9, decay=dur * 0.6, tone=6000, rng=rng)
    w = w[:n_of(dur)]
    return reverse(w)


def reverse_cymbal(rng, dur=2.0):
    x = D.crash(rng, decay=dur * 0.5, hp_f=3000)
    return reverse(x[:n_of(dur)])


def vinyl(rng, dur=4.0, pop_rate=6.0, tone=9000, hiss=0.06):
    n = n_of(dur)
    t = np.arange(n) / FS
    sig = rng.standard_normal(n) * hiss
    sig = lp(sig, tone, 2)
    sig = hp(sig, 200, 2)
    # dust / pops
    k = int(pop_rate * dur)
    for _ in range(k):
        i = int(rng.integers(0, n - 400))
        L = int(rng.integers(20, 400))
        pop = rng.standard_normal(L) * np.exp(-np.arange(L) / (L * 0.3))
        sig[i:i + L] += pop * rng.uniform(0.2, 1.0)
    # slow wow
    sig *= 1 + 0.05 * np.sin(2 * np.pi * 0.35 * t)
    return sig


def tape_hiss(rng, dur=4.0):
    n = n_of(dur)
    sig = rng.standard_normal(n) * 0.08
    sig = lp(sig, 11000, 2)
    sig = hp(sig, 400, 2)
    sig *= 1 + 0.08 * np.sin(2 * np.pi * 0.6 * np.arange(n) / FS)
    return sig


def rain(rng, dur=5.0):
    n = n_of(dur)
    sig = bp(noise(n, rng), 400, 9000) * 0.5
    drops = int(60 * dur)
    for _ in range(drops):
        i = int(rng.integers(0, n - 2000))
        L = int(rng.integers(200, 1800))
        d = np.sin(2 * np.pi * rng.uniform(1200, 4000) * np.arange(L) / FS) * np.exp(-np.arange(L) / (L * 0.25))
        sig[i:i + L] += d * rng.uniform(0.05, 0.25)
    return sig * 0.6


def wind(rng, dur=5.0):
    n = n_of(dur)
    t = np.arange(n) / FS
    cen = 400 + 300 * np.sin(2 * np.pi * 0.13 * t) + 150 * np.sin(2 * np.pi * 0.31 * t)
    sig = tv_bp(noise(n, rng), cen * 0.7, cen * 1.5, block=256)
    env = 0.6 + 0.4 * np.sin(2 * np.pi * 0.09 * t)
    return sig * env


def fire(rng, dur=4.0):
    n = n_of(dur)
    base = bp(noise(n, rng), 100, 2500) * 0.3
    for _ in range(int(25 * dur)):
        i = int(rng.integers(0, n - 1500))
        L = int(rng.integers(100, 1200))
        burst = rng.standard_normal(L) * np.exp(-np.arange(L) / (L * 0.2))
        base[i:i + L] += burst * rng.uniform(0.05, 0.4)
    return base


def static_noise(rng, dur=2.0):
    n = n_of(dur)
    sig = rng.standard_normal(n)
    sig = bitcrush(sig, bits=3, downsample=6)
    sig = bp(sig, 500, 9000)
    return sig


def underwater(rng, dur=3.0):
    n = n_of(dur)
    t = np.arange(n) / FS
    sig = lp(noise(n, rng), 700, 2)
    sig *= 1 + 0.3 * np.sin(2 * np.pi * 2.5 * t)
    sig += 0.2 * np.sin(2 * np.pi * 60 * t) * np.exp(-t / 0.5)
    return sig


def glitch(rng, dur=1.2, bits=6, stutter=True):
    n = n_of(dur)
    sig = np.zeros(n)
    pos = 0
    while pos < n:
        L = int(rng.integers(200, 4000))
        kind = rng.integers(0, 4)
        m = min(L, n - pos)
        if kind == 0:
            seg = rng.standard_normal(m) * 0.5
        elif kind == 1:
            seg = np.sin(2 * np.pi * rng.uniform(80, 3000) * np.arange(m) / FS)
        elif kind == 2:
            seg = np.repeat(rng.standard_normal(max(1, m // 40)), 40)[:m]
        else:
            seg = np.sin(2 * np.pi * np.cumsum(np.linspace(2000, 100, m)) / FS)
        seg = bitcrush(seg, bits=int(rng.integers(3, 9)), downsample=int(rng.integers(1, 5)))
        seg = seg[:m]
        if len(seg) < m:
            seg = np.pad(seg, (0, m - len(seg)))
        sig[pos:pos + m] = seg * rng.uniform(0.3, 1.0)
        pos += m
    sig = bp(sig, 150, 12000)
    return sat(sig, 1.4, 'tanh')


def sub_drop(rng, dur=1.8, f0=90, f1=25):
    n = n_of(dur)
    t = np.arange(n) / FS
    f = f1 + (f0 - f1) * np.exp(-t / (dur * 0.35))
    sig = np.sin(2 * np.pi * np.cumsum(f) / FS) * np.exp(-t / (dur * 0.6))
    sig = sat(sig, 2.0, 'tanh')
    return lp(sig, 300)


def tape_stop(rng, dur=1.5, f0=220, kind='saw'):
    n = n_of(dur)
    t = np.arange(n) / FS
    speed = np.clip(1 - (t / dur) ** 1.5, 0, 1)
    f = f0 * speed + 8
    sig = osc(kind, f, n, fs=FS)
    env = (1 - np.exp(-t / 0.01)) * np.clip(1 - t / dur, 0, 1) ** 0.4
    sig = sat(sig * env, 1.3, 'tanh')
    return lp(sig, 8000)


def snare_roll(rng, dur=2.0, start_rate=8, end_rate=40, tone=200):
    n = n_of(dur)
    sig = np.zeros(n)
    t = 0.0
    while t < dur:
        rate = start_rate + (end_rate - start_rate) * (t / dur) ** 1.4
        i = n_of(t)
        hit = D.snare(rng, tone=tone * rng.uniform(0.9, 1.1), decay=0.08, bright=6000)
        L = min(len(hit), n - i)
        if L > 0:
            sig[i:i + L] += hit[:L] * (0.4 + 0.6 * t / dur)
        t += 1.0 / rate
    return sig


def sub_blast(rng, dur=1.0):
    n = n_of(dur)
    t = np.arange(n) / FS
    sig = np.sin(2 * np.pi * 45 * t) * np.exp(-t / 0.25)
    sig += bp(noise(n, rng), 2000, 14000) * np.exp(-t / 0.05) * 0.6
    return sat(sig, 2.2, 'tanh')


def siren(rng, dur=2.0, f_lo=500, f_hi=1400, rate=2.2, kind='sine'):
    n = n_of(dur)
    t = np.arange(n) / FS
    f = f_lo + (f_hi - f_lo) * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t))
    sig = osc(kind, f, n, fs=FS)
    sig *= (1 - np.exp(-t / 0.02))
    return sat(lp(sig, 6000), 1.2, 'tanh')


# ---------------------------------------------------------------- foley
def knock(rng, hits=2, decay=0.12, low=180):
    dur = 0.3 * hits + 0.2
    n = n_of(dur)
    sig = np.zeros(n)
    t0 = 0.0
    for k in range(hits):
        i = n_of(t0)
        L = min(n - i, n_of(0.35))
        tt = np.arange(L) / FS
        f = low * (1 + 0.6 * np.exp(-tt / 0.02))
        hit = np.sin(2 * np.pi * np.cumsum(f) / FS) * np.exp(-tt / decay)
        hit += bp(noise(L, rng), 300, 4000) * np.exp(-tt / 0.02) * 0.6
        sig[i:i + L] += hit
        t0 += 0.18 * rng.uniform(0.8, 1.4)
    return sat(sig, 1.4, 'tanh')


def glass_break(rng, decay=0.8):
    n = n_of(decay * 1.6)
    sig = np.zeros(n)
    for k in range(int(rng.integers(8, 18))):
        i = int(rng.integers(0, n // 3))
        L = int(rng.integers(400, 4000))
        L = min(L, n - i)
        f = rng.uniform(2000, 7000)
        g = np.sin(2 * np.pi * f * np.arange(L) / FS) * np.exp(-np.arange(L) / (L * 0.3))
        sig[i:i + L] += g * rng.uniform(0.1, 0.5)
    sig += bp(noise(n, rng), 3000, 15000) * np.exp(-np.arange(n) / FS / 0.05) * 0.7
    return sat(sig, 1.2, 'tanh')


def water_drop(rng, dur=0.5):
    n = n_of(dur)
    t = np.arange(n) / FS
    f = 900 * np.exp(-t / 0.05) + 350
    sig = np.sin(2 * np.pi * np.cumsum(f) / FS) * np.exp(-t / 0.08)
    sig += 0.3 * bp(noise(n, rng), 1500, 6000) * np.exp(-t / 0.01)
    return sat(sig, 1.1, 'tanh')


def camera_shutter(rng):
    n = n_of(0.35)
    sig = np.zeros(n)
    for i, g in [(0, 1.0), (n_of(0.09), 0.8), (n_of(0.13), 0.5)]:
        L = min(n - i, n_of(0.03))
        sig[i:i + L] += bp(noise(L, rng), 1500, 9000) * np.exp(-np.arange(L) / (L * 0.3)) * g
    return sat(sig, 1.3, 'tanh')


def switch_click(rng):
    n = n_of(0.12)
    t = np.arange(n) / FS
    sig = bp(noise(n, rng), 800, 9000) * np.exp(-t / 0.004)
    sig += np.sin(2 * np.pi * 1400 * t) * np.exp(-t / 0.008) * 0.5
    return sat(sig, 1.4, 'tanh')


def lighter(rng, dur=1.0):
    n = n_of(dur)
    t = np.arange(n) / FS
    sig = bp(noise(n, rng), 1500, 8000) * np.exp(-t / 0.15) * 0.6
    for _ in range(int(rng.integers(20, 50))):
        i = int(rng.integers(0, n - 500))
        L = int(rng.integers(20, 300))
        sig[i:i + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L * 0.2)) * 0.3
    return sig


def paper(rng, dur=0.6):
    n = n_of(dur)
    sig = np.zeros(n)
    for _ in range(int(rng.integers(10, 25))):
        i = int(rng.integers(0, max(1, n - 800)))
        L = int(rng.integers(100, 700))
        L = min(L, n - i)
        sig[i:i + L] += bp(noise(L, rng), 2000, 9000) * np.exp(-np.arange(L) / (L * 0.35)) * rng.uniform(0.2, 0.7)
    return sig


def whoosh_bang(rng, dur=1.2):
    x = sweep(rng, dur * 0.7, 300, 6000, rise=True)
    b = impact(rng, decay=0.8, f0=60)
    out = np.zeros(max(len(x), len(b)))
    out[:len(x)] += x * 0.7
    off = n_of(dur * 0.6)
    m = min(len(b), len(out) - off)
    out[off:off + m] += b[:m] * 0.9
    return out
