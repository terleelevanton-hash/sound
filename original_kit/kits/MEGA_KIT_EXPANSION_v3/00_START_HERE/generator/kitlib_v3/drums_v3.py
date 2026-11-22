"""Genre-authentic drum, cymbal, percussion & chromatic 808 cowbell models for MEGA KIT v3."""
import numpy as np
from .dsp import (
    FS, n_of, tvec, sine, polyblep_square, polyblep_pulse, polyblep_saw,
    noise, pink_noise, exp_dec, perc_env, lp, hp, bp, peaking,
    resonant_lp, resonant_bp, sat, bitcrush, stereo_reverb, fade, midi_to_freq,
)


def _cymbal_modes(n, base_f, ratios, rng):
    t = np.arange(n, dtype=np.float64) / FS
    sig = np.zeros(n, dtype=np.float64)
    for r in ratios:
        f = base_f * r * float(rng.uniform(0.994, 1.006))
        if f < FS * 0.46:
            ph = float(rng.uniform(0, 1.0))
            sig += polyblep_square(f, n, phase=ph) * (1.0 / np.sqrt(r))
    return sig / max(len(ratios) ** 0.5, 1.0)


def synth_kick(rng, f_start=150.0, f_end=48.0, pitch_tau=0.022, decay=0.32,
               click=0.28, drive=1.6, tone=6500.0, sub=0.35, punch=0.22, beater_f=2200.0):
    dur = max(0.22, decay * 2.4)
    n = n_of(dur)
    t = tvec(dur)
    f_env = f_end + (f_start - f_end) * np.exp(-t / pitch_tau) + punch * 45.0 * np.exp(-t / 0.007)
    body = sine(n, f_env) * exp_dec(n, decay)
    sub_layer = sine(n, f_end) * exp_dec(n, decay * 1.18) * sub
    clk = bp(noise(n, rng), 500.0, min(beater_f * 2.2, 12000.0)) * exp_dec(n, 0.0045) * click
    clk += sine(n, f_start * 3.1) * exp_dec(n, 0.0028) * (click * 0.6)
    mix = body + sub_layer + clk
    mix = sat(mix, drive=drive, kind='tanh')
    mix = lp(mix, tone, order=2)
    return fade(mix, 0.0004, 0.015)


def gabber_kick(rng, f_base=52.0, dur=0.52, drive=6.5):
    """Authentic Rotterdam 909 overdriven Gabber / Hardcore kick."""
    n = n_of(dur)
    t = tvec(dur)
    f_env = f_base + 220.0 * np.exp(-t / 0.026) + 90.0 * np.exp(-t / 0.085)
    raw = sine(n, f_env) * (0.85 * np.exp(-t / 0.38) + 0.25 * np.exp(-t / 0.12))
    raw += bp(noise(n, rng), 900.0, 5500.0) * np.exp(-t / 0.012) * 0.35
    boosted = peaking(raw, 165.0, gain_db=9.5, q=1.3)
    dist = sat(boosted, drive=drive, kind='hard')
    dist = peaking(dist, f_base, gain_db=5.0, q=1.5)
    dist = lp(dist, 6800.0, order=2)
    env = np.ones(n)
    tail = n_of(0.08)
    env[-tail:] = np.linspace(1.0, 0.0, tail) ** 1.5
    return dist * env


def psytrance_kick(rng, f_end=47.0, dur=0.25):
    """Laser-accurate phase-locked Psytrance kick."""
    n = n_of(dur)
    t = tvec(dur)
    f_env = f_end + 340.0 * np.exp(-t / 0.009) + 65.0 * np.exp(-t / 0.038)
    sig = sine(n, f_env)
    env = (1.0 - np.exp(-t / 0.0005)) * np.exp(-t / 0.16)
    env *= np.clip((dur - t) / 0.035, 0.0, 1.0)
    sig = sat(sig * env, drive=1.35, kind='tanh')
    return lp(sig, 8500.0, order=2)


def synth_snare(rng, f1=195.0, f2=315.0, decay=0.22, noise_decay=0.20,
                noise_amt=1.1, bright=6800.0, drive=1.5, rim_amt=0.18):
    dur = max(decay, noise_decay) * 2.3 + 0.05
    n = n_of(dur)
    t = tvec(dur)
    f1_e = f1 + 85.0 * np.exp(-t / 0.009)
    f2_e = f2 + 95.0 * np.exp(-t / 0.007)
    shell = 0.68 * sine(n, f1_e) * exp_dec(n, decay * 0.65)
    shell += 0.38 * sine(n, f2_e) * exp_dec(n, decay * 0.45)
    wires = bp(noise(n, rng) * 0.7 + pink_noise(n, rng) * 0.3, 950.0, min(bright, 15000.0))
    wires *= (0.35 * exp_dec(n, 0.025) + 0.65 * exp_dec(n, noise_decay))
    rim = bp(noise(n, rng), 1800.0, 6200.0) * exp_dec(n, 0.004) * rim_amt
    mix = sat(shell + wires * noise_amt + rim, drive=drive, kind='tanh')
    return fade(mix, 0.0004, 0.015)


def jazz_brush_snare(rng, mode='sweep'):
    """Jazz wire brush tap or lush swish sweep."""
    if mode == 'sweep':
        dur = float(rng.uniform(0.38, 0.62))
        n = n_of(dur)
        t = tvec(dur)
        n1 = pink_noise(n, rng) * 0.5 + noise(n, rng) * 0.5
        sweep_f = 1800.0 + 2600.0 * np.sin(np.pi * t / dur)
        swish = resonant_bp(n1, sweep_f, q=1.4)
        hi_air = bp(noise(n, rng), 4500.0, 13500.0) * 0.45
        env = np.sin(np.pi * (t / dur) ** 0.85) ** 1.2
        shell = sine(n, 188.0) * np.exp(-t / 0.08) * 0.12
        return fade((swish + hi_air) * env + shell, 0.005, 0.03)
    else:
        dur = float(rng.uniform(0.18, 0.28))
        n = n_of(dur)
        t = tvec(dur)
        wires = bp(noise(n, rng), 1600.0, 12500.0) * exp_dec(n, 0.085)
        shell = (0.55 * sine(n, 186.0) + 0.3 * sine(n, 292.0)) * exp_dec(n, 0.075)
        return fade(shell * 0.55 + wires * 0.85, 0.0006, 0.015)


def synthwave_gated_snare(rng):
    """Iconic 80s LinnDrum / Phil Collins stereo gated reverb snare."""
    dry = synth_snare(
        rng,
        f1=float(rng.uniform(175, 205)),
        f2=float(rng.uniform(290, 330)),
        decay=0.19,
        noise_decay=0.22,
        noise_amt=1.25,
        bright=9200.0,
        drive=1.85,
        rim_amt=0.32,
    )
    wet = stereo_reverb(dry, wet=0.46, decay=float(rng.uniform(0.34, 0.48)),
                        tone=7200.0, predelay=0.018, gated=True, rng=rng)
    return fade(wet, 0.0005, 0.025)


def simmons_tom(rng, f_start=260.0, f_end=85.0):
    """Iconic 80s Simmons SDS-V hexagonal electronic pitch-bend tom."""
    dur = float(rng.uniform(0.38, 0.55))
    n = n_of(dur)
    t = tvec(dur)
    f_env = f_end + (f_start - f_end) * np.exp(-t / 0.085)
    osc = 0.72 * sine(n, f_env) + 0.28 * polyblep_pulse(f_env, n, duty=0.35)
    osc = lp(osc, 2200.0) * exp_dec(n, dur * 0.52)
    noise_hit = bp(noise(n, rng), 700.0, 4200.0) * exp_dec(n, 0.032) * 0.42
    return fade(sat(osc + noise_hit, drive=1.4, kind='tanh'), 0.0005, 0.02)


def synth_clap(rng, bursts=4, spacing=0.011, decay=0.20, lo=850.0, hi=4800.0, stereo_wide=False):
    dur = decay * 2.4 + bursts * spacing + 0.05
    n = n_of(dur)
    raw = bp(noise(n, rng), lo, hi, order=2)
    env = np.zeros(n)
    t = tvec(dur)
    for b in range(bursts):
        t0 = b * spacing * float(rng.uniform(0.88, 1.12))
        mask = t >= t0
        env[mask] += 0.75 * np.exp(-(t[mask] - t0) / 0.0065)
    t_tail = (bursts - 1) * spacing
    mask = t >= t_tail
    env[mask] += 0.85 * np.exp(-(t[mask] - t_tail) / decay)
    out = sat(raw * env, drive=1.55, kind='tanh')
    if stereo_wide:
        out = stereo_reverb(out, wet=0.24, decay=0.55, tone=5800.0, rng=rng)
    return fade(out, 0.0005, 0.018)


def closed_hat(rng, decay=0.042, tone=10500.0, metallic=0.75, chick=False):
    dur = max(0.06, decay * 3.2)
    n = n_of(dur)
    ratios = [1.0, 1.342, 1.618, 1.927, 2.415, 2.879]
    metal = _cymbal_modes(n, float(rng.uniform(320, 440)), ratios, rng)
    metal = hp(metal, 5200.0, order=2)
    air = bp(noise(n, rng), 6500.0, min(tone * 1.35, 19500.0))
    env = exp_dec(n, decay)
    if chick:
        # Foot hi-hat chick has slightly softer attack & warm mid-high body
        body = bp(noise(n, rng), 2200.0, 7500.0) * exp_dec(n, 0.025) * 0.6
        sig = (metal * metallic * 0.55 + air * 0.55 + body) * env
        return fade(sig, 0.002, 0.01)
    sig = (metal * metallic + air * 0.75) * env
    return fade(lp(sig, min(tone * 1.4, 19800.0)), 0.0004, 0.008)


def jazz_ride(rng, bell=False, sizzle=True):
    dur = 1.45 if not bell else 1.15
    n = n_of(dur)
    t = tvec(dur)
    ratios = [1.0, 1.47, 1.89, 2.38, 2.96, 3.65, 4.41]
    shimmer = hp(_cymbal_modes(n, float(rng.uniform(390, 450)), ratios, rng), 2600.0)
    shimmer *= (0.45 * exp_dec(n, 0.18) + 0.55 * exp_dec(n, 0.72))
    ping = (sine(n, float(rng.uniform(2350, 2580))) * 0.75 +
            sine(n, float(rng.uniform(3720, 4050))) * 0.42) * exp_dec(n, 0.36 if bell else 0.14)
    stick = bp(noise(n, rng), 2500.0, 11000.0) * exp_dec(n, 0.004) * 0.5
    rivet = bp(noise(n, rng), 6500.0, 15000.0) * exp_dec(n, 0.95) * (0.24 if sizzle else 0.05)
    sig = ping * (1.25 if bell else 0.45) + shimmer * (0.45 if bell else 0.85) + stick + rivet
    return fade(lp(sig, 16500.0), 0.0005, 0.04)


def drift_phonk_cowbell(freq, dur=0.46, drive=2.6, rng=None):
    """
    Chromatic TR-808 Drift Phonk Cowbell!
    Classic 808 ratio 1 : 1.48148 (540 Hz & 800 Hz) pitch-locked to `freq`,
    bandpass-filtered + saturated for authentic Memphis / Drift Phonk melodies.
    """
    rng = rng or np.random.default_rng(808)
    n = n_of(dur)
    t = tvec(dur)
    osc1 = polyblep_pulse(freq, n, duty=0.50)
    osc2 = polyblep_pulse(freq * 1.48148, n, duty=0.48)
    raw = 0.62 * osc1 + 0.48 * osc2
    # Dual-stage 808 cowbell envelope (sharp hit + singing ring)
    env = 0.62 * np.exp(-t / 0.042) + 0.38 * np.exp(-t / (dur * 0.52))
    flt = bp(raw * env, max(180.0, freq * 0.72), min(freq * 5.5, 13500.0), order=2)
    flt = peaking(flt, min(freq * 1.48, 9000.0), gain_db=4.5, q=2.2)
    click = bp(noise(n, rng), 1800.0, 6500.0) * np.exp(-t / 0.0025) * 0.12
    out = sat(flt + click, drive=drive, kind='tube')
    return fade(out, 0.0004, 0.018)


def baile_cuica(rng, high=True):
    """Brazilian Funk / Samba friction-drum Cuica squeak ('hu-hu!')."""
    dur = float(rng.uniform(0.24, 0.40))
    n = n_of(dur)
    t = tvec(dur)
    f0 = float(rng.uniform(520, 680) if high else rng.uniform(330, 440))
    f_curve = f0 * (1.0 + 0.24 * np.sin(np.pi * t / dur) - 0.15 * (t / dur) ** 2)
    stick = polyblep_saw(f_curve, n)
    reson = resonant_bp(stick, f_curve * 1.02, q=5.5) + 0.45 * resonant_bp(stick, f_curve * 2.02, q=4.0)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.7
    rub = bp(noise(n, rng), 800.0, 3200.0) * env * 0.08
    return fade(sat(reson * env + rub, drive=1.5, kind='tanh'), 0.004, 0.018)


def automotivo_stab(rng, midi_note=60):
    """Metallic Brazilian Automotivo / Mandelão synth-percussion stab."""
    dur = float(rng.uniform(0.22, 0.36))
    n = n_of(dur)
    t = tvec(dur)
    f = midi_to_freq(midi_note)
    mod = sine(n, f * 3.5) * (4.5 * np.exp(-t / 0.06) + 0.8)
    car = np.sin(2.0 * np.pi * f * t + mod)
    sub = sine(n, f * 0.5) * 0.35
    env = exp_dec(n, dur * 0.55)
    return fade(sat((car + sub) * env, drive=2.8, kind='fold'), 0.0005, 0.015)
