import sys, os; sys.path.insert(0, 'work')
import numpy as np
from kitlib import drums as D, dsp, sequencer as S, midi as MIDIW
from kitlib.io import emit, set_root
from kitlib.dsp import FS

ROOTDIR = sys.argv[1] if len(sys.argv) > 1 else 'build/kit'
set_root(ROOTDIR)
rng = np.random.default_rng(31337)
U = lambda a, b: float(rng.uniform(a, b))

MIDI_DIR = os.path.join(ROOTDIR, '17_MIDI/drum_patterns')
os.makedirs(MIDI_DIR, exist_ok=True)
os.makedirs(os.path.join(ROOTDIR, '17_MIDI/progressions'), exist_ok=True)

# GM drum map (channel 10)
GM = dict(kick=36, snare=38, clap=39, rim=37, hat=42, ohat=46, crash=49, ride=51,
          tom_hi=50, tom_mid=47, tom_lo=43, perc=69, cowbell=56, shaker=70, tick=76)


def kit(kind):
    if kind == 'trap':
        return {
            'kick': lambda r: D.kick(r, f_start=U(140, 175), f_end=U(45, 52), decay=U(0.28, 0.38), drive=U(1.6, 2.2), tone=9000),
            'snare': lambda r: D.snare(r, tone=U(190, 220), decay=0.14, bright=6500, drive=1.8, clap_layer=0.25),
            'hat': lambda r: D.hat_closed(r, decay=0.035, noise_amt=0.5, tone=12000),
            'ohat': lambda r: D.hat_open(r, decay=0.3, noise_amt=0.4, tone=11000),
            'clap': lambda r: D.clap(r, decay=0.16, bursts=4),
            'perc': lambda r: D.blip(r, f0=U(900, 1600), f1=400, decay=0.06),
            'crash': lambda r: D.crash(r, decay=1.4),
        }
    if kind == 'drill':
        return {
            'kick': lambda r: D.kick(r, f_start=U(170, 210), f_end=U(42, 48), decay=U(0.32, 0.44), drive=U(2.4, 3.2), tone=10000),
            'snare': lambda r: D.snare(r, tone=U(180, 210), decay=0.16, bright=8000, drive=2.4, clap_layer=0.3),
            'hat': lambda r: D.hat_closed(r, decay=0.03, noise_amt=0.55, tone=13000),
            'ohat': lambda r: D.hat_open(r, decay=0.26, noise_amt=0.45, tone=12000),
            'clap': lambda r: D.clap(r, decay=0.14, bursts=4, hi=4200),
            'perc': lambda r: D.blip(r, f0=U(700, 1300), f1=300, decay=0.07),
            'crash': lambda r: D.crash(r, decay=1.2),
        }
    if kind == 'boombap':
        return {
            'kick': lambda r: D.kick(r, f_start=U(95, 120), f_end=U(55, 68), decay=U(0.34, 0.48), drive=1.3, tone=6500, beater=0.2),
            'snare': lambda r: D.snare(r, tone=U(195, 235), decay=U(0.18, 0.24), bright=5000, drive=1.3, rattle=0.6),
            'hat': lambda r: D.hat_closed(r, decay=0.045, noise_amt=0.5, tone=9000),
            'ohat': lambda r: D.hat_open(r, decay=0.32, noise_amt=0.4, tone=8000),
            'rim': lambda r: D.rim(r, tone=U(700, 950), decay=0.04),
            'perc': lambda r: D.shaker(r, decay=0.05),
            'crash': lambda r: D.crash(r, decay=1.2, hp_f=3500),
        }
    if kind == 'phonk':
        return {
            'kick': lambda r: D.kick(r, f_start=U(120, 160), f_end=U(40, 50), decay=U(0.2, 0.3), drive=U(3.0, 4.5), tone=5000),
            'snare': lambda r: D.snare(r, tone=U(160, 200), decay=0.1, bright=4500, drive=3.0),
            'hat': lambda r: D.hat_closed(r, decay=0.025, noise_amt=0.7, tone=10000, digital=0.4),
            'ohat': lambda r: D.hat_open(r, decay=0.22, noise_amt=0.5, tone=9000),
            'cowbell': lambda r: D.cowbell(r, f1=U(520, 600), f2=U(780, 860), decay=0.25),
            'perc': lambda r: D.glitch_perc(r, decay=0.08, bits=6),
            'crash': lambda r: D.crash(r, decay=1.0, hp_f=3000),
        }
    if kind == 'dnb':
        return {
            'kick': lambda r: D.kick(r, f_start=U(160, 200), f_end=U(48, 56), decay=0.2, drive=2.0, tone=9000, punch=0.3),
            'snare': lambda r: D.snare(r, tone=U(200, 240), decay=0.2, bright=9000, drive=2.0, rattle=0.4),
            'hat': lambda r: D.hat_closed(r, decay=0.03, noise_amt=0.6, tone=13000),
            'ohat': lambda r: D.hat_open(r, decay=0.24, noise_amt=0.5, tone=12000),
            'ride': lambda r: D.ride(r, decay=0.8, base=320),
            'perc': lambda r: D.shaker(r, decay=0.04),
            'crash': lambda r: D.crash(r, decay=1.4),
        }
    if kind == 'house':
        return {
            'kick': lambda r: D.kick(r, f_start=U(120, 150), f_end=U(48, 55), decay=0.3, drive=1.8, tone=11000, click=0.4),
            'clap': lambda r: D.clap(r, decay=0.18, bursts=4, hi=4200, room=0.3),
            'hat': lambda r: D.hat_closed(r, decay=0.04, noise_amt=0.45, tone=12000),
            'ohat': lambda r: D.hat_open(r, decay=0.4, noise_amt=0.4, tone=11000),
            'perc': lambda r: D.conga(r, f0=U(180, 240), decay=0.2),
            'snare': lambda r: D.snare(r, tone=210, decay=0.12, bright=6000, drive=1.4),
            'crash': lambda r: D.crash(r, decay=1.2),
        }
    if kind == 'techno':
        return {
            'kick': lambda r: D.kick(r, f_start=U(150, 190), f_end=U(44, 52), decay=0.24, drive=2.6, tone=7000, punch=0.35),
            'hat': lambda r: D.hat_closed(r, decay=0.03, noise_amt=0.6, tone=14000, digital=0.3),
            'ohat': lambda r: D.hat_open(r, decay=0.3, noise_amt=0.5, tone=13000),
            'ride': lambda r: D.ride(r, decay=0.7, base=360, bell=0.3),
            'rim': lambda r: D.rim(r, tone=U(800, 1100), decay=0.035, click=0.8),
            'clap': lambda r: D.clap(r, decay=0.14, bursts=3, hi=3800),
            'crash': lambda r: D.crash(r, decay=1.3),
        }
    if kind == 'lofi':
        return {
            'kick': lambda r: D.kick(r, f_start=U(85, 115), f_end=U(50, 62), decay=U(0.38, 0.52), drive=1.6, tone=3500),
            'snare': lambda r: D.snare(r, tone=U(180, 220), decay=0.18, bright=3200, drive=1.6, pink=0.4),
            'hat': lambda r: D.hat_closed(r, decay=0.045, noise_amt=0.6, tone=7000, digital=0.4),
            'rim': lambda r: D.rim(r, tone=U(650, 850), decay=0.05),
            'perc': lambda r: D.shaker(r, decay=0.06),
            'crash': lambda r: D.crash(r, decay=1.0, hp_f=2500),
        }
    if kind == 'reggaeton':
        return {
            'kick': lambda r: D.kick(r, f_start=U(110, 140), f_end=U(44, 52), decay=0.34, drive=2.0, tone=10000),
            'snare': lambda r: D.snare(r, tone=U(200, 230), decay=0.12, bright=7000, drive=1.8),
            'hat': lambda r: D.hat_closed(r, decay=0.035, noise_amt=0.5, tone=12000),
            'perc': lambda r: D.conga(r, f0=U(200, 260), decay=0.2),
            'clap': lambda r: D.clap(r, decay=0.16, bursts=4),
            'crash': lambda r: D.crash(r, decay=1.1),
        }
    if kind == 'jersey':
        return {
            'kick': lambda r: D.kick(r, f_start=U(180, 240), f_end=U(50, 60), decay=U(0.13, 0.2), drive=2.6, tone=12000, click=0.5),
            'snare': lambda r: D.snare(r, tone=U(190, 230), decay=0.1, bright=8000, drive=2.0),
            'hat': lambda r: D.hat_closed(r, decay=0.02, noise_amt=0.7, tone=15000, digital=0.5),
            'clap': lambda r: D.clap(r, decay=0.12, bursts=4, hi=5000),
            'ohat': lambda r: D.hat_open(r, decay=0.2, noise_amt=0.5, tone=13000),
            'perc': lambda r: D.blip(r, f0=U(1000, 1800), f1=500, decay=0.05),
            'crash': lambda r: D.crash(r, decay=1.0),
        }
    raise KeyError(kind)


PATTERNS = {}


def add(name, bpm, bars, kind, pattern, swing=0.0, midi=True):
    k = kit(kind)
    x = S.render_loop(bpm, bars, k, pattern, swing=swing, rng=rng)
    emit(f'16_LOOPS/drum_loops/{name}_{bpm}bpm.wav', x, 'LOOP', f'{kind}_{bpm}bpm', bpm=str(bpm),
         tags=f'{kind}, {bars} bars')
    PATTERNS[name] = (bpm, bars, pattern)


# ---------------------------------------------------------------- patterns
add('boombap', 90, 2, 'boombap', {
    'kick': S.every(2, [0, 7, 10], 1.0) + [(19, 0.8), (27, 0.9)],
    'snare': S.every(2, [4, 12], 1.0) + [(14, 0.35), (30, 0.3)],
    'hat': S.hat_16(2, 0.45, accents=(0, 8)),
    'rim': S.every(2, [15], 0.4),
    'perc': S.every(2, [6, 22], 0.35),
    'crash': [(0, 0.8)],
}, swing=0.28)

add('trap', 140, 2, 'trap', {
    'kick': S.every(2, [0, 6, 10], 1.0) + [(14, 0.85), (18, 0.9), (26, 0.8)],
    'snare': S.every(2, [4, 12], 1.0),
    'clap': S.every(2, [4, 12], 0.7),
    'hat': S.hat_16(2, 0.4, accents=(0, 8)) + [(29, 0.3), (30, 0.35), (31, 0.4)],
    'ohat': S.every(2, [14], 0.45),
    'perc': [(7, 0.4), (23, 0.4)],
    'crash': [(0, 0.7)],
})

add('drill', 142, 2, 'drill', {
    'kick': S.every(2, [0, 3, 10], 1.0) + [(6, 0.8), (18, 0.9), (22, 0.85), (27, 0.7)],
    'snare': S.every(2, [4, 12], 1.0) + [(15, 0.25)],
    'clap': S.every(2, [4, 12], 0.6),
    'hat': S.hat_16(2, 0.35, accents=(0, 6, 8, 14)) + [(31, 0.3)],
    'ohat': [(11, 0.4), (27, 0.35)],
    'crash': [(0, 0.7)],
})

add('phonk', 160, 2, 'phonk', {
    'kick': S.every(2, [0, 6, 8, 11], 1.0) + [(22, 0.8)],
    'snare': S.every(2, [4, 12], 1.0),
    'hat': S.hat_16(2, 0.32, accents=(0, 4, 8, 12)),
    'cowbell': [(0, 0.5), (3, 0.35), (6, 0.45), (10, 0.4), (16, 0.5), (19, 0.35), (22, 0.45), (26, 0.4)],
    'perc': [(14, 0.3), (30, 0.3)],
    'crash': [(0, 0.6)],
})

add('dnb', 174, 2, 'dnb', {
    'kick': [(0, 1.0), (10, 0.9), (16, 1.0), (26, 0.85)],
    'snare': [(4, 1.0), (12, 1.0), (20, 1.0), (28, 0.95), (14, 0.3), (30, 0.3)],
    'hat': S.hat_16(2, 0.3, accents=(0, 8)) + [(15, 0.25), (31, 0.25)],
    'ohat': [(6, 0.35), (22, 0.35)],
    'ride': [(7, 0.3), (23, 0.3)],
    'crash': [(0, 0.6)],
})

add('house', 128, 2, 'house', {
    'kick': S.every(2, [0, 4, 8, 12], 1.0),
    'clap': S.every(2, [4, 12], 0.85),
    'hat': S.hat_16(2, 0.3, accents=(4, 12)),
    'ohat': S.every(2, [2, 6, 10, 14], 0.45),
    'perc': [(15, 0.4), (31, 0.4)],
    'crash': [(0, 0.5)],
})

add('techno', 132, 2, 'techno', {
    'kick': S.every(2, [0, 4, 8, 12], 1.0),
    'ohat': S.every(2, [2, 6, 10, 14], 0.5),
    'hat': S.hat_16(2, 0.25, accents=(2, 6, 10, 14)),
    'rim': [(7, 0.4), (15, 0.35), (23, 0.4), (31, 0.35)],
    'clap': [(12, 0.5)],
    'crash': [(0, 0.5)],
})

add('lofi', 82, 2, 'lofi', {
    'kick': S.every(2, [0, 7, 10], 0.95) + [(18, 0.7)],
    'snare': S.every(2, [4, 12], 0.9) + [(15, 0.3)],
    'hat': S.hat_16(2, 0.35, accents=(0, 8)),
    'rim': [(11, 0.3), (27, 0.3)],
    'perc': [(6, 0.3), (22, 0.3)],
    'crash': [(0, 0.5)],
}, swing=0.3)

add('reggaeton', 100, 2, 'reggaeton', {
    'kick': S.every(2, [0, 8], 1.0) + [(6, 0.8), (14, 0.8), (22, 0.8), (30, 0.8)],
    'snare': [(3, 0.7), (11, 0.7), (19, 0.7), (27, 0.7)],
    'clap': S.every(2, [4, 12], 0.6),
    'hat': S.hat_16(2, 0.3, accents=(2, 6, 10, 14)),
    'perc': [(7, 0.4), (23, 0.4)],
    'crash': [(0, 0.5)],
})

add('jersey', 150, 2, 'jersey', {
    'kick': S.every(2, [0, 6, 8], 1.0) + [(14, 0.9), (19, 0.8), (27, 0.8)],
    'clap': S.every(2, [4, 8, 12], 0.8),
    'hat': S.hat_16(2, 0.3, accents=(0, 4, 8, 12)) + [(31, 0.3)],
    'ohat': [(3, 0.35), (11, 0.35), (19, 0.35), (27, 0.35)],
    'perc': [(15, 0.35), (30, 0.35)],
    'crash': [(0, 0.6)],
})

# ---------------------------------------------------------------- perc loops
PERC_KITS = {
    'shaker_16': ('shaker', lambda r: D.shaker(r, decay=0.05, lo=4000, hi=12000)),
    'tambourine_8': ('tambourine', lambda r: D.tambourine(r, decay=0.3)),
    'conga_pattern': ('conga', lambda r: D.conga(r, f0=210, decay=0.22)),
    'cowbell_pattern': ('cowbell', lambda r: D.cowbell(r, f1=560, f2=850, decay=0.22)),
    'rim_pattern': ('rim', lambda r: D.rim(r, tone=800, decay=0.04)),
}
perc_patterns = {
    'shaker_16': S.hat_16(2, 0.45, accents=(2, 6, 10, 14)),
    'tambourine_8': S.every(2, [0, 2, 4, 6, 8, 10, 12, 14], 0.5),
    'conga_pattern': [(0, 0.8), (3, 0.5), (6, 0.7), (10, 0.6), (16, 0.8), (19, 0.5), (22, 0.7), (26, 0.6), (30, 0.4)],
    'cowbell_pattern': [(0, 0.6), (4, 0.4), (6, 0.55), (12, 0.45), (16, 0.6), (20, 0.4), (22, 0.55), (28, 0.45)],
    'rim_pattern': [(2, 0.4), (7, 0.35), (11, 0.4), (18, 0.4), (23, 0.35), (27, 0.4)],
}
for name, pat in perc_patterns.items():
    key, fn = PERC_KITS[name]
    x = S.render_loop(100, 2, {key: fn}, {key: pat}, rng=rng, humanize_ms=4)
    emit(f'16_LOOPS/perc_loops/{name}_100bpm.wav', x, 'LOOP', 'perc', bpm='100', tags='percussion loop')

# ---------------------------------------------------------------- MIDI export
for name, (bpm, bars, pat) in PATTERNS.items():
    notes = []
    for voice, hits in pat.items():
        gm = {'perc': 69, 'cowbell': 56, 'shaker': 70, 'tick': 76}.get(voice, GM.get(voice, 39))
        for (step, vel) in hits:
            notes.append((step / 4.0, 0.2, gm, int(np.clip(vel * 110 + 12, 20, 127))))
    MIDIW.write_midi(os.path.join(MIDI_DIR, f'{name}_{bpm}bpm_drums.mid'),
                     [{'name': name, 'channel': 10, 'notes': notes}], bpm=bpm)

# chord progressions in a few keys (piano/harmony reference)
PROGS = {
    'i_VI_III_VII_minor': [0, 8, 3, 10],
    'i_iv_vII_v_minor': [0, 5, 10, 7],
    'Imaj7_vi7_ii7_V7': [0, 9, 2, 7],
    'i_VII_VI_VII': [0, 10, 8, 10],
    'i_III_VII_iv': [0, 3, 10, 5],
    'ii7_V7_Imaj7_Imaj7': [2, 7, 0, 0],
}
MAJOR = {'Imaj7_vi7_ii7_V7', 'ii7_V7_Imaj7_Imaj7'}
for pname, degs in PROGS.items():
    for root_key in ('C', 'F', 'G'):
        base = {'C': 48, 'F': 53, 'G': 55}[root_key]
        notes = []
        for i, d in enumerate(degs):
            if pname in MAJOR:
                chord = [0, 4, 7, 11] if d == 0 else ([0, 3, 7, 10] if d in (2, 9) else ([-1, 4, 7, 10] if d == 5 else [0, 3, 7, 10]))
            else:
                chord = [0, 3, 7, 10] if d == 0 else ([0, 3, 7, 10] if d == 5 else [0, 4, 7, 11] if d in (3, 8) else [0, 4, 7, 10])
            for j, iv in enumerate(chord):
                notes.append((i * 4 + j * 0.02, 3.6, base + d + iv, 90))
        MIDIW.write_midi(os.path.join(ROOTDIR, '17_MIDI/progressions', f'{pname}_{root_key}.mid'),
                         [{'name': pname, 'channel': 1, 'notes': notes}], bpm=120)
print('loops + midi done')
