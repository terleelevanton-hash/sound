"""Multi-genre 808 & acoustic/electric/synth bass models for MEGA KIT v3."""
import numpy as np
from .dsp import (
    FS, n_of, tvec, sine, polyblep_saw, polyblep_square, polyblep_pulse,
    noise, exp_dec, adsr, lp, hp, bp, peaking, resonant_lp, resonant_bp,
    ks_string, sat, stereo_chorus, fade,
)


def spinz_808(freq, dur=1.45, punch=1.0, buzz=0.0, rng=None):
    """Clean, punchy modern Spinz / Zay / Opium 808 tuned to exact MIDI root."""
    rng = rng or np.random.default_rng(808)
    n = n_of(dur)
    t = tvec(dur)
    f_env = freq + (freq * 2.1 * punch) * np.exp(-t / 0.016)
    sub = sine(n, f_env)
    harm2 = sine(n, f_env * 2.0) * (0.22 + 0.25 * buzz)
    harm3 = polyblep_saw(f_env, n) * (0.06 + 0.32 * buzz) * np.exp(-t / 0.55)
    env = (1.0 - np.exp(-t / 0.0012)) * np.exp(-t / (dur * 0.78))
    click = bp(noise(n, rng), 700.0, 3800.0) * np.exp(-t / 0.004) * 0.08 * punch
    sig = (sub + harm2 + harm3) * env + click
    sig = sat(sig, drive=1.55 + 2.4 * buzz, kind='tube')
    sig = lp(sig, 2600.0 + 3800.0 * buzz, order=2)
    return fade(sig, 0.0005, 0.025)


def drill_glide_808(f_low, f_high, dur=1.55, up_then_down=False, rng=None):
    """UK / NY Drill dramatic octave-glide 808."""
    rng = rng or np.random.default_rng(142)
    n = n_of(dur)
    t = tvec(dur)
    f_curve = np.full(n, f_low, dtype=np.float64)
    # Kick transient into sub, then signature drill glide at ~0.28s
    f_curve += (f_low * 2.2) * np.exp(-t / 0.014)
    g1 = int(0.26 * FS)
    g2 = int(0.36 * FS)
    if up_then_down:
        g3 = int(0.72 * FS)
        g4 = int(0.82 * FS)
        f_curve[g1:g2] = np.geomspace(f_low, f_high, g2 - g1)
        f_curve[g2:g3] = f_high
        f_curve[g3:g4] = np.geomspace(f_high, f_low, g4 - g3)
    else:
        f_curve[g1:g2] = np.geomspace(f_low, f_high, g2 - g1)
        f_curve[g2:] = f_high
    raw = sine(n, f_curve) + 0.26 * polyblep_saw(f_curve, n)
    env = (1.0 - np.exp(-t / 0.0012)) * np.exp(-t / 1.25)
    sig = lp(sat(raw * env, drive=2.1, kind='tube'), 3600.0, order=2)
    return fade(sig, 0.0005, 0.03)


def upright_double_bass(freq, dur=1.35, rng=None):
    """Woody Jazz / Lo-Fi / Folk pizzicato Upright Acoustic Double Bass."""
    rng = rng or np.random.default_rng(55)
    n = n_of(dur)
    t = tvec(dur)
    string = ks_string(freq, dur, bright=0.28, damp=0.45, pick_pos=0.28, rng=rng)
    # Spruce/maple hollow body resonances
    body = peaking(string, 98.0, gain_db=6.5, q=1.8)
    body = peaking(body, 210.0, gain_db=4.5, q=2.1)
    body = peaking(body, 430.0, gain_db=-3.0, q=1.6)
    sub = sine(n, freq) * exp_dec(n, dur * 0.65) * 0.55
    finger_thump = bp(noise(n, rng), 90.0, 550.0) * np.exp(-t / 0.014) * 0.22
    sig = lp(body * 0.8 + sub + finger_thump, 2400.0, order=2)
    return fade(sat(sig, drive=1.18, kind='tube'), 0.001, 0.025)


def slap_bass(freq, dur=1.05, rng=None):
    """Funk / Disco / City-Pop / Anime thumb-slap roundwound electric bass."""
    rng = rng or np.random.default_rng(77)
    n = n_of(dur)
    t = tvec(dur)
    string = ks_string(freq, dur, bright=0.88, damp=0.18, pick_pos=0.11, rng=rng)
    # Metallic fret clank & roundwound zing
    zing = resonant_lp(polyblep_saw(freq, n), cutoff=420.0 + 4800.0 * np.exp(-t / 0.065), q=2.4)
    fret_clank = bp(noise(n, rng), 1800.0, 6800.0) * np.exp(-t / 0.008) * 0.42
    sub = sine(n, freq) * exp_dec(n, dur * 0.7) * 0.48
    mix = string * 0.72 + zing * exp_dec(n, dur * 0.5) * 0.45 + sub + fret_clank
    # Classic scooped-mid funk slap EQ (boost 80 Hz & 3.2 kHz, cut 450 Hz)
    mix = peaking(mix, 85.0, gain_db=4.5, q=1.2)
    mix = peaking(mix, 460.0, gain_db=-5.0, q=1.4)
    mix = peaking(mix, 3100.0, gain_db=5.5, q=1.6)
    return fade(sat(mix, drive=1.45, kind='tube'), 0.0006, 0.02)


def picked_rock_bass(freq, dur=1.15, rng=None):
    """Driving Punk / Indie / Post-Punk / Metal picked P-Bass with Ampeg grit."""
    rng = rng or np.random.default_rng(99)
    n = n_of(dur)
    t = tvec(dur)
    s1 = ks_string(freq, dur, bright=0.72, damp=0.24, pick_pos=0.13, rng=rng)
    growl = polyblep_pulse(freq, n, duty=0.38) * exp_dec(n, dur * 0.62) * 0.35
    pick = bp(noise(n, rng), 1200.0, 4800.0) * np.exp(-t / 0.005) * 0.36
    mix = sat(s1 * 0.8 + growl + pick, drive=2.05, kind='tube')
    mix = peaking(mix, 950.0, gain_db=4.5, q=1.5)
    return fade(lp(mix, 4600.0, order=2), 0.0006, 0.02)


def fretless_bass(freq, dur=1.35, rng=None):
    """Expressive Jazz / R&B fretless bass with warm 'mwah' bloom."""
    rng = rng or np.random.default_rng(64)
    n = n_of(dur)
    t = tvec(dur)
    f_vib = freq * (1.0 + 0.003 * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - 0.15) * 3.0, 0, 1))
    raw = 0.65 * polyblep_saw(f_vib, n) + 0.45 * sine(n, f_vib)
    # Slow-blooming bandpass 'mwah'
    mwah_cut = 320.0 + 1450.0 * np.sin(np.pi * np.clip(t / (dur * 0.65), 0, 1)) ** 1.3
    flt = resonant_lp(raw, cutoff=mwah_cut, q=3.1)
    env = adsr(n, a=0.018, d=0.25, s=0.58, r=0.32)
    out = stereo_chorus(flt * env, depth_ms=4.5, rate_hz=0.55, mix=0.28)
    return fade(out.mean(axis=1), 0.001, 0.025)


def donk_organ_bass(freq, dur=0.68):
    """Legendary Korg M1 / 90s House / UK Garage percussive Organ Bass."""
    n = n_of(dur)
    t = tvec(dur)
    # Fundamental + 3rd harmonic (octave + fifth = 3*f) + 2nd harmonic
    f1 = sine(n, freq) * exp_dec(n, 0.44)
    f2 = sine(n, freq * 2.0) * exp_dec(n, 0.26) * 0.52
    f3 = sine(n, freq * 3.0) * exp_dec(n, 0.15) * 0.68
    click = sine(n, freq * 6.0) * exp_dec(n, 0.014) * 0.24
    env = (1.0 - np.exp(-t / 0.0012)) * np.clip((dur - t) / 0.05, 0.0, 1.0)
    sig = sat((f1 + f2 + f3 + click) * env, drive=1.35, kind='tanh')
    return fade(sig, 0.0005, 0.018)


def hardbass_donk(freq, dur=0.45):
    """Authentic Eastern European Rave / Hardbass FM hollow 'DONK' bass."""
    n = n_of(dur)
    t = tvec(dur)
    mod_idx = 5.4 * np.exp(-t / 0.058) + 0.25
    mod = np.sin(2.0 * np.pi * (freq * 2.0) * t)
    car = np.sin(2.0 * np.pi * freq * t + mod_idx * mod)
    sub = sine(n, freq) * 0.55
    env = (1.0 - np.exp(-t / 0.0008)) * np.exp(-t / 0.21)
    sig = sat((car + sub) * env, drive=1.8, kind='tanh')
    return fade(peaking(sig, freq * 2.0, gain_db=4.0, q=2.0), 0.0004, 0.015)


def moog_fat_bass(freq, dur=1.05):
    """3-Oscillator Model-D style fat analog ladder bass."""
    n = n_of(dur)
    t = tvec(dur)
    o1 = polyblep_saw(freq * 0.997, n)
    o2 = polyblep_saw(freq * 1.003, n, phase=0.31)
    o3 = polyblep_pulse(freq * 0.5, n, duty=0.48, phase=0.14) * 0.75
    cutoff = freq * 1.6 + 2600.0 * np.exp(-t / 0.14)
    flt = resonant_lp((o1 + o2 + o3) / 2.4, cutoff=cutoff, q=2.8)
    env = adsr(n, a=0.003, d=0.22, s=0.62, r=0.22)
    return fade(sat(flt * env, drive=1.55, kind='tube'), 0.0006, 0.02)


def neuro_bass(freq, dur=1.35, rng=None):
    """DnB / Dubstep Neurofunk morphing Reese tearout bass."""
    rng = rng or np.random.default_rng(174)
    n = n_of(dur)
    t = tvec(dur)
    saws = (
        polyblep_saw(freq * 0.991, n)
        + polyblep_saw(freq, n, phase=0.27)
        + polyblep_saw(freq * 1.009, n, phase=0.63)
    ) / 2.2
    mid_in = hp(sat(saws, drive=3.2, kind='fold'), 130.0, order=2)
    sweep1 = 380.0 + 1900.0 * (0.5 + 0.5 * np.sin(2 * np.pi * 1.6 * t - 0.6))
    sweep2 = 1200.0 + 2400.0 * (0.5 + 0.5 * np.cos(2 * np.pi * 2.3 * t))
    mids = resonant_bp(mid_in, sweep1, q=3.2) * 0.8 + resonant_bp(mid_in, sweep2, q=2.6) * 0.6
    clean_sub = sine(n, freq) * 0.78
    env = adsr(n, a=0.008, d=0.15, s=0.82, r=0.22)
    return fade(sat((clean_sub + mids) * env, drive=1.6, kind='tanh'), 0.001, 0.025)
