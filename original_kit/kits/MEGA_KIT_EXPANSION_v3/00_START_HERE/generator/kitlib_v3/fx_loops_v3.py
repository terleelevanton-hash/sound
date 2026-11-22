"""Studio FX, textures, fills, sample-exact loops, and rich MIDI library for MEGA KIT v3."""
import numpy as np
from .dsp import (
    FS, n_of, tvec, sine, polyblep_saw, polyblep_square, polyblep_pulse,
    unison_supersaw, noise, pink_noise, exp_dec, adsr, lp, hp, bp, peaking,
    resonant_lp, resonant_bp, sat, stereo_reverb, pingpong_delay,
    wrap_loop_exact, fade, midi_to_freq,
)


# ================================================================== STUDIO FX & TEXTURES
def cinema_braaam(rng, root_midi=28, dur=3.2):
    """Hans-Zimmer / Trailer massive brass + sub stereo BRAAAM."""
    n = n_of(dur)
    t = tvec(dur)
    f0 = midi_to_freq(root_midi)
    bend = 1.0 - 0.045 * (t / dur) ** 1.4
    uni = unison_supersaw(f0 * bend, n, voices=7, detune_cents=28.0, stereo_spread=0.95, rng=rng)
    sub = sine(n, f0 * bend) * 0.9 + sine(n, f0 * 0.5 * bend) * 0.55
    uni[:, 0] += sub
    uni[:, 1] += sub
    cut = 280.0 + 2600.0 * np.exp(-np.abs(t - 0.35) / 0.9)
    flt = resonant_lp(sat(uni, drive=2.8, kind='tube'), cutoff=cut, q=1.8)
    env = adsr(n, a=0.06, d=0.4, s=0.72, r=0.9)
    st = stereo_reverb(flt * env[:, None], wet=0.38, decay=2.0, tone=4500.0, rng=rng)[:n]
    return fade(st, 0.005, 0.08)


def sub_drop(f_start=95.0, f_end=26.0, dur=2.2, rng=None):
    rng = rng or np.random.default_rng(801)
    n = n_of(dur)
    t = tvec(dur)
    f_curve = f_end + (f_start - f_end) * np.exp(-t / 0.52)
    boom = sine(n, f_curve) * exp_dec(n, dur * 0.62)
    thud = bp(noise(n, rng), 60.0, 420.0) * exp_dec(n, 0.045) * 0.35
    return fade(sat(boom + thud, drive=1.45, kind='tanh'), 0.001, 0.05)


def tape_stop_fx(rng, f_start=440.0, dur=0.95):
    n = n_of(dur)
    t = tvec(dur)
    speed = np.clip(1.0 - (t / dur) ** 1.85, 0.03, 1.0)
    uni = polyblep_saw(f_start * speed, n) + 0.5 * polyblep_saw(f_start * 1.5 * speed, n)
    flt = resonant_lp(uni, cutoff=4500.0 * speed + 80.0, q=2.0)
    return fade(sat(flt * np.sqrt(speed), drive=1.5, kind='tube'), 0.002, 0.03)


def dub_siren(rng, f_base=580.0, rate_hz=4.5, dur=2.4):
    n = n_of(dur)
    t = tvec(dur)
    lfo = 1.0 + 0.35 * polyblep_square(rate_hz, n)
    osc = polyblep_pulse(f_base * lfo, n, duty=0.42) * adsr(n, a=0.01, d=0.2, s=0.75, r=0.4)
    st = pingpong_delay(osc, time_s=0.28, fb=0.55, mix=0.48, taps=6, tone=3200.0)[:n]
    return fade(st, 0.002, 0.05)


def cyber_riser(rng, bars=2, bpm=140):
    dur = bars * 4.0 * (60.0 / bpm)
    n = n_of(dur)
    t = tvec(dur)
    prog = (t / dur) ** 1.6
    f_sweep = 110.0 * (2.0 ** (3.5 * prog))
    l = polyblep_saw(f_sweep * 0.995, n) + bp(noise(n, rng), 400.0, 14000.0) * 0.65
    r = polyblep_saw(f_sweep * 1.005, n, phase=0.35) + bp(noise(n, rng), 400.0, 14000.0) * 0.65
    chop = 0.55 + 0.45 * np.sin(2 * np.pi * (2.0 + 18.0 * prog) * t)
    st = np.stack([l, r], axis=1) * (prog * chop)[:, None]
    st = resonant_lp(st, cutoff=300.0 + 12000.0 * prog, q=2.4)
    return fade(st, 0.01, 0.008)


def vinyl_texture_loop(rng, bpm=90, bars=2, mode='vinyl'):
    dur = bars * 4.0 * (60.0 / bpm) + 0.2
    n = n_of(dur)
    if mode == 'vinyl':
        hiss_l = bp(pink_noise(n, rng), 350.0, 7500.0) * 0.16
        hiss_r = bp(pink_noise(n, rng), 350.0, 7500.0) * 0.16
        # Sparse realistic needle crackles & pops
        pops_l = (rng.random(n) < 0.0014).astype(float) * rng.uniform(0.2, 1.0, n)
        pops_r = (rng.random(n) < 0.0014).astype(float) * rng.uniform(0.2, 1.0, n)
        crackle_l = bp(pops_l, 1200.0, 9500.0)
        crackle_r = bp(pops_r, 1200.0, 9500.0)
        raw = np.stack([hiss_l + crackle_l, hiss_r + crackle_r], axis=1)
    elif mode == 'rain':
        rain_l = bp(pink_noise(n, rng), 500.0, 9500.0) * 0.35
        rain_r = bp(pink_noise(n, rng), 500.0, 9500.0) * 0.35
        drops_l = bp((rng.random(n) < 0.003).astype(float) * rng.uniform(0.1, 0.8, n), 1600.0, 7000.0)
        drops_r = bp((rng.random(n) < 0.003).astype(float) * rng.uniform(0.1, 0.8, n), 1600.0, 7000.0)
        raw = np.stack([rain_l + drops_l, rain_r + drops_r], axis=1)
    else:  # cassette_tape
        t = tvec(dur)
        hum = 0.06 * sine(n, 60.0) + 0.03 * sine(n, 180.0)
        hiss_l = bp(pink_noise(n, rng), 800.0, 11000.0) * (0.22 + 0.03 * np.sin(2 * np.pi * 0.8 * t)) + hum
        hiss_r = bp(pink_noise(n, rng), 800.0, 11000.0) * (0.22 + 0.03 * np.cos(2 * np.pi * 0.8 * t)) + hum
        raw = np.stack([hiss_l, hiss_r], axis=1)
    return wrap_loop_exact(raw, bpm=bpm, bars=bars)


def reverse_chord_swell(chord_wav):
    rev = chord_wav[::-1].copy()
    n = len(rev)
    ramp = (np.linspace(0.0, 1.0, n) ** 1.8)
    rev = rev * (ramp[:, None] if rev.ndim == 2 else ramp)
    return fade(rev, 0.01, 0.012)


# ================================================================== SAMPLE-EXACT SEQUENCER FOR LOOPS
def render_exact_loop(bpm, bars, voices, events, swing=0.0, stereo_out=True, rng=None):
    """
    Render pattern and wrap reverb/decay tail seamlessly onto bar 1 so sample count is
    100% exact to `bars * 4 * 60 / bpm * FS`.
    events: list of (step_16th_float, voice_name, gain, pan_0_to_1)
    """
    rng = rng or np.random.default_rng(900)
    step_s = (60.0 / float(bpm)) / 4.0
    total_s = bars * 16.0 * step_s
    buf_n = n_of(total_s + 1.5)
    out_l = np.zeros(buf_n, dtype=np.float64)
    out_r = np.zeros(buf_n, dtype=np.float64)

    for step, vname, vel, pan in events:
        t0 = float(step) * step_s
        if swing > 0 and (int(round(step)) % 2 == 1):
            t0 += step_s * swing * 0.45
        idx = max(0, int(round(t0 * FS)))
        smp = voices[vname]
        if smp.ndim == 1:
            gl = np.cos(pan * np.pi * 0.5) * vel
            gr = np.sin(pan * np.pi * 0.5) * vel
            m = min(len(smp), buf_n - idx)
            if m > 0:
                out_l[idx:idx + m] += smp[:m] * gl
                out_r[idx:idx + m] += smp[:m] * gr
        else:
            m = min(len(smp), buf_n - idx)
            if m > 0:
                out_l[idx:idx + m] += smp[:m, 0] * vel
                out_r[idx:idx + m] += smp[:m, 1] * vel

    glued = sat(np.stack([out_l, out_r], axis=1), drive=1.18, kind='tanh')
    exact = wrap_loop_exact(glued, bpm=bpm, bars=bars)
    return exact if stereo_out else exact.mean(axis=1)
