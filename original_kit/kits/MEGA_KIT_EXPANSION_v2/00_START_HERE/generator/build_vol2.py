"""VOL.2 - second expansion wave: new genres, orchestral perc, fills, world, loops."""
import sys, os; sys.path.insert(0, 'work')
import numpy as np
from kitlib import drums as D, extra as E, dsp, sequencer as S, midi as MIDIW
from kitlib.io import emit, set_root
from kitlib.dsp import midi_to_freq, note_filename, FS

OUT = sys.argv[1] if len(sys.argv) > 1 else 'build/kit'
set_root(OUT)
rng = np.random.default_rng(202602)
U = lambda a, b: float(rng.uniform(a, b))

# ============================================================ KICKS: new genres
KICKS2 = {
 'amapiano': dict(f_start=(110, 145), f_end=(42, 52), pitch_tau=(0.02, 0.04), decay=(0.32, 0.5),
                  click=(0.05, 0.2), drive=(1.2, 1.9), tone=(5500, 9000), sub=(0.3, 0.55), punch=(0.05, 0.2)),
 'afrobeat': dict(f_start=(95, 135), f_end=(48, 60), pitch_tau=(0.015, 0.035), decay=(0.26, 0.42),
                  click=(0.15, 0.35), drive=(1.3, 2.0), tone=(5000, 8000), sub=(0.2, 0.4), punch=(0.1, 0.28), beater=(0.1, 0.3)),
 'ukg': dict(f_start=(140, 190), f_end=(50, 60), pitch_tau=(0.01, 0.025), decay=(0.16, 0.26),
             click=(0.3, 0.55), drive=(1.6, 2.6), tone=(9000, 13000), sub=(0.15, 0.35), punch=(0.2, 0.4)),
 'dubstep': dict(f_start=(130, 180), f_end=(38, 48), pitch_tau=(0.012, 0.03), decay=(0.24, 0.4),
                 click=(0.2, 0.45), drive=(3.0, 5.0), tone=(4500, 8000), sub=(0.3, 0.6), punch=(0.15, 0.35)),
 'breakbeat': dict(f_start=(150, 200), f_end=(48, 58), pitch_tau=(0.01, 0.022), decay=(0.18, 0.3),
                   click=(0.35, 0.6), drive=(2.0, 3.2), tone=(8000, 12000), sub=(0.2, 0.4), punch=(0.2, 0.4)),
 'plugg': dict(f_start=(90, 130), f_end=(45, 56), pitch_tau=(0.02, 0.045), decay=(0.34, 0.55),
               click=(0.05, 0.2), drive=(1.1, 1.6), tone=(2800, 5000), sub=(0.25, 0.45), punch=(0.0, 0.12)),
 'rage': dict(f_start=(160, 230), f_end=(44, 54), pitch_tau=(0.01, 0.025), decay=(0.2, 0.34),
              click=(0.3, 0.55), drive=(4.0, 6.5), tone=(7000, 11000), sub=(0.25, 0.5), punch=(0.2, 0.4)),
 'memphis': dict(f_start=(100, 150), f_end=(40, 50), pitch_tau=(0.012, 0.03), decay=(0.16, 0.3),
                 click=(0.25, 0.5), drive=(3.0, 5.5), tone=(2500, 4500), sub=(0.3, 0.55), punch=(0.1, 0.3)),
 'footwork': dict(f_start=(180, 250), f_end=(50, 62), pitch_tau=(0.006, 0.018), decay=(0.12, 0.2),
                  click=(0.4, 0.65), drive=(2.2, 3.6), tone=(10000, 15000), sub=(0.15, 0.35), punch=(0.25, 0.45)),
 'synthwave': dict(f_start=(120, 165), f_end=(46, 56), pitch_tau=(0.015, 0.032), decay=(0.24, 0.36),
                   click=(0.2, 0.4), drive=(1.5, 2.4), tone=(7000, 10500), sub=(0.2, 0.4), punch=(0.15, 0.32)),
 'latin': dict(f_start=(100, 140), f_end=(52, 66), pitch_tau=(0.012, 0.03), decay=(0.2, 0.34),
               click=(0.2, 0.4), drive=(1.2, 1.8), tone=(4500, 7500), sub=(0.15, 0.35), punch=(0.12, 0.3), beater=(0.25, 0.5)),
 'reggae': dict(f_start=(90, 125), f_end=(52, 66), pitch_tau=(0.018, 0.04), decay=(0.28, 0.46),
                click=(0.1, 0.3), drive=(1.35, 2.0), tone=(3500, 6000), sub=(0.25, 0.45), punch=(0.08, 0.22), beater=(0.1, 0.3)),
 'metal': dict(f_start=(130, 200), f_end=(55, 70), pitch_tau=(0.006, 0.016), decay=(0.12, 0.2),
               click=(0.45, 0.7), drive=(2.2, 3.6), tone=(6000, 10000), sub=(0.1, 0.28), punch=(0.25, 0.5), beater=(0.4, 0.75)),
 'country': dict(f_start=(85, 120), f_end=(55, 72), pitch_tau=(0.012, 0.03), decay=(0.18, 0.3),
                 click=(0.12, 0.3), drive=(1.15, 1.7), tone=(4000, 6500), sub=(0.15, 0.32), punch=(0.1, 0.25), beater=(0.3, 0.6)),
}
for style, p in KICKS2.items():
    for i in range(3):
        kw = {k: U(*v) for k, v in p.items()}
        x = D.kick(rng, **kw)
        if style == 'synthwave':
            x = dsp.reverb(x, wet=0.22, decay=0.5, tone=6000, rng=rng)
            x = np.concatenate([x, np.zeros(int(0.05 * FS))])
        if style in ('memphis', 'plugg'):
            x = dsp.bitcrush(x, bits=int(U(9, 12)))
            x = dsp.reverb(x, wet=0.12, decay=0.3, tone=3000, rng=rng)
        if style == 'metal':
            x = dsp.reverb(x, wet=0.1, decay=0.25, tone=5000, rng=rng)
        emit(f'01_KICKS/{style}/kick_{style}_{i+1:02d}.wav', x, 'KICK', style)

# ============================================================ SNARES: new genres
SNARES2 = {
 'amapiano': dict(tone=(200, 250), decay=(0.16, 0.26), bright=(3500, 6500), drive=(1.2, 1.7), noise_amt=(1.1, 1.5), clap_layer=(0.3, 0.6), rattle=(0.5, 0.8)),
 'afrobeat': dict(tone=(190, 240), decay=(0.18, 0.3), bright=(4000, 7000), drive=(1.2, 1.8), noise_amt=(1.1, 1.4), rattle=(0.5, 0.9)),
 'ukg': dict(tone=(210, 260), decay=(0.1, 0.18), bright=(6000, 9500), drive=(1.5, 2.2), noise_amt=(1.0, 1.3), clap_layer=(0.1, 0.35)),
 'dubstep': dict(tone=(170, 220), decay=(0.2, 0.34), bright=(5000, 9000), drive=(2.4, 4.0), noise_amt=(1.1, 1.5), clap_layer=(0.2, 0.45)),
 'breakbeat': dict(tone=(200, 260), decay=(0.16, 0.28), bright=(7000, 12000), drive=(2.0, 3.0), noise_amt=(1.1, 1.5), rattle=(0.3, 0.6)),
 'plugg': dict(tone=(180, 230), decay=(0.12, 0.22), bright=(2200, 4200), drive=(1.3, 1.9), noise_amt=(0.9, 1.2), pink=(0.3, 0.6)),
 'memphis': dict(tone=(160, 210), decay=(0.08, 0.16), bright=(2500, 5000), drive=(3.0, 5.0), noise_amt=(0.9, 1.3)),
 'metal': dict(tone=(240, 320), decay=(0.05, 0.1), bright=(5000, 9000), drive=(2.4, 3.6), noise_amt=(0.7, 1.1), second=(1.5, 2.0)),
 'country': dict(tone=(190, 240), decay=(0.2, 0.34), bright=(3000, 5500), drive=(1.1, 1.5), noise_amt=(1.2, 1.6), pink=(0.2, 0.5)),
 'latin': dict(tone=(280, 360), decay=(0.1, 0.2), bright=(6000, 10000), drive=(1.4, 2.2), noise_amt=(0.8, 1.1)),
}
for style, p in SNARES2.items():
    for i in range(2):
        kw = {k: U(*v) for k, v in p.items()}
        kw.setdefault('second', U(1.55, 1.75))
        x = D.snare(rng, **kw)
        if style in ('plugg', 'memphis'):
            x = dsp.bitcrush(x, bits=int(U(10, 13)))
        emit(f'02_SNARES/{style}/snare_{style}_{i+1:02d}.wav', x, 'SNARE', style)

# ============================================================ CLAPS: new
CLAPS2 = {
 'amapiano': dict(decay=(0.16, 0.28), spacing=(0.012, 0.02), bursts=(4, 6), lo=(700, 1000), hi=(2400, 4200), room=(0.3, 0.55)),
 'ukg': dict(decay=(0.09, 0.16), spacing=(0.007, 0.012), bursts=(3, 4), lo=(900, 1300), hi=(3500, 6000), room=(0.1, 0.28)),
 'breakbeat': dict(decay=(0.12, 0.2), spacing=(0.009, 0.014), bursts=(3, 5), lo=(800, 1200), hi=(3000, 5500), room=(0.15, 0.35)),
 'dubstep': dict(decay=(0.18, 0.3), spacing=(0.012, 0.018), bursts=(4, 6), lo=(600, 950), hi=(3000, 6000), room=(0.35, 0.6)),
}
for style, p in CLAPS2.items():
    for i in range(3):
        kw = {k: U(*v) for k, v in p.items()}
        kw['bursts'] = int(kw['bursts'])
        x = D.clap(rng, **kw)
        emit(f'03_CLAPS/{style}/clap_{style}_{i+1:02d}.wav', x, 'CLAP', style)

# ============================================================ HATS: new
HATS2 = [
 ('ukg', dict(decay=(0.02, 0.04), noise_amt=(0.4, 0.7), metal=(0.8, 1.2), tone=(11000, 16000))),
 ('footwork', dict(decay=(0.012, 0.03), noise_amt=(0.6, 0.9), metal=(0.4, 0.9), tone=(13000, 18000), digital=(0.4, 0.8))),
 ('breakbeat', dict(decay=(0.03, 0.06), noise_amt=(0.5, 0.8), metal=(0.7, 1.1), tone=(9000, 14000))),
 ('amapiano', dict(decay=(0.04, 0.08), noise_amt=(0.5, 0.85), metal=(0.5, 0.9), tone=(8000, 13000))),
]
for style, p in HATS2:
    for i in range(4):
        kw = {k: U(*v) for k, v in p.items()}
        kw['digital'] = kw.get('digital', 0.0)
        x = D.hat_closed(rng, **kw)
        emit(f'05_HATS_CLOSED/{style}/hat_{style}_{i+1:02d}.wav', x, 'HAT_CLOSED', style)
for style, p in [('ukg', dict(decay=(0.18, 0.32), noise_amt=(0.4, 0.7), tone=(11000, 16000))),
                 ('amapiano', dict(decay=(0.25, 0.45), noise_amt=(0.45, 0.75), tone=(9000, 13000)))]:
    for i in range(3):
        kw = {k: U(*v) for k, v in p.items()}
        emit(f'06_HATS_OPEN/{style}/openhat_{style}_{i+1:02d}.wav', D.hat_open(rng, **kw), 'HAT_OPEN', style)

# ============================================================ PERC: latin / afro / cinematic-ish
for i in range(3):
    emit(f'09_PERC_ACOUSTIC/timbales/timbales_{i+1:02d}.wav',
         E.timbales(rng, f0=U(290, 380), decay=U(0.22, 0.4)), 'PERC', 'timbales')
for i in range(3):
    emit(f'09_PERC_ACOUSTIC/agogo/agogo_{i+1:02d}.wav',
         E.agogo(rng, f1=U(620, 800), f2=U(980, 1200), decay=U(0.16, 0.3)), 'PERC', 'agogo')
for i in range(3):
    emit(f'09_PERC_ACOUSTIC/surdo/surdo_{i+1:02d}.wav',
         E.surdo(rng, f0=U(60, 85), decay=U(0.4, 0.7)), 'PERC', 'surdo')
for i in range(3):
    emit(f'09_PERC_ACOUSTIC/wood_plank/wood_plank_{i+1:02d}.wav',
         E.wood_plank(rng, tone=U(420, 700), decay=U(0.05, 0.12)), 'PERC', 'wood_plank')
for i in range(4):
    emit(f'09_PERC_ACOUSTIC/afro_shaker/afro_shaker_{i+1:02d}.wav',
         D.shaker(rng, decay=U(0.06, 0.14), lo=U(2500, 4500), hi=U(9000, 13000), grains=int(rng.integers(2, 5))),
         'PERC', 'afro_shaker')
for i in range(2):
    emit(f'09_PERC_ACOUSTIC/tambourine/tambourine_hi_{i+1:02d}.wav',
         D.tambourine(rng, decay=U(0.12, 0.25)), 'PERC', 'tambourine')

# ============================================================ ORCHESTRAL / CINEMATIC PERC
TIMP = {'C2': 65.41, 'F2': 87.31, 'A2': 110.0, 'C3': 130.81}
for nm, f in TIMP.items():
    emit(f'20_TONAL_PERC/timpani/timpani_{nm}.wav', E.timpani(rng, f, dur=U(1.6, 2.2)), 'TONAL_PERC',
         'timpani', root_note=nm, tags=f'{f:.1f}Hz')
for nm, f in {'C1': 32.7, 'F1': 43.65, 'A1': 55.0}.items():
    emit(f'20_TONAL_PERC/gong/gong_{nm}.wav', E.gong(rng, f, dur=U(2.6, 3.4)), 'TONAL_PERC',
         'gong', root_note=nm, tags=f'{f:.1f}Hz')
for nm, f in {'C3': 130.81, 'Fs3': 185.0, 'A3': 220.0}.items():
    emit(f'20_TONAL_PERC/singing_bowl/bowl_{nm}.wav', E.singing_bowl(rng, f, dur=U(2.4, 3.2)), 'TONAL_PERC',
         'bowl', root_note=nm, tags=f'{f:.1f}Hz')
for nm, f in {'C4': 261.63, 'G4': 392.0}.items():
    emit(f'20_TONAL_PERC/tubular_bells/bells_{nm}.wav', E.tubular_bells(rng, f, dur=U(2.2, 3.0)), 'TONAL_PERC',
         'bells', root_note=nm, tags=f'{f:.1f}Hz')
for i in range(2):
    emit(f'20_TONAL_PERC/chimes/chimes_{i+1:02d}.wav', E.chimes(rng, base=U(1100, 1700), count=int(rng.integers(4, 8))),
         'TONAL_PERC', 'chimes')
for i in range(3):
    emit(f'20_TONAL_PERC/cymbal_swell/cymbal_swell_{i+1:02d}.wav', E.cymbal_swell(rng, dur=U(1.6, 2.6)),
         'TONAL_PERC', 'swell')
for i in range(2):
    emit(f'20_TONAL_PERC/gong_swell/gong_swell_{i+1:02d}.wav', E.gong(rng, U(40, 70), dur=U(2.6, 3.4), swell=U(0.8, 1.6)),
         'TONAL_PERC', 'gong_swell')

# ============================================================ LOG DRUM / ACID / WOBBLE
for style, kw in {'soft': dict(drive=1.2, tone=1800, bend=1.45), 'hard': dict(drive=2.6, tone=3200, bend=1.75)}.items():
    for m in range(24, 36):
        f = midi_to_freq(m)
        x = E.log_drum(rng, f, dur=U(0.6, 0.85), **kw)
        emit(f'13_BASS/log_drum_{style}/log_drum_{style}_{note_filename(m)}.wav', x, 'LOGDROM',
             style, root_note=note_filename(m), tags=f'{f:.1f}Hz;midi{m}')
for m in range(36, 48):
    f = midi_to_freq(m)
    emit(f'13_BASS/acid_303/acid_303_{note_filename(m)}.wav',
         E.acid(rng, f, dur=0.9, cutoff=U(900, 1800), env_amt=U(3000, 6000), res=U(4, 9), drive=U(1.8, 3.2)),
         'BASS', 'acid', root_note=note_filename(m), tags=f'{f:.1f}Hz;midi{m}')
for m in range(36, 48):
    f = midi_to_freq(m)
    emit(f'13_BASS/wobble/wobble_{note_filename(m)}.wav',
         E.wobble(rng, f, dur=1.0, bpm=140, rate=U(0.7, 1.5), depth=U(800, 2200), drive=U(1.6, 3.0)),
         'BASS', 'wobble', root_note=note_filename(m), tags=f'{f:.1f}Hz;midi{m}')

# ============================================================ MELODIC VOL.2
MEL2 = [
 ('accordion', 'keys', lambda f, d: E.accordion(rng, f, d), 1.5, [60, 63, 66, 69]),
 ('harmonica', 'world', lambda f, d: E.harmonica(rng, f, d), 1.4, [60, 63, 66, 69]),
 ('guzheng', 'world', lambda f, d: E.guzheng(rng, f, d), 1.6, [60, 63, 66, 69]),
 ('didgeridoo', 'world', lambda f, d: E.didgeridoo(rng, f, d), 1.6, [36, 39, 42, 45]),
]
for name, folder, fn, dur, notes in MEL2:
    for m in notes:
        x = fn(midi_to_freq(m), dur)[:int(dur * FS)]
        emit(f'14_MELODIC/{folder}/{name}/{name}_{note_filename(m)}.wav', x, 'MELODIC', name,
             root_note=note_filename(m), tags=f'{folder};midi{m}')
for i in range(2):
    emit(f'15_FX/air_horn/air_horn_{i+1:02d}.wav', E.air_horn(rng, dur=U(1.0, 1.8), f=U(180, 260)), 'FX', 'air_horn')

# ============================================================ VOX / SHOUTS
for i, v in enumerate(['e', 'a', 'o', 'e', 'a', 'o']):
    emit(f'14_MELODIC/vox/shout/shout_{v}_{i//3+1}.wav',
         E.shout(rng, freq=U(150, 230), dur=U(0.4, 0.7), vowel=v), 'MELODIC', 'shout',
         tags=f'vowel {v}')

# ============================================================ SCRATCHES / FX VOL.2
for i in range(4):
    emit(f'15_FX/scratches/scratch_{i+1:02d}.wav', E.scratch(rng, dur=U(0.2, 0.5), rev=U(0.6, 1.6)), 'FX', 'scratch')
for i in range(3):
    emit(f'15_FX/transitions/uplifter_{i+1:02d}.wav', dsp.stereo(E.cymbal_swell(rng, dur=U(1.2, 2.4)), 0.4),
         'FX', 'uplifter', stereo=True)
for i in range(2):
    emit(f'15_FX/glitch/glitch_{i+4:02d}.wav', E.shout(rng, freq=U(90, 140), dur=U(0.2, 0.4), vowel='o'), 'FX', 'glitch_vox')
for i in range(2):
    x = E.scratch(rng, dur=0.4, rev=2.0)
    x = dsp.delay(x, time_s=0.125, fb=0.5, mix=0.5, taps=3)
    emit(f'15_FX/scratches/scratch_delay_{i+1:02d}.wav', x, 'FX', 'scratch')
for i in range(2):
    emit(f'15_FX/impacts/timpani_hit_{i+1:02d}.wav', E.timpani(rng, U(45, 70), dur=1.8, mallet=0.8), 'FX', 'timpani_impact')

# ============================================================ FILLS / ROLLS
def render_fill(hits, bpm, tail=0.3):
    """hits: list of (time_in_beats, sample, gain)"""
    beat = 60.0 / bpm
    total = max(t * beat for t, _, _ in hits) + tail
    n = int(total * FS)
    out = np.zeros(n)
    for (bt, smp, g) in hits:
        i = int(bt * beat * FS)
        m = min(len(smp), n - i)
        if m > 0:
            out[i:i + m] += smp[:m] * g
    return dsp.fade(dsp.sat(out, 1.1, 'tanh'), 0.001, 0.04)

def snare_smp():  return D.snare(rng, tone=U(190, 230), decay=U(0.06, 0.12), bright=7000, drive=1.6)
def hat_smp():    return D.hat_closed(rng, decay=0.03, noise_amt=0.5, tone=12000)
def tom_smp(f):   return D.tom(rng, f0=f, decay=0.22, skin=0.3)
def clap_smp():   return D.clap(rng, decay=0.12, bursts=4)
def perc_smp():   return D.blip(rng, f0=U(700, 1400), f1=300, decay=0.05)

FILLS = []
# snare rolls
for bpm, steps, bars_name in [(120, 8, '1bar'), (120, 4, 'halfbar'), (140, 8, '1bar'), (90, 8, '1bar')]:
    hits = []
    for k in range(steps):
        hits.append((k * (4.0 / steps), snare_smp(), 0.4 + 0.6 * k / steps))
    FILLS.append((f'fill_snare_roll_{steps}th_{bars_name}_{bpm}bpm', render_fill(hits, bpm), bpm))
# 32nd rolls
for bpm in (120, 140):
    hits = [(k * 0.125, snare_smp(), 0.45 + 0.55 * k / 16) for k in range(16)]
    FILLS.append((f'fill_snare_roll_32nd_1bar_{bpm}bpm', render_fill(hits, bpm), bpm))
# hat roll
for bpm in (120, 140):
    hits = [(k * 0.25, hat_smp(), 0.35 + 0.5 * k / 16) for k in range(16)]
    FILLS.append((f'fill_hat_roll_16th_1bar_{bpm}bpm', render_fill(hits, bpm), bpm))
# tom fills
for bpm in (100, 120, 140):
    hits = []
    for k in range(8):
        f = [220, 200, 175, 155, 130, 115, 95, 85][k]
        hits.append((k * 0.5, tom_smp(f), 0.6 + 0.4 * k / 8))
    FILLS.append((f'fill_tom_desc_1bar_{bpm}bpm', render_fill(hits, bpm, tail=0.5), bpm))
# clap roll
for bpm in (120,):
    hits = [(k * 0.25, clap_smp(), 0.35 + 0.55 * k / 16) for k in range(16)]
    FILLS.append((f'fill_clap_roll_1bar_{bpm}bpm', render_fill(hits, bpm), bpm))
# perc fill
for bpm in (120, 140):
    hits = [(k * 0.25, perc_smp(), U(0.3, 0.9)) for k in range(16)]
    FILLS.append((f'fill_perc_1bar_{bpm}bpm', render_fill(hits, bpm), bpm))
# mixed fill (kick+snare+tom)
for bpm in (120, 140):
    hits = []
    for k in range(16):
        t = k * 0.25
        if k % 4 == 0:
            hits.append((t, D.kick(rng, f_start=U(120, 170), decay=0.25), 0.9))
        elif k % 2 == 0:
            hits.append((t, snare_smp(), 0.5 + 0.4 * k / 16))
        else:
            hits.append((t, tom_smp(U(100, 220)), 0.4 + 0.4 * k / 16))
    FILLS.append((f'fill_mixed_1bar_{bpm}bpm', render_fill(hits, bpm, tail=0.4), bpm))
# riser + roll
for bpm in (140,):
    hits = [(k * 0.25, snare_smp(), 0.4 + 0.6 * k / 16) for k in range(16)]
    roll = render_fill(hits, bpm)
    from kitlib import fx as X
    ris = X.riser(rng, dur=len(roll) / FS, lo=300, hi=9000)
    m = min(len(ris), len(roll))
    FILLS.append((f'fill_riser_roll_1bar_{bpm}bpm', roll[:m] * 0.8 + ris[:m] * 0.5, bpm))

for name, x, bpm in FILLS:
    emit(f'19_FILLS_ROLLS/{name}.wav', x, 'FILL', 'fill', bpm=str(bpm), tags=f'reference {bpm}bpm')

# ============================================================ LOOPS VOL.2
MIDI_DIR = os.path.join(OUT, '17_MIDI/drum_patterns')
os.makedirs(MIDI_DIR, exist_ok=True)
GM = dict(kick=36, snare=38, clap=39, rim=37, hat=42, ohat=46, crash=49, ride=51, perc=69, log=43)

amapiano_kit = {
    'kick': lambda r: D.kick(r, f_start=U(110, 140), f_end=U(44, 50), decay=0.4, drive=1.5, tone=7000, click=0.12),
    'log': lambda r: E.log_drum(r, midi_to_freq(int(r.integers(33, 45))), dur=0.7, drive=1.6),
    'shaker': lambda r: D.shaker(r, decay=0.07, lo=3000, hi=11000),
    'clap': lambda r: D.clap(r, decay=0.22, bursts=5, room=0.45),
    'ohat': lambda r: D.hat_open(r, decay=0.3, noise_amt=0.5, tone=10000),
    'crash': lambda r: D.crash(r, decay=1.1),
}
ukg_kit = {
    'kick': lambda r: D.kick(r, f_start=U(150, 190), f_end=U(52, 60), decay=0.2, drive=2.2, tone=11000, click=0.45),
    'snare': lambda r: D.snare(r, tone=U(210, 250), decay=0.12, bright=8000, drive=2.0),
    'clap': lambda r: D.clap(r, decay=0.12, bursts=4, hi=5000),
    'hat': lambda r: D.hat_closed(r, decay=0.025, noise_amt=0.6, tone=14000),
    'ohat': lambda r: D.hat_open(r, decay=0.22, noise_amt=0.5, tone=12000),
    'perc': lambda r: D.blip(r, f0=U(900, 1600), f1=400, decay=0.06),
}
break_kit = {
    'kick': lambda r: D.kick(r, f_start=U(160, 200), f_end=U(48, 58), decay=0.2, drive=2.4, tone=10000, click=0.5),
    'snare': lambda r: D.snare(r, tone=U(200, 250), decay=0.18, bright=10000, drive=2.4, rattle=0.4),
    'hat': lambda r: D.hat_closed(r, decay=0.03, noise_amt=0.55, tone=13000),
    'ohat': lambda r: D.hat_open(r, decay=0.25, noise_amt=0.5, tone=12000),
    'crash': lambda r: D.crash(r, decay=1.3),
}
LOOPS2 = [
    ('amapiano', 112, amapiano_kit, {
        'kick': [(0, 1.0), (6, 0.9), (10, 0.85), (16, 1.0), (22, 0.9), (26, 0.85)],
        'log': [(4, 0.7), (7, 0.5), (12, 0.65), (14, 0.45), (20, 0.7), (23, 0.5), (28, 0.65), (30, 0.45)],
        'shaker': S.hat_16(2, 0.35, accents=(2, 6, 10, 14)),
        'clap': [(8, 0.6), (24, 0.6)],
        'ohat': [(6, 0.3), (22, 0.3)],
        'crash': [(0, 0.45)],
    }, 0.1),
    ('ukg', 132, ukg_kit, {
        'kick': [(0, 1.0), (6, 0.85), (10, 0.9), (16, 1.0), (22, 0.85), (26, 0.9)],
        'snare': [(4, 0.9), (12, 0.9), (20, 0.9), (28, 0.9)],
        'clap': [(12, 0.6), (28, 0.6)],
        'hat': S.hat_16(2, 0.35, accents=(0, 8)) + [(15, 0.25), (31, 0.25)],
        'ohat': [(2, 0.3), (18, 0.3)],
        'perc': [(7, 0.35), (23, 0.35)],
    }, 0.0),
    ('breakbeat', 165, break_kit, {
        'kick': [(0, 1.0), (3, 0.8), (10, 0.9), (16, 1.0), (19, 0.8), (26, 0.9)],
        'snare': [(4, 1.0), (12, 0.95), (20, 1.0), (28, 0.95), (15, 0.3), (31, 0.3)],
        'hat': S.hat_16(2, 0.3, accents=(0, 8)),
        'ohat': [(6, 0.3), (22, 0.3)],
        'crash': [(0, 0.5)],
    }, 0.0),
]
for name, bpm, kit, pat, swing in LOOPS2:
    x = S.render_loop(bpm, 2, kit, pat, swing=swing, rng=rng)
    emit(f'16_LOOPS/drum_loops/{name}_{bpm}bpm.wav', x, 'LOOP', f'{name}_{bpm}bpm', bpm=str(bpm),
         tags=f'{name}, 2 bars')
    notes = []
    for voice, hits in pat.items():
        for (step, vel) in hits:
            notes.append((step / 4.0, 0.2, GM.get(voice, 39), int(np.clip(vel * 110 + 12, 20, 127))))
    MIDIW.write_midi(os.path.join(MIDI_DIR, f'{name}_{bpm}bpm_drums.mid'),
                     [{'name': name, 'channel': 10, 'notes': notes}], bpm=bpm)

# extra genre MIDI patterns (no audio, tiny)
EXTRA_MIDI = {
 'dubstep_140': [(0, 36), (0, 30), (12, 36), (8, 38), (8, 4), (11, 46)],
 'footwork_160': [(0, 36), (6, 36), (8, 38), (12, 36), (14, 38)],
 'citypop_104': [(0, 36), (6, 38), (8, 36), (14, 38)],
 'amapiano_112': [(0, 36), (6, 36), (10, 36), (8, 39)],
}
for name, hits in EXTRA_MIDI.items():
    bpm = int(name.split('_')[1])
    notes = [(s / 4.0, 0.2, 36, 100) for s, _ in hits]
    pattern = []
    for s, p in hits:
        pattern.append((s / 4.0, 0.2, p, 110))
    MIDIW.write_midi(os.path.join(MIDI_DIR, f'{name}_skeleton.mid'),
                     [{'name': name, 'channel': 10, 'notes': pattern}], bpm=bpm)
print('vol2 done')
