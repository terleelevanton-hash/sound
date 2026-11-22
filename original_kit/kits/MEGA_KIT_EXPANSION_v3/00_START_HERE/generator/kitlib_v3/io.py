"""WAV emitter and metadata index builder for MEGA KIT v3."""
import csv
import os
import numpy as np
import soundfile as sf
from .dsp import FS, dc_block, normalize, trim_silence, fade, peak_db, rms, spectral_centroid

ROOT = None
INDEX = []


def set_root(path):
    global ROOT
    ROOT = path
    os.makedirs(path, exist_ok=True)


STEREO_KEEP_MARKERS = (
    '14_MELODIC/pads/',
    '16_LOOPS/melodic_loops/',
    'synthwave_gated',
    'DEMO_',
)


def emit(rel, x, category, style='', root_note='', bpm='', tags='',
         trim=True, peak=-1.0, fade_in_s=0.0007, fade_out_s=0.012, is_loop=False):
    """Sanitize, DC-block, trim/preserve loop length, normalize, write 16-bit 44.1kHz WAV."""
    if ROOT is None:
        raise RuntimeError('Call set_root(output_dir) first')
    x = np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)
    rel_posix = rel.replace(os.sep, '/')
    if x.ndim == 2 and not any(m in rel_posix for m in STEREO_KEEP_MARKERS):
        x = x.mean(axis=1)
    x = dc_block(x, FS)
    if trim and not is_loop:
        x = trim_silence(x, thresh_db=-46.0, pad_ms=2.0, fs=FS)
    if not is_loop:
        x = fade(x, fin=fade_in_s, fout=fade_out_s, fs=FS)
    x = normalize(x, peak_db=peak)

    full_path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    sf.write(full_path, x.astype(np.float32), FS, subtype='PCM_16')

    mono = x if x.ndim == 1 else x.mean(axis=1)
    dur = len(x) / float(FS)
    INDEX.append({
        'path': rel.replace(os.sep, '/'),
        'category': category,
        'style': style,
        'root_note': root_note,
        'bpm': bpm,
        'seconds': round(dur, 4),
        'samples': len(x),
        'peak_db': round(peak_db(x), 2),
        'rms_db': round(20.0 * np.log10(rms(mono) + 1e-12), 2),
        'centroid_hz': int(round(spectral_centroid(mono, FS))),
        'channels': 2 if x.ndim == 2 else 1,
        'tags': tags,
    })
    return full_path


def save_index(csv_path):
    if not INDEX:
        return
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=list(INDEX[0].keys()), delimiter=';')
        writer.writeheader()
        writer.writerows(INDEX)
