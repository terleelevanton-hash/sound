import sys, numpy as np
sys.path.insert(0, 'work')
from kitlib import drums as D, dsp
from kitlib.io import emit, set_root
from kitlib.dsp import midi_to_freq, note_filename

OUT = sys.argv[1] if len(sys.argv) > 1 else 'build/kit'
set_root(OUT)
rng = np.random.default_rng(20261122)
U = lambda a, b: float(rng.uniform(a, b))
INT_KEYS = {'bursts', 'grains', 'bits', 'downsample', 'voices', 'layers', 'taps'}


def fixint(kw):
    for k in INT_KEYS:
        if k in kw and kw[k] is not None:
            kw[k] = int(kw[k])
    return kw

# ============================================================ KICKS
KICKS = {
 'trap':      dict(f_start=(125, 190), f_end=(43, 56), pitch_tau=(0.018, 0.045), decay=(0.24, 0.44),
                   click=(0.15, 0.45), drive=(1.2, 2.2), tone=(7500, 12000), sub=(0.2, 0.45), punch=(0.12, 0.3), beater=(0, 0.15)),
 'drill':     dict(f_start=(150, 220), f_end=(40, 50), pitch_tau=(0.014, 0.03), decay=(0.3, 0.5),
                   click=(0.25, 0.5), drive=(2.0, 3.4), tone=(8500, 13000), sub=(0.25, 0.5), punch=(0.15, 0.35), beater=(0, 0.1)),
 'phonk':     dict(f_start=(110, 175), f_end=(38, 52), pitch_tau=(0.015, 0.035), decay=(0.18, 0.34),
                   click=(0.2, 0.5), drive=(2.8, 5.5), tone=(2800, 6500), sub=(0.3, 0.6), punch=(0.1, 0.3), beater=(0, 0.12)),
 'boombap':   dict(f_start=(85, 125), f_end=(52, 72), pitch_tau=(0.02, 0.05), decay=(0.3, 0.55),
                   click=(0.2, 0.42), drive=(1.1, 1.8), tone=(4500, 8500), sub=(0.25, 0.5), punch=(0.1, 0.28), beater=(0.05, 0.3)),
 'lofi':      dict(f_start=(80, 130), f_end=(50, 68), pitch_tau=(0.02, 0.05), decay=(0.32, 0.6),
                   click=(0.1, 0.3), drive=(1.4, 2.4), tone=(2200, 4500), sub=(0.25, 0.45), punch=(0.05, 0.18), beater=(0.05, 0.25)),
 'house':     dict(f_start=(110, 160), f_end=(48, 58), pitch_tau=(0.015, 0.035), decay=(0.25, 0.4),
                   click=(0.25, 0.55), drive=(1.3, 2.2), tone=(9000, 14000), sub=(0.2, 0.4), punch=(0.2, 0.4), beater=(0.1, 0.3)),
 'techno':    dict(f_start=(140, 200), f_end=(44, 54), pitch_tau=(0.01, 0.025), decay=(0.18, 0.32),
                   click=(0.3, 0.6), drive=(2.2, 4.0), tone=(5500, 9000), sub=(0.2, 0.4), punch=(0.25, 0.5), beater=(0, 0.1)),
 'dnb':       dict(f_start=(160, 230), f_end=(46, 58), pitch_tau=(0.008, 0.02), decay=(0.14, 0.26),
                   click=(0.35, 0.6), drive=(1.6, 2.8), tone=(7000, 12000), sub=(0.2, 0.4), punch=(0.2, 0.4), beater=(0, 0.12)),
 'rock':      dict(f_start=(90, 130), f_end=(55, 75), pitch_tau=(0.015, 0.04), decay=(0.22, 0.4),
                   click=(0.15, 0.35), drive=(1.2, 2.0), tone=(4500, 8000), sub=(0.15, 0.35), punch=(0.1, 0.25), beater=(0.2, 0.5)),
 'jersey':    dict(f_start=(160, 240), f_end=(50, 62), pitch_tau=(0.01, 0.025), decay=(0.12, 0.22),
                   click=(0.4, 0.65), drive=(2.0, 3.5), tone=(9000, 15000), sub=(0.15, 0.35), punch=(0.25, 0.45), beater=(0, 0.1)),
 'hyperpop':  dict(f_start=(180, 280), f_end=(50, 70), pitch_tau=(0.005, 0.02), decay=(0.1, 0.2),
                   click=(0.45, 0.7), drive=(3.0, 6.0), tone=(8000, 16000), sub=(0.1, 0.3), punch=(0.3, 0.5), beater=(0, 0.15)),
 'reggaeton': dict(f_start=(100, 150), f_end=(42, 55), pitch_tau=(0.015, 0.04), decay=(0.28, 0.45),
                   click=(0.15, 0.35), drive=(1.6, 2.6), tone=(8000, 12000), sub=(0.3, 0.55), punch=(0.1, 0.3), beater=(0, 0.1)),
 'hardstyle': dict(f_start=(240, 340), f_end=(48, 60), pitch_tau=(0.03, 0.06), decay=(0.3, 0.5),
                   click=(0.3, 0.5), drive=(4.5, 7.5), tone=(6000, 11000), sub=(0.3, 0.5), punch=(0.3, 0.5), beater=(0, 0.1)),
 'funk':      dict(f_start=(95, 140), f_end=(58, 78), pitch_tau=(0.012, 0.03), decay=(0.18, 0.32),
                   click=(0.2, 0.4), drive=(1.1, 1.7), tone=(4000, 7500), sub=(0.2, 0.4), punch=(0.15, 0.3), beater=(0.25, 0.55)),
 '808':       dict(f_start=(80, 140), f_end=(33, 45), pitch_tau=(0.02, 0.06), decay=(0.6, 1.0),
                   click=(0.05, 0.25), drive=(1.3, 2.4), tone=(2000, 6000), sub=(0.35, 0.6), punch=(0.0, 0.12), beater=(0, 0.05)),
}
for style, p in KICKS.items():
    count = 8 if style in ('trap', 'phonk', 'drill', 'boombap') else 5
    for i in range(count):
        kw = fixint({k: U(*v) for k, v in p.items()})
        x = D.kick(rng, **kw)
        if style in ('lofi', 'phonk'):
            x = dsp.bitcrush(x, bits=int(U(10, 13)), downsample=1)
            x = dsp.reverb(x, wet=0.08, decay=0.25, tone=3000, rng=rng)
        if style == 'rock':
            x = dsp.reverb(x, wet=0.12, decay=0.4, tone=4500, rng=rng)
        emit(f'01_KICKS/{style}/kick_{style}_{i+1:02d}.wav', x, 'KICK', style,
             tags=f'f_start={kw["f_start"]:.0f};f_end={kw["f_end"]:.0f}')

# ============================================================ SNARES
SNARES = {
 'trap':     dict(tone=(180, 240), decay=(0.1, 0.2), bright=(5000, 9000), drive=(1.2, 2.0), noise_amt=(0.9, 1.3), clap_layer=(0, 0.25)),
 'drill':    dict(tone=(160, 220), decay=(0.12, 0.22), bright=(6000, 11000), drive=(1.8, 3.0), noise_amt=(1.0, 1.4), clap_layer=(0.1, 0.35)),
 'phonk':    dict(tone=(150, 210), decay=(0.06, 0.14), bright=(3000, 6500), drive=(2.2, 4.5), noise_amt=(0.8, 1.2), clap_layer=(0, 0.2)),
 'boombap':  dict(tone=(190, 260), decay=(0.15, 0.28), bright=(3500, 7000), drive=(1.1, 1.7), noise_amt=(0.9, 1.3), clap_layer=(0, 0.2)),
 'lofi':     dict(tone=(170, 230), decay=(0.12, 0.22), bright=(2200, 4500), drive=(1.3, 2.0), noise_amt=(0.8, 1.1), pink=(0.2, 0.5)),
 'acoustic': dict(tone=(180, 250), decay=(0.18, 0.32), bright=(4500, 8000), drive=(1.0, 1.3), noise_amt=(1.1, 1.5), rattle=(0.3, 0.7)),
 'rim':      dict(tone=(240, 380), decay=(0.04, 0.09), bright=(3000, 7000), drive=(1.2, 2.0), noise_amt=(0.5, 0.9), second=(1.4, 2.2)),
 'dnb':      dict(tone=(200, 280), decay=(0.14, 0.26), bright=(6500, 12000), drive=(1.5, 2.5), noise_amt=(1.0, 1.5), rattle=(0.2, 0.5)),
 'rock':     dict(tone=(160, 220), decay=(0.2, 0.36), bright=(4000, 7500), drive=(1.3, 1.9), noise_amt=(1.1, 1.5), rattle=(0.4, 0.8)),
 'vinyl':    dict(tone=(170, 240), decay=(0.1, 0.2), bright=(1800, 3800), drive=(1.4, 2.2), noise_amt=(0.9, 1.2), pink=(0.3, 0.6)),
 'wide':     dict(tone=(190, 250), decay=(0.16, 0.3), bright=(5000, 9000), drive=(1.2, 1.8), noise_amt=(1.0, 1.4), clap_layer=(0.2, 0.45)),
}
for style, p in SNARES.items():
    count = 7 if style in ('trap', 'drill') else 5
    for i in range(count):
        kw = fixint({k: U(*v) for k, v in p.items()})
        if kw.get('second') is None:
            kw['second'] = U(1.5, 1.75)
        x = D.snare(rng, **kw)
        if style in ('lofi', 'vinyl'):
            x = dsp.bitcrush(x, bits=int(U(10, 13)))
            x = dsp.reverb(x, wet=0.15, decay=0.3, tone=3500, rng=rng)
        if style == 'rock':
            x = dsp.reverb(x, wet=0.2, decay=0.5, tone=5000, rng=rng)
        if style == 'phonk':
            x = dsp.reverb(x, wet=0.1, decay=0.2, tone=4000, rng=rng)
        emit(f'02_SNARES/{style}/snare_{style}_{i+1:02d}.wav', x, 'SNARE', style,
             tags=f'tone={kw["tone"]:.0f}Hz')

# ============================================================ CLAPS
CLAPS = {
 'trap':    dict(decay=(0.12, 0.2), spacing=(0.009, 0.014), bursts=(3, 5), lo=(800, 1200), hi=(2800, 4500), room=(0.15, 0.3)),
 'drill':   dict(decay=(0.1, 0.18), spacing=(0.008, 0.012), bursts=(3, 5), lo=(900, 1400), hi=(3200, 5200), room=(0.1, 0.25)),
 'phonk':   dict(decay=(0.08, 0.15), spacing=(0.007, 0.011), bursts=(3, 4), lo=(700, 1100), hi=(2000, 3400), room=(0.05, 0.2), drive=(1.4, 2.6)),
 'boombap': dict(decay=(0.16, 0.26), spacing=(0.011, 0.017), bursts=(4, 6), lo=(700, 1000), hi=(2200, 3600), room=(0.25, 0.45)),
 'wide':    dict(decay=(0.14, 0.24), spacing=(0.01, 0.016), bursts=(4, 6), lo=(600, 900), hi=(4000, 6500), room=(0.3, 0.5)),
 'lofi':    dict(decay=(0.12, 0.2), spacing=(0.012, 0.018), bursts=(3, 5), lo=(600, 900), hi=(1600, 3000), room=(0.2, 0.4), tail_lp=(3000, 5000)),
 'snap':    dict(decay=(0.05, 0.1), spacing=(0.005, 0.009), bursts=(2, 3), lo=(1500, 2500), hi=(5000, 9000), room=(0.1, 0.3)),
 'house':   dict(decay=(0.1, 0.18), spacing=(0.008, 0.013), bursts=(3, 5), lo=(900, 1300), hi=(3000, 5000), room=(0.15, 0.35)),
}
for style, p in CLAPS.items():
    count = 8 if style in ('trap', 'phonk') else 5
    for i in range(count):
        kw = fixint({k: U(*v) for k, v in p.items()})
        kw.setdefault('drive', U(1.1, 1.8))
        x = D.clap(rng, **kw)
        if style == 'lofi':
            x = dsp.bitcrush(x, bits=int(U(10, 13)))
        emit(f'03_CLAPS/{style}/clap_{style}_{i+1:02d}.wav', x, 'CLAP', style)

# ============================================================ SNAPS / RIM / STICK
for i in range(12):
    x = D.snap(rng, decay=U(0.04, 0.11), lo=U(1200, 2200), hi=U(5000, 9000), layers=int(rng.integers(2, 5)))
    emit(f'04_SNAPS_RIMS_STICKS/snap/snap_{i+1:02d}.wav', x, 'SNAP', 'snap')
for i in range(10):
    x = D.rim(rng, tone=U(620, 1100), decay=U(0.03, 0.07), click=U(0.4, 0.9))
    emit(f'04_SNAPS_RIMS_STICKS/rim/rim_{i+1:02d}.wav', x, 'RIM', 'rim')
for i in range(8):
    x = D.stick(rng, tone=U(900, 1800), decay=U(0.02, 0.045))
    emit(f'04_SNAPS_RIMS_STICKS/stick/stick_{i+1:02d}.wav', x, 'STICK', 'stick')

# ============================================================ HATS
HAT_CLOSED = {
 'tight':   dict(decay=(0.015, 0.03), noise_amt=(0.3, 0.6), metal=(0.7, 1.2), tone=(9000, 15000)),
 'trap':    dict(decay=(0.03, 0.06), noise_amt=(0.4, 0.7), metal=(0.8, 1.3), tone=(10000, 16000)),
 'phonk':   dict(decay=(0.02, 0.05), noise_amt=(0.5, 0.9), metal=(0.6, 1.1), tone=(7000, 12000), digital=(0.2, 0.6)),
 'digital': dict(decay=(0.02, 0.05), noise_amt=(0.6, 1.0), metal=(0.3, 0.8), tone=(11000, 17000), digital=(0.5, 0.9)),
 'analog':  dict(decay=(0.03, 0.07), noise_amt=(0.2, 0.5), metal=(1.0, 1.5), tone=(8000, 13000)),
 'lofi':    dict(decay=(0.03, 0.06), noise_amt=(0.5, 0.9), metal=(0.5, 1.0), tone=(5000, 9000), digital=(0.3, 0.7)),
 'dnb':     dict(decay=(0.02, 0.045), noise_amt=(0.5, 0.8), metal=(0.8, 1.2), tone=(9000, 15000)),
 'house':   dict(decay=(0.025, 0.055), noise_amt=(0.4, 0.7), metal=(0.7, 1.1), tone=(9000, 14000)),
 'bright':  dict(decay=(0.02, 0.04), noise_amt=(0.6, 0.9), metal=(0.6, 1.0), tone=(14000, 18000)),
}
for style, p in HAT_CLOSED.items():
    for i in range(7):
        kw = fixint({k: U(*v) for k, v in p.items()})
        kw.setdefault('digital', 0.0)
        if kw.get('digital') is None:
            kw['digital'] = 0.0
        x = D.hat_closed(rng, **kw)
        emit(f'05_HATS_CLOSED/{style}/hat_{style}_{i+1:02d}.wav', x, 'HAT_CLOSED', style)

HAT_OPEN = {
 'trap':    dict(decay=(0.25, 0.45), metal=(0.9, 1.3), noise_amt=(0.3, 0.6), tone=(10000, 16000)),
 'phonk':   dict(decay=(0.18, 0.35), metal=(0.7, 1.1), noise_amt=(0.5, 0.9), tone=(7000, 12000)),
 'analog':  dict(decay=(0.3, 0.55), metal=(1.1, 1.6), noise_amt=(0.2, 0.4), tone=(8000, 13000)),
 'lofi':    dict(decay=(0.25, 0.5), metal=(0.6, 1.0), noise_amt=(0.5, 0.9), tone=(5000, 9000)),
 'house':   dict(decay=(0.3, 0.6), metal=(0.8, 1.2), noise_amt=(0.4, 0.7), tone=(9000, 14000)),
 'dnb':     dict(decay=(0.2, 0.4), metal=(0.9, 1.3), noise_amt=(0.4, 0.7), tone=(10000, 15000)),
 'ridey':   dict(decay=(0.6, 1.0), metal=(1.2, 1.8), noise_amt=(0.2, 0.5), tone=(8000, 12000)),
 'bright':  dict(decay=(0.2, 0.4), metal=(0.7, 1.1), noise_amt=(0.6, 0.9), tone=(13000, 17000)),
}
for style, p in HAT_OPEN.items():
    for i in range(5):
        kw = fixint({k: U(*v) for k, v in p.items()})
        x = D.hat_open(rng, **kw)
        emit(f'06_HATS_OPEN/{style}/openhat_{style}_{i+1:02d}.wav', x, 'HAT_OPEN', style)

# ============================================================ CYMBALS
for i in range(14):
    x = D.crash(rng, decay=U(1.0, 2.6), base=U(140, 260), noise_amt=U(0.7, 1.2), metal=U(0.5, 1.0),
                hp_f=U(2500, 5000), shimmer=U(0.05, 0.25))
    emit(f'07_CYMBALS/crash/crash_{i+1:02d}.wav', x, 'CRASH', 'crash', tags=f'{U(1,2.6):.1f}s decay')
for i in range(10):
    x = D.ride(rng, decay=U(0.6, 1.4), base=U(240, 400), bell=U(0.15, 0.5))
    emit(f'07_CYMBALS/ride/ride_{i+1:02d}.wav', x, 'RIDE', 'ride')
for i in range(6):
    x = D.china(rng, decay=U(0.9, 1.8))
    emit(f'07_CYMBALS/china/china_{i+1:02d}.wav', x, 'CHINA', 'china')
for i in range(6):
    x = D.splash(rng, decay=U(0.35, 0.7))
    emit(f'07_CYMBALS/splash/splash_{i+1:02d}.wav', x, 'SPLASH', 'splash')

# ============================================================ TOMS
TOM_KITS = {
 'acoustic_high': (220, 0.28, 0.45), 'acoustic_mid': (155, 0.34, 0.5), 'acoustic_floor': (95, 0.42, 0.55),
 'trap_high': (240, 0.2, 0.3), 'trap_mid': (170, 0.26, 0.35), 'trap_floor': (105, 0.34, 0.4),
 'lofi_high': (200, 0.24, 0.35), 'lofi_mid': (140, 0.3, 0.4), 'lofi_floor': (88, 0.4, 0.45),
 '808_high': (260, 0.35, 0.2), '808_mid': (180, 0.45, 0.2), '808_floor': (110, 0.6, 0.2),
}
for name, (f0, dec, skin) in TOM_KITS.items():
    style = name.split('_')[0]
    for i in range(2):
        x = D.tom(rng, f0=f0 * U(0.94, 1.06), decay=dec * U(0.9, 1.1), skin=skin * U(0.8, 1.2), drop=U(1.3, 1.8))
        if style == 'lofi':
            x = dsp.bitcrush(x, bits=11)
        emit(f'08_TOMS/{style}/{name}_{i+1}.wav', x, 'TOM', style, tags=f'{f0:.0f}Hz')

# ============================================================ PERC ACOUSTIC
for i in range(8):
    x = D.shaker(rng, decay=U(0.04, 0.1), lo=U(3500, 5500), hi=U(10000, 14000), grains=int(rng.integers(1, 4)))
    emit(f'09_PERC_ACOUSTIC/shaker/shaker_{i+1:02d}.wav', x, 'PERC', 'shaker')
for i in range(5):
    x = D.tambourine(rng, decay=U(0.2, 0.5))
    emit(f'09_PERC_ACOUSTIC/tambourine/tambourine_{i+1:02d}.wav', x, 'PERC', 'tambourine')
for i in range(4):
    x = D.cabasa(rng, decay=U(0.08, 0.2), grains=int(rng.integers(8, 18)))
    emit(f'09_PERC_ACOUSTIC/cabasa/cabasa_{i+1:02d}.wav', x, 'PERC', 'cabasa')
for i in range(3):
    x = D.guiro(rng, decay=U(0.15, 0.3), grains=int(rng.integers(6, 12)))
    emit(f'09_PERC_ACOUSTIC/guiro/guiro_{i+1:02d}.wav', x, 'PERC', 'guiro')
for i in range(5):
    x = D.cowbell(rng, f1=U(480, 640), f2=U(760, 900), decay=U(0.15, 0.4))
    emit(f'09_PERC_ACOUSTIC/cowbell/cowbell_{i+1:02d}.wav', x, 'PERC', 'cowbell')
for i in range(4):
    x = D.clave(rng, tone=U(2000, 3000), decay=U(0.03, 0.07))
    emit(f'09_PERC_ACOUSTIC/clave/clave_{i+1:02d}.wav', x, 'PERC', 'clave')
for i in range(4):
    x = D.woodblock(rng, tone=U(800, 1300), decay=U(0.03, 0.07))
    emit(f'09_PERC_ACOUSTIC/woodblock/woodblock_{i+1:02d}.wav', x, 'PERC', 'woodblock')
for i in range(4):
    x = D.triangle_ring(rng, tone=U(2800, 4200), decay=U(0.5, 1.2))
    emit(f'09_PERC_ACOUSTIC/triangle/triangle_{i+1:02d}.wav', x, 'PERC', 'triangle')
for name, (f0, dec) in {'conga_high': (260, 0.22), 'conga_mid': (200, 0.28), 'conga_low': (150, 0.34),
                        'bongo_high': (330, 0.18), 'bongo_low': (250, 0.22), 'djembe': (105, 0.26),
                        'tabla': (285, 0.2), 'tabla_bass': (150, 0.4), 'frame_drum': (95, 0.32),
                        'cajon': (85, 0.16)}.items():
    for i in range(2):
        fn = D.conga if 'conga' in name or 'bongo' in name else (
            D.djembe if 'djembe' in name else (D.tabla if 'tabla' in name else (
                D.frame_drum if 'frame' in name else D.cajon)))
        x = fn(rng, f0=f0 * U(0.95, 1.05), decay=dec * U(0.9, 1.15))
        emit(f'09_PERC_ACOUSTIC/{name.split("_")[0]}/{name}_{i+1}.wav', x, 'PERC', name.split('_')[0])
for i in range(5):
    x = D.anvil(rng, base=U(380, 700), decay=U(0.4, 1.2))
    emit(f'09_PERC_ACOUSTIC/anvil/anvil_{i+1:02d}.wav', x, 'PERC', 'anvil')
for i in range(4):
    x = D.glass(rng, base=U(1600, 3000), decay=U(0.3, 0.8))
    emit(f'09_PERC_ACOUSTIC/glass/glass_{i+1:02d}.wav', x, 'PERC', 'glass')
for i in range(3):
    x = D.bottle(rng, base=U(700, 1100), decay=U(0.15, 0.35))
    emit(f'09_PERC_ACOUSTIC/bottle/bottle_{i+1:02d}.wav', x, 'PERC', 'bottle')
for i in range(4):
    x = D.coins(rng, decay=U(0.2, 0.45))
    emit(f'09_PERC_ACOUSTIC/coins/coins_{i+1:02d}.wav', x, 'PERC', 'coins')
for i in range(3):
    x = D.vibraslap(rng, decay=U(0.25, 0.45))
    emit(f'09_PERC_ACOUSTIC/vibraslap/vibraslap_{i+1:02d}.wav', x, 'PERC', 'vibraslap')

# ============================================================ PERC ELECTRONIC
for i in range(10):
    x = D.blip(rng, f0=U(600, 2200), f1=U(150, 600), decay=U(0.03, 0.12))
    emit(f'10_PERC_ELECTRONIC/blip/blip_{i+1:02d}.wav', x, 'PERC_EL', 'blip')
for i in range(8):
    x = D.laser(rng, f0=U(3000, 8000), f1=U(150, 500), decay=U(0.08, 0.25))
    emit(f'10_PERC_ELECTRONIC/laser/laser_{i+1:02d}.wav', x, 'PERC_EL', 'laser')
for i in range(8):
    x = D.glitch_perc(rng, decay=U(0.05, 0.18), bits=int(rng.integers(4, 9)))
    emit(f'10_PERC_ELECTRONIC/glitch/glitch_perc_{i+1:02d}.wav', x, 'PERC_EL', 'glitch')
for i in range(8):
    x = D.metal_stab(rng, base=U(300, 700), decay=U(0.15, 0.5))
    emit(f'10_PERC_ELECTRONIC/metal_stab/metal_stab_{i+1:02d}.wav', x, 'PERC_EL', 'metal')
for i in range(6):
    x = D.hat_closed(rng, decay=U(0.01, 0.03), tone=U(14000, 18000), digital=U(0.4, 0.9), noise_amt=U(0.5, 0.9))
    x = dsp.delay(x, time_s=0.0625, fb=0.4, mix=0.4, taps=2)
    emit(f'10_PERC_ELECTRONIC/tick_delay/tick_delay_{i+1:02d}.wav', x, 'PERC_EL', 'tick')

# ============================================================ STOMPS / BODY
for i in range(8):
    x = D.stomp(rng, decay=U(0.07, 0.2), f0=U(50, 90), thud=U(0.5, 1.0), room=U(0.1, 0.35))
    emit(f'11_STOMPS_BODY/stomp/stomp_{i+1:02d}.wav', x, 'STOMP', 'stomp')
for i in range(6):
    x = D.kick(rng, f_start=U(90, 140), f_end=U(45, 65), decay=U(0.1, 0.2), click=U(0.4, 0.7),
               drive=U(2.0, 4.0), tone=U(3000, 7000), sub=U(0.1, 0.3), punch=U(0.2, 0.4), beater=U(0.2, 0.5))
    emit(f'11_STOMPS_BODY/body_hit/body_hit_{i+1:02d}.wav', x, 'BODY', 'body')
for i in range(6):
    x = D.clap(rng, decay=U(0.2, 0.4), spacing=U(0.014, 0.022), bursts=int(rng.integers(5, 9)), room=U(0.3, 0.6))
    emit(f'11_STOMPS_BODY/group_clap/group_clap_{i+1:02d}.wav', x, 'BODY', 'group_clap')

print('drums done')
