import sys; sys.path.insert(0, 'work')
import numpy as np
from kitlib import drums as D, dsp
from kitlib.io import emit, set_root
from kitlib.dsp import midi_to_freq, note_filename

set_root(sys.argv[1] if len(sys.argv) > 1 else 'build/kit')
rng = np.random.default_rng(771)
U = lambda a, b: float(rng.uniform(a, b))

# tuned 808 sets: root notes C1..B1 (midi 24..35)
STYLES = {
 'clean':  dict(drive=1.3, harmonic=0.18, decay_tau=1.15, style='clean', click=0.0, lp_f=2600),
 'hard':   dict(drive=3.2, harmonic=0.35, decay_tau=1.0, style='distorted', click=0.03, lp_f=4200),
 'soft':   dict(drive=0.7, harmonic=0.10, decay_tau=1.35, style='soft', click=0.0, lp_f=1800),
 'reese':  dict(drive=2.0, harmonic=0.2, decay_tau=1.2, style='reese', click=0.0, lp_f=3000),
}
for style, base in STYLES.items():
    for m in range(24, 36):
        f = midi_to_freq(m)
        kw = dict(base)
        kw['decay_tau'] *= U(0.9, 1.1)
        kw['drive'] *= U(0.92, 1.1)
        x = D.sub808(rng, f, dur=1.35, **kw)
        name = note_filename(m)
        emit(f'12_808_SUB/808_tuned_{style}/808_{style}_{name}.wav', x, '808', style,
             root_note=name, tags=f'{f:.1f}Hz;midi{m}')

# 808 glides (from one note down to another)
GLIDES = [(28, 24), (31, 28), (33, 28), (36, 31), (31, 24), (34, 29), (26, 22), (29, 25), (32, 27), (35, 30), (27, 23), (30, 26)]
for i, (a, b) in enumerate(GLIDES):
    x = D.sub808(rng, midi_to_freq(b), dur=1.5, glide_from=midi_to_freq(a),
                 glide_time=U(0.05, 0.14), drive=U(1.2, 2.6), harmonic=U(0.15, 0.35),
                 style=rng.choice(['clean', 'distorted']), lp_f=U(2200, 4000))
    emit(f'12_808_SUB/808_glide/808_glide_{note_filename(a)}_to_{note_filename(b)}.wav', x, '808', 'glide',
         root_note=note_filename(b), tags=f'glide {note_filename(a)}->{note_filename(b)}')

# 808 one-shots (untuned / character)
for i in range(16):
    f = midi_to_freq(int(rng.integers(24, 34)))
    x = D.sub808(rng, f, dur=U(0.7, 1.6), drive=U(1.0, 4.0), harmonic=U(0.05, 0.45),
                 decay_tau=U(0.5, 1.3), style=rng.choice(['clean', 'distorted', 'reese', 'soft']),
                 click=U(0, 0.2), lp_f=U(1500, 5000))
    if i % 4 == 0:
        x = dsp.bitcrush(x, bits=int(U(8, 11)))
    emit(f'12_808_SUB/808_oneshots/808_oneshot_{i+1:02d}.wav', x, '808', 'oneshot',
         root_note=note_filename(int(round(12 * np.log2(f / 440) + 69))), tags=f'{f:.1f}Hz')

# sub bass tuned C1..B1
for m in range(24, 36):
    f = midi_to_freq(m)
    x = D.sub808(rng, f, dur=1.4, drive=0.5, harmonic=0.0, decay_tau=1.2, style='soft', lp_f=900)
    x = dsp.lp(x, 400, 2)
    emit(f'13_BASS/sub/sub_{note_filename(m)}.wav', x, 'SUB', 'sub', root_note=note_filename(m), tags=f'{f:.1f}Hz')

# synth bass (2 styles x 12 notes, C2..B2 / midi 36..47)
for style in ('saw', 'square'):
    for m in range(36, 48):
        f = midi_to_freq(m)
        x = D.bass_synth(rng, f, dur=U(0.7, 1.1), style=style, cutoff=U(180, 420),
                         env_amt=U(1200, 3000), drive=U(1.1, 1.8), sub=U(0.3, 0.6))
        emit(f'13_BASS/synth_bass_{style}/synth_bass_{style}_{note_filename(m)}.wav', x, 'BASS', style,
             root_note=note_filename(m), tags=f'{f:.1f}Hz')

# bass guitar C2..B2
for m in range(36, 48):
    f = midi_to_freq(m)
    x = D.bass_guitar(rng, f, dur=U(0.8, 1.2), bright=U(0.35, 0.6), damp=U(0.45, 0.7), drive=U(1.1, 1.6))
    emit(f'13_BASS/bass_guitar/bass_guitar_{note_filename(m)}.wav', x, 'BASS', 'guitar',
         root_note=note_filename(m), tags=f'{f:.1f}Hz')

print('bass done')
