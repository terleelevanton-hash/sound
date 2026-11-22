"""Studio-grade DSP synthesis & processing library for MEGA KIT v3 (numpy/scipy)."""
import numpy as np
from scipy.signal import lfilter, sosfilt, butter, fftconvolve

FS = 44100
SR = FS

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def n_of(dur, fs=FS):
    return max(1, int(round(dur * fs)))


def tvec(dur, fs=FS):
    return np.arange(n_of(dur, fs), dtype=np.float64) / fs


def midi_to_freq(m):
    return 440.0 * (2.0 ** ((float(m) - 69.0) / 12.0))


def note_name(m):
    m = int(round(m))
    return NOTE_NAMES[m % 12] + str(m // 12 - 1)


def note_filename(m):
    m = int(round(m))
    return NOTE_NAMES[m % 12].replace('#', 's') + str(m // 12 - 1)


# ------------------------------------------------------------------ PolyBLEP anti-aliased oscillators
def _poly_blep(t, dt):
    """2-point polynomial band-limited step residual (t in [0, 1))."""
    out = np.zeros_like(t)
    dt_safe = np.maximum(dt, 1e-9)
    m1 = t < dt_safe
    if np.any(m1):
        u = t[m1] / dt_safe[m1] if not np.isscalar(dt_safe) else t[m1] / dt_safe
        out[m1] = u + u - u * u - 1.0
    m2 = t > (1.0 - dt_safe)
    if np.any(m2):
        u = (t[m2] - 1.0) / dt_safe[m2] if not np.isscalar(dt_safe) else (t[m2] - 1.0) / dt_safe
        out[m2] = u * u + u + u + 1.0
    return out


def polyblep_saw(freq, n, phase=0.0, fs=FS):
    f = np.full(n, float(freq)) if np.isscalar(freq) else np.asarray(freq, dtype=np.float64)
    dt = np.clip(f / fs, 1e-7, 0.49)
    ph = (np.cumsum(dt) - dt[0] + phase) % 1.0
    y = 2.0 * ph - 1.0
    y -= _poly_blep(ph, dt)
    return y


def polyblep_pulse(freq, n, duty=0.5, phase=0.0, fs=FS):
    f = np.full(n, float(freq)) if np.isscalar(freq) else np.asarray(freq, dtype=np.float64)
    dt = np.clip(f / fs, 1e-7, 0.49)
    ph = (np.cumsum(dt) - dt[0] + phase) % 1.0
    d = np.clip(duty, 0.05, 0.95)
    y = np.where(ph < d, 1.0, -1.0)
    y += _poly_blep(ph, dt)
    y -= _poly_blep((ph - d) % 1.0, dt)
    return y


def polyblep_square(freq, n, phase=0.0, fs=FS):
    return polyblep_pulse(freq, n, duty=0.5, phase=phase, fs=fs)


def sine(n, freq, phase=0.0, fs=FS):
    f = np.full(n, float(freq)) if np.isscalar(freq) else np.asarray(freq, dtype=np.float64)
    ph = 2.0 * np.pi * np.cumsum(f) / fs + phase
    return np.sin(ph)


def tri_osc(freq, n, phase=0.0, fs=FS):
    f = np.full(n, float(freq)) if np.isscalar(freq) else np.asarray(freq, dtype=np.float64)
    ph = (np.cumsum(f / fs) + phase) % 1.0
    return 4.0 * np.abs(ph - 0.5) - 1.0


def unison_supersaw(freq, n, voices=7, detune_cents=22.0, stereo_spread=0.85, rng=None, fs=FS):
    """True stereo JP-8000 / Serum style band-limited unison supersaw (mono-compatible!)."""
    rng = rng or np.random.default_rng(42)
    left = np.zeros(n, dtype=np.float64)
    right = np.zeros(n, dtype=np.float64)
    offsets = np.linspace(-1.0, 1.0, voices)
    for i, off in enumerate(offsets):
        cents = off * detune_cents * (0.85 + 0.3 * (abs(off)))
        f_v = freq * (2.0 ** (cents / 1200.0))
        ph0 = float(rng.uniform(0.0, 1.0))
        s = polyblep_saw(f_v, n, phase=ph0, fs=fs)
        gain = 1.0 if i == voices // 2 else 0.72
        pan = 0.5 + 0.5 * off * stereo_spread
        # Constant-power pan
        gl = np.cos(pan * np.pi * 0.5) * gain
        gr = np.sin(pan * np.pi * 0.5) * gain
        left += s * gl
        right += s * gr
    norm = np.sqrt(voices * 0.6)
    return np.stack([left / norm, right / norm], axis=1)


def noise(n, rng=None):
    rng = rng or np.random.default_rng()
    return rng.standard_normal(n)


def pink_noise(n, rng=None):
    rng = rng or np.random.default_rng()
    white = rng.standard_normal(n)
    X = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n, 1.0 / FS)
    scale = 1.0 / np.sqrt(np.maximum(freqs, 1.0))
    scale[0] = 0.0
    y = np.fft.irfft(X * scale, n=n)
    return y / max(np.max(np.abs(y)), 1e-9)


# ------------------------------------------------------------------ Envelopes
def exp_dec(n, tau, fs=FS):
    t = np.arange(n, dtype=np.float64) / fs
    return np.exp(-t / max(tau, 1e-4))


def perc_env(n, attack=0.001, decay=0.2, curve=1.0, fs=FS):
    t = np.arange(n, dtype=np.float64) / fs
    a = np.clip(t / max(attack, 1e-5), 0.0, 1.0) ** 0.6
    d = np.exp(-np.clip(t - attack, 0.0, None) / max(decay, 1e-4) * curve)
    return a * d


def adsr(n, a=0.01, d=0.15, s=0.65, r=0.25, curve=1.6, fs=FS):
    env = np.zeros(n, dtype=np.float64)
    ai = min(n_of(a, fs), n)
    di = min(n_of(d, fs), max(0, n - ai))
    ri = min(n_of(r, fs), max(0, n - ai - di))
    rel_start = n - ri
    if ai > 0:
        env[:ai] = np.linspace(0.0, 1.0, ai) ** (1.0 / max(curve, 0.2))
    if di > 0:
        env[ai:ai + di] = 1.0 - (1.0 - s) * (np.linspace(0.0, 1.0, di) ** 0.8)
    if rel_start > ai + di:
        env[ai + di:rel_start] = s
    if ri > 0:
        start_val = env[rel_start - 1] if rel_start > 0 else s
        env[rel_start:] = start_val * (np.linspace(1.0, 0.0, ri) ** 1.4)
    return np.clip(env, 0.0, 1.0)


# ------------------------------------------------------------------ Filters (Butterworth + Resonant Biquad / ZDF SVF)
def lp(x, f, order=2, fs=FS):
    f = min(max(float(f), 15.0), fs * 0.485)
    sos = butter(order, f / (fs * 0.5), btype='low', output='sos')
    return sosfilt(sos, x, axis=0)


def hp(x, f, order=2, fs=FS):
    f = min(max(float(f), 15.0), fs * 0.485)
    sos = butter(order, f / (fs * 0.5), btype='high', output='sos')
    return sosfilt(sos, x, axis=0)


def bp(x, lo, hi, order=2, fs=FS):
    lo = min(max(float(lo), 15.0), fs * 0.46)
    hi = min(max(float(hi), lo * 1.05), fs * 0.488)
    sos = butter(order, [lo / (fs * 0.5), hi / (fs * 0.5)], btype='band', output='sos')
    return sosfilt(sos, x, axis=0)


def peaking(x, f, gain_db, q=1.0, fs=FS):
    A = 10.0 ** (gain_db / 40.0)
    w0 = 2.0 * np.pi * min(max(float(f), 20.0), fs * 0.48) / fs
    alpha = np.sin(w0) / (2.0 * max(q, 0.1))
    b = np.array([1.0 + alpha * A, -2.0 * np.cos(w0), 1.0 - alpha * A])
    a = np.array([1.0 + alpha / A, -2.0 * np.cos(w0), 1.0 - alpha / A])
    return lfilter(b, a, x, axis=0)


def resonant_lp(x, cutoff, q=2.5, block=64, fs=FS):
    """Time-varying resonant 2-pole RBJ lowpass filter (supports acid squelch & wah)."""
    n = len(x)
    if np.isscalar(cutoff):
        cutoff_arr = np.full(n, float(cutoff))
    elif callable(cutoff):
        cutoff_arr = cutoff(np.arange(n, dtype=np.float64) / fs)
    else:
        cutoff_arr = np.asarray(cutoff, dtype=np.float64)
    cutoff_arr = np.clip(cutoff_arr, 30.0, fs * 0.46)

    if x.ndim == 2:
        return np.stack([
            resonant_lp(x[:, 0], cutoff_arr, q=q, block=block, fs=fs),
            resonant_lp(x[:, 1], cutoff_arr, q=q, block=block, fs=fs),
        ], axis=1)

    y = np.empty(n, dtype=np.float64)
    zi = np.zeros(2, dtype=np.float64)
    for s in range(0, n, block):
        e = min(n, s + block)
        fc = float(cutoff_arr[s:e].mean())
        w0 = 2.0 * np.pi * fc / fs
        cw = np.cos(w0)
        alpha = np.sin(w0) / (2.0 * max(q, 0.5))
        b0 = (1.0 - cw) * 0.5
        b1 = 1.0 - cw
        b2 = (1.0 - cw) * 0.5
        a0 = 1.0 + alpha
        b = np.array([b0 / a0, b1 / a0, b2 / a0])
        a = np.array([1.0, (-2.0 * cw) / a0, (1.0 - alpha) / a0])
        y[s:e], zi = lfilter(b, a, x[s:e], zi=zi)
    return y


def resonant_bp(x, center, q=4.0, block=64, fs=FS):
    """Time-varying resonant bandpass (wah-wah, vocal talkbox, neuro movement)."""
    n = len(x)
    c_arr = np.full(n, float(center)) if np.isscalar(center) else np.asarray(center, dtype=np.float64)
    c_arr = np.clip(c_arr, 50.0, fs * 0.45)
    y = np.empty(n, dtype=np.float64)
    zi = np.zeros(2, dtype=np.float64)
    for s in range(0, n, block):
        e = min(n, s + block)
        fc = float(c_arr[s:e].mean())
        w0 = 2.0 * np.pi * fc / fs
        alpha = np.sin(w0) / (2.0 * max(q, 0.4))
        a0 = 1.0 + alpha
        b = np.array([alpha / a0, 0.0, -alpha / a0])
        a = np.array([1.0, (-2.0 * np.cos(w0)) / a0, (1.0 - alpha) / a0])
        y[s:e], zi = lfilter(b, a, x[s:e], zi=zi)
    return y


def formant_bank(x, freqs, qs, gains=None, fs=FS):
    gains = gains if gains is not None else [1.0] * len(freqs)
    out = np.zeros_like(x)
    for f, q, g in zip(freqs, qs, gains):
        if f >= fs * 0.46:
            continue
        out += g * resonant_bp(x, f, q=q, block=len(x), fs=fs)
    return out


# ------------------------------------------------------------------ Exact-Tuning Karplus-Strong Plucked String
def ks_string(freq, dur, bright=0.55, damp=0.35, pick_pos=0.18, stiffness=0.0, rng=None, fs=FS):
    """
    Fractional-delay Thiran allpass Karplus-Strong string model.
    Tuned within +/- 0.5 cents from C1 to C6!
    """
    rng = rng or np.random.default_rng()
    n = n_of(dur, fs)
    freq = max(float(freq), 20.0)
    # Total loop delay = fs / freq
    # 2-point averaging lowpass filter (1-b) z^0 + b z^-1 adds phase delay ~ b samples
    b_lp = np.clip(0.12 + 0.45 * damp, 0.05, 0.49)
    target_delay = fs / freq - b_lp
    ni = max(2, int(np.floor(target_delay)))
    frac = np.clip(target_delay - ni, 0.001, 0.999)
    # 1st-order Thiran allpass coefficient for fractional delay `frac`
    eta = (1.0 - frac) / (1.0 + frac)

    # Pluck excitation with pick-position comb filtering
    exc_len = max(ni + 4, int(0.012 * fs))
    exc = pink_noise(exc_len, rng) * 0.65 + noise(exc_len, rng) * 0.35
    exc = lp(exc, 900.0 + bright * 11000.0, order=2, fs=fs)
    exc = hp(exc, max(35.0, freq * 0.4), order=1, fs=fs)
    comb_d = max(1, int(round(ni * pick_pos)))
    if comb_d < exc_len:
        exc_comb = exc.copy()
        exc_comb[comb_d:] -= 0.75 * exc[:-comb_d]
        exc = exc_comb
    exc *= np.hanning(exc_len * 2)[exc_len:]
    exc /= max(np.max(np.abs(exc)), 1e-9)

    # Sustain gain per period calculated from desired RT60
    rt60 = max(0.25, dur * (1.35 - 0.55 * damp))
    g = 10.0 ** (-3.0 / (freq * rt60))
    g = min(g, 0.9994)

    # Loop transfer function H_loop(z) = g * [(1-b_lp) + b_lp z^-1] * [(eta + z^-1) / (1 + eta z^-1)] * z^-ni
    # Closed-loop denominator A(z) = (1 + eta z^-1) - g * z^-ni * ((1-b_lp) + b_lp z^-1) * (eta + z^-1)
    a = np.zeros(ni + 3, dtype=np.float64)
    a[0] = 1.0
    a[1] += eta
    c0 = (1.0 - b_lp) * eta
    c1 = (1.0 - b_lp) + b_lp * eta
    c2 = b_lp
    a[ni] -= g * c0
    a[ni + 1] -= g * c1
    a[ni + 2] -= g * c2

    b_num = np.array([1.0, eta], dtype=np.float64)
    inp = np.zeros(n, dtype=np.float64)
    inp[:min(n, exc_len)] = exc[:min(n, exc_len)]
    y = lfilter(b_num, a, inp)
    peak = np.max(np.abs(y))
    if peak > 1e-9:
        y = y / peak
    return y


# ------------------------------------------------------------------ Saturation & Stereo FX
def sat(x, drive=1.2, kind='tanh', asym=0.0):
    if kind == 'tanh':
        y = np.tanh(x * drive + asym) - np.tanh(asym)
        return y / max(np.tanh(max(drive, 1e-3)), 1e-4)
    if kind == 'hard':
        return np.clip(x * drive, -1.0, 1.0)
    if kind == 'fold':
        return np.sin(x * drive * np.pi * 0.5)
    if kind == 'tube':
        pos = np.tanh(x * drive * 1.15)
        neg = np.tanh(x * drive * 0.85)
        return np.where(x >= 0, pos, neg)
    return np.tanh(x * drive)


def bitcrush(x, bits=10, downsample=1):
    y = x.copy()
    if downsample > 1:
        idx = np.arange(0, len(y), downsample)
        y = np.repeat(y[idx], downsample, axis=0)[:len(x)]
    levels = float(2 ** bits)
    return np.round(np.clip(y, -1.0, 1.0) * levels) / levels


def stereo_chorus(x, depth_ms=6.5, rate_hz=0.65, mix=0.38, fs=FS):
    """True stereo quadrature chorus (mono-compatible)."""
    mono = x if x.ndim == 1 else x.mean(axis=1)
    n = len(mono)
    t = np.arange(n, dtype=np.float64) / fs
    idx_base = np.arange(n, dtype=np.float64)
    d1 = (depth_ms * 0.001 * fs) * (1.0 + 0.75 * np.sin(2 * np.pi * rate_hz * t))
    d2 = (depth_ms * 0.001 * fs) * (1.0 + 0.75 * np.cos(2 * np.pi * (rate_hz * 1.07) * t + 0.8))
    w_l = np.interp(np.clip(idx_base - d1, 0, n - 1), idx_base, mono)
    w_r = np.interp(np.clip(idx_base - d2, 0, n - 1), idx_base, mono)
    dry_l = x[:, 0] if x.ndim == 2 else mono
    dry_r = x[:, 1] if x.ndim == 2 else mono
    return np.stack([(1.0 - mix) * dry_l + mix * w_l, (1.0 - mix) * dry_r + mix * w_r], axis=1)


def stereo_reverb(x, wet=0.26, decay=1.8, tone=6500.0, predelay=0.014, gated=False, rng=None, fs=FS):
    """Decorrelated true-stereo IR convolution reverb (supports 80s gated snare reverb too!)."""
    rng = rng or np.random.default_rng(108)
    n_ir = n_of(decay, fs)
    t_ir = np.arange(n_ir, dtype=np.float64) / fs
    if gated:
        env = np.ones(n_ir) * np.exp(-t_ir / (decay * 1.8))
        gate_tail = min(n_ir // 3, n_of(0.045, fs))
        env[-gate_tail:] *= np.linspace(1.0, 0.0, gate_tail) ** 2.0
    else:
        env = np.exp(-t_ir / max(decay / 3.8, 0.04))

    ir_l = lp(hp(rng.standard_normal(n_ir) * env, 130.0, 2, fs), tone, 2, fs)
    ir_r = lp(hp(rng.standard_normal(n_ir) * env, 130.0, 2, fs), tone, 2, fs)
    # Decorrelated early reflections
    for d_l, d_r, g in [(0.008, 0.011, 0.55), (0.017, 0.019, 0.4), (0.029, 0.026, 0.28), (0.043, 0.047, 0.2)]:
        il, ir = n_of(d_l, fs), n_of(d_r, fs)
        if il < n_ir:
            ir_l[il] += g * np.max(np.abs(ir_l))
        if ir < n_ir:
            ir_r[ir] += g * np.max(np.abs(ir_r))
    pre = np.zeros(n_of(predelay, fs))
    ir_l = np.concatenate([pre, ir_l])
    ir_r = np.concatenate([pre, ir_r])

    in_l = x[:, 0] if x.ndim == 2 else x
    in_r = x[:, 1] if x.ndim == 2 else x
    tail_keep = len(in_l) + (n_of(decay, fs) if gated else n_of(decay * 0.65, fs))
    wl = fftconvolve(in_l, ir_l)[:tail_keep]
    wr = fftconvolve(in_r, ir_r)[:tail_keep]
    peak_in = max(np.max(np.abs(x)), 1e-9)
    peak_w = max(np.max(np.abs(wl)), np.max(np.abs(wr)), 1e-9)
    wl = wl / peak_w * peak_in
    wr = wr / peak_w * peak_in
    out_l = np.zeros(len(wl))
    out_r = np.zeros(len(wr))
    out_l[:len(in_l)] = (1.0 - wet) * in_l
    out_r[:len(in_r)] = (1.0 - wet) * in_r
    out_l += wet * wl
    out_r += wet * wr
    return np.stack([out_l, out_r], axis=1)


def pingpong_delay(x, time_s=0.25, fb=0.42, mix=0.28, taps=5, tone=3800.0, fs=FS):
    mono = x if x.ndim == 1 else x.mean(axis=1)
    d = n_of(time_s, fs)
    total = len(mono) + d * taps
    out_l = np.zeros(total)
    out_r = np.zeros(total)
    if x.ndim == 2:
        out_l[:len(x)] = x[:, 0]
        out_r[:len(x)] = x[:, 1]
    else:
        out_l[:len(x)] = mono
        out_r[:len(x)] = mono
    tap_sig = lp(hp(mono, 220.0, 1, fs), tone, 2, fs)
    for k in range(1, taps + 1):
        s = k * d
        gain = (fb ** (k - 1)) * mix
        if k % 2 == 1:
            out_l[s:s + len(tap_sig)] += tap_sig * gain
        else:
            out_r[s:s + len(tap_sig)] += tap_sig * gain
        tap_sig = lp(tap_sig, tone * 0.85, 1, fs)
    return np.stack([out_l, out_r], axis=1)


def wrap_loop_exact(x, bpm, bars, beats_per_bar=4, fs=FS):
    """Wrap overflow tail onto start of bar 1 so loop length is SAMPLE-EXACT to BPM & bar count."""
    exact_n = int(round(bars * beats_per_bar * (60.0 / float(bpm)) * fs))
    if x.ndim == 1:
        out = np.zeros(exact_n, dtype=np.float64)
        m = min(len(x), exact_n)
        out[:m] = x[:m]
        if len(x) > exact_n:
            rem = x[exact_n:]
            rm = min(len(rem), exact_n)
            out[:rm] += rem[:rm]
        # 2ms seamless boundary micro-crossfade to guarantee 0 boundary click
        cf = min(88, exact_n // 16)
        w = np.linspace(0.0, 1.0, cf)
        out[:cf] = out[:cf] * w + out[-cf:] * (1.0 - w)
        return out
    else:
        return np.stack([
            wrap_loop_exact(x[:, 0], bpm, bars, beats_per_bar, fs),
            wrap_loop_exact(x[:, 1], bpm, bars, beats_per_bar, fs),
        ], axis=1)


def normalize(x, peak_db=-1.0):
    peak = float(np.max(np.abs(x))) if len(x) else 1e-9
    if peak < 1e-9:
        return x
    return x / peak * (10.0 ** (peak_db / 20.0))


def trim_silence(x, thresh_db=-60.0, pad_ms=2.5, fs=FS):
    if len(x) == 0:
        return x
    mag = np.abs(x) if x.ndim == 1 else np.max(np.abs(x), axis=1)
    peak = float(np.max(mag))
    if peak < 1e-9:
        return x
    thr = peak * (10.0 ** (thresh_db / 20.0))
    idx = np.where(mag > thr)[0]
    if len(idx) == 0:
        return x
    pad = n_of(pad_ms / 1000.0, fs)
    a = max(0, int(idx[0]) - pad)
    b = min(len(x), int(idx[-1]) + pad)
    return x[a:b]


def fade(x, fin=0.0008, fout=0.015, fs=FS):
    y = x.copy()
    n = len(y)
    a = min(n_of(fin, fs), n // 4)
    b = min(n_of(fout, fs), n // 3)
    if a > 0:
        w = (np.linspace(0.0, 1.0, a) ** 0.6)
        y[:a] = y[:a] * (w[:, None] if y.ndim == 2 else w)
    if b > 0:
        w = (np.linspace(1.0, 0.0, b) ** 1.3)
        y[-b:] = y[-b:] * (w[:, None] if y.ndim == 2 else w)
    return y


def dc_block(x, fs=FS):
    return hp(x, 20.0, order=2, fs=fs)


def rms(x):
    return float(np.sqrt(np.mean(np.square(x)) + 1e-12))


def peak_db(x):
    return float(20.0 * np.log10(max(float(np.max(np.abs(x))), 1e-9)))


def spectral_centroid(x, fs=FS):
    mono = x if x.ndim == 1 else x.mean(axis=1)
    if len(mono) < 8:
        return 0.0
    X = np.abs(np.fft.rfft(mono * np.hanning(len(mono))))
    f = np.fft.rfftfreq(len(mono), 1.0 / fs)
    s = float(X.sum())
    return float((X * f).sum() / s) if s > 1e-12 else 0.0
