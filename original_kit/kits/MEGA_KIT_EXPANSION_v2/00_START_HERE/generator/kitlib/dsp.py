"""DSP primitives for the mega drum kit generator (numpy/scipy only)."""
import numpy as np
from scipy.signal import lfilter, sosfilt, butter, fftconvolve, sosfilt_zi

FS = 44100
SR = FS


# ----------------------------------------------------------------------------- basics
def n_of(dur, fs=FS):
    return max(1, int(round(dur * fs)))


def tvec(dur, fs=FS):
    return np.arange(n_of(dur, fs)) / fs


def sine(n, freq, phase=0.0, fs=FS):
    f = np.full(n, float(freq)) if np.isscalar(freq) else np.asarray(freq, float)
    ph = 2 * np.pi * np.cumsum(f) / fs + phase
    return np.sin(ph)


def saw_ph(ph):
    return 2.0 * (ph / (2 * np.pi) % 1.0) - 1.0


def sqr_ph(ph):
    return np.sign(np.sin(ph))


def tri_ph(ph):
    return 2.0 * np.abs(2.0 * (ph / (2 * np.pi) % 1.0) - 1.0) - 1.0


def osc(kind, freq, n, phase=0.0, fs=FS):
    f = np.full(n, float(freq)) if np.isscalar(freq) else np.asarray(freq, float)
    ph = 2 * np.pi * np.cumsum(f) / fs + phase
    if kind == 'sine':
        return np.sin(ph)
    if kind == 'saw':
        return saw_ph(ph)
    if kind == 'square':
        return sqr_ph(ph)
    if kind == 'tri':
        return tri_ph(ph)
    if kind == 'pulse25':
        return np.where((ph / (2 * np.pi) % 1.0) < 0.25, 1.0, -1.0)
    raise ValueError(kind)


def noise(n, rng=None):
    rng = rng or np.random.default_rng()
    return rng.standard_normal(n)


# ----------------------------------------------------------------------------- envelopes
def exp_dec(n, tau, fs=FS, floor=1e-4):
    t = np.arange(n) / fs
    return np.exp(-t / max(tau, 1e-4))


def perc_env(n, attack=0.001, decay=0.2, curve=1.0, fs=FS):
    t = np.arange(n) / fs
    a = np.clip(t / max(attack, 1e-5), 0, 1)
    if attack > 0:
        a = a ** 0.6
    d = np.exp(-np.clip(t - attack, 0, None) / max(decay, 1e-4) * curve)
    return a * d


def adsr(n, a=0.01, d=0.1, s=0.7, r=0.2, fs=FS, curve=2.0):
    t = np.arange(n) / fs
    total = n / fs
    env = np.zeros(n)
    ai, di, ri = n_of(a, fs), n_of(d, fs), n_of(r, fs)
    ai = min(ai, n)
    di = min(di, n - ai)
    rel_start = max(0, n - ri)
    # attack
    if ai:
        env[:ai] = (np.linspace(0, 1, ai)) ** (1 / curve)
    # decay to sustain
    if di:
        env[ai:ai + di] = np.linspace(1, s, di)
    env[ai + di:] = s
    if ri and rel_start > ai + di:
        env[rel_start:] = np.linspace(env[rel_start], 0.0, n - rel_start) ** 1.0
    return np.clip(env, 0, None)


def shape_env(env, curve):
    return np.power(np.clip(env, 0, None), curve)


# ----------------------------------------------------------------------------- filters
def lp(x, f, order=2, fs=FS):
    f = min(max(f, 10.0), fs * 0.49)
    sos = butter(order, f / (fs / 2), btype='low', output='sos')
    return sosfilt(sos, x)


def hp(x, f, order=2, fs=FS):
    f = min(max(f, 10.0), fs * 0.49)
    sos = butter(order, f / (fs / 2), btype='high', output='sos')
    return sosfilt(sos, x)


def bp(x, lo, hi, order=2, fs=FS):
    lo = min(max(lo, 10.0), fs * 0.49)
    hi = min(max(hi, lo * 1.01), fs * 0.49)
    sos = butter(order, [lo / (fs / 2), hi / (fs / 2)], btype='band', output='sos')
    return sosfilt(sos, x)


def notch(x, f, q=4.0, fs=FS):
    sos = butter(2, [f / (fs / 2) * (1 - 1 / (2 * q)), min(0.99, f / (fs / 2) * (1 + 1 / (2 * q)))],
                 btype='bandstop', output='sos')
    return sosfilt(sos, x)


def peaking(x, f, gain_db, q=1.0, fs=FS):
    """RBJ peaking EQ, single biquad."""
    A = 10 ** (gain_db / 40.0)
    w0 = 2 * np.pi * min(max(f, 20.0), fs * 0.48) / fs
    alpha = np.sin(w0) / (2 * q)
    b = [1 + alpha * A, -2 * np.cos(w0), 1 - alpha * A]
    a = [1 + alpha / A, -2 * np.cos(w0), 1 - alpha / A]
    return lfilter(b, a, x)


def tv_lp(x, cutoff, q=0.707, block=96, fs=FS):
    """Time varying lowpass; cutoff array (per sample) or callable(t)->hz."""
    n = len(x)
    if callable(cutoff):
        t = np.arange(n) / fs
        cutoff = cutoff(t)
    cutoff = np.clip(np.asarray(cutoff, float), 30.0, fs * 0.48)
    y = np.empty(n)
    zi = None
    for s in range(0, n, block):
        e = min(n, s + block)
        f = float(cutoff[s:e].mean())
        sos = butter(2, f / (fs / 2), btype='low', output='sos')
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        y[s:e], zi = sosfilt(sos, x[s:e], zi=zi)
    return y


def tv_bp(x, lo, hi, block=96, fs=FS):
    n = len(x)
    if callable(lo):
        t = np.arange(n) / fs
        lo, hi = lo(t), hi(t)
    lo = np.clip(np.asarray(lo, float), 20.0, fs * 0.47)
    hi = np.clip(np.asarray(hi, float), 40.0, fs * 0.49)
    y = np.empty(n)
    zi = None
    for s in range(0, n, block):
        e = min(n, s + block)
        f1, f2 = float(lo[s:e].mean()), float(hi[s:e].mean())
        f2 = max(f2, f1 * 1.05)
        f1 = min(f1, fs * 0.45)
        sos = butter(2, [f1 / (fs / 2), min(f2, fs * 0.48) / (fs / 2)], btype='band', output='sos')
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        y[s:e], zi = sosfilt(sos, x[s:e], zi=zi)
    return y


def formant(x, freqs, qs, gains=None, fs=FS):
    """Parallel bandpass formant bank (vowel-ish resonator)."""
    gains = gains if gains is not None else [1.0] * len(freqs)
    out = np.zeros_like(x)
    for f, q, g in zip(freqs, qs, gains):
        bw = f / max(q, 0.3)
        lo, hi = max(20, f - bw / 2), min(fs * 0.48, f + bw / 2)
        out += g * bp(x, lo, hi, order=2, fs=fs)
    return out


# ----------------------------------------------------------------------------- character
def sat(x, drive=1.0, kind='tanh', asym=0.0):
    if kind == 'tanh':
        return np.tanh(x * drive + asym) / np.tanh(max(drive, 1e-3))
    if kind == 'soft':
        y = np.tanh(x * drive)
        return y / max(np.max(np.abs(y)), 1e-9)
    if kind == 'hard':
        return np.clip(x * drive, -1, 1) / max(1.0, 1.0)
    if kind == 'fold':
        return np.sin(x * drive * np.pi * 0.5)
    raise ValueError(kind)


def bitcrush(x, bits=8, downsample=1):
    if downsample > 1:
        idx = np.arange(0, len(x), downsample)
        y = np.zeros_like(x)
        y[idx] = x[idx]
        # sample and hold
        x = np.repeat(y[idx], downsample)[:len(x)]
        if len(x) < len(y):
            x = np.pad(x, (0, len(y) - len(x)), mode='edge')
    levels = 2 ** bits
    return np.round(np.clip(x, -1, 1) * levels) / levels


def make_ir(decay=1.4, predelay=0.01, tone=6000, early=0.5, rng=None, fs=FS):
    rng = rng or np.random.default_rng(1)
    n = n_of(decay, fs)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / fs / (decay / 4.0))
    ir = lp(ir, tone, 2, fs)
    ir = hp(ir, 120, 2, fs)
    # early reflections
    e = np.zeros(n)
    for d, g in [(0.007, .6), (0.013, .45), (0.021, .35), (0.031, .3), (0.045, .22)]:
        i = n_of(d, fs)
        if i < n:
            e[i] += g
    ir = ir + early * e * np.max(np.abs(ir))
    ir *= np.exp(-np.arange(n) / fs / (decay / 3.0))
    ir = np.concatenate([np.zeros(n_of(predelay, fs)), ir])
    return ir / max(np.max(np.abs(ir)), 1e-9)


def reverb(x, wet=0.25, decay=1.4, tone=6000, predelay=0.01, rng=None, fs=FS):
    ir = make_ir(decay, predelay, tone, rng=rng, fs=fs)
    w = fftconvolve(x, ir)[:len(x) + n_of(decay * 0.8, fs)]
    w = w / max(np.max(np.abs(w)), 1e-9) * np.max(np.abs(x))
    out = np.zeros(len(w))
    out[:len(x)] += x * (1 - wet)
    out += w * wet
    return out


def chorus(x, depth_ms=8, rate=0.7, mix=0.4, taps=3, fs=FS):
    n = len(x)
    t = np.arange(n) / fs
    out = np.zeros(n + n_of(depth_ms / 1000 * 4, fs))
    out[:n] += (1 - mix) * x
    for k in range(taps):
        d = (depth_ms / 1000) * (0.6 + 0.4 * np.sin(2 * np.pi * rate * (1 + 0.23 * k) * t + k * 1.7))
        idx = np.arange(n) - d * fs
        lag = np.interp(idx, np.arange(n), x)
        out[:n] += (mix / taps) * lag * (0.8 ** k if k < 2 else 0.6)
    return out


def delay(x, time_s=0.25, fb=0.35, mix=0.25, taps=3, fs=FS):
    n = len(x)
    out = x.copy()
    d = n_of(time_s, fs)
    for k in range(1, taps + 1):
        s = k * d
        if s >= n:
            break
        seg = x[:n - s] * (fb ** (k - 1)) * mix
        out[s:] += seg
    return out


def reverse(x):
    return x[::-1].copy()


def normalize(x, peak_db=-1.0):
    peak = np.max(np.abs(x)) or 1e-9
    return x / peak * (10 ** (peak_db / 20))


def limiter_soft(x, ceiling=0.95):
    return np.tanh(x / ceiling) * ceiling


def fade(x, fin=0.001, fout=0.01, fs=FS):
    x = x.copy()
    a, b = n_of(fin, fs), n_of(fout, fs)
    a, b = min(a, len(x)), min(b, len(x))
    if a:
        x[:a] *= np.linspace(0, 1, a) ** 0.5
    if b:
        x[-b:] *= np.linspace(1, 0, b) ** 1.5
    return x


def dc_block(x, fs=FS):
    return hp(x, 20, 2, fs)


def trim_silence(x, thresh_db=-70, fs=FS, pad_ms=2):
    if len(x) == 0:
        return x
    peak = np.max(np.abs(x)) or 1e-9
    thr = peak * 10 ** (thresh_db / 20)
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0:
        return x
    pad = n_of(pad_ms / 1000, fs)
    a = max(0, idx[0] - pad)
    b = min(len(x), idx[-1] + pad)
    return x[a:b]


def ks_pluck(freq, dur, bright=0.5, damp=0.5, drive=1.0, fs=FS, rng=None):
    """Karplus-Strong plucked string with fractional delay."""
    rng = rng or np.random.default_rng()
    n = n_of(dur, fs)
    d = fs / max(freq, 20.0) - 0.5
    ni = int(np.floor(d))
    frac = d - ni
    ni = max(ni, 2)
    # excitation: filtered noise burst
    exc = rng.standard_normal(ni)
    exc = lp(exc, 1000 + bright * 12000, 2, fs)
    exc = hp(exc, 80, 1, fs)
    exc /= max(np.max(np.abs(exc)), 1e-9)
    buf = list(exc)
    y = np.zeros(n)
    g = 0.5 * (1.0 - 0.35 * damp) * 2  # loop gain
    g = min(0.9995, 0.98 + 0.019 * (1 - damp))
    # vectorized via lfilter: y[n] = exc + g*(0.5 y[n-ni] + 0.5 y[n-ni-1])
    y = np.zeros(n)
    y[:ni] = exc
    # process in blocks with a delay line (python loop over samples but only for tail)
    b = [1.0]
    a = np.zeros(ni + 2)
    a[0] = 1.0
    a[ni] = -g * (1 - frac * 0.0)
    a[ni + 1] = -g * 0.5
    a[ni] = -g * 0.5
    y = lfilter(b, a, np.concatenate([exc, np.zeros(n - ni)]))[:n]
    y = y / max(np.max(np.abs(y)), 1e-9)
    return y


def stereo(x, width=0.3, fs=FS):
    """Cheap pseudo-stereo: haas + slight detune-ish allpass."""
    d = int(0.004 * fs * (1 + width))
    r = np.zeros(len(x) + d)
    r[d:] = x
    l = x.copy()
    r = r[:len(x)]
    return np.stack([l * (1 - 0.1 * width), r * (1 + 0.0)], axis=1)


def rms(x):
    return float(np.sqrt(np.mean(np.square(x)) + 1e-12))


def peak_db(x):
    return float(20 * np.log10(max(np.max(np.abs(x)), 1e-9)))


def spectral_centroid(x, fs=FS):
    X = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    f = np.fft.rfftfreq(len(x), 1 / fs)
    if X.sum() == 0:
        return 0.0
    return float((X * f).sum() / X.sum())


def midi_to_freq(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def note_name(m):
    return NOTE_NAMES[m % 12] + str(m // 12 - 1)


def note_filename(m):
    return NOTE_NAMES[m % 12].replace('#', 's') + str(m // 12 - 1)
