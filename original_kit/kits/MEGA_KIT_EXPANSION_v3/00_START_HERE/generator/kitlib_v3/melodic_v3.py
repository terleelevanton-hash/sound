"""Studio multi-octave melodic instruments, stereo pads & strummed chords for MEGA KIT v3."""
import numpy as np
from .dsp import (
    FS, n_of, tvec, sine, tri_osc, polyblep_saw, polyblep_square, polyblep_pulse,
    unison_supersaw, noise, pink_noise, exp_dec, adsr, lp, hp, bp, peaking,
    resonant_lp, resonant_bp, formant_bank, ks_string, sat, bitcrush,
    stereo_chorus, stereo_reverb, pingpong_delay, fade, midi_to_freq,
)


# ================================================================== KEYS
def concert_grand(freq, dur=2.2, rng=None):
    rng = rng or np.random.default_rng(101)
    n = n_of(dur)
    t = tvec(dur)
    B = 0.00028 * (1.0 + (freq / 440.0) * 0.25)
    sig = np.zeros(n)
    max_h = min(26, int(FS * 0.44 / max(freq, 25.0)))
    for k in range(1, max_h + 1):
        fk = freq * k * np.sqrt(1.0 + B * k * k)
        amp = (1.0 / (k ** 1.22)) * (1.0 if k == 1 else 0.88)
        dec = max(0.14, (dur * 1.15) / (1.0 + 0.42 * (k - 1)))
        s = (
            np.sin(2 * np.pi * fk * t)
            + 0.72 * np.sin(2 * np.pi * fk * 1.0005 * t + 0.4)
            + 0.45 * np.sin(2 * np.pi * fk * 0.9995 * t + 1.1)
        )
        sig += amp * s * np.exp(-t / dec)
    hammer = bp(noise(n, rng), 600.0, 5800.0) * np.exp(-t / 0.0055) * 0.22
    thump = sine(n, min(120.0, freq * 0.5)) * np.exp(-t / 0.045) * 0.16
    mono = lp((sig / 2.2 + hammer + thump) * (1.0 - np.exp(-t / 0.0014)), 11500.0)
    st = stereo_reverb(mono, wet=0.16, decay=1.1, tone=6800.0, predelay=0.010, rng=rng)[:n]
    return fade(st, 0.0006, 0.03)


def felt_upright(freq, dur=2.3, rng=None):
    rng = rng or np.random.default_rng(102)
    n = n_of(dur)
    t = tvec(dur)
    # Subtle tape wow
    f_wow = freq * (1.0 + 0.0012 * np.sin(2 * np.pi * 1.3 * t))
    sig = np.zeros(n)
    max_h = min(14, int(FS * 0.42 / max(freq, 25.0)))
    for k in range(1, max_h + 1):
        amp = 1.0 / (k ** 1.75)
        dec = max(0.18, (dur * 1.1) / (1.0 + 0.55 * (k - 1)))
        sig += amp * sine(n, f_wow * k * (1.0 + 0.0003 * (k % 3))) * np.exp(-t / dec)
    felt = bp(pink_noise(n, rng), 250.0, 1800.0) * np.exp(-t / 0.012) * 0.18
    mono = lp((sig + felt) * (1.0 - np.exp(-t / 0.004)), 3400.0)
    st = stereo_reverb(mono, wet=0.22, decay=1.35, tone=3200.0, predelay=0.012, rng=rng)[:n]
    return fade(st, 0.001, 0.035)


def wurli_ep(freq, dur=2.0, rng=None):
    """Wurlitzer 200A reed electric piano with warm bark & tremolo."""
    n = n_of(dur)
    t = tvec(dur)
    mod = np.sin(2 * np.pi * freq * t) * (1.85 * np.exp(-t / 0.14) + 0.25)
    reed = np.sin(2 * np.pi * freq * t + mod) + 0.36 * np.sin(2 * np.pi * freq * 3.0 * t + 0.5 * mod)
    env = (1.0 - np.exp(-t / 0.0018)) * (0.65 * np.exp(-t / (dur * 0.72)) + 0.35 * np.exp(-t / 0.22))
    trem = 1.0 - 0.18 * (0.5 + 0.5 * np.sin(2 * np.pi * 5.6 * t))
    sig = sat(reed * env * trem, drive=1.45, kind='tube')
    return fade(lp(sig, 5800.0), 0.0006, 0.025)


def clavinet(freq, dur=1.25, rng=None):
    """Hohner Clavinet D6 funky crisp keyboard."""
    rng = rng or np.random.default_rng(106)
    s1 = ks_string(freq, dur, bright=0.92, damp=0.18, pick_pos=0.09, rng=rng)
    s2 = ks_string(freq * 1.001, dur, bright=0.85, damp=0.22, pick_pos=0.24, rng=rng)
    raw = hp(s1 - 0.55 * s2, max(110.0, freq * 0.65), order=2)
    raw = peaking(raw, 1850.0, gain_db=5.5, q=1.6)
    return fade(sat(raw, drive=1.55, kind='tube'), 0.0005, 0.02)


def pipe_organ(freq, dur=2.4, rng=None):
    """Stereo Cathedral / Gothic / Trap Pipe Organ (16', 8', 4', Nazard, 2', Mixture)."""
    rng = rng or np.random.default_rng(109)
    n = n_of(dur)
    t = tvec(dur)
    stops = [(0.5, 0.55), (1.0, 1.0), (1.498, 0.28), (2.0, 0.68), (3.0, 0.34), (4.0, 0.42), (6.0, 0.18), (8.0, 0.14)]
    sig = np.zeros(n)
    for ratio, gain in stops:
        f = freq * ratio
        if f < FS * 0.44:
            sig += gain * (0.75 * sine(n, f, phase=float(rng.uniform(0, 6.28))) + 0.25 * polyblep_saw(f, n))
    chiff = bp(noise(n, rng), 1200.0, 5200.0) * np.exp(-t / 0.028) * 0.12
    env = adsr(n, a=0.035, d=0.1, s=0.92, r=0.28)
    mono = lp((sig / 2.6 + chiff) * env, 9500.0)
    st = stereo_reverb(mono, wet=0.34, decay=2.0, tone=6200.0, predelay=0.022, rng=rng)[:n]
    return fade(st, 0.002, 0.04)


def mellotron_flute(freq, dur=2.2, rng=None):
    rng = rng or np.random.default_rng(112)
    n = n_of(dur)
    t = tvec(dur)
    wow = 1.0 + 0.0028 * np.sin(2 * np.pi * 1.9 * t) + 0.0014 * np.sin(2 * np.pi * 6.3 * t)
    f = freq * wow
    tone = sine(n, f) + 0.34 * sine(n, f * 2.0) + 0.14 * sine(n, f * 3.0)
    breath = bp(pink_noise(n, rng), 900.0, 4200.0) * 0.22
    env = adsr(n, a=0.065, d=0.15, s=0.82, r=0.25)
    sig = bp((tone + breath) * env, 240.0, 3900.0, order=2)
    return fade(sat(sig, drive=1.25, kind='tube'), 0.003, 0.03)


def mellotron_strings(freq, dur=2.4, rng=None):
    rng = rng or np.random.default_rng(113)
    n = n_of(dur)
    t = tvec(dur)
    wow = 1.0 + 0.0025 * np.sin(2 * np.pi * 1.4 * t) + 0.0018 * np.sin(2 * np.pi * 5.4 * t)
    s1 = polyblep_saw(freq * wow * 0.997, n)
    s2 = polyblep_saw(freq * wow * 1.004, n, phase=0.37)
    hiss = bp(pink_noise(n, rng), 700.0, 3800.0) * 0.08
    env = adsr(n, a=0.14, d=0.2, s=0.84, r=0.32)
    sig = bp(((s1 + s2) * 0.5 + hiss) * env, 220.0, 3400.0, order=2)
    return fade(sat(sig, drive=1.35, kind='tube'), 0.004, 0.035)


# ================================================================== WINDS & BRASS
def saxophone(freq, dur=1.85, alto=False, rng=None):
    """Expressive Jazz / R&B / Smooth House Saxophone (conical reed + vocal formants)."""
    rng = rng or np.random.default_rng(201)
    n = n_of(dur)
    t = tvec(dur)
    vib_env = np.clip((t - 0.22) / 0.25, 0.0, 1.0)
    f_curve = freq * (1.0 - 0.018 * np.exp(-t / 0.035) + 0.0065 * vib_env * np.sin(2 * np.pi * 5.4 * t))
    reed_drive = 0.72 * polyblep_saw(f_curve, n) + 0.35 * polyblep_pulse(f_curve, n, duty=0.34)
    reed = sat(reed_drive, drive=1.85, kind='tube', asym=0.22)
    if alto:
        formants = formant_bank(reed, [520, 1380, 2650, 3900], [3.2, 4.0, 4.5, 5.0], [1.0, 0.85, 0.55, 0.28])
    else:
        formants = formant_bank(reed, [410, 1080, 2250, 3300], [3.0, 3.8, 4.2, 4.8], [1.1, 0.82, 0.48, 0.22])
    body = 0.55 * lp(reed, freq * 4.5) + 0.75 * formants
    breath = bp(noise(n, rng), 1100.0, 5800.0) * (0.14 * np.exp(-t / 0.04) + 0.045)
    env = adsr(n, a=0.032, d=0.14, s=0.82, r=0.22)
    return fade(lp((body + breath) * env, 7800.0), 0.002, 0.028)


def brass_horn(freq, dur=1.75, kind='trombone', rng=None):
    rng = rng or np.random.default_rng(210)
    n = n_of(dur)
    t = tvec(dur)
    f_lip = freq * (1.0 - 0.015 * np.exp(-t / 0.025) + 0.003 * np.sin(2 * np.pi * 4.8 * t))
    raw = 0.75 * polyblep_saw(f_lip, n) + 0.25 * polyblep_pulse(f_lip, n, duty=0.42)
    if kind == 'french_horn':
        cut = freq * 1.8 + freq * 3.8 * adsr(n, a=0.09, d=0.25, s=0.58, r=0.28)
        sig = resonant_lp(raw, cutoff=np.clip(cut, 160.0, 3800.0), q=1.5)
        env = adsr(n, a=0.075, d=0.18, s=0.82, r=0.28)
    elif kind == 'tuba':
        cut = freq * 2.0 + freq * 4.2 * adsr(n, a=0.04, d=0.18, s=0.60, r=0.22)
        sig = resonant_lp(raw + 0.4 * sine(n, f_lip), cutoff=np.clip(cut, 110.0, 2200.0), q=1.4)
        env = adsr(n, a=0.038, d=0.15, s=0.78, r=0.22)
    else:  # trombone
        cut = freq * 2.2 + freq * 6.5 * adsr(n, a=0.035, d=0.16, s=0.65, r=0.22)
        sig = resonant_lp(raw, cutoff=np.clip(cut, 180.0, 6200.0), q=1.7)
        sig = peaking(sig, 1150.0, gain_db=3.5, q=1.5)
        env = adsr(n, a=0.028, d=0.14, s=0.80, r=0.22)
    lip_buzz = bp(noise(n, rng), 600.0, 3200.0) * np.exp(-t / 0.022) * 0.09
    return fade(sat((sig + lip_buzz) * env, drive=1.35, kind='tube'), 0.002, 0.025)


def funk_brass_section(freq, dur=1.35, rng=None):
    """Stereo tight Funk / Soul / Latin 3-piece horn section (Trumpet + Alto Sax + Trombone)."""
    rng = rng or np.random.default_rng(215)
    trp = brass_horn(freq * 1.002, dur, kind='trombone', rng=rng)
    trp = peaking(trp, 2200.0, gain_db=4.5, q=1.5)
    sax = saxophone(freq * 0.998, dur, alto=True, rng=rng)
    tmb = brass_horn(freq * 0.5, dur, kind='trombone', rng=rng)
    l = 0.65 * trp + 0.35 * sax + 0.45 * tmb
    r = 0.35 * trp + 0.68 * sax + 0.45 * tmb
    st = stereo_reverb(np.stack([l, r], axis=1), wet=0.18, decay=0.9, tone=6500.0, rng=rng)[:len(l)]
    return fade(st, 0.001, 0.025)


def double_reed_wind(freq, dur=1.8, kind='oboe', rng=None):
    rng = rng or np.random.default_rng(220)
    n = n_of(dur)
    t = tvec(dur)
    vib = 1.0 + 0.0055 * np.clip((t - 0.18) * 3.5, 0, 1) * np.sin(2 * np.pi * 5.3 * t)
    if kind == 'duduk':
        # Soulful Armenian duduk (cylindrical reed, warm hollow vocal formants)
        raw = 0.72 * polyblep_square(freq * vib, n) + 0.28 * polyblep_saw(freq * vib, n)
        flt = formant_bank(raw, [480, 1120, 2150], [3.6, 4.2, 4.0], [1.2, 0.75, 0.25])
        breath = bp(pink_noise(n, rng), 600.0, 2600.0) * 0.08
        env = adsr(n, a=0.085, d=0.2, s=0.85, r=0.3)
        return fade(lp((flt + breath) * env, 3600.0), 0.004, 0.03)
    elif kind == 'bassoon':
        raw = polyblep_pulse(freq * vib, n, duty=0.22)
        flt = formant_bank(raw, [440, 1180, 2200], [4.0, 4.5, 4.0], [1.1, 0.85, 0.35])
        env = adsr(n, a=0.035, d=0.15, s=0.80, r=0.22)
        return fade(lp((flt + 0.35 * raw) * env, 4500.0), 0.002, 0.025)
    else:  # oboe
        raw = polyblep_pulse(freq * vib, n, duty=0.18)
        flt = formant_bank(raw, [1050, 2450, 3600], [4.5, 5.0, 5.0], [1.0, 0.78, 0.42])
        env = adsr(n, a=0.028, d=0.12, s=0.82, r=0.22)
        return fade(lp((flt + 0.25 * raw) * env, 7200.0), 0.002, 0.025)


# ================================================================== GUITARS & WORLD
def nylon_guitar(freq, dur=1.85, rng=None):
    rng = rng or np.random.default_rng(301)
    s = ks_string(freq, dur, bright=0.44, damp=0.28, pick_pos=0.22, rng=rng)
    # Classical guitar cedar top & sound-hole air resonance (~102 Hz, ~208 Hz, ~415 Hz)
    body = peaking(s, 104.0, gain_db=5.0, q=2.0)
    body = peaking(body, 212.0, gain_db=4.0, q=2.2)
    body = peaking(body, 2800.0, gain_db=2.0, q=1.5)
    return fade(lp(body, 6800.0), 0.0006, 0.025)


def steel_acoustic(freq, dur=1.95, rng=None):
    rng = rng or np.random.default_rng(302)
    s1 = ks_string(freq, dur, bright=0.86, damp=0.16, pick_pos=0.14, rng=rng)
    s2 = ks_string(freq * 1.0008, dur, bright=0.80, damp=0.18, pick_pos=0.16, rng=rng)
    body = peaking(0.65 * s1 + 0.35 * s2, 98.0, gain_db=4.0, q=1.8)
    body = peaking(body, 4200.0, gain_db=4.5, q=1.6)
    return fade(body, 0.0005, 0.025)


def funk_wah_guitar(freq, dur=1.1, rng=None):
    rng = rng or np.random.default_rng(303)
    n = n_of(dur)
    t = tvec(dur)
    s = ks_string(freq, dur, bright=0.92, damp=0.22, pick_pos=0.12, rng=rng)
    wah_f = 480.0 + 2400.0 * np.exp(-t / 0.11)
    wah = resonant_bp(s, wah_f, q=3.8) + 0.35 * s
    return fade(sat(wah, drive=1.45, kind='tube'), 0.0005, 0.02)


def jazz_guitar(freq, dur=1.65, rng=None):
    rng = rng or np.random.default_rng(304)
    s = ks_string(freq, dur, bright=0.24, damp=0.36, pick_pos=0.28, rng=rng)
    warm = lp(peaking(s, 260.0, gain_db=4.5, q=1.5), 2900.0)
    return fade(sat(warm, drive=1.2, kind='tube'), 0.0008, 0.025)


def metal_chug_8str(freq, dur=1.25, rng=None):
    """Tight modern 8-string Djent / Metal high-gain dual-rectifier guitar."""
    rng = rng or np.random.default_rng(305)
    root = ks_string(freq, dur, bright=0.90, damp=0.20, pick_pos=0.11, rng=rng)
    fifth = ks_string(freq * 1.4983, dur, bright=0.88, damp=0.22, pick_pos=0.12, rng=rng)
    pre = hp(root + 0.72 * fifth, 135.0, order=2)  # TubeScreamer tight low-cut before amp!
    pre = peaking(pre, 1450.0, gain_db=6.0, q=1.4)
    amp = sat(pre, drive=7.5, kind='tube', asym=0.15)
    # 4x12 Celestion Vintage-30 cab simulation
    cab = lp(hp(amp, 75.0, order=2), 4600.0, order=3)
    cab = peaking(cab, 2400.0, gain_db=4.5, q=1.8)
    cab = peaking(cab, 3900.0, gain_db=-5.0, q=3.0)
    return fade(cab, 0.0005, 0.02)


def shimmer_guitar(freq, dur=2.5, rng=None):
    """Stereo Shoegaze / Post-Rock / Midwest Emo chorus + octave shimmer clean guitar."""
    rng = rng or np.random.default_rng(306)
    dry = steel_acoustic(freq, dur, rng=rng)
    oct_hi = ks_string(freq * 2.0, dur, bright=0.65, damp=0.25, pick_pos=0.2, rng=rng) * 0.28
    ch = stereo_chorus(dry + oct_hi, depth_ms=7.0, rate_hz=0.55, mix=0.45)
    rev = stereo_reverb(ch, wet=0.38, decay=1.8, tone=6800.0, rng=rng)[:len(dry)]
    return fade(rev, 0.001, 0.04)


def world_plucked(freq, dur=1.45, kind='balalaika', rng=None):
    rng = rng or np.random.default_rng(320)
    if kind == 'balalaika':
        s1 = ks_string(freq, dur, bright=0.90, damp=0.26, pick_pos=0.13, rng=rng)
        s2 = ks_string(freq * 1.0022, dur, bright=0.88, damp=0.28, pick_pos=0.15, rng=rng)
        # Triangular wooden body formant
        out = peaking(0.6 * s1 + 0.5 * s2, 580.0, gain_db=5.5, q=2.2)
        return fade(peaking(out, 2900.0, gain_db=4.0, q=1.8), 0.0005, 0.02)
    elif kind == 'gusli':
        s1 = ks_string(freq, dur, bright=0.85, damp=0.12, pick_pos=0.17, rng=rng)
        s2 = ks_string(freq * 2.0, dur, bright=0.75, damp=0.18, pick_pos=0.2, rng=rng) * 0.25
        return fade(peaking(s1 + s2, 1600.0, gain_db=3.5, q=1.5), 0.0005, 0.025)
    elif kind == 'ukulele':
        s = ks_string(freq, dur * 0.9, bright=0.48, damp=0.38, pick_pos=0.26, rng=rng)
        return fade(peaking(lp(s, 5200.0), 390.0, gain_db=5.5, q=2.0), 0.0005, 0.02)
    else:  # mandolin (paired unison steel strings)
        s1 = ks_string(freq, dur, bright=0.94, damp=0.20, pick_pos=0.10, rng=rng)
        s2 = ks_string(freq * 1.0018, dur, bright=0.92, damp=0.21, pick_pos=0.11, rng=rng)
        return fade(peaking(0.55 * s1 + 0.55 * s2, 3400.0, gain_db=4.5, q=1.8), 0.0005, 0.02)


def bayan(freq, dur=1.85):
    """Russian Bayan / Garmon button accordion with warm dual-reed musette."""
    n = n_of(dur)
    t = tvec(dur)
    r1 = 0.65 * polyblep_pulse(freq * 0.9982, n, duty=0.32) + 0.35 * polyblep_saw(freq * 0.9982, n)
    r2 = 0.65 * polyblep_pulse(freq * 1.0018, n, duty=0.32, phase=0.25) + 0.35 * polyblep_saw(freq * 1.0018, n)
    oct_dn = polyblep_saw(freq * 0.5, n) * 0.28
    flt = formant_bank((r1 + r2) * 0.5 + oct_dn, [620, 1480, 2850], [2.4, 3.0, 3.5], [1.0, 0.85, 0.45])
    env = adsr(n, a=0.032, d=0.12, s=0.86, r=0.22)
    return fade(lp((flt + 0.3 * (r1 + r2)) * env, 6200.0), 0.002, 0.025)


def erhu(freq, dur=1.9, rng=None):
    """Expressive bowed 2-string Erhu with subtle portamento slide & vibrato."""
    rng = rng or np.random.default_rng(330)
    n = n_of(dur)
    t = tvec(dur)
    slide = 1.0 - 0.035 * np.exp(-t / 0.065)
    vib = 1.0 + 0.0075 * np.clip((t - 0.2) * 3.0, 0, 1) * np.sin(2 * np.pi * 5.6 * t)
    bow = polyblep_saw(freq * slide * vib, n)
    body = formant_bank(bow, [780, 1520, 2950, 4200], [4.5, 5.2, 4.8, 4.0], [1.1, 0.95, 0.6, 0.3])
    rosin = bp(noise(n, rng), 1800.0, 6500.0) * 0.055
    env = adsr(n, a=0.08, d=0.18, s=0.82, r=0.28)
    return fade(lp((body + rosin) * env, 7500.0), 0.003, 0.03)


def kalimba_stereo(freq, dur=1.55, rng=None):
    rng = rng or np.random.default_rng(340)
    n = n_of(dur)
    t = tvec(dur)
    tine = (
        sine(n, freq) * exp_dec(n, dur * 0.82)
        + 0.28 * sine(n, freq * 2.92) * exp_dec(n, 0.09)
        + 0.14 * sine(n, freq * 5.85) * exp_dec(n, 0.035)
    )
    thumb = bp(noise(n, rng), 900.0, 4800.0) * exp_dec(n, 0.006) * 0.22
    mono = (tine + thumb) * (1.0 - np.exp(-t / 0.001))
    st = stereo_reverb(mono, wet=0.24, decay=0.95, tone=5800.0, rng=rng)[:n]
    return fade(st, 0.0005, 0.025)


# ================================================================== MODERN SYNTHS & LEADS
def rage_lead(freq, dur=1.45, rng=None):
    """Stereo Opium / Rage (Yeat / Carti / Ken Carson) aggressive hyper-saw lead."""
    rng = rng or np.random.default_rng(401)
    n = n_of(dur)
    t = tvec(dur)
    uni = unison_supersaw(freq, n, voices=7, detune_cents=32.0, stereo_spread=0.92, rng=rng)
    sub_sq = polyblep_square(freq * 0.5, n) * 0.22
    uni[:, 0] += sub_sq
    uni[:, 1] += sub_sq
    env = adsr(n, a=0.004, d=0.18, s=0.82, r=0.20)
    driven = sat(uni * env[:, None], drive=2.35, kind='tube')
    return fade(peaking(driven, 3200.0, gain_db=3.5, q=1.4), 0.0006, 0.022)


def pluggnb_lead(freq, dur=1.55):
    """Smooth Purity-style Pluggnb / R&B sine-triangle glide lead."""
    n = n_of(dur)
    t = tvec(dur)
    f_glide = freq * (1.0 - 0.055 * np.exp(-t / 0.048) + 0.0035 * np.sin(2 * np.pi * 5.2 * t))
    sig = 0.72 * sine(n, f_glide) + 0.28 * tri_osc(f_glide, n) + 0.14 * sine(n, f_glide * 2.0)
    env = adsr(n, a=0.012, d=0.15, s=0.85, r=0.24)
    return fade(lp(sig * env, 4200.0), 0.001, 0.025)


def pluggnb_bell(freq, dur=1.65, rng=None):
    """Dreamy glassy FM Pluggnb / Cloud-Rap bell."""
    rng = rng or np.random.default_rng(403)
    n = n_of(dur)
    t = tvec(dur)
    mod = np.sin(2 * np.pi * freq * 3.0 * t) * (2.6 * np.exp(-t / 0.22) + 0.2)
    car = np.sin(2 * np.pi * freq * t + mod) + 0.35 * np.sin(2 * np.pi * freq * 2.0 * t) * np.exp(-t / 0.45)
    env = exp_dec(n, dur * 0.62) * (1.0 - np.exp(-t / 0.0015))
    st = stereo_reverb(car * env, wet=0.28, decay=1.25, tone=7500.0, rng=rng)[:n]
    return fade(st, 0.0006, 0.03)


def retro_poly80(freq, dur=1.75):
    """Juno-106 / Synthwave stereo chorus warm analog polysynth."""
    n = n_of(dur)
    t = tvec(dur)
    pwm_duty = 0.5 + 0.28 * np.sin(2 * np.pi * 1.4 * t)
    # Approximate smooth PWM via two slightly detuned saws + pulse
    osc = 0.55 * polyblep_saw(freq, n) + 0.45 * polyblep_pulse(freq * 1.002, n, duty=0.38) + 0.25 * polyblep_square(freq * 0.5, n)
    cut = freq * 1.5 + 3600.0 * np.exp(-t / 0.38)
    flt = resonant_lp(osc, cutoff=cut, q=1.9)
    env = adsr(n, a=0.014, d=0.28, s=0.68, r=0.28)
    st = stereo_chorus(flt * env, depth_ms=7.5, rate_hz=0.72, mix=0.48)
    return fade(st, 0.001, 0.03)


def gfunk_whistle_lead(freq, dur=1.6):
    """West Coast G-Funk high portamento sine whine."""
    n = n_of(dur)
    t = tvec(dur)
    f_whine = freq * (1.0 - 0.11 * np.exp(-t / 0.075) + 0.006 * np.clip((t - 0.15) * 4.0, 0, 1) * np.sin(2 * np.pi * 6.0 * t))
    sig = sine(n, f_whine) + 0.18 * polyblep_saw(f_whine, n)
    sig = resonant_lp(sig, cutoff=min(freq * 2.6, 8500.0), q=2.1)
    env = adsr(n, a=0.018, d=0.1, s=0.88, r=0.22)
    return fade(sat(sig * env, drive=1.25, kind='tube'), 0.001, 0.025)


def hyperpop_lead(freq, dur=1.25, rng=None):
    rng = rng or np.random.default_rng(406)
    n = n_of(dur)
    t = tvec(dur)
    f_pop = freq * (1.0 + 0.5 * np.exp(-t / 0.018))
    l = polyblep_saw(f_pop * 0.994, n) + 0.5 * polyblep_pulse(f_pop * 2.0, n, duty=0.25)
    r = polyblep_saw(f_pop * 1.006, n, phase=0.33) + 0.5 * polyblep_pulse(f_pop * 2.003, n, duty=0.25)
    st = np.stack([l, r], axis=1)
    st = bitcrush(sat(st, drive=2.2, kind='tanh'), bits=11, downsample=2)
    env = adsr(n, a=0.002, d=0.15, s=0.75, r=0.18)
    return fade(st * env[:, None], 0.0005, 0.02)


def rave_hoover(freq, dur=1.55, rng=None):
    """Classic 90s Alpha-Juno / Prodigy / Techno pitch-swept Rave Hoover."""
    rng = rng or np.random.default_rng(407)
    n = n_of(dur)
    t = tvec(dur)
    bend = 1.0 - 0.25 * np.exp(-t / 0.14) + 0.08 * np.sin(2 * np.pi * 1.2 * t)
    l = np.zeros(n)
    r = np.zeros(n)
    for k, det in enumerate([-28, -12, 0, 12, 28]):
        fv = freq * bend * (2.0 ** (det / 1200.0))
        v = polyblep_saw(fv, n, phase=k * 0.19) + 0.7 * polyblep_square(fv * 0.5, n, phase=k * 0.31)
        if k % 2 == 0:
            l += v
        else:
            r += v
        if k == 2:
            l += v * 0.5
            r += v * 0.5
    st = sat(np.stack([l, r], axis=1) / 3.2, drive=2.1, kind='tanh')
    env = adsr(n, a=0.008, d=0.15, s=0.85, r=0.22)
    return fade(st * env[:, None], 0.001, 0.025)


def dx_crystal_bell(freq, dur=2.0, rng=None):
    rng = rng or np.random.default_rng(408)
    n = n_of(dur)
    t = tvec(dur)
    m1 = np.sin(2 * np.pi * freq * 14.0 * t) * 1.4 * np.exp(-t / 0.045)
    c1 = np.sin(2 * np.pi * freq * t + m1) * np.exp(-t / (dur * 0.75))
    m2 = np.sin(2 * np.pi * freq * 3.5 * t) * 1.8 * np.exp(-t / 0.28)
    c2 = np.sin(2 * np.pi * freq * 2.0 * t + m2) * np.exp(-t / (dur * 0.45)) * 0.45
    st = stereo_chorus(c1 + c2, depth_ms=5.0, rate_hz=0.8, mix=0.35)
    return fade(st, 0.0005, 0.03)


def psy_fm_lead(freq, dur=0.85):
    n = n_of(dur)
    t = tvec(dur)
    idx = 6.5 * np.exp(-t / 0.12) + 1.2 * (0.5 + 0.5 * np.sin(2 * np.pi * 8.0 * t))
    mod = polyblep_saw(freq * 1.5, n)
    car = np.sin(2 * np.pi * freq * t + idx * mod)
    flt = resonant_bp(car, center=600.0 + 3800.0 * np.exp(-t / 0.16), q=3.4)
    env = adsr(n, a=0.002, d=0.14, s=0.65, r=0.15)
    return fade(sat(flt * env, drive=2.0, kind='tanh'), 0.0005, 0.018)


def chiptune_lead(freq, dur=0.95, arp=False):
    n = n_of(dur)
    t = tvec(dur)
    if arp:
        # 50 Hz NES/C64 rapid minor-7th chord arpeggiator (0, +3, +7, +12 semitones)
        semis = np.array([0, 3, 7, 12])
        step_idx = (t * 48.0).astype(int) % len(semis)
        f_seq = freq * (2.0 ** (semis[step_idx] / 12.0))
        raw = polyblep_pulse(f_seq, n, duty=0.25)
    else:
        raw = polyblep_pulse(freq, n, duty=0.125)
    crushed = bitcrush(raw, bits=6, downsample=2)
    env = adsr(n, a=0.002, d=0.12, s=0.72, r=0.14)
    return fade(crushed * env, 0.0004, 0.015)


# ================================================================== LONG LUSH STEREO PADS & DRONES
def stereo_pad(freq, dur=3.5, kind='shimmer', rng=None):
    rng = rng or np.random.default_rng(501)
    n = n_of(dur)
    t = tvec(dur)
    env = adsr(n, a=0.65, d=0.5, s=0.82, r=0.85, curve=1.2)
    if kind == 'shimmer':
        base = unison_supersaw(freq, n, voices=7, detune_cents=18.0, stereo_spread=0.85, rng=rng)
        oct_up = unison_supersaw(freq * 2.0, n, voices=5, detune_cents=24.0, stereo_spread=0.95, rng=rng) * 0.35
        cut = 900.0 + 2800.0 * np.sin(np.pi * t / dur) ** 0.8
        st = resonant_lp(base + oct_up, cutoff=cut, q=1.2) * env[:, None]
        return fade(stereo_reverb(st, wet=0.45, decay=2.1, tone=7500.0, rng=rng)[:n], 0.01, 0.08)
    elif kind == 'cs80_dark':
        # Blade Runner / Vangelis warm brassy dark analog stereo pad
        drift = 1.0 + 0.003 * np.sin(2 * np.pi * 0.45 * t)
        s_l = polyblep_saw(freq * drift * 0.996, n) + 0.5 * polyblep_saw(freq * 0.5, n)
        s_r = polyblep_saw(freq * drift * 1.004, n, phase=0.4) + 0.5 * polyblep_saw(freq * 0.501, n, phase=0.2)
        st = np.stack([s_l, s_r], axis=1)
        cut = 320.0 + 1850.0 * np.sin(np.pi * (t / dur) ** 0.75) ** 1.4
        st = resonant_lp(st, cutoff=cut, q=2.1) * env[:, None]
        return fade(stereo_reverb(sat(st, drive=1.4, kind='tube'), wet=0.38, decay=2.0, tone=4200.0, rng=rng)[:n], 0.01, 0.08)
    elif kind == 'glass_ambient':
        m1 = np.sin(2 * np.pi * freq * 2.0 * t) * (1.2 + 0.8 * np.sin(2 * np.pi * 0.35 * t))
        l = np.sin(2 * np.pi * freq * 0.999 * t + m1) + 0.4 * np.sin(2 * np.pi * freq * 3.0 * t)
        r = np.sin(2 * np.pi * freq * 1.001 * t + m1 * 0.9) + 0.4 * np.sin(2 * np.pi * freq * 4.0 * t)
        st = np.stack([l, r], axis=1) * env[:, None]
        return fade(stereo_reverb(st, wet=0.42, decay=2.2, tone=8200.0, rng=rng)[:n], 0.01, 0.08)
    elif kind == 'tape_strings':
        wow = 1.0 + 0.003 * np.sin(2 * np.pi * 1.1 * t)
        uni = unison_supersaw(freq * wow, n, voices=5, detune_cents=15.0, stereo_spread=0.75, rng=rng)
        flt = bp(uni, 180.0, 3200.0, order=2) * env[:, None]
        return fade(stereo_reverb(sat(flt, drive=1.3, kind='tube'), wet=0.35, decay=1.8, tone=3600.0, rng=rng)[:n], 0.01, 0.08)
    else:  # drone_dark_cinema
        sub = sine(n, freq) * 0.85
        fifth = polyblep_saw(freq * 1.498, n) * 0.35
        tex_l = bp(pink_noise(n, rng), 120.0, 900.0) * 0.35
        tex_r = bp(pink_noise(n, rng), 140.0, 950.0) * 0.35
        l = resonant_lp(sub + fifth + tex_l, cutoff=240.0 + 450.0 * np.sin(np.pi * t / dur), q=2.2)
        r = resonant_lp(sub + fifth * 0.95 + tex_r, cutoff=260.0 + 480.0 * np.sin(np.pi * t / dur + 0.4), q=2.2)
        return fade(np.stack([l, r], axis=1) * env[:, None], 0.015, 0.08)


# ================================================================== CHORDS & GUITAR STRUMS
def acoustic_guitar_strum(root_midi, quality='minor', dur=2.2, rng=None):
    """6-string realistic strummed acoustic guitar chord with 12ms per-string pick stagger."""
    rng = rng or np.random.default_rng(600 + root_midi)
    n = n_of(dur)
    if quality == 'major':
        intervals = [0, 7, 12, 16, 19, 24]
    else:
        intervals = [0, 7, 12, 15, 19, 24]
    out_l = np.zeros(n)
    out_r = np.zeros(n)
    stagger = int(0.012 * FS)
    for i, iv in enumerate(intervals):
        start = i * stagger
        rem_dur = dur - (start / FS)
        if rem_dur <= 0.2:
            continue
        f = midi_to_freq(root_midi + iv)
        s = steel_acoustic(f, rem_dur, rng=rng)
        m = min(len(s), n - start)
        pan = 0.32 + 0.36 * (i / 5.0)
        out_l[start:start + m] += s[:m] * np.cos(pan * np.pi * 0.5) * (0.95 ** i)
        out_r[start:start + m] += s[:m] * np.sin(pan * np.pi * 0.5) * (0.95 ** i)
    st = stereo_reverb(np.stack([out_l, out_r], axis=1), wet=0.16, decay=0.95, tone=6500.0, rng=rng)[:n]
    return fade(st, 0.0008, 0.035)


def electric_power_chord(root_midi, dur=1.55, rng=None):
    """Double-tracked hard-panned L/R Rock / Punk / Metal distorted guitar power chord."""
    rng = rng or np.random.default_rng(650 + root_midi)
    f = midi_to_freq(root_midi)
    take_l = metal_chug_8str(f * 0.999, dur, rng=rng)
    take_r = metal_chug_8str(f * 1.001, dur, rng=rng)
    oct_mid = metal_chug_8str(f * 2.0, dur, rng=rng) * 0.35
    m = min(len(take_l), len(take_r), len(oct_mid))
    return fade(np.stack([take_l[:m] + oct_mid[:m], take_r[:m] + oct_mid[:m]], axis=1), 0.0006, 0.025)


def house_organ_stab(root_midi, dur=0.75, rng=None):
    """Classic 90s House / UKG minor7 organ+piano chord stab."""
    rng = rng or np.random.default_rng(700 + root_midi)
    n = n_of(dur)
    sig = np.zeros(n)
    for iv, g in [(0, 1.0), (3, 0.85), (7, 0.9), (10, 0.78), (14, 0.55)]:
        f = midi_to_freq(root_midi + iv)
        v = wurli_ep(f, dur, rng=rng)[:n]
        sig[:len(v)] += v * g
    st = stereo_reverb(sig, wet=0.22, decay=0.8, tone=6000.0, rng=rng)[:n]
    return fade(st, 0.0006, 0.02)


def dub_techno_chord(root_midi, dur=2.6, rng=None):
    """Basic Channel / Berlin Dub Techno filtered minor9 chord with stereo ping-pong tape delay."""
    rng = rng or np.random.default_rng(720 + root_midi)
    hit_n = n_of(0.32)
    t = tvec(0.32)
    raw = np.zeros(hit_n)
    for iv in [0, 3, 7, 10, 14]:
        f = midi_to_freq(root_midi + iv)
        raw += polyblep_saw(f * float(rng.uniform(0.997, 1.003)), hit_n)
    stab = resonant_lp(raw / 4.0, cutoff=280.0 + 2600.0 * np.exp(-t / 0.075), q=3.0) * exp_dec(hit_n, 0.14)
    delayed = pingpong_delay(stab, time_s=0.375, fb=0.58, mix=0.55, taps=6, tone=2400.0)
    rev = stereo_reverb(delayed, wet=0.38, decay=1.8, tone=3200.0, rng=rng)[:n_of(dur)]
    return fade(rev, 0.001, 0.05)


def neosoul_rhodes_chord(root_midi, dur=2.2, rng=None):
    """Lush Neo-Soul / R&B / Lo-Fi extended minor9 stereo electric piano chord."""
    rng = rng or np.random.default_rng(740 + root_midi)
    n = n_of(dur)
    sig = np.zeros(n)
    for i, iv in enumerate([0, 3, 7, 10, 14, 17]):
        f = midi_to_freq(root_midi + iv)
        v = wurli_ep(f, dur, rng=rng)[:n]
        offset = i * int(0.008 * FS)
        m = min(len(v), n - offset)
        sig[offset:offset + m] += v[:m] * (0.88 ** i)
    st = stereo_chorus(sig, depth_ms=5.5, rate_hz=0.55, mix=0.4)
    return fade(st, 0.001, 0.035)
