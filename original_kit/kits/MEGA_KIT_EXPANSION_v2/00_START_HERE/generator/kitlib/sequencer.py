"""Pattern-based loop renderer."""
import numpy as np
from .dsp import *


def _hit_voices(rng, kit):
    return {name: fn(rng) for name, fn in kit.items()}


def render_loop(bpm, bars, kit_fns, pattern, steps_per_bar=16, swing=0.0,
                humanize_ms=3.0, rng=None, tail=0.35, kit_variants=2):
    """pattern: {voice: [(step, vel), ...]} steps are global 16th indices."""
    rng = rng or np.random.default_rng()
    beat = 60.0 / bpm
    step_dur = (beat * 4.0 / steps_per_bar)
    total_steps = bars * steps_per_bar
    total = total_steps * step_dur
    n = n_of(total + tail)
    out = np.zeros(n)
    variants = {v: [kit_fns[v](rng) for _ in range(kit_variants)] for v in pattern}
    for voice, hits in pattern.items():
        for (step, vel) in hits:
            t = step * step_dur
            if swing and (step % 2 == 1):
                t += step_dur * swing * 0.5
            t += rng.normal(0, humanize_ms / 1000.0)
            t = max(0.0, t)
            smp = variants[voice][int(rng.integers(0, kit_variants))]
            i = n_of(t)
            m = min(len(smp), n - i)
            if m <= 0:
                continue
            out[i:i + m] += smp[:m] * vel
    out = sat(out, 1.15, 'tanh')
    out = fade(out, 0.002, 0.05)
    return out


def roll(steps, voices_vel=None):
    return list(steps)


def hat_16(bars, vel=0.5, jitter=True, rng=None, accents=(0, 4, 8, 12)):
    rng = rng or np.random.default_rng()
    hits = []
    for s in range(bars * 16):
        v = vel * (1.25 if s % 16 in accents else 1.0)
        if jitter:
            v *= rng.uniform(0.85, 1.1)
        hits.append((s, v))
    return hits


def every(bars, positions, vel=1.0, repeat_each_bar=True):
    hits = []
    for b in range(bars if repeat_each_bar else 1):
        for p in positions:
            hits.append((b * 16 + p, vel))
    return hits
