import sys; sys.path.insert(0, 'work')
import numpy as np
from kitlib import melodic as M, dsp
from kitlib.io import emit, set_root
from kitlib.dsp import midi_to_freq, note_filename, FS

set_root(sys.argv[1] if len(sys.argv) > 1 else 'build/kit')
rng = np.random.default_rng(424242)
U = lambda a, b: float(rng.uniform(a, b))

MAIN_NOTES = list(range(60, 72))          # C4..B4 chromatic
MINI_NOTES = [60, 63, 66, 69]             # C4, D#4, F#4, A4

# (name, folder, generator(freq, dur), dur, note set)
INSTRUMENTS = [
    # ---------------- keys
    ('piano_soft',   'keys',    lambda f, d: M.piano(f, d, bright=U(0.2, 0.38), rng=rng), 1.7, MAIN_NOTES),
    ('piano_bright', 'keys',    lambda f, d: M.piano(f, d, bright=U(0.72, 0.95), rng=rng), 1.7, MAIN_NOTES),
    ('rhodes',       'keys',    lambda f, d: M.rhodes(f, d, bark=U(0.7, 1.3), rng=rng), 1.9, MAIN_NOTES),
    ('fm_ep',        'keys',    lambda f, d: M.fm_ep(f, d, rng=rng), 1.5, MINI_NOTES),
    ('organ',        'keys',    lambda f, d: M.organ(f, d, rng=rng), 1.7, MAIN_NOTES),
    ('harpsichord',  'keys',    lambda f, d: M.harpsichord(f, d, rng=rng), 1.3, MINI_NOTES),
    ('celesta',      'keys',    lambda f, d: M.celesta(f, d, rng=rng), 1.4, MINI_NOTES),
    ('music_box',    'keys',    lambda f, d: M.music_box(f, d, rng=rng), 1.5, MAIN_NOTES),
    # ---------------- mallets / bars / metal
    ('marimba',      'mallets', lambda f, d: M.marimba(f, d, rng=rng), 1.0, MAIN_NOTES),
    ('vibraphone',   'mallets', lambda f, d: M.vibraphone(f, d, rng=rng), 1.7, MINI_NOTES),
    ('glockenspiel', 'mallets', lambda f, d: M.glockenspiel(f, d, rng=rng), 1.3, MINI_NOTES),
    ('kalimba',      'mallets', lambda f, d: M.kalimba(f, d, rng=rng), 1.3, MINI_NOTES),
    ('steel_drum',   'mallets', lambda f, d: M.steel_drum(f, d, rng=rng), 1.2, MINI_NOTES),
    ('handpan',      'mallets', lambda f, d: M.handpan(f, d, rng=rng), 1.7, MINI_NOTES),
    # ---------------- synths
    ('pluck_synth',  'synths',  lambda f, d: M.pluck(f, d, cutoff=U(1600, 3600), rng=rng), 1.15, MAIN_NOTES),
    ('saw_lead',     'synths',  lambda f, d: M.saw_lead(f, d, cutoff=U(3800, 6500), rng=rng), 1.3, MAIN_NOTES),
    ('supersaw',     'synths',  lambda f, d: M.supersaw(f, d, rng=rng), 1.6, MAIN_NOTES),
    ('pulse_lead',   'synths',  lambda f, d: M.pulse_lead(f, d, duty=U(0.2, 0.35), crush=0, rng=rng), 0.9, MINI_NOTES),
    ('square_lead',  'synths',  lambda f, d: M.square_lead(f, d, rng=rng), 1.1, MINI_NOTES),
    ('fm_bell',      'synths',  lambda f, d: M.fm_bell(f, d, ratio=U(2.8, 4.2), index=U(2.2, 4.5), rng=rng), 1.7, MINI_NOTES),
    # ---------------- pads
    ('pad_warm',     'pads',    lambda f, d: M.pad_warm(f, d, rng=rng), 1.95, MAIN_NOTES),
    ('pad_choir',    'pads',    lambda f, d: M.pad_choir(f, d, rng=rng), 1.95, MAIN_NOTES),
    # ---------------- guitars
    ('guitar_clean', 'guitars', lambda f, d: M.guitar_clean(f, d, bright=U(0.4, 0.65), rng=rng), 1.5, MAIN_NOTES),
    ('guitar_dist',  'guitars', lambda f, d: M.guitar_dist(f, d, drive=U(4.0, 9.0), rng=rng), 1.3, MAIN_NOTES),
    ('guitar_muted', 'guitars', lambda f, d: M.guitar_muted(f, d, rng=rng), 0.7, MINI_NOTES),
    # ---------------- strings / bowed
    ('strings',      'strings', lambda f, d: M.strings_ensemble(f, d, rng=rng), 1.95, MAIN_NOTES),
    ('cello',        'strings', lambda f, d: M.cello(f, d, rng=rng), 1.8, MINI_NOTES),
    ('violin',       'strings', lambda f, d: M.solo_violin(f, d, rng=rng), 1.7, MINI_NOTES),
    ('pizz',         'strings', lambda f, d: M.pizz(f, d, rng=rng), 0.8, MINI_NOTES),
    ('harp',         'strings', lambda f, d: M.harp(f, d, rng=rng), 1.7, MINI_NOTES),
    # ---------------- winds / brass
    ('flute',        'winds',   lambda f, d: M.flute(f, d, rng=rng), 1.5, MINI_NOTES),
    ('pan_flute',    'winds',   lambda f, d: M.pan_flute(f, d, rng=rng), 1.35, MINI_NOTES),
    ('ocarina',      'winds',   lambda f, d: M.ocarina(f, d, rng=rng), 1.35, MINI_NOTES),
    ('clarinet',     'winds',   lambda f, d: M.clarinet(f, d, rng=rng), 1.55, MINI_NOTES),
    ('shakuhachi',   'winds',   lambda f, d: M.shakuhachi(f, d, rng=rng), 1.55, MINI_NOTES),
    ('trumpet',      'brass',   lambda f, d: M.trumpet(f, d, rng=rng), 1.45, MINI_NOTES),
    ('synth_brass',  'brass',   lambda f, d: M.synth_brass(f, d, rng=rng), 1.4, MINI_NOTES),
    # ---------------- world / plucked
    ('sitar',        'world',   lambda f, d: M.sitar(f, d, rng=rng), 1.55, MINI_NOTES),
    ('koto',         'world',   lambda f, d: M.koto(f, d, rng=rng), 1.3, MINI_NOTES),
    ('banjo',        'world',   lambda f, d: M.banjo(f, d, rng=rng), 1.0, MINI_NOTES),
    ('oud',          'world',   lambda f, d: M.oud(f, d, rng=rng), 1.15, MINI_NOTES),
    # ---------------- vox
    ('vocal_aah',    'vox',     lambda f, d: M.vocal_aah(f, d, vowel='a', rng=rng), 1.9, MINI_NOTES),
    ('vocal_ooh',    'vox',     lambda f, d: M.vocal_aah(f, d, vowel='o', rng=rng), 1.9, MINI_NOTES),
    ('vocal_chop',   'vox',     lambda f, d: M.vocal_chop(f, d, rng=rng), 0.9, MINI_NOTES),
]

MEL_TAGS = {'piano_soft': 'felt piano, warm', 'piano_bright': 'pop/classical piano',
            'rhodes': 'electric piano, soul', 'organ': 'drawbar organ, gospel/soul',
            'supersaw': 'trance/EDM', 'pad_warm': 'ambient pad, long attack',
            'pad_choir': 'choir pad, long attack', 'guitar_dist': 'distorted power chord',
            'saw_lead': 'supersaw-ish lead', 'pluck_synth': 'pluck, trap/EDM'}

for name, folder, fn, dur, notes in INSTRUMENTS:
    for m in notes:
        f = midi_to_freq(m)
        dur = dur * 0.88
        x = fn(f, dur)
        n = int(dur * FS)
        if len(x) > n:
            x = x[:n]
        x = dsp.fade(x, fin=0.0008, fout=0.02)
        emit(f'14_MELODIC/{folder}/{name}/{name}_{note_filename(m)}.wav', x, 'MELODIC', name,
             root_note=note_filename(m), tags=MEL_TAGS.get(name, folder) + ';midi' + str(m))
    print('  ', name, len(notes), 'notes')

# ---------------- bonus: chord / stab one-shots (stacked instrument hits)
CHORDSET = {
 'minor9': [0, 3, 7, 10, 14], 'major9': [0, 4, 7, 11, 14], 'minor7': [0, 3, 7, 10],
 'maj7': [0, 4, 7, 11], 'sus2': [0, 2, 7, 12], 'dim': [0, 3, 6, 9],
}
for i, (cname, iv) in enumerate(CHORDSET.items()):
    root = 48 + int(rng.integers(0, 12))
    sig = np.zeros(int(1.8 * FS))
    for k, j in enumerate(iv):
        f = midi_to_freq(root + j)
        v = M.piano(f, 1.7, bright=0.45, rng=rng)[:len(sig)]
        sig[:len(v)] += v * (0.9 ** k)
    sig = dsp.reverb(sig, wet=0.18, decay=1.2, tone=6000, rng=rng)[:int(1.8 * FS)]
    emit(f'14_MELODIC/chords_stabs/chord_piano_{cname}_{note_filename(root)}.wav', sig, 'CHORD', 'piano_' + cname,
         root_note=note_filename(root), tags=f'piano {cname} chord')
for i, (cname, iv) in enumerate(CHORDSET.items()):
    root = 48 + int(rng.integers(0, 12))
    sig = np.zeros(int(1.5 * FS))
    for k, j in enumerate(iv):
        f = midi_to_freq(root + j)
        v = M.supersaw(f, 1.4, rng=rng)[:len(sig)]
        sig[:len(v)] += v * (0.9 ** k)
    emit(f'14_MELODIC/chords_stabs/chord_supersaw_{cname}_{note_filename(root)}.wav', sig, 'CHORD', 'synth_' + cname,
         root_note=note_filename(root), tags=f'supersaw {cname} chord')
print('melodic done')
