"""Sample writing + kit index."""
import os, json
import numpy as np
import soundfile as sf
from .dsp import FS, normalize, trim_silence, peak_db, rms, spectral_centroid

ROOT = None
INDEX = []


def set_root(p):
    global ROOT
    ROOT = p
    os.makedirs(p, exist_ok=True)


def emit(rel, x, category, style='', root_note='', bpm='', tags='', stereo=False,
         trim=True, peak=-1.0, fade_ms=10.0, note=''):
    """Normalize, trim, write 16-bit wav, register in index."""
    if ROOT is None:
        raise RuntimeError('set_root first')
    x = np.nan_to_num(np.asarray(x, dtype=np.float64))
    if stereo and x.ndim == 1:
        x = np.stack([x, x], axis=1)
    if trim:
        x = trim_silence(x, -54)
    x = normalize(x, peak)
    # safety fade in/out to kill clicks
    n = len(x)
    f = min(int(0.0008 * FS) + 6, max(1, n // 8))
    env = np.ones(n)
    env[:f] = np.linspace(0, 1, f) ** 0.5
    b = min(int(fade_ms / 1000 * FS), max(1, n // 4))
    env[n - b:] *= np.linspace(1, 0, b) ** 1.2
    if x.ndim == 1:
        x = x * env
    else:
        x = x * env[:, None]
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sf.write(path, x.astype(np.float32), FS, subtype='PCM_16')
    dur = n / FS
    mono = x if x.ndim == 1 else x.mean(axis=1)
    INDEX.append(dict(
        path=rel.replace(os.sep, '/'), category=category, style=style, note=root_note,
        bpm=bpm, seconds=round(dur, 3), peak_db=round(peak_db(x), 1),
        rms_db=round(20 * np.log10(rms(mono) + 1e-12), 1),
        centroid_hz=round(spectral_centroid(mono), 0),
        channels=2 if x.ndim == 2 else 1, tags=tags, note_detail=note))
    return path


def save_index(path):
    import csv
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(INDEX[0].keys()), delimiter=';')
        w.writeheader()
        for row in INDEX:
            w.writerow(row)
    print('index rows:', len(INDEX))


def report():
    import collections
    c = collections.Counter(r['category'] for r in INDEX)
    tot = sum(r['seconds'] for r in INDEX)
    for k, v in sorted(c.items()):
        print(f'  {k:28s} {v:4d}')
    print(f'  {"TOTAL":28s} {len(INDEX):4d}  ({tot/60:.1f} min audio)')
