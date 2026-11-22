#!/usr/bin/env python3
"""
Master builder for MEGA_KIT_EXPANSION_v3 — Universal All-Genres Studio Kit.
Usage:
    python3 build_all_v3.py <output_dir>
"""
import os
import sys
import time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from kitlib_v3 import dsp
from kitlib_v3 import io as kio
from kitlib_v3 import drums_v3 as D3
from kitlib_v3 import bass_v3 as B3
from kitlib_v3 import melodic_v3 as M3
from kitlib_v3 import fx_loops_v3 as F3
from kitlib_v3.midi_sfz import write_midi, write_melodic_sfz, write_drum_kit_sfz_and_txt
from kitlib_v3.dsp import FS, midi_to_freq, note_filename, fade, normalize, stereo_reverb


def build_drums_and_perc(rng):
    U = lambda a, b: float(rng.uniform(a, b))
    print('[1/7] Synthesizing missing genre drums, jazz brushes, Simmons toms & 24 chromatic 808 cowbells...')

    KICK_STYLES = {
        'baile_funk': dict(f_start=(145, 195), f_end=(42, 50), pitch_tau=(0.016, 0.032), decay=(0.34, 0.52),
                           click=(0.25, 0.45), drive=(2.4, 3.8), tone=(4500, 7500), sub=(0.45, 0.70), punch=(0.25, 0.45)),
        'postpunk':   dict(f_start=(125, 160), f_end=(52, 62), pitch_tau=(0.014, 0.024), decay=(0.18, 0.28),
                           click=(0.28, 0.48), drive=(1.4, 2.0), tone=(5500, 8500), sub=(0.20, 0.35), punch=(0.20, 0.35)),
        'jazz':       dict(f_start=(88, 112), f_end=(56, 68), pitch_tau=(0.015, 0.030), decay=(0.24, 0.38),
                           click=(0.08, 0.18), drive=(1.05, 1.3), tone=(2800, 4600), sub=(0.15, 0.28), punch=(0.05, 0.15)),
        'disco':      dict(f_start=(115, 150), f_end=(50, 58), pitch_tau=(0.018, 0.030), decay=(0.22, 0.32),
                           click=(0.22, 0.38), drive=(1.35, 1.9), tone=(5200, 8200), sub=(0.25, 0.42), punch=(0.18, 0.32)),
        'rnb_neosoul': dict(f_start=(92, 122), f_end=(42, 50), pitch_tau=(0.020, 0.036), decay=(0.28, 0.42),
                            click=(0.06, 0.16), drive=(1.2, 1.65), tone=(2600, 4800), sub=(0.35, 0.55), punch=(0.08, 0.18)),
        'modern_pop': dict(f_start=(140, 185), f_end=(45, 54), pitch_tau=(0.012, 0.022), decay=(0.20, 0.30),
                           click=(0.30, 0.50), drive=(1.6, 2.3), tone=(7500, 11500), sub=(0.30, 0.48), punch=(0.22, 0.38)),
    }
    for style, params in KICK_STYLES.items():
        for i in range(5):
            kw = {k: U(*v) for k, v in params.items()}
            kio.emit(f'01_KICKS/{style}/kick_{style}_{i+1:02d}.wav', D3.synth_kick(rng, **kw), 'KICK', style)

    for i in range(5):
        kio.emit(f'01_KICKS/psytrance/kick_psytrance_{i+1:02d}.wav',
                 D3.psytrance_kick(rng, f_end=U(44, 52), dur=U(0.22, 0.28)), 'KICK', 'psytrance')
    for i in range(5):
        kio.emit(f'01_KICKS/gabber_hardcore/kick_gabber_{i+1:02d}.wav',
                 D3.gabber_kick(rng, f_base=U(46, 58), dur=U(0.45, 0.62), drive=U(5.0, 8.0)), 'KICK', 'gabber_hardcore')

    SNARE_STYLES = {
        'house':            dict(f1=(195, 225), f2=(310, 355), decay=(0.14, 0.22), noise_decay=(0.16, 0.25), noise_amt=(1.0, 1.35), bright=(7500, 11500), drive=(1.35, 1.85), rim_amt=(0.15, 0.30)),
        'disco_funk':       dict(f1=(185, 215), f2=(295, 340), decay=(0.16, 0.24), noise_decay=(0.18, 0.28), noise_amt=(1.1, 1.45), bright=(6800, 10500), drive=(1.45, 2.0), rim_amt=(0.25, 0.45)),
        'baile_funk':       dict(f1=(245, 310), f2=(390, 480), decay=(0.10, 0.18), noise_decay=(0.10, 0.18), noise_amt=(0.8, 1.15), bright=(6500, 10000), drive=(2.2, 3.4), rim_amt=(0.45, 0.75)),
        'postpunk':         dict(f1=(175, 205), f2=(280, 320), decay=(0.18, 0.26), noise_decay=(0.20, 0.30), noise_amt=(1.2, 1.5), bright=(5500, 8500), drive=(1.4, 1.9), rim_amt=(0.20, 0.35)),
        'reggaeton_dembow': dict(f1=(235, 285), f2=(370, 440), decay=(0.09, 0.16), noise_decay=(0.09, 0.15), noise_amt=(0.75, 1.1), bright=(5500, 9000), drive=(1.8, 2.6), rim_amt=(0.40, 0.65)),
        'rnb_rim_snare':    dict(f1=(210, 255), f2=(340, 410), decay=(0.08, 0.14), noise_decay=(0.08, 0.14), noise_amt=(0.65, 0.95), bright=(5000, 8200), drive=(1.3, 1.75), rim_amt=(0.55, 0.85)),
        'modern_pop':       dict(f1=(190, 225), f2=(310, 360), decay=(0.14, 0.20), noise_decay=(0.16, 0.24), noise_amt=(1.15, 1.5), bright=(8500, 13000), drive=(1.6, 2.2), rim_amt=(0.25, 0.40)),
        'ghost_notes':      dict(f1=(180, 205), f2=(285, 315), decay=(0.06, 0.10), noise_decay=(0.07, 0.11), noise_amt=(0.65, 0.90), bright=(3800, 6200), drive=(1.05, 1.25), rim_amt=(0.05, 0.15)),
        'edm_buildup_hit':  dict(f1=(205, 240), f2=(330, 380), decay=(0.15, 0.22), noise_decay=(0.18, 0.26), noise_amt=(1.3, 1.6), bright=(9000, 14000), drive=(1.8, 2.5), rim_amt=(0.25, 0.4)),
    }
    for style, params in SNARE_STYLES.items():
        cnt = 4 if style == 'edm_buildup_hit' else 5
        for i in range(cnt):
            kw = {k: U(*v) for k, v in params.items()}
            s = D3.synth_snare(rng, **kw)
            if style == 'postpunk':
                s = stereo_reverb(s, wet=0.22, decay=0.55, tone=5200.0, rng=rng)
            kio.emit(f'02_SNARES/{style}/snare_{style}_{i+1:02d}.wav', s, 'SNARE', style,
                     peak=(-5.0 if style == 'ghost_notes' else -1.0))

    for i in range(5):
        kio.emit(f'02_SNARES/synthwave_gated/snare_synthwave_gated_{i+1:02d}.wav',
                 D3.synthwave_gated_snare(rng), 'SNARE', 'synthwave_gated')
    for i in range(5):
        kio.emit(f'02_SNARES/jazz_brush_tap/brush_tap_{i+1:02d}.wav',
                 D3.jazz_brush_snare(rng, mode='tap'), 'SNARE', 'jazz_brush_tap')
    for i in range(5):
        kio.emit(f'02_SNARES/jazz_brush_sweep/brush_sweep_{i+1:02d}.wav',
                 D3.jazz_brush_snare(rng, mode='sweep'), 'SNARE', 'jazz_brush_sweep')

    # Claps
    for style, bursts, dec, wide in [
        ('disco_layered', (4, 6), (0.20, 0.30), True),
        ('rnb_finger_clap', (2, 3), (0.10, 0.16), False),
        ('modern_pop', (3, 5), (0.16, 0.24), True),
        ('baile_clap', (2, 4), (0.12, 0.18), False),
    ]:
        for i in range(4 if style == 'baile_clap' else 5):
            kio.emit(
                f'03_CLAPS/{style}/clap_{style}_{i+1:02d}.wav',
                D3.synth_clap(rng, bursts=int(rng.integers(bursts[0], bursts[1] + 1)),
                              spacing=U(0.008, 0.015), decay=U(*dec),
                              lo=U(750, 1200), hi=U(4200, 7500), stereo_wide=wide),
                'CLAP', style,
            )

    # Closed & Open Hats
    for style, dec, tone, chick in [
        ('jazz_foot_chick', (0.035, 0.065), (6500, 9500), True),
        ('postpunk', (0.030, 0.055), (8500, 12000), False),
        ('disco_crisp', (0.035, 0.060), (10500, 15000), False),
        ('rnb_tight', (0.018, 0.036), (9000, 13500), False),
        ('baile_hat', (0.022, 0.045), (10000, 14500), False),
    ]:
        for i in range(4 if style == 'baile_hat' else 5):
            kio.emit(f'05_HATS_CLOSED/{style}/hat_{style}_{i+1:02d}.wav',
                     D3.closed_hat(rng, decay=U(*dec), tone=U(*tone), chick=chick), 'HAT_CLOSED', style)

    for style, dec, tone in [
        ('disco_sizzle', (0.24, 0.42), (11000, 16000)),
        ('postpunk', (0.18, 0.30), (8500, 12500)),
        ('synthwave', (0.25, 0.40), (9500, 14000)),
        ('rnb', (0.16, 0.28), (8500, 12500)),
    ]:
        for i in range(5 if style == 'disco_sizzle' else 4):
            kio.emit(f'06_HATS_OPEN/{style}/openhat_{style}_{i+1:02d}.wav',
                     D3.closed_hat(rng, decay=U(*dec), tone=U(*tone), metallic=0.82), 'HAT_OPEN', style)

    # Jazz Rides & Ride Bells
    for i in range(5):
        kio.emit(f'07_CYMBALS/jazz_sizzle_ride/jazz_ride_{i+1:02d}.wav',
                 D3.jazz_ride(rng, bell=False, sizzle=True), 'CYMBAL', 'jazz_sizzle_ride')
    for i in range(5):
        kio.emit(f'07_CYMBALS/jazz_ride_bell/ride_bell_{i+1:02d}.wav',
                 D3.jazz_ride(rng, bell=True, sizzle=False), 'CYMBAL', 'jazz_ride_bell')

    # Toms: Simmons 80s & Jazz Tuned
    for idx, (lbl, fs_t, fe_t) in enumerate([
        ('hi_1', 340, 130), ('hi_2', 310, 115),
        ('mid_1', 250, 92), ('mid_2', 225, 82),
        ('low_1', 180, 62), ('low_2', 155, 52),
    ]):
        kio.emit(f'08_TOMS/simmons_80s/simmons_tom_{lbl}.wav',
                 D3.simmons_tom(rng, f_start=fs_t, f_end=fe_t), 'TOM', 'simmons_80s')

    for nm, midi_m in [('C3', 48), ('G2', 43), ('D2', 38), ('A1', 33)]:
        f = midi_to_freq(midi_m)
        kio.emit(f'08_TOMS/jazz_tuned/jazz_tom_{nm}.wav',
                 D3.synth_kick(rng, f_start=f * 1.35, f_end=f, pitch_tau=0.04, decay=0.42,
                               click=0.12, drive=1.1, tone=3800.0, sub=0.15, punch=0.05),
                 'TOM', 'jazz_tuned', root_note=nm)

    # 24 Chromatic Tuned TR-808 Drift Phonk Cowbells (C4..B5 = MIDI 60..83)
    for m in range(60, 84):
        nm = note_filename(m)
        f = midi_to_freq(m)
        kio.emit(f'09_PERC_ACOUSTIC/drift_cowbell_tuned/cowbell_808_{nm}.wav',
                 D3.drift_phonk_cowbell(f, dur=0.45, drive=2.65, rng=rng),
                 'PERC', 'drift_cowbell_tuned', root_note=nm, tags=f'808_cowbell;midi{m};{f:.1f}Hz')

    # Brazilian Cuica & Automotivo Stabs
    for i in range(6):
        kio.emit(f'09_PERC_ACOUSTIC/cuica/cuica_{i+1:02d}.wav',
                 D3.baile_cuica(rng, high=(i % 2 == 0)), 'PERC', 'cuica')
    for i, m in enumerate([48, 51, 53, 55, 58, 60, 63, 67]):
        nm = note_filename(m)
        kio.emit(f'10_PERC_ELECTRONIC/automotivo_stab/automotivo_stab_{nm}.wav',
                 D3.automotivo_stab(rng, midi_note=m), 'PERC_ELEC', 'automotivo_stab', root_note=nm)

    # Tonal Perc: Cinematic Taiko & Church Bells
    for m in [24, 26, 29, 31, 33, 36]:
        nm = note_filename(m)
        f = midi_to_freq(m)
        taiko = D3.synth_kick(rng, f_start=f * 1.8, f_end=f, pitch_tau=0.045, decay=0.85,
                              click=0.22, drive=1.55, tone=2800.0, sub=0.55, punch=0.2)
        taiko = stereo_reverb(taiko, wet=0.35, decay=1.8, tone=3200.0, rng=rng)
        kio.emit(f'20_TONAL_PERC/orchestral_taiko/taiko_{nm}.wav', taiko, 'TONAL_PERC', 'taiko', root_note=nm)

    for m in [48, 52, 55, 60, 64, 67]:
        nm = note_filename(m)
        f = midi_to_freq(m)
        bell = M3.dx_crystal_bell(f, dur=2.4, rng=rng)
        kio.emit(f'20_TONAL_PERC/church_bell/church_bell_{nm}.wav', bell, 'TONAL_PERC', 'church_bell', root_note=nm)


def build_basses(rng):
    print('[2/7] Synthesizing multi-genre 808s & acoustic/electric/synth basses...')
    for m in range(24, 36):  # C1..B1
        nm = note_filename(m)
        f = midi_to_freq(m)
        kio.emit(f'12_808_SUB/808_spinz_pro/808_spinz_{nm}.wav',
                 B3.spinz_808(f, dur=1.45, punch=1.0, buzz=0.08, rng=rng),
                 '808', '808_spinz_pro', root_note=nm, tags=f'midi{m}')
        kio.emit(f'12_808_SUB/808_opium_buzz/808_opium_{nm}.wav',
                 B3.spinz_808(f, dur=1.40, punch=1.2, buzz=0.85, rng=rng),
                 '808', '808_opium_buzz', root_note=nm, tags=f'midi{m}')
        kio.emit(f'13_BASS/neuro_bass/neuro_bass_{nm}.wav',
                 B3.neuro_bass(f, dur=1.30, rng=rng),
                 'BASS', 'neuro_bass', root_note=nm, tags=f'midi{m}')

    DRILL_SLIDES = [
        (24, 36, False), (26, 38, False), (28, 40, False), (29, 41, False),
        (31, 43, False), (33, 45, False), (24, 36, True), (28, 40, True),
        (29, 41, True), (31, 43, True), (26, 33, False), (29, 36, False),
    ]
    for idx, (m_lo, m_hi, ud) in enumerate(DRILL_SLIDES):
        n_lo, n_hi = note_filename(m_lo), note_filename(m_hi)
        tag_mode = 'updown' if ud else 'up'
        kio.emit(
            f'12_808_SUB/808_drill_slide_long/808_drill_{n_lo}_{tag_mode}_{n_hi}.wav',
            B3.drill_glide_808(midi_to_freq(m_lo), midi_to_freq(m_hi), dur=1.50, up_then_down=ud, rng=rng),
            '808', '808_drill_slide_long', root_note=n_lo,
        )

    BASS_NOTES_EXT = [28, 31, 33, 35] + list(range(36, 48))  # E1..B1 anchors + full chromatic C2..B2
    for name, fn, notes, dur in [
        ('upright_double_bass', lambda f, d: B3.upright_double_bass(f, d, rng=rng), list(range(24, 36)) + [36, 40, 43, 47], 1.25),
        ('slap_bass',           lambda f, d: B3.slap_bass(f, d, rng=rng), BASS_NOTES_EXT, 1.00),
        ('picked_rock_bass',    lambda f, d: B3.picked_rock_bass(f, d, rng=rng), BASS_NOTES_EXT, 1.10),
        ('fretless_bass',       lambda f, d: B3.fretless_bass(f, d, rng=rng), list(range(36, 48)), 1.25),
        ('donk_organ_bass',     lambda f, d: B3.donk_organ_bass(f, d), [24, 28, 31, 33] + list(range(36, 48)), 0.65),
        ('hardbass_donk',       lambda f, d: B3.hardbass_donk(f, d), list(range(36, 48)), 0.45),
        ('moog_fat_bass',       lambda f, d: B3.moog_fat_bass(f, d), [24, 28, 31, 33] + list(range(36, 48)), 1.00),
    ]:
        for m in notes:
            nm = note_filename(m)
            kio.emit(f'13_BASS/{name}/{name}_{nm}.wav', fn(midi_to_freq(m), dur),
                     'BASS', name, root_note=nm, tags=f'midi{m}')


def build_melodic_and_chords(rng):
    print('[3/7] Synthesizing 38 multi-octave melodic instruments, lush stereo pads & 72 guitar/synth chords...')
    # Multi-octave grids spanning 3 to 4 full octaves
    FULL_4OCT = [36, 42, 48, 54, 60, 66, 72, 78, 84]                      # C2..C6 (9 notes)
    MID_3OCT = [48, 53, 58, 63, 68, 73, 78, 84]                           # C3..C6 (8 notes)
    LOW_MID_3OCT = [36, 41, 46, 51, 56, 61, 66, 72]                       # C2..C5 (8 notes)
    GUITAR_RANGE = [40, 45, 50, 55, 60, 64, 69, 76]                       # E2..E5 (8 notes)
    DJENT_RANGE = [30, 35, 40, 45, 50, 55, 60, 66]                        # F#1..F#4 (8 notes)
    PAD_RANGE = [36, 45, 54, 63, 72]                                      # C2..C5 (5 notes)

    INSTRUMENTS = [
        # Keys
        ('concert_grand',      'keys',    lambda f, d: M3.concert_grand(f, d, rng=rng),     1.35, FULL_4OCT),
        ('felt_upright',       'keys',    lambda f, d: M3.felt_upright(f, d, rng=rng),      1.40, FULL_4OCT),
        ('wurli_ep',           'keys',    lambda f, d: M3.wurli_ep(f, d, rng=rng),          1.35, FULL_4OCT),
        ('clavinet',           'keys',    lambda f, d: M3.clavinet(f, d, rng=rng),          0.95, LOW_MID_3OCT),
        ('pipe_organ',         'keys',    lambda f, d: M3.pipe_organ(f, d, rng=rng),        1.45, LOW_MID_3OCT),
        ('mellotron_flute',    'keys',    lambda f, d: M3.mellotron_flute(f, d, rng=rng),   1.45, MID_3OCT),
        ('mellotron_strings',  'keys',    lambda f, d: M3.mellotron_strings(f, d, rng=rng), 1.50, LOW_MID_3OCT),
        # Winds & Brass
        ('tenor_sax',          'winds',   lambda f, d: M3.saxophone(f, d, alto=False, rng=rng), 1.30, [46, 50, 54, 58, 62, 66, 70, 74, 78]),
        ('alto_sax',           'winds',   lambda f, d: M3.saxophone(f, d, alto=True, rng=rng),  1.30, [52, 56, 60, 64, 68, 72, 76, 80, 84]),
        ('oboe',               'winds',   lambda f, d: M3.double_reed_wind(f, d, 'oboe', rng),  1.25, [60, 63, 66, 69, 72, 75, 78, 81, 84]),
        ('bassoon',            'winds',   lambda f, d: M3.double_reed_wind(f, d, 'bassoon', rng), 1.30, [36, 40, 44, 48, 52, 56, 60, 64]),
        ('duduk',              'winds',   lambda f, d: M3.double_reed_wind(f, d, 'duduk', rng), 1.45, [45, 48, 52, 55, 57, 60, 64, 67, 69]),
        ('trombone',           'brass',   lambda f, d: M3.brass_horn(f, d, 'trombone', rng),    1.25, [40, 44, 48, 52, 56, 60, 64, 68, 72]),
        ('french_horn',        'brass',   lambda f, d: M3.brass_horn(f, d, 'french_horn', rng), 1.35, [36, 40, 44, 48, 52, 56, 60, 64, 68]),
        ('tuba_stab',          'brass',   lambda f, d: M3.brass_horn(f, d, 'tuba', rng),        1.10, [24, 28, 32, 36, 40, 44, 48]),
        ('funk_brass_section', 'brass',   lambda f, d: M3.funk_brass_section(f, d, rng=rng),    0.95, MID_3OCT),
        # Guitars
        ('nylon_guitar',       'guitars', lambda f, d: M3.nylon_guitar(f, d, rng=rng),          1.35, GUITAR_RANGE),
        ('steel_acoustic',     'guitars', lambda f, d: M3.steel_acoustic(f, d, rng=rng),        1.40, GUITAR_RANGE),
        ('funk_wah_guitar',    'guitars', lambda f, d: M3.funk_wah_guitar(f, d, rng=rng),       0.90, GUITAR_RANGE),
        ('jazz_guitar',        'guitars', lambda f, d: M3.jazz_guitar(f, d, rng=rng),           1.25, GUITAR_RANGE),
        ('metal_chug_8str',    'guitars', lambda f, d: M3.metal_chug_8str(f, d, rng=rng),       1.00, DJENT_RANGE),
        ('shimmer_guitar',     'guitars', lambda f, d: M3.shimmer_guitar(f, d, rng=rng),        1.65, [40, 45, 50, 55, 60, 64, 69, 74]),
        # World & CIS Folk
        ('balalaika',          'world',   lambda f, d: M3.world_plucked(f, d, 'balalaika', rng), 1.10, [52, 56, 60, 64, 68, 72, 76, 80, 84]),
        ('bayan',              'world',   lambda f, d: M3.bayan(f, d),                           1.30, LOW_MID_3OCT),
        ('gusli',              'world',   lambda f, d: M3.world_plucked(f, d, 'gusli', rng),     1.35, MID_3OCT),
        ('ukulele',            'world',   lambda f, d: M3.world_plucked(f, d, 'ukulele', rng),   0.95, [60, 63, 66, 69, 72, 75, 78, 81, 84]),
        ('mandolin',           'world',   lambda f, d: M3.world_plucked(f, d, 'mandolin', rng),  1.05, [55, 59, 62, 66, 69, 73, 76, 80, 84]),
        ('erhu',               'world',   lambda f, d: M3.erhu(f, d, rng=rng),                   1.40, [50, 54, 58, 62, 66, 70, 74, 78, 82]),
        ('kalimba_stereo',     'mallets', lambda f, d: M3.kalimba_stereo(f, d, rng=rng),         1.15, MID_3OCT),
        # Modern Synths
        ('rage_lead',          'synths',  lambda f, d: M3.rage_lead(f, d, rng=rng),              1.05, MID_3OCT),
        ('pluggnb_lead',       'synths',  lambda f, d: M3.pluggnb_lead(f, d),                    1.15, MID_3OCT),
        ('pluggnb_bell',       'synths',  lambda f, d: M3.pluggnb_bell(f, d, rng=rng),           1.20, MID_3OCT),
        ('retro_poly80',       'synths',  lambda f, d: M3.retro_poly80(f, d),                    1.20, LOW_MID_3OCT),
        ('gfunk_whistle_lead', 'synths',  lambda f, d: M3.gfunk_whistle_lead(f, d),              1.20, [60, 64, 68, 72, 76, 80, 84, 88, 92]),
        ('hyperpop_lead',      'synths',  lambda f, d: M3.hyperpop_lead(f, d, rng=rng),          0.95, MID_3OCT),
        ('rave_hoover',        'synths',  lambda f, d: M3.rave_hoover(f, d, rng=rng),            1.15, LOW_MID_3OCT),
        ('dx_crystal_bell',    'synths',  lambda f, d: M3.dx_crystal_bell(f, d, rng=rng),        1.30, MID_3OCT),
        ('psy_fm_lead',        'synths',  lambda f, d: M3.psy_fm_lead(f, d),                     0.75, LOW_MID_3OCT),
        ('chiptune_duty',      'synths',  lambda f, d: M3.chiptune_lead(f, d, arp=False),        0.75, MID_3OCT),
        ('chiptune_arp',       'synths',  lambda f, d: M3.chiptune_lead(f, d, arp=True),         0.85, MID_3OCT),
        # Lush Stereo Pads & Drones
        ('pad_shimmer_stereo', 'pads',    lambda f, d: M3.stereo_pad(f, d, 'shimmer', rng),      1.95, PAD_RANGE),
        ('pad_cs80_dark',      'pads',    lambda f, d: M3.stereo_pad(f, d, 'cs80_dark', rng),    1.95, PAD_RANGE),
        ('pad_glass_ambient',  'pads',    lambda f, d: M3.stereo_pad(f, d, 'glass_ambient', rng), 1.95, PAD_RANGE),
        ('pad_tape_strings',   'pads',    lambda f, d: M3.stereo_pad(f, d, 'tape_strings', rng), 1.95, PAD_RANGE),
        ('drone_dark_cinema',  'pads',    lambda f, d: M3.stereo_pad(f, d, 'drone', rng),        2.05, [24, 28, 31, 36, 40, 43, 48]),
    ]

    for name, folder, fn, base_dur, notes in INSTRUMENTS:
        for m in notes:
            nm = note_filename(m)
            f = midi_to_freq(m)
            wav = fn(f, base_dur)  # Fixed! Never mutates base_dur across loop iterations!
            kio.emit(f'14_MELODIC/{folder}/{name}/{name}_{nm}.wav', wav,
                     'MELODIC', name, root_note=nm, tags=f'{folder};midi{m}')

    # 72 Chords & Guitar Strums across all 12 chromatic roots!
    for pc in range(12):
        m_strum = 48 + pc  # C3..B3
        nm3 = note_filename(m_strum)
        m_pwr = 36 + pc    # C2..B2
        nm2 = note_filename(m_pwr)
        kio.emit(f'14_MELODIC/chords_stabs/acoustic_strum_major/strum_maj_{nm3}.wav',
                 M3.acoustic_guitar_strum(m_strum, 'major', dur=1.15, rng=rng),
                 'CHORD', 'acoustic_strum_major', root_note=nm3)
        kio.emit(f'14_MELODIC/chords_stabs/acoustic_strum_minor/strum_min_{nm3}.wav',
                 M3.acoustic_guitar_strum(m_strum, 'minor', dur=1.15, rng=rng),
                 'CHORD', 'acoustic_strum_minor', root_note=nm3)
        kio.emit(f'14_MELODIC/chords_stabs/rock_power_chord/power_chord_{nm2}.wav',
                 M3.electric_power_chord(m_pwr, dur=0.95, rng=rng),
                 'CHORD', 'rock_power_chord', root_note=nm2)
        kio.emit(f'14_MELODIC/chords_stabs/house_organ_chord/house_min7_{nm3}.wav',
                 M3.house_organ_stab(m_strum, dur=0.58, rng=rng),
                 'CHORD', 'house_organ_chord', root_note=nm3)
        kio.emit(f'14_MELODIC/chords_stabs/dub_techno_chord/dub_chord_{nm3}.wav',
                 M3.dub_techno_chord(m_strum, dur=1.35, rng=rng),
                 'CHORD', 'dub_techno_chord', root_note=nm3)
        kio.emit(f'14_MELODIC/chords_stabs/neosoul_rhodes_chord/rhodes_min9_{nm3}.wav',
                 M3.neosoul_rhodes_chord(m_strum, dur=1.20, rng=rng),
                 'CHORD', 'neosoul_rhodes_chord', root_note=nm3)


def build_fx_and_fills(rng):
    print('[4/7] Synthesizing studio FX, braaams, vinyl/tape/rain textures & genre drum fills...')
    for m in [24, 26, 28, 29, 31, 33]:
        nm = note_filename(m)
        kio.emit(f'15_FX/cinema_braaam/braaam_{nm}.wav',
                 F3.cinema_braaam(rng, root_midi=m, dur=2.8), 'FX', 'cinema_braaam', root_note=nm)

    for i, (fs_d, fe_d) in enumerate([(110, 28), (95, 25), (85, 24), (130, 30), (75, 22), (105, 27)]):
        kio.emit(f'15_FX/sub_drops/sub_drop_{i+1:02d}.wav',
                 F3.sub_drop(f_start=fs_d, f_end=fe_d, dur=2.0, rng=rng), 'FX', 'sub_drop')

    for i, f0 in enumerate([330, 440, 523.25, 659.25, 261.63, 880]):
        kio.emit(f'15_FX/tape_stops/tape_stop_{i+1:02d}.wav',
                 F3.tape_stop_fx(rng, f_start=f0, dur=0.9), 'FX', 'tape_stop')

    for i, (fb, rt) in enumerate([(520, 4.0), (640, 6.0), (740, 3.2), (460, 8.0), (820, 5.0), (580, 10.0)]):
        kio.emit(f'15_FX/dub_sirens/dub_siren_{i+1:02d}.wav',
                 F3.dub_siren(rng, f_base=fb, rate_hz=rt, dur=2.1), 'FX', 'dub_siren')

    for bpm in [120, 128, 140, 150, 160, 174]:
        kio.emit(f'15_FX/cyber_risers/cyber_riser_2bar_{bpm}bpm.wav',
                 F3.cyber_riser(rng, bars=2, bpm=bpm), 'FX', 'cyber_riser', bpm=bpm)

    for idx, m in enumerate([48, 53, 55, 57, 60, 62]):
        nm = note_filename(m)
        ch = M3.neosoul_rhodes_chord(m, dur=1.8, rng=rng) if idx % 2 == 0 else M3.acoustic_guitar_strum(m, 'minor', dur=1.8, rng=rng)
        kio.emit(f'15_FX/reverse_swells/reverse_chord_swell_{nm}.wav',
                 F3.reverse_chord_swell(ch), 'FX', 'reverse_swell', root_note=nm)

    for mode, bpm in [('vinyl', 85), ('vinyl', 95), ('rain', 80), ('rain', 120), ('cassette', 90), ('cassette', 140)]:
        kio.emit(f'15_FX/atmos_loops/{mode}_texture_1bar_{bpm}bpm.wav',
                 F3.vinyl_texture_loop(rng, bpm=bpm, bars=1, mode=mode),
                 'FX', f'{mode}_texture', bpm=bpm, trim=False, is_loop=True)

    # 12 Genre Drum Fills (sample-exact 1-bar or 2-bar!)
    sn_pop = D3.synth_snare(rng, f1=205, f2=330, decay=0.16, noise_decay=0.18)
    sn_80s = D3.synthwave_gated_snare(rng)
    kick_m = D3.synth_kick(rng, f_start=170, f_end=58, decay=0.15, click=0.55, drive=2.6)
    brush_s = D3.jazz_brush_snare(rng, 'sweep')
    brush_t = D3.jazz_brush_snare(rng, 'tap')
    sim_hi = D3.simmons_tom(rng, 330, 125)
    sim_md = D3.simmons_tom(rng, 240, 90)
    sim_lo = D3.simmons_tom(rng, 170, 58)
    dembow_s = D3.synth_snare(rng, f1=260, f2=410, decay=0.12, noise_decay=0.11, rim_amt=0.6)

    FILL_SPECS = [
        ('fill_synthwave_simmons_1bar_108bpm', 108, 1,
         {'th': sim_hi, 'tm': sim_md, 'tl': sim_lo, 'sn': sn_80s},
         [(0, 'sn', 0.9, 0.5), (2, 'th', 0.85, 0.3), (3, 'th', 0.75, 0.3),
          (4, 'tm', 0.9, 0.5), (6, 'tm', 0.85, 0.55), (8, 'tl', 0.95, 0.7),
          (10, 'tl', 0.9, 0.7), (12, 'sn', 1.0, 0.5), (14, 'sn', 0.95, 0.5)]),
        ('fill_metal_doublekick_1bar_160bpm', 160, 1,
         {'k': kick_m, 'sn': sn_pop, 'th': sim_hi, 'tl': sim_lo},
         [(s, 'k', 0.85, 0.5) for s in range(16)] + [(4, 'sn', 0.95, 0.5), (12, 'sn', 1.0, 0.5), (14, 'tl', 0.9, 0.65)]),
        ('fill_jazz_brush_turnaround_1bar_120bpm', 120, 1,
         {'bs': brush_s, 'bt': brush_t},
         [(0, 'bs', 0.8, 0.45), (4, 'bt', 0.75, 0.52), (6.66, 'bt', 0.65, 0.48),
          (8, 'bs', 0.85, 0.5), (10.66, 'bt', 0.8, 0.55), (12, 'bt', 0.9, 0.5), (14.66, 'bt', 0.95, 0.5)]),
        ('fill_edm_snare_buildup_2bar_128bpm', 128, 2,
         {'sn': sn_pop},
         [(s * 2, 'sn', 0.45 + 0.04 * s, 0.5) for s in range(8)]
         + [(16 + s, 'sn', 0.65 + 0.022 * s, 0.5) for s in range(8)]
         + [(24 + s * 0.5, 'sn', 0.75 + 0.015 * s, 0.5) for s in range(16)]),
        ('fill_reggaeton_dembow_1bar_100bpm', 100, 1,
         {'sn': dembow_s, 'k': kick_m},
         [(0, 'k', 0.95, 0.5), (3, 'sn', 0.9, 0.5), (6, 'sn', 0.85, 0.5),
          (8, 'sn', 0.9, 0.45), (10, 'sn', 0.88, 0.55), (12, 'sn', 0.95, 0.4), (13, 'sn', 0.85, 0.6), (14, 'sn', 1.0, 0.5)]),
        ('fill_trap_triplet_snare_1bar_140bpm', 140, 1,
         {'sn': sn_pop},
         [(0, 'sn', 0.7, 0.5), (4, 'sn', 0.8, 0.5),
          (8, 'sn', 0.75, 0.4), (9.33, 'sn', 0.8, 0.5), (10.66, 'sn', 0.85, 0.6),
          (12, 'sn', 0.9, 0.45), (13.33, 'sn', 0.95, 0.5), (14.66, 'sn', 1.0, 0.55)]),
        ('fill_drill_countersnare_1bar_142bpm', 142, 1,
         {'sn': dembow_s},
         [(0, 'sn', 0.8, 0.45), (3, 'sn', 0.75, 0.55), (6, 'sn', 0.85, 0.5),
          (9, 'sn', 0.78, 0.45), (11, 'sn', 0.82, 0.55), (12, 'sn', 0.9, 0.5), (14, 'sn', 0.95, 0.45), (15, 'sn', 1.0, 0.55)]),
        ('fill_baile_tamborzao_1bar_130bpm', 130, 1,
         {'k': kick_m, 'sn': dembow_s},
         [(0, 'k', 1.0, 0.5), (3, 'sn', 0.9, 0.5), (6, 'k', 0.95, 0.5), (8, 'sn', 0.9, 0.45),
          (10, 'sn', 0.9, 0.55), (12, 'k', 0.95, 0.5), (13, 'sn', 0.85, 0.45), (14, 'sn', 0.95, 0.55), (15, 'sn', 1.0, 0.5)]),
    ]
    for fname, bpm, bars, vcs, evs in FILL_SPECS:
        wav = F3.render_exact_loop(bpm, bars, vcs, evs, stereo_out=True, rng=rng)
        kio.emit(f'19_FILLS_ROLLS/{fname}.wav', wav, 'FILL', fname, bpm=bpm, trim=False, is_loop=True)


def build_loops(rng):
    print('[5/7] Rendering 24 sample-exact seamless drum & melodic/bass loops...')
    # Reusable crisp voices
    v_kick_baile = D3.synth_kick(rng, f_start=170, f_end=45, decay=0.40, drive=3.0, sub=0.55)
    v_sn_baile = D3.synth_snare(rng, f1=270, f2=420, decay=0.14, drive=2.6, rim_amt=0.6)
    v_cuica_hi = D3.baile_cuica(rng, True)
    v_cuica_lo = D3.baile_cuica(rng, False)

    v_kick_pp = D3.synth_kick(rng, f_start=145, f_end=55, decay=0.22, drive=1.6)
    v_sn_pp = stereo_reverb(D3.synth_snare(rng, f1=190, f2=300, decay=0.20, drive=1.6), wet=0.25, decay=0.5, rng=rng)
    v_hh_pp = D3.closed_hat(rng, decay=0.04, tone=10500)
    v_oh_pp = D3.closed_hat(rng, decay=0.22, tone=11000)

    v_kick_jz = D3.synth_kick(rng, f_start=95, f_end=62, decay=0.28, click=0.12, drive=1.1, tone=3200)
    v_ride_jz = D3.jazz_ride(rng, bell=False, sizzle=True)
    v_chick_jz = D3.closed_hat(rng, decay=0.045, tone=8000, chick=True)
    v_brush = D3.jazz_brush_snare(rng, 'tap')

    v_kick_ds = D3.synth_kick(rng, f_start=135, f_end=52, decay=0.25, drive=1.6)
    v_sn_ds = D3.synth_snare(rng, f1=198, f2=320, decay=0.20, drive=1.7)
    v_cl_ds = D3.synth_clap(rng, bursts=4, decay=0.22, stereo_wide=True)
    v_hh_ds = D3.closed_hat(rng, decay=0.04, tone=12500)
    v_oh_ds = D3.closed_hat(rng, decay=0.28, tone=13500)

    v_kick_sw = D3.synth_kick(rng, f_start=145, f_end=48, decay=0.30, drive=1.8)
    v_sn_sw = D3.synthwave_gated_snare(rng)

    v_kick_psy = D3.psytrance_kick(rng, 47.0, 0.24)
    v_kick_gab = D3.gabber_kick(rng, 52.0, 0.36, drive=6.5)

    DRUM_LOOPS = [
        ('baile_funk_130bpm', 130, 2, 0.0,
         {'k': v_kick_baile, 's': v_sn_baile, 'ch': v_cuica_hi, 'cl': v_cuica_lo},
         [(b * 16 + p, 'k', 1.0, 0.5) for b in range(2) for p in (0, 6, 12)]
         + [(b * 16 + p, 's', 0.9, 0.5) for b in range(2) for p in (3, 8, 11, 14)]
         + [(b * 16 + 4, 'ch', 0.55, 0.35) for b in range(2)]
         + [(b * 16 + 10, 'cl', 0.55, 0.65) for b in range(2)]),

        ('postpunk_148bpm', 148, 2, 0.0,
         {'k': v_kick_pp, 's': v_sn_pp, 'h': v_hh_pp, 'oh': v_oh_pp},
         [(b * 16 + p, 'k', 0.95, 0.5) for b in range(2) for p in (0, 6, 8, 10)]
         + [(b * 16 + p, 's', 0.95, 0.5) for b in range(2) for p in (4, 12)]
         + [(b * 16 + p, 'h', 0.55 if p % 2 == 0 else 0.4, 0.42) for b in range(2) for p in range(16) if p != 14]
         + [(b * 16 + 14, 'oh', 0.65, 0.42) for b in range(2)]),

        ('jazz_swing_120bpm', 120, 2, 0.55,
         {'k': v_kick_jz, 'r': v_ride_jz, 'c': v_chick_jz, 'b': v_brush},
         [(b * 16 + p, 'r', 0.78, 0.62) for b in range(2) for p in (0, 4, 7, 8, 12, 15)]
         + [(b * 16 + p, 'c', 0.65, 0.35) for b in range(2) for p in (4, 12)]
         + [(b * 16 + p, 'k', 0.45, 0.5) for b in range(2) for p in (0, 11)]
         + [(b * 16 + p, 'b', 0.42, 0.48) for b in range(2) for p in (2, 9, 14)]),

        ('bossa_nova_116bpm', 116, 2, 0.0,
         {'k': v_kick_jz, 'r': v_sn_baile, 'h': v_hh_pp},
         [(b * 16 + p, 'k', 0.85, 0.5) for b in range(2) for p in (0, 3, 4, 7, 8, 11, 12, 15)]
         + [(b * 16 + s, 'h', 0.42, 0.4) for b in range(2) for s in range(0, 16, 2)]
         + [(0, 'r', 0.55, 0.58), (3, 'r', 0.55, 0.58), (6, 'r', 0.55, 0.58),
            (10, 'r', 0.55, 0.58), (13, 'r', 0.55, 0.58),
            (16 + 2, 'r', 0.55, 0.58), (16 + 5, 'r', 0.55, 0.58), (16 + 8, 'r', 0.55, 0.58),
            (16 + 11, 'r', 0.55, 0.58), (16 + 14, 'r', 0.55, 0.58)]),

        ('disco_funk_118bpm', 118, 2, 0.12,
         {'k': v_kick_ds, 's': v_sn_ds, 'c': v_cl_ds, 'h': v_hh_ds, 'oh': v_oh_ds},
         [(b * 16 + p, 'k', 0.95, 0.5) for b in range(2) for p in (0, 4, 8, 12)]
         + [(b * 16 + p, 's', 0.85, 0.5) for b in range(2) for p in (4, 12)]
         + [(b * 16 + p, 'c', 0.72, 0.5) for b in range(2) for p in (4, 12)]
         + [(b * 16 + p, 'h', 0.48, 0.4) for b in range(2) for p in range(16) if p % 4 != 2]
         + [(b * 16 + p, 'oh', 0.68, 0.4) for b in range(2) for p in (2, 6, 10, 14)]),

        ('synthwave_108bpm', 108, 2, 0.0,
         {'k': v_kick_sw, 's': v_sn_sw, 'h': v_hh_pp, 't': D3.simmons_tom(rng, 220, 82)},
         [(b * 16 + p, 'k', 1.0, 0.5) for b in range(2) for p in (0, 8, 10)]
         + [(b * 16 + p, 's', 0.95, 0.5) for b in range(2) for p in (4, 12)]
         + [(b * 16 + p, 'h', 0.45, 0.42) for b in range(2) for p in range(0, 16, 2)]
         + [(30, 't', 0.8, 0.6), (31, 't', 0.85, 0.65)]),

        ('rnb_neosoul_86bpm', 86, 2, 0.35,
         {'k': D3.synth_kick(rng, 98, 45, decay=0.35, click=0.1, drive=1.3),
          's': D3.synth_snare(rng, 225, 365, decay=0.11, rim_amt=0.7),
          'h': D3.closed_hat(rng, 0.025, 10000)},
         [(0, 'k', 0.95, 0.5), (7, 'k', 0.75, 0.5), (10, 'k', 0.88, 0.5),
          (16, 'k', 0.95, 0.5), (23, 'k', 0.72, 0.5), (26, 'k', 0.9, 0.5), (30, 'k', 0.65, 0.5)]
         + [(b * 16 + p, 's', 0.88, 0.5) for b in range(2) for p in (4, 12)]
         + [(b * 16 + p, 'h', 0.42 if p % 2 == 0 else 0.28, 0.44) for b in range(2) for p in range(16)]),

        ('psytrance_140bpm', 140, 2, 0.0,
         {'k': v_kick_psy, 's': v_sn_ds, 'h': v_hh_ds, 'oh': v_oh_ds},
         [(b * 16 + p, 'k', 1.0, 0.5) for b in range(2) for p in (0, 4, 8, 12)]
         + [(b * 16 + p, 's', 0.78, 0.5) for b in range(2) for p in (4, 12)]
         + [(b * 16 + p, 'oh', 0.58, 0.45) for b in range(2) for p in (2, 6, 10, 14)]
         + [(b * 16 + p, 'h', 0.35, 0.55) for b in range(2) for p in (1, 3, 5, 7, 9, 11, 13, 15)]),

        ('dubstep_halftime_140bpm', 140, 2, 0.0,
         {'k': D3.synth_kick(rng, 165, 42, decay=0.32, drive=3.5, sub=0.5),
          's': D3.synth_snare(rng, 185, 295, decay=0.28, drive=3.0, noise_amt=1.35),
          'h': v_hh_ds},
         [(0, 'k', 1.0, 0.5), (11, 'k', 0.85, 0.5), (16, 'k', 1.0, 0.5), (22, 'k', 0.85, 0.5), (27, 'k', 0.8, 0.5)]
         + [(8, 's', 1.0, 0.5), (24, 's', 1.0, 0.5)]
         + [(b * 16 + p, 'h', 0.48, 0.42) for b in range(2) for p in range(0, 16, 2)]),

        ('afrobeats_104bpm', 104, 2, 0.18,
         {'k': D3.synth_kick(rng, 115, 52, decay=0.30, drive=1.6),
          'r': D3.synth_snare(rng, 250, 410, decay=0.09, rim_amt=0.75),
          'h': v_hh_pp},
         [(b * 16 + p, 'k', 0.92, 0.5) for b in range(2) for p in (0, 7, 8, 15)]
         + [(b * 16 + p, 'r', 0.82, 0.54) for b in range(2) for p in (3, 6, 10, 12)]
         + [(b * 16 + p, 'h', 0.40, 0.42) for b in range(2) for p in range(16)]),

        ('rock_driving_124bpm', 124, 2, 0.0,
         {'k': v_kick_ds, 's': v_sn_ds, 'h': v_oh_pp},
         [(b * 16 + p, 'k', 0.95, 0.5) for b in range(2) for p in (0, 6, 8, 10)]
         + [(b * 16 + p, 's', 0.98, 0.5) for b in range(2) for p in (4, 12)]
         + [(b * 16 + p, 'h', 0.55, 0.4) for b in range(2) for p in range(0, 16, 2)]),

        ('metal_doublekick_160bpm', 160, 2, 0.0,
         {'k': D3.synth_kick(rng, 180, 60, decay=0.14, click=0.6, drive=2.8),
          's': D3.synth_snare(rng, 230, 350, decay=0.15, drive=2.5),
          'c': D3.jazz_ride(rng, bell=True, sizzle=False)},
         [(s, 'k', 0.88, 0.5) for s in range(32)]
         + [(b * 16 + p, 's', 1.0, 0.5) for b in range(2) for p in (4, 12)]
         + [(b * 16 + p, 'c', 0.65, 0.62) for b in range(2) for p in (0, 4, 8, 12)]),

        ('reggae_onedrop_78bpm', 78, 2, 0.22,
         {'k': D3.synth_kick(rng, 95, 54, decay=0.36, drive=1.4),
          'r': D3.synth_snare(rng, 260, 430, decay=0.09, rim_amt=0.8),
          'h': v_hh_pp},
         [(b * 16 + 8, 'k', 0.98, 0.5) for b in range(2)]
         + [(b * 16 + 8, 'r', 0.90, 0.52) for b in range(2)]
         + [(b * 16 + p, 'h', 0.45 if p % 4 == 2 else 0.32, 0.42) for b in range(2) for p in range(0, 16, 2)]),

        ('pluggnb_144bpm', 144, 2, 0.0,
         {'k': D3.synth_kick(rng, 115, 48, decay=0.38, drive=1.4, tone=4200),
          'c': D3.synth_clap(rng, bursts=3, decay=0.14),
          'r': D3.synth_snare(rng, 235, 380, decay=0.09, rim_amt=0.65),
          'h': D3.closed_hat(rng, 0.025, 11500)},
         [(0, 'k', 0.95, 0.5), (10, 'k', 0.9, 0.5), (16, 'k', 0.95, 0.5), (22, 'k', 0.88, 0.5), (28, 'k', 0.85, 0.5)]
         + [(b * 16 + p, 'c', 0.9, 0.5) for b in range(2) for p in (4, 12)]
         + [(b * 16 + p, 'r', 0.72, 0.56) for b in range(2) for p in (7, 14)]
         + [(s, 'h', 0.46, 0.44) for s in range(0, 32, 2)] + [(13, 'h', 0.38, 0.44), (29, 'h', 0.38, 0.44)]),

        ('rage_opium_152bpm', 152, 2, 0.0,
         {'k': D3.synth_kick(rng, 195, 48, decay=0.28, drive=4.5, sub=0.45),
          'c': D3.synth_clap(rng, bursts=4, decay=0.18, stereo_wide=True),
          'h': D3.closed_hat(rng, 0.022, 14000)},
         [(0, 'k', 1.0, 0.5), (6, 'k', 0.92, 0.5), (10, 'k', 0.95, 0.5), (16, 'k', 1.0, 0.5), (26, 'k', 0.96, 0.5)]
         + [(b * 16 + p, 'c', 0.95, 0.5) for b in range(2) for p in (4, 12)]
         + [(s, 'h', 0.50, 0.45) for s in range(0, 32, 2)]
         + [(6.5, 'h', 0.4, 0.45), (7.0, 'h', 0.42, 0.45), (7.5, 'h', 0.45, 0.45)]),

        ('hardbass_155bpm', 155, 2, 0.0,
         {'k': v_kick_gab, 'd': B3.hardbass_donk(midi_to_freq(45), 0.32), 'c': v_cl_ds, 'h': v_oh_ds},
         [(b * 16 + p, 'k', 1.0, 0.5) for b in range(2) for p in (0, 4, 8, 12)]
         + [(b * 16 + p, 'd', 0.95, 0.5) for b in range(2) for p in (2, 6, 10, 14)]
         + [(b * 16 + p, 'c', 0.8, 0.5) for b in range(2) for p in (4, 12)]
         + [(b * 16 + p, 'h', 0.45, 0.45) for b in range(2) for p in (2, 6, 10, 14)]),
    ]

    for lname, bpm, bars, sw, vcs, evs in DRUM_LOOPS:
        wav = F3.render_exact_loop(bpm, bars, vcs, evs, swing=sw, stereo_out=True, rng=rng)
        kio.emit(f'16_LOOPS/drum_loops/{lname}.wav', wav, 'LOOP_DRUM', lname, bpm=bpm, trim=False, is_loop=True)

    # 8 Sample-Exact Melodic & Bass Loops!
    # 1) Drift Phonk Cowbell Melody (160 BPM, A minor)
    cb_voices = {str(m): D3.drift_phonk_cowbell(midi_to_freq(m), 0.36, 2.7, rng) for m in [69, 72, 74, 76, 77, 81]}
    cb_evs = [
        (0, '69', 0.95, 0.5), (2, '69', 0.85, 0.5), (4, '76', 0.95, 0.52), (6, '77', 0.9, 0.48),
        (8, '76', 0.92, 0.5), (10, '74', 0.88, 0.5), (12, '72', 0.9, 0.48), (14, '74', 0.85, 0.52),
        (16, '69', 0.95, 0.5), (18, '69', 0.85, 0.5), (20, '81', 0.98, 0.54), (22, '77', 0.9, 0.46),
        (24, '76', 0.92, 0.5), (26, '74', 0.88, 0.5), (28, '72', 0.92, 0.5), (30, '76', 0.9, 0.5),
    ]
    kio.emit('16_LOOPS/melodic_loops/phonk_cowbell_melody_160bpm_Am.wav',
             F3.render_exact_loop(160, 2, cb_voices, cb_evs, rng=rng),
             'LOOP_MELODIC', 'phonk_cowbell', root_note='A4', bpm=160, trim=False, is_loop=True)

    # 2) Post-Punk Chorus Bass Riff (148 BPM, E minor: E2 -> C2 -> A1 -> B1)
    pp_voices = {str(m): dsp.stereo_chorus(B3.picked_rock_bass(midi_to_freq(m), 0.35, rng), 6.0, 0.9, 0.42) for m in [40, 36, 33, 35]}
    pp_evs = (
        [(s * 2, '40', 0.9, 0.5) for s in range(4)]
        + [(8 + s * 2, '36', 0.9, 0.5) for s in range(4)]
        + [(16 + s * 2, '33', 0.9, 0.5) for s in range(4)]
        + [(24 + s * 2, '35', 0.9, 0.5) for s in range(4)]
    )
    kio.emit('16_LOOPS/melodic_loops/postpunk_bass_riff_148bpm_Em.wav',
             F3.render_exact_loop(148, 2, pp_voices, pp_evs, rng=rng),
             'LOOP_MELODIC', 'postpunk_bass', root_note='E2', bpm=148, trim=False, is_loop=True)

    # 3) Neo-Soul Rhodes Chord Loop (86 BPM, Dm9 -> Gm9 -> Am9 -> Dm9)
    ns_voices = {str(m): M3.neosoul_rhodes_chord(m, 1.8, rng) for m in [50, 55, 57]}
    ns_evs = [(0, '50', 0.92, 0.5), (8, '55', 0.9, 0.5), (16, '57', 0.9, 0.5), (24, '50', 0.92, 0.5)]
    kio.emit('16_LOOPS/melodic_loops/neosoul_rhodes_loop_86bpm_Dm.wav',
             F3.render_exact_loop(86, 2, ns_voices, ns_evs, rng=rng),
             'LOOP_MELODIC', 'neosoul_rhodes', root_note='D3', bpm=86, trim=False, is_loop=True)

    # 4) Classic 90s House M1 Organ Bass Loop (126 BPM, C minor)
    hs_voices = {str(m): B3.donk_organ_bass(midi_to_freq(m), 0.38) for m in [36, 39, 41, 43, 46]}
    hs_evs = [
        (2, '36', 0.95, 0.5), (5, '36', 0.85, 0.5), (7, '39', 0.9, 0.5), (10, '41', 0.92, 0.5), (14, '43', 0.9, 0.5),
        (18, '36', 0.95, 0.5), (21, '36', 0.85, 0.5), (23, '46', 0.92, 0.5), (26, '43', 0.9, 0.5), (30, '41', 0.88, 0.5),
    ]
    kio.emit('16_LOOPS/melodic_loops/house_organ_bass_126bpm_Cm.wav',
             F3.render_exact_loop(126, 2, hs_voices, hs_evs, rng=rng),
             'LOOP_MELODIC', 'house_organ_bass', root_note='C2', bpm=126, trim=False, is_loop=True)

    # 5) Synthwave 16th Analog Arp Loop (108 BPM, A minor)
    sw_notes = [57, 60, 64, 69, 64, 60, 57, 64, 53, 57, 60, 65, 60, 57, 53, 60]
    sw_voices = {str(m): M3.retro_poly80(midi_to_freq(m), 0.32) for m in set(sw_notes)}
    sw_evs = [(i, str(sw_notes[i % 16]), 0.85, 0.5) for i in range(32)]
    kio.emit('16_LOOPS/melodic_loops/synthwave_arp_108bpm_Am.wav',
             F3.render_exact_loop(108, 2, sw_voices, sw_evs, rng=rng),
             'LOOP_MELODIC', 'synthwave_arp', root_note='A3', bpm=108, trim=False, is_loop=True)

    # 6) Bossanova Nylon Guitar Chords Loop (116 BPM, Gm)
    bn_voices = {'gm': M3.acoustic_guitar_strum(55, 'minor', 1.1, rng), 'cm': M3.acoustic_guitar_strum(48, 'minor', 1.1, rng)}
    bn_evs = [
        (0, 'gm', 0.9, 0.5), (3, 'gm', 0.72, 0.5), (6, 'gm', 0.8, 0.5), (10, 'gm', 0.78, 0.5), (13, 'gm', 0.72, 0.5),
        (16, 'cm', 0.9, 0.5), (19, 'cm', 0.72, 0.5), (22, 'cm', 0.8, 0.5), (26, 'cm', 0.78, 0.5), (29, 'cm', 0.72, 0.5),
    ]
    kio.emit('16_LOOPS/melodic_loops/bossa_nylon_chords_116bpm_Gm.wav',
             F3.render_exact_loop(116, 2, bn_voices, bn_evs, rng=rng),
             'LOOP_MELODIC', 'bossa_nylon', root_note='G3', bpm=116, trim=False, is_loop=True)

    # 7) Rage / Opium Hyper-Saw Loop (152 BPM, F minor)
    rg_voices = {str(m): M3.rage_lead(midi_to_freq(m), 0.42, rng) for m in [53, 56, 60, 61, 65]}
    rg_evs = [
        (0, '53', 0.95, 0.5), (3, '60', 0.9, 0.5), (6, '61', 0.92, 0.5), (8, '53', 0.9, 0.5), (12, '56', 0.88, 0.5),
        (16, '53', 0.95, 0.5), (19, '65', 0.95, 0.5), (22, '61', 0.92, 0.5), (24, '60', 0.9, 0.5), (28, '56', 0.88, 0.5),
    ]
    kio.emit('16_LOOPS/melodic_loops/rage_synths_152bpm_Fm.wav',
             F3.render_exact_loop(152, 2, rg_voices, rg_evs, rng=rng),
             'LOOP_MELODIC', 'rage_synths', root_note='F3', bpm=152, trim=False, is_loop=True)

    # 8) Funk Slap Octave Groove (118 BPM, E minor)
    fk_voices = {str(m): B3.slap_bass(midi_to_freq(m), 0.36, rng) for m in [28, 40, 38, 43, 45]}
    fk_evs = [
        (0, '28', 1.0, 0.5), (2, '40', 0.88, 0.5), (6, '28', 0.85, 0.5), (7, '40', 0.9, 0.5),
        (10, '43', 0.9, 0.5), (12, '38', 0.88, 0.5), (14, '40', 0.92, 0.5),
        (16, '28', 1.0, 0.5), (18, '40', 0.88, 0.5), (22, '28', 0.85, 0.5), (23, '45', 0.92, 0.5),
        (26, '43', 0.9, 0.5), (28, '40', 0.88, 0.5), (30, '38', 0.9, 0.5),
    ]
    kio.emit('16_LOOPS/melodic_loops/funk_slap_groove_118bpm_Em.wav',
             F3.render_exact_loop(118, 2, fk_voices, fk_evs, rng=rng),
             'LOOP_MELODIC', 'funk_slap', root_note='E1', bpm=118, trim=False, is_loop=True)


def build_midi_library(out_root):
    print('[6/7] Generating 84 studio MIDI files (drum grooves, FL hat rolls, chord progressions, basslines)...')
    midi_root = os.path.join(out_root, '17_MIDI')

    # --- A) 20 Multi-Genre Drum Pattern MIDIs (GM Drum Map: 36 Kick, 38 Snare, 39 Clap, 42 CH, 46 OH, 51 Ride, 56 Cowbell)
    GM_DRUM_PATTERNS = [
        ('baile_funk_130bpm', 130, [(0, 36), (0.75, 38), (1.5, 36), (2.0, 38), (2.75, 38), (3.0, 36), (3.5, 38)]),
        ('postpunk_148bpm', 148, [(0, 36), (1.0, 38), (1.5, 36), (2.0, 36), (2.5, 36), (3.0, 38), (3.5, 46)] + [(s * 0.25, 42) for s in range(14)]),
        ('jazz_swing_120bpm', 120, [(0, 51), (1.0, 51), (1.0, 44), (1.66, 51), (2.0, 51), (3.0, 51), (3.0, 44), (3.66, 51), (0, 36), (2.66, 38)]),
        ('bossa_nova_116bpm', 116, [(0, 36), (0.75, 36), (1.0, 36), (1.75, 36), (2.0, 36), (2.75, 36), (3.0, 36), (3.75, 36), (0, 37), (0.75, 37), (1.5, 37), (2.5, 37), (3.25, 37)] + [(s * 0.5, 42) for s in range(8)]),
        ('disco_funk_118bpm', 118, [(b, 36) for b in range(4)] + [(1, 38), (1, 39), (3, 38), (3, 39)] + [(b + 0.5, 46) for b in range(4)] + [(b + o, 42) for b in range(4) for o in (0.0, 0.25, 0.75)]),
        ('synthwave_108bpm', 108, [(0, 36), (1, 38), (2, 36), (2.5, 36), (3, 38)] + [(s * 0.5, 42) for s in range(8)]),
        ('rnb_neosoul_86bpm', 86, [(0, 36), (1, 37), (1.75, 36), (2.5, 36), (3, 37)] + [(s * 0.25, 42) for s in range(16)]),
        ('psytrance_140bpm', 140, [(b, 36) for b in range(4)] + [(1, 38), (3, 38)] + [(b + 0.5, 46) for b in range(4)] + [(s * 0.25, 42) for s in range(16) if s % 2 == 1]),
        ('dubstep_halftime_140bpm', 140, [(0, 36), (2.0, 38), (2.75, 36), (3.5, 36)] + [(s * 0.5, 42) for s in range(8)]),
        ('afrobeats_104bpm', 104, [(0, 36), (0.75, 37), (1.5, 37), (1.75, 36), (2.0, 36), (2.5, 37), (3.0, 37), (3.75, 36)] + [(s * 0.25, 42) for s in range(16)]),
        ('rock_driving_124bpm', 124, [(0, 36), (1, 38), (1.5, 36), (2, 36), (2.5, 36), (3, 38)] + [(s * 0.5, 46) for s in range(8)]),
        ('metal_doublekick_160bpm', 160, [(s * 0.25, 36) for s in range(16)] + [(1, 38), (3, 38)] + [(b, 51) for b in range(4)]),
        ('reggae_onedrop_78bpm', 78, [(2.0, 36), (2.0, 37)] + [(s * 0.5, 42) for s in range(8)]),
        ('pluggnb_144bpm', 144, [(0, 36), (1, 39), (1.75, 37), (2.5, 36), (3, 39), (3.5, 37)] + [(s * 0.5, 42) for s in range(8)]),
        ('rage_opium_152bpm', 152, [(0, 36), (1, 39), (1.5, 36), (2.5, 36), (3, 39)] + [(s * 0.5, 42) for s in range(8)]),
        ('hardbass_155bpm', 155, [(b, 36) for b in range(4)] + [(b + 0.5, 56) for b in range(4)] + [(1, 39), (3, 39)]),
        ('gabber_rave_180bpm', 180, [(b, 36) for b in range(4)] + [(b + 0.5, 46) for b in range(4)] + [(1, 39), (3, 39)]),
        ('ska_upbeat_150bpm', 150, [(0, 36), (1, 38), (2, 36), (3, 38)] + [(b + 0.5, 46) for b in range(4)]),
        ('waltz_3_4_cinematic_108bpm', 108, [(0, 36), (1, 42), (2, 42), (3, 36), (4, 38), (5, 42)]),
        ('country_train_beat_126bpm', 126, [(0, 36), (2, 36)] + [(s * 0.25, 38) for s in range(16)]),
    ]
    for pname, bpm, bar1 in GM_DRUM_PATTERNS:
        notes_2bar = []
        for bar_i in range(2):
            for beat_pos, pitch in bar1:
                vel = 108 if pitch in (36, 38, 39) else 84
                notes_2bar.append((bar_i * 4.0 + beat_pos, 0.20, pitch, vel))
        write_midi(f'{midi_root}/drum_patterns/{pname}_drums.mid',
                   [{'name': pname, 'channel': 9, 'notes': notes_2bar}], bpm=bpm)

    # --- B) 16 FL Studio Hi-Hat & Snare Roll MIDIs (pitched around C5 = MIDI 72 for Piano Roll!)
    HAT_ROLLS = [
        ('trap_triplet_bounce_140bpm', 140, [(i * 0.5, 0.2, 72, 95) for i in range(16)] + [(3.0 + k / 6.0, 0.12, 72 - k % 3, 85 + k * 4) for k in range(6)]),
        ('southside_fast_32nd_148bpm', 148, [(i * 0.5, 0.2, 72, 98) for i in range(16)] + [(1.5 + k * 0.125, 0.1, 72, 78 + k * 6) for k in range(4)] + [(5.5 + k * 0.125, 0.1, 74 - k, 90) for k in range(4)]),
        ('uk_drill_counter_bounce_142bpm', 142, [(p * 0.25, 0.18, 72, 102 if p in (0, 3, 6, 12) else 76) for p in [0, 3, 6, 8, 11, 12, 14, 16, 19, 22, 24, 27, 28, 30, 31]]),
        ('ny_drill_stutter_144bpm', 144, [(p * 0.25, 0.15, 72, 96) for p in [0, 3, 6, 7, 10, 12, 15, 16, 19, 22, 25, 26, 27, 28, 30]]),
        ('pluggnb_bouncy_144bpm', 144, [(i * 0.5, 0.2, 72, 90) for i in range(16)] + [(2.75, 0.15, 74, 82), (6.75, 0.15, 71, 82), (7.5, 0.12, 69, 88), (7.75, 0.12, 67, 92)]),
        ('rage_opium_staircase_152bpm', 152, [(i * 0.5, 0.2, 72, 95) for i in range(14)] + [(7.0 + k * 0.125, 0.1, 76 - k, 96) for k in range(8)]),
        ('phonk_memphis_roll_160bpm', 160, [(i * 0.5, 0.2, 72, 95) for i in range(16)] + [(3.5 + k * 0.125, 0.1, 72, 90) for k in range(4)]),
        ('ukg_shuffled_132bpm', 132, [(b + o, 0.18, 72, 95 if o == 0.5 else 72) for b in range(8) for o in (0.0, 0.5, 0.83)]),
        ('dnb_fast_16th_roller_174bpm', 174, [(i * 0.25, 0.15, 72, 100 if i % 4 == 2 else 74) for i in range(32)]),
        ('house_groovy_16th_126bpm', 126, [(i * 0.25, 0.16, 72, 105 if i % 4 == 2 else 68) for i in range(32)]),
        ('lofi_drunk_swing_82bpm', 82, [(i * 0.5 + (0.08 if i % 2 == 1 else 0.0), 0.25, 72, 85 if i % 2 == 0 else 64) for i in range(16)]),
        ('jazz_ride_spang_a_lang_120bpm', 120, [(b, 0.4, 72, 96) for b in range(8)] + [(b + 0.67, 0.25, 72, 80) for b in (1, 3, 5, 7)]),
        ('edm_pitch_rising_snare_roll_128bpm', 128, [(i * 0.25, 0.18, 60 + i // 2, 70 + int(i * 1.7)) for i in range(32)]),
        ('afrobeats_shaker_groove_104bpm', 104, [(i * 0.25, 0.16, 72, 95 if i % 4 in (0, 3) else 66) for i in range(32)]),
        ('baile_chop_roll_130bpm', 130, [(p * 0.25, 0.18, 72, 98) for p in [0, 3, 6, 8, 11, 14, 16, 19, 22, 24, 26, 28, 29, 30, 31]]),
        ('westcoast_bounce_hat_98bpm', 98, [(i * 0.25, 0.16, 72, 92 if i % 2 == 0 else 70) for i in range(32)]),
    ]
    for rname, bpm, rnotes in HAT_ROLLS:
        write_midi(f'{midi_root}/hihat_rolls/{rname}.mid',
                   [{'name': rname, 'channel': 0, 'notes': rnotes}], bpm=bpm)

    # --- C) 32 Multi-Genre Chord Progressions (4 bars = 16 beats, rich voicings + bass note!)
    PROGRESSIONS = [
        # (genre_name, bpm, root_pc, root_label, list_of_4_chords_as_semitone_offsets_from_C3)
        ('trap_dark_phrygian', 140, 2, 'Dm', [[0, 7, 12, 15, 19], [1, 8, 13, 17, 20], [0, 7, 12, 15, 19], [-2, 5, 10, 15, 17]]),
        ('trap_dark_phrygian', 140, 4, 'Em', [[0, 7, 12, 15, 19], [1, 8, 13, 17, 20], [0, 7, 12, 15, 19], [-2, 5, 10, 15, 17]]),
        ('pluggnb_dreamy_min9', 144, 5, 'Fm', [[0, 7, 10, 14, 15, 19], [-4, 3, 7, 11, 15], [-2, 5, 8, 12, 17], [-5, 2, 7, 11, 14]]),
        ('pluggnb_dreamy_min9', 144, 9, 'Am', [[0, 7, 10, 14, 15, 19], [-4, 3, 7, 11, 15], [-2, 5, 8, 12, 17], [-5, 2, 7, 11, 14]]),
        ('neosoul_rnb_lush', 86, 2, 'Dm', [[0, 7, 10, 14, 15, 19], [5, 12, 15, 19, 21], [-2, 5, 9, 12, 16], [-5, 1, 4, 10, 13]]),
        ('neosoul_rnb_lush', 86, 7, 'Gm', [[0, 7, 10, 14, 15, 19], [5, 12, 15, 19, 21], [-2, 5, 9, 12, 16], [-5, 1, 4, 10, 13]]),
        ('anime_jpop_royal_road', 128, 0, 'C', [[5, 12, 16, 19, 23], [7, 14, 19, 23, 26], [4, 11, 16, 19, 23], [9, 16, 21, 24, 28]]),
        ('anime_jpop_royal_road', 128, 5, 'F', [[5, 12, 16, 19, 23], [7, 14, 19, 23, 26], [4, 11, 16, 19, 23], [9, 16, 21, 24, 28]]),
        ('postpunk_doomer_wave', 148, 4, 'Em', [[0, 7, 12, 15, 19], [-4, 3, 8, 12, 15], [3, 10, 15, 19, 22], [-2, 5, 10, 14, 17]]),
        ('postpunk_doomer_wave', 148, 9, 'Am', [[0, 7, 12, 15, 19], [-4, 3, 8, 12, 15], [3, 10, 15, 19, 22], [-2, 5, 10, 14, 17]]),
        ('jazz_ii_V_I_VI7alt', 120, 0, 'C', [[2, 9, 12, 16, 17], [7, 13, 17, 20, 23], [0, 7, 11, 14, 16], [9, 15, 19, 22, 24]]),
        ('jazz_ii_V_I_VI7alt', 120, 10, 'Bb', [[2, 9, 12, 16, 17], [7, 13, 17, 20, 23], [0, 7, 11, 14, 16], [9, 15, 19, 22, 24]]),
        ('bossa_nova_sunset', 116, 7, 'Gm', [[0, 7, 10, 14, 15], [5, 11, 14, 17, 21], [-2, 5, 9, 12, 16], [-3, 3, 7, 10, 13]]),
        ('flamenco_andalusian', 110, 9, 'Am', [[0, 7, 12, 15, 19], [-2, 5, 10, 14, 17], [-4, 3, 8, 12, 15], [-5, 2, 7, 11, 16]]),
        ('synthwave_80s_epic', 108, 9, 'Am', [[0, 7, 12, 15, 19], [-4, 3, 8, 12, 16], [3, 10, 15, 19, 22], [5, 12, 17, 21, 24]]),
        ('synthwave_80s_epic', 108, 2, 'Dm', [[0, 7, 12, 15, 19], [-4, 3, 8, 12, 16], [3, 10, 15, 19, 22], [5, 12, 17, 21, 24]]),
        ('house_deep_soulful', 124, 0, 'Cm', [[0, 7, 10, 14, 15], [3, 10, 14, 17, 19], [5, 12, 15, 19, 20], [7, 14, 17, 20, 23]]),
        ('ukg_2step_chords', 132, 4, 'Em', [[0, 7, 10, 14, 15], [-2, 5, 9, 12, 14], [-4, 3, 7, 11, 14], [-5, 2, 6, 10, 14]]),
        ('rage_opium_anthem', 152, 5, 'Fm', [[0, 7, 12, 15], [8, 15, 20, 24], [7, 14, 19, 22], [1, 8, 13, 17]]),
        ('drill_gritty_strings', 142, 0, 'Cm', [[0, 7, 12, 15], [1, 8, 12, 17], [0, 7, 12, 15], [-1, 7, 11, 14]]),
        ('cinematic_zimmer_epic', 100, 2, 'Dm', [[0, 7, 12, 15, 19], [-4, 3, 8, 12, 16], [3, 10, 15, 19, 22], [-5, 2, 7, 11, 14]]),
        ('midwest_emo_indie', 130, 5, 'Fmaj9', [[0, 7, 11, 14, 16], [4, 11, 14, 16, 19], [9, 16, 19, 23, 24], [7, 14, 16, 19, 23]]),
        ('pop_axis_hit', 120, 0, 'C', [[0, 7, 12, 16, 19], [7, 14, 19, 23, 26], [9, 16, 21, 24, 28], [5, 12, 17, 21, 24]]),
        ('pop_axis_hit', 120, 7, 'G', [[0, 7, 12, 16, 19], [7, 14, 19, 23, 26], [9, 16, 21, 24, 28], [5, 12, 17, 21, 24]]),
        ('blues_12bar_turnaround', 96, 9, 'A7', [[0, 7, 10, 16, 19], [5, 12, 15, 21, 24], [0, 7, 10, 16, 19], [7, 14, 17, 23, 26]]),
        ('disco_french_touch', 120, 6, 'F#m', [[0, 7, 10, 15, 19], [2, 9, 14, 18, 21], [-2, 5, 9, 14, 17], [4, 11, 15, 19, 23]]),
        ('reggae_dub_skank', 78, 9, 'Am', [[0, 7, 12, 15, 19], [5, 12, 17, 20, 24], [0, 7, 12, 15, 19], [7, 14, 19, 22, 26]]),
        ('dnb_liquid_atmospheric', 174, 5, 'Fm', [[0, 7, 10, 14, 15, 19], [-4, 3, 7, 11, 14, 19], [3, 10, 14, 17, 22], [-2, 5, 9, 12, 17]]),
        ('country_folk_warm', 112, 7, 'G', [[0, 7, 12, 16, 19], [5, 12, 17, 21, 24], [0, 7, 12, 16, 19], [7, 14, 19, 23, 26]]),
        ('russian_romance_ballad', 92, 9, 'Am', [[0, 7, 12, 15, 19], [5, 12, 17, 20, 24], [7, 14, 19, 23, 26], [0, 7, 12, 16, 20]]),
        ('gospel_organ_uplift', 110, 3, 'Eb', [[0, 7, 11, 14, 16], [4, 10, 15, 19], [5, 12, 16, 19, 21], [6, 12, 15, 18, 21]]),
        ('cyberpunk_industrial', 132, 2, 'Dm', [[0, 7, 12], [1, 8, 13], [0, 7, 12], [6, 13, 18]]),
    ]
    for gname, bpm, rpc, rlbl, chords in PROGRESSIONS:
        base_m = 48 + rpc
        c_notes = []
        for idx, ivs in enumerate(chords):
            start_b = idx * 4.0
            for iv in ivs:
                c_notes.append((start_b, 3.9, base_m + iv, 92))
        write_midi(f'{midi_root}/progressions/{gname}_{rlbl}.mid',
                   [{'name': f'{gname}_{rlbl}', 'channel': 0, 'notes': c_notes}], bpm=bpm)

    # --- D) 16 Genre Bassline MIDIs (2 bars = 8 beats)
    BASSLINES = [
        ('trap_808_bounce_Dm_140bpm', 140, [(0, 1.5, 38, 115), (1.5, 1.0, 38, 108), (2.5, 1.5, 45, 112), (4.0, 1.5, 38, 115), (5.5, 1.0, 39, 110), (6.5, 0.75, 46, 114), (7.25, 0.75, 45, 110)]),
        ('drill_808_glide_Cm_142bpm', 142, [(0, 2.5, 36, 118), (2.5, 0.5, 48, 115), (3.0, 0.5, 51, 118), (3.5, 0.5, 48, 112), (4.0, 2.0, 37, 116), (6.0, 0.5, 49, 114), (6.5, 0.5, 55, 118), (7.0, 1.0, 36, 115)]),
        ('funk_slap_octaves_Em_118bpm', 118, [(0, 0.4, 28, 112), (0.5, 0.4, 40, 105), (1.5, 0.25, 28, 100), (1.75, 0.4, 40, 110), (2.5, 0.4, 43, 108), (3.0, 0.4, 38, 104), (3.5, 0.4, 40, 110), (4.0, 0.4, 28, 112), (4.5, 0.4, 40, 105), (5.75, 0.4, 45, 112), (6.5, 0.4, 43, 108), (7.0, 0.4, 40, 105), (7.5, 0.4, 38, 106)]),
        ('disco_octave_pump_Am_120bpm', 120, [(b * 0.5, 0.42, 33 if b % 2 == 0 else 45, 106) for b in range(16)]),
        ('postpunk_driving_8ths_Em_148bpm', 148, [(i * 0.5, 0.42, 40 if i < 4 else (36 if i < 8 else (33 if i < 12 else 35)), 104) for i in range(16)]),
        ('jazz_walking_bass_C_120bpm', 120, [(0, 0.95, 36, 95), (1, 0.95, 40, 92), (2, 0.95, 43, 94), (3, 0.95, 42, 90), (4, 0.95, 41, 96), (5, 0.95, 45, 92), (6, 0.95, 43, 95), (7, 0.95, 35, 90)]),
        ('house_m1_organ_Cm_126bpm', 126, [(0.5, 0.4, 36, 110), (1.25, 0.4, 36, 100), (1.75, 0.5, 39, 108), (2.5, 0.5, 41, 110), (3.5, 0.4, 43, 106), (4.5, 0.4, 36, 110), (5.25, 0.4, 36, 100), (5.75, 0.5, 46, 112), (6.5, 0.5, 43, 108), (7.5, 0.4, 41, 104)]),
        ('acid_303_squelch_Am_134bpm', 134, [(i * 0.25, 0.2, p, 118 if i in (0, 3, 6, 12, 18, 25) else 85) for i, p in enumerate([33, 33, 45, 33, 36, 33, 48, 45, 33, 33, 40, 41, 45, 33, 36, 35] * 2)]),
        ('psytrance_kbbb_rolling_Fm_140bpm', 140, [(b + o, 0.2, 29, 108) for b in range(8) for o in (0.25, 0.5, 0.75)]),
        ('hardbass_offbeat_donk_Am_155bpm', 155, [(b + 0.5, 0.4, p, 115) for b, p in enumerate([45, 45, 48, 45, 41, 41, 40, 43])]),
        ('reggae_onedrop_sub_Am_78bpm', 78, [(0.5, 0.75, 33, 108), (1.5, 0.5, 36, 102), (2.0, 1.0, 40, 110), (4.5, 0.75, 29, 108), (5.5, 0.5, 33, 102), (6.0, 1.0, 31, 108)]),
        ('amapiano_logdrum_bounce_Fm_112bpm', 112, [(0, 0.75, 29, 112), (0.75, 0.75, 29, 106), (1.5, 0.5, 36, 115), (2.5, 0.75, 29, 110), (3.25, 0.5, 34, 114), (4.0, 0.75, 25, 112), (4.75, 0.75, 25, 106), (5.5, 0.5, 37, 118), (6.5, 0.75, 28, 110), (7.25, 0.5, 36, 112)]),
        ('synthwave_8th_bass_Am_108bpm', 108, [(i * 0.25, 0.2, 33 if i < 8 else (29 if i < 16 else (36 if i < 24 else 31)), 102) for i in range(32)]),
        ('rnb_neosoul_pocket_Dm_86bpm', 86, [(0, 1.5, 38, 104), (1.75, 1.0, 40, 98), (3.0, 1.0, 41, 102), (4.0, 1.5, 33, 104), (5.75, 1.0, 36, 98), (7.0, 1.0, 38, 100)]),
        ('baile_sub_groove_Cm_130bpm', 130, [(0, 1.25, 24, 118), (1.5, 1.25, 24, 115), (3.0, 1.0, 27, 116), (4.0, 1.25, 24, 118), (5.5, 1.25, 24, 115), (7.0, 1.0, 26, 116)]),
        ('dnb_reese_roller_Fm_174bpm', 174, [(0, 2.5, 29, 114), (2.5, 1.5, 32, 112), (4.0, 2.5, 25, 114), (6.5, 1.5, 28, 112)]),
    ]
    for bname, bpm, bnotes in BASSLINES:
        write_midi(f'{midi_root}/basslines/{bname}.mid',
                   [{'name': bname, 'channel': 0, 'notes': bnotes}], bpm=bpm)


def build_kit_maps_and_demo(out_root, rng):
    print('[7/7] Building verified full-keyboard SFZ maps, 24 genre 16-pad layouts & 8-genre audio demo...')
    from kitlib_v3.midi_sfz import note_str_to_midi

    # Group all tuned instruments (14_MELODIC, 12_808_SUB, 13_BASS, drift_cowbell_tuned, tonal_perc) into SFZs!
    by_instr = {}
    for row in kio.INDEX:
        rn = row['root_note']
        rel = row['path']
        cat = row['category']
        st = row['style']
        if not rn or cat in ('CHORD', 'LOOP_MELODIC', 'FX'):
            continue
        if st == '808_drill_slide_long':
            continue
        try:
            m = note_str_to_midi(rn)
        except ValueError:
            continue
        by_instr.setdefault(st, []).append((m, rel))

    mel_sfz_dir = os.path.join(out_root, '18_KIT_MAPS', 'melodic_and_bass_sfz')
    for instr_name, entries in sorted(by_instr.items()):
        if len(entries) >= 4:
            rel_s = 0.85 if 'pad' in instr_name or 'drone' in instr_name else 0.35
            write_melodic_sfz(
                os.path.join(mel_sfz_dir, f'{instr_name}.sfz'),
                out_root, instr_name, entries, release_s=rel_s,
            )

    # Helper to pick indexed relative paths
    all_paths = [r['path'] for r in kio.INDEX]

    def pick(prefix, idx=0):
        matches = [p for p in all_paths if p.startswith(prefix)]
        if not matches:
            raise KeyError(f'No sample found for prefix: {prefix}')
        return matches[min(idx, len(matches) - 1)]

    GENRE_PAD_SPECS = {
        '01_baile_funk_automotivo': [
            ('Kick 1', '01_KICKS/baile_funk'), ('Kick 2', '01_KICKS/modern_pop'),
            ('Snare', '02_SNARES/baile_funk'), ('Clap', '03_CLAPS/baile_clap'),
            ('Cuica Hi', '09_PERC_ACOUSTIC/cuica'), ('Hat Closed', '05_HATS_CLOSED/baile_hat'),
            ('Hat Open', '06_HATS_OPEN/disco_sizzle'), ('Automotivo Stab', '10_PERC_ELECTRONIC/automotivo_stab'),
            ('808 Spinz', '12_808_SUB/808_spinz_pro'), ('808 Opium', '12_808_SUB/808_opium_buzz'),
            ('Cowbell C5', '09_PERC_ACOUSTIC/drift_cowbell_tuned'), ('FX Siren', '15_FX/dub_sirens'),
            ('Brass Stab', '14_MELODIC/brass/funk_brass_section'), ('Rage Lead', '14_MELODIC/synths/rage_lead'),
            ('Drum Loop', '16_LOOPS/drum_loops/baile_funk'), ('Fill', '19_FILLS_ROLLS/fill_baile'),
        ],
        '02_postpunk_doomer_wave': [
            ('Kick 1', '01_KICKS/postpunk'), ('Kick 2', '01_KICKS/disco'),
            ('Snare Room', '02_SNARES/postpunk'), ('Snare 80s', '02_SNARES/synthwave_gated'),
            ('Clap', '03_CLAPS/modern_pop'), ('Hat Closed', '05_HATS_CLOSED/postpunk'),
            ('Hat Open', '06_HATS_OPEN/postpunk'), ('Simmons Tom', '08_TOMS/simmons_80s'),
            ('Picked Bass', '13_BASS/picked_rock_bass'), ('Moog Bass', '13_BASS/moog_fat_bass'),
            ('Shimmer Guitar', '14_MELODIC/guitars/shimmer_guitar'), ('Retro Poly', '14_MELODIC/synths/retro_poly80'),
            ('Dark Pad', '14_MELODIC/pads/pad_cs80_dark'), ('TapeStrings', '14_MELODIC/pads/pad_tape_strings'),
            ('Drum Loop', '16_LOOPS/drum_loops/postpunk'), ('Bass Riff Loop', '16_LOOPS/melodic_loops/postpunk_bass'),
        ],
        '03_drift_phonk_memphis': [
            ('Kick Hard', '01_KICKS/baile_funk'), ('Kick Gabber', '01_KICKS/gabber_hardcore'),
            ('Snare Crisp', '02_SNARES/modern_pop'), ('Clap', '03_CLAPS/modern_pop'),
            ('Cowbell A4', '09_PERC_ACOUSTIC/drift_cowbell_tuned'), ('Hat Tight', '05_HATS_CLOSED/rnb_tight'),
            ('Hat Open', '06_HATS_OPEN/synthwave'), ('Cowbell E5', '09_PERC_ACOUSTIC/drift_cowbell_tuned'),
            ('808 Opium', '12_808_SUB/808_opium_buzz'), ('808 Spinz', '12_808_SUB/808_spinz_pro'),
            ('Braaam FX', '15_FX/cinema_braaam'), ('Tape Stop', '15_FX/tape_stops'),
            ('Cowbell Loop', '16_LOOPS/melodic_loops/phonk_cowbell'), ('Cassette Hiss', '15_FX/atmos_loops/cassette'),
            ('Sub Drop', '15_FX/sub_drops'), ('Triplet Fill', '19_FILLS_ROLLS/fill_trap_triplet'),
        ],
        '04_rage_opium_yeat': [
            ('Kick Punch', '01_KICKS/modern_pop'), ('Kick Hard', '01_KICKS/gabber_hardcore'),
            ('Snare Pop', '02_SNARES/modern_pop'), ('Clap Wide', '03_CLAPS/modern_pop'),
            ('Church Bell', '20_TONAL_PERC/church_bell'), ('Hat Closed', '05_HATS_CLOSED/rnb_tight'),
            ('Hat Open', '06_HATS_OPEN/synthwave'), ('Cyber Riser', '15_FX/cyber_risers'),
            ('808 Opium Buzz', '12_808_SUB/808_opium_buzz'), ('808 Spinz Pro', '12_808_SUB/808_spinz_pro'),
            ('Rage Lead C4', '14_MELODIC/synths/rage_lead'), ('Hyperpop Lead', '14_MELODIC/synths/hyperpop_lead'),
            ('Pipe Organ', '14_MELODIC/keys/pipe_organ'), ('Rage Loop', '16_LOOPS/melodic_loops/rage_synths'),
            ('Drum Loop', '16_LOOPS/drum_loops/rage_opium'), ('Sub Drop', '15_FX/sub_drops'),
        ],
        '05_pluggnb_dreamy_rnb': [
            ('Kick Soft', '01_KICKS/rnb_neosoul'), ('Kick Pop', '01_KICKS/modern_pop'),
            ('Rim Snare', '02_SNARES/rnb_rim_snare'), ('Finger Clap', '03_CLAPS/rnb_finger_clap'),
            ('Ghost Snare', '02_SNARES/ghost_notes'), ('Hat Tight', '05_HATS_CLOSED/rnb_tight'),
            ('Hat Open', '06_HATS_OPEN/rnb'), ('Reverse Swell', '15_FX/reverse_swells'),
            ('808 Spinz', '12_808_SUB/808_spinz_pro'), ('Fretless Bass', '13_BASS/fretless_bass'),
            ('Pluggnb Lead', '14_MELODIC/synths/pluggnb_lead'), ('Pluggnb Bell', '14_MELODIC/synths/pluggnb_bell'),
            ('Rhodes Chord', '14_MELODIC/chords_stabs/neosoul_rhodes_chord'), ('Shimmer Pad', '14_MELODIC/pads/pad_shimmer_stereo'),
            ('Pluggnb Loop', '16_LOOPS/drum_loops/pluggnb'), ('Rhodes Loop', '16_LOOPS/melodic_loops/neosoul_rhodes'),
        ],
        '06_jazz_club_quartet': [
            ('Jazz Kick', '01_KICKS/jazz'), ('Jazz Tom', '08_TOMS/jazz_tuned'),
            ('Brush Tap', '02_SNARES/jazz_brush_tap'), ('Brush Sweep', '02_SNARES/jazz_brush_sweep'),
            ('Ghost Snare', '02_SNARES/ghost_notes'), ('Foot Chick Hat', '05_HATS_CLOSED/jazz_foot_chick'),
            ('Sizzle Ride', '07_CYMBALS/jazz_sizzle_ride'), ('Ride Bell', '07_CYMBALS/jazz_ride_bell'),
            ('Upright Bass C1', '13_BASS/upright_double_bass'), ('Fretless Bass', '13_BASS/fretless_bass'),
            ('Concert Grand', '14_MELODIC/keys/concert_grand'), ('Jazz Guitar', '14_MELODIC/guitars/jazz_guitar'),
            ('Tenor Sax', '14_MELODIC/winds/tenor_sax'), ('Alto Sax', '14_MELODIC/winds/alto_sax'),
            ('Swing Loop', '16_LOOPS/drum_loops/jazz_swing'), ('Brush Fill', '19_FILLS_ROLLS/fill_jazz_brush'),
        ],
        '07_bossa_nova_latin': [
            ('Warm Kick', '01_KICKS/jazz'), ('Reggaeton Snare', '02_SNARES/reggaeton_dembow'),
            ('Rim Snare', '02_SNARES/rnb_rim_snare'), ('Brush Sweep', '02_SNARES/jazz_brush_sweep'),
            ('Cuica', '09_PERC_ACOUSTIC/cuica'), ('Closed Hat', '05_HATS_CLOSED/jazz_foot_chick'),
            ('Sizzle Ride', '07_CYMBALS/jazz_sizzle_ride'), ('Mellotron Flute', '14_MELODIC/keys/mellotron_flute'),
            ('Upright Bass', '13_BASS/upright_double_bass'), ('Nylon Guitar', '14_MELODIC/guitars/nylon_guitar'),
            ('Guitar Strum Min', '14_MELODIC/chords_stabs/acoustic_strum_minor'), ('Guitar Strum Maj', '14_MELODIC/chords_stabs/acoustic_strum_major'),
            ('Alto Sax', '14_MELODIC/winds/alto_sax'), ('Wurli EP', '14_MELODIC/keys/wurli_ep'),
            ('Bossa Loop', '16_LOOPS/drum_loops/bossa_nova'), ('Nylon Loop', '16_LOOPS/melodic_loops/bossa_nylon'),
        ],
        '08_disco_funk_citypop': [
            ('Disco Kick', '01_KICKS/disco'), ('Pop Kick', '01_KICKS/modern_pop'),
            ('Disco Snare', '02_SNARES/disco_funk'), ('Layered Clap', '03_CLAPS/disco_layered'),
            ('Ghost Snare', '02_SNARES/ghost_notes'), ('Crisp Hat', '05_HATS_CLOSED/disco_crisp'),
            ('Open Sizzle Hat', '06_HATS_OPEN/disco_sizzle'), ('Ride Bell', '07_CYMBALS/jazz_ride_bell'),
            ('Slap Bass', '13_BASS/slap_bass'), ('Moog Bass', '13_BASS/moog_fat_bass'),
            ('Clavinet', '14_MELODIC/keys/clavinet'), ('Funk Wah Guitar', '14_MELODIC/guitars/funk_wah_guitar'),
            ('Funk Brass Sec', '14_MELODIC/brass/funk_brass_section'), ('DX Crystal Bell', '14_MELODIC/synths/dx_crystal_bell'),
            ('Disco Loop', '16_LOOPS/drum_loops/disco_funk'), ('Slap Groove Loop', '16_LOOPS/melodic_loops/funk_slap'),
        ],
        '09_synthwave_retrowave_80s': [
            ('80s Kick', '01_KICKS/disco'), ('Pop Kick', '01_KICKS/modern_pop'),
            ('Gated Snare 1', '02_SNARES/synthwave_gated'), ('Disco Clap', '03_CLAPS/disco_layered'),
            ('Simmons Tom Hi', '08_TOMS/simmons_80s'), ('Hat Closed', '05_HATS_CLOSED/postpunk'),
            ('Hat Open 80s', '06_HATS_OPEN/synthwave'), ('Simmons Tom Low', '08_TOMS/simmons_80s'),
            ('Moog Fat Bass', '13_BASS/moog_fat_bass'), ('Picked Bass', '13_BASS/picked_rock_bass'),
            ('Retro Poly 80', '14_MELODIC/synths/retro_poly80'), ('CS-80 Dark Pad', '14_MELODIC/pads/pad_cs80_dark'),
            ('Alto Sax Solo', '14_MELODIC/winds/alto_sax'), ('DX Bell', '14_MELODIC/synths/dx_crystal_bell'),
            ('Synthwave Loop', '16_LOOPS/drum_loops/synthwave'), ('Simmons Fill', '19_FILLS_ROLLS/fill_synthwave_simmons'),
        ],
        '10_house_ukg_organ': [
            ('House Kick', '01_KICKS/disco'), ('Pop Kick', '01_KICKS/modern_pop'),
            ('House Snare', '02_SNARES/house'), ('House Clap', '03_CLAPS/disco_layered'),
            ('Rim Snare', '02_SNARES/rnb_rim_snare'), ('Crisp Hat', '05_HATS_CLOSED/disco_crisp'),
            ('Open Hat', '06_HATS_OPEN/disco_sizzle'), ('Ride Bell', '07_CYMBALS/jazz_ride_bell'),
            ('M1 Organ Bass', '13_BASS/donk_organ_bass'), ('Moog Bass', '13_BASS/moog_fat_bass'),
            ('House Organ Stab', '14_MELODIC/chords_stabs/house_organ_chord'), ('Dub Techno Chord', '14_MELODIC/chords_stabs/dub_techno_chord'),
            ('Concert Grand', '14_MELODIC/keys/concert_grand'), ('Tenor Sax', '14_MELODIC/winds/tenor_sax'),
            ('Organ Bass Loop', '16_LOOPS/melodic_loops/house_organ_bass'), ('EDM Buildup', '19_FILLS_ROLLS/fill_edm_snare'),
        ],
        '11_hardbass_rave_gabber': [
            ('Gabber Kick 1', '01_KICKS/gabber_hardcore'), ('Psy Kick', '01_KICKS/psytrance'),
            ('House Snare', '02_SNARES/house'), ('Wide Clap', '03_CLAPS/modern_pop'),
            ('Buildup Snare', '02_SNARES/edm_buildup_hit'), ('Hat Closed', '05_HATS_CLOSED/disco_crisp'),
            ('Open Hat', '06_HATS_OPEN/disco_sizzle'), ('Dub Siren', '15_FX/dub_sirens'),
            ('Hardbass Donk', '13_BASS/hardbass_donk'), ('M1 Organ Bass', '13_BASS/donk_organ_bass'),
            ('Rave Hoover', '14_MELODIC/synths/rave_hoover'), ('Psy FM Lead', '14_MELODIC/synths/psy_fm_lead'),
            ('Bayan Folk', '14_MELODIC/world/bayan'), ('Cyber Riser', '15_FX/cyber_risers'),
            ('Hardbass Loop', '16_LOOPS/drum_loops/hardbass'), ('EDM Buildup', '19_FILLS_ROLLS/fill_edm_snare'),
        ],
        '12_psytrance_acid_techno': [
            ('Psy Kick 1', '01_KICKS/psytrance'), ('Psy Kick 2', '01_KICKS/psytrance'),
            ('Techno Snare', '02_SNARES/house'), ('Clap', '03_CLAPS/modern_pop'),
            ('Automotivo Perc', '10_PERC_ELECTRONIC/automotivo_stab'), ('Hat Closed', '05_HATS_CLOSED/disco_crisp'),
            ('Open Hat', '06_HATS_OPEN/synthwave'), ('Cyber Riser', '15_FX/cyber_risers'),
            ('Moog Bass', '13_BASS/moog_fat_bass'), ('Neuro Bass', '13_BASS/neuro_bass'),
            ('Psy FM Lead', '14_MELODIC/synths/psy_fm_lead'), ('Dub Techno Chord', '14_MELODIC/chords_stabs/dub_techno_chord'),
            ('Rave Hoover', '14_MELODIC/synths/rave_hoover'), ('Dark Drone', '14_MELODIC/pads/drone_dark_cinema'),
            ('Psytrance Loop', '16_LOOPS/drum_loops/psytrance'), ('Sub Drop', '15_FX/sub_drops'),
        ],
        '13_dnb_neuro_dubstep': [
            ('Punch Kick', '01_KICKS/modern_pop'), ('Baile Sub Kick', '01_KICKS/baile_funk'),
            ('Pop Snare', '02_SNARES/modern_pop'), ('Wide Clap', '03_CLAPS/modern_pop'),
            ('Ghost Snare', '02_SNARES/ghost_notes'), ('Hat Crisp', '05_HATS_CLOSED/disco_crisp'),
            ('Open Hat', '06_HATS_OPEN/disco_sizzle'), ('Ride Bell', '07_CYMBALS/jazz_ride_bell'),
            ('Neuro Reese Bass', '13_BASS/neuro_bass'), ('808 Drill Slide', '12_808_SUB/808_drill_slide_long'),
            ('Rave Hoover', '14_MELODIC/synths/rave_hoover'), ('Glass Pad', '14_MELODIC/pads/pad_glass_ambient'),
            ('Braaam FX', '15_FX/cinema_braaam'), ('Dub Siren', '15_FX/dub_sirens'),
            ('Halftime Loop', '16_LOOPS/drum_loops/dubstep_halftime'), ('Cyber Riser', '15_FX/cyber_risers'),
        ],
        '14_metal_djent_rock': [
            ('Rock Kick', '01_KICKS/modern_pop'), ('Postpunk Kick', '01_KICKS/postpunk'),
            ('Punch Snare', '02_SNARES/modern_pop'), ('Disco Snare', '02_SNARES/disco_funk'),
            ('Ghost Snare', '02_SNARES/ghost_notes'), ('Closed Hat', '05_HATS_CLOSED/postpunk'),
            ('Open Hat', '06_HATS_OPEN/postpunk'), ('Ride Bell', '07_CYMBALS/jazz_ride_bell'),
            ('Picked Rock Bass', '13_BASS/picked_rock_bass'), ('8-Str Djent Chug', '14_MELODIC/guitars/metal_chug_8str'),
            ('Power Chord C2', '14_MELODIC/chords_stabs/rock_power_chord'), ('Acoustic Strum', '14_MELODIC/chords_stabs/acoustic_strum_minor'),
            ('Shimmer Guitar', '14_MELODIC/guitars/shimmer_guitar'), ('Pipe Organ', '14_MELODIC/keys/pipe_organ'),
            ('Doublekick Loop', '16_LOOPS/drum_loops/metal_doublekick'), ('Metal Fill', '19_FILLS_ROLLS/fill_metal_doublekick'),
        ],
        '15_indie_folk_country': [
            ('Warm Kick', '01_KICKS/jazz'), ('Disco Kick', '01_KICKS/disco'),
            ('Brush Tap', '02_SNARES/jazz_brush_tap'), ('Finger Clap', '03_CLAPS/rnb_finger_clap'),
            ('Rim Snare', '02_SNARES/rnb_rim_snare'), ('Foot Hat', '05_HATS_CLOSED/jazz_foot_chick'),
            ('Sizzle Ride', '07_CYMBALS/jazz_sizzle_ride'), ('Jazz Tom', '08_TOMS/jazz_tuned'),
            ('Upright Bass', '13_BASS/upright_double_bass'), ('Picked Bass', '13_BASS/picked_rock_bass'),
            ('Steel Acoustic', '14_MELODIC/guitars/steel_acoustic'), ('Strum Major', '14_MELODIC/chords_stabs/acoustic_strum_major'),
            ('Mandolin', '14_MELODIC/world/mandolin'), ('Ukulele', '14_MELODIC/world/ukulele'),
            ('Felt Upright', '14_MELODIC/keys/felt_upright'), ('Mellotron Flute', '14_MELODIC/keys/mellotron_flute'),
        ],
        '16_cis_russian_folk_fusion': [
            ('Punch Kick', '01_KICKS/postpunk'), ('Hardbass Kick', '01_KICKS/gabber_hardcore'),
            ('Snare', '02_SNARES/postpunk'), ('Clap', '03_CLAPS/disco_layered'),
            ('Church Bell', '20_TONAL_PERC/church_bell'), ('Closed Hat', '05_HATS_CLOSED/postpunk'),
            ('Open Hat', '06_HATS_OPEN/postpunk'), ('Taiko Drum', '20_TONAL_PERC/orchestral_taiko'),
            ('Upright Bass', '13_BASS/upright_double_bass'), ('Hardbass Donk', '13_BASS/hardbass_donk'),
            ('Balalaika', '14_MELODIC/world/balalaika'), ('Bayan Accordion', '14_MELODIC/world/bayan'),
            ('Gusli Zither', '14_MELODIC/world/gusli'), ('Duduk', '14_MELODIC/winds/duduk'),
            ('Nylon Guitar', '14_MELODIC/guitars/nylon_guitar'), ('Felt Upright', '14_MELODIC/keys/felt_upright'),
        ],
        '17_rnb_neosoul_lofi': [
            ('Neo-Soul Kick', '01_KICKS/rnb_neosoul'), ('Jazz Kick', '01_KICKS/jazz'),
            ('Rim Snare', '02_SNARES/rnb_rim_snare'), ('Finger Clap', '03_CLAPS/rnb_finger_clap'),
            ('Ghost Snare', '02_SNARES/ghost_notes'), ('Tight Hat', '05_HATS_CLOSED/rnb_tight'),
            ('Open Hat', '06_HATS_OPEN/rnb'), ('Kalimba Stereo', '14_MELODIC/mallets/kalimba_stereo'),
            ('Fretless Bass', '13_BASS/fretless_bass'), ('808 Spinz', '12_808_SUB/808_spinz_pro'),
            ('Wurli EP', '14_MELODIC/keys/wurli_ep'), ('Rhodes Min9', '14_MELODIC/chords_stabs/neosoul_rhodes_chord'),
            ('Felt Piano', '14_MELODIC/keys/felt_upright'), ('Tenor Sax', '14_MELODIC/winds/tenor_sax'),
            ('Vinyl Crackle', '15_FX/atmos_loops/vinyl'), ('Rain Texture', '15_FX/atmos_loops/rain'),
        ],
        '18_westcoast_gfunk_hiphop': [
            ('Punch Kick', '01_KICKS/rnb_neosoul'), ('Disco Kick', '01_KICKS/disco'),
            ('Funk Snare', '02_SNARES/disco_funk'), ('Layered Clap', '03_CLAPS/disco_layered'),
            ('Rim Snare', '02_SNARES/rnb_rim_snare'), ('Tight Hat', '05_HATS_CLOSED/rnb_tight'),
            ('Open Hat', '06_HATS_OPEN/disco_sizzle'), ('Cowbell', '09_PERC_ACOUSTIC/drift_cowbell_tuned'),
            ('Moog Fat Bass', '13_BASS/moog_fat_bass'), ('Slap Bass', '13_BASS/slap_bass'),
            ('G-Funk Whistle', '14_MELODIC/synths/gfunk_whistle_lead'), ('Wurli EP', '14_MELODIC/keys/wurli_ep'),
            ('Clavinet', '14_MELODIC/keys/clavinet'), ('Funk Wah Guitar', '14_MELODIC/guitars/funk_wah_guitar'),
            ('Brass Section', '14_MELODIC/brass/funk_brass_section'), ('Tape Stop', '15_FX/tape_stops'),
        ],
        '19_reggaeton_afrobeats': [
            ('Afro/Baile Kick', '01_KICKS/baile_funk'), ('Warm Kick', '01_KICKS/rnb_neosoul'),
            ('Dembow Snare', '02_SNARES/reggaeton_dembow'), ('Rim Snare', '02_SNARES/rnb_rim_snare'),
            ('Cuica', '09_PERC_ACOUSTIC/cuica'), ('Closed Hat', '05_HATS_CLOSED/baile_hat'),
            ('Open Hat', '06_HATS_OPEN/rnb'), ('Kalimba', '14_MELODIC/mallets/kalimba_stereo'),
            ('808 Spinz', '12_808_SUB/808_spinz_pro'), ('Moog Sub Bass', '13_BASS/moog_fat_bass'),
            ('Nylon Guitar', '14_MELODIC/guitars/nylon_guitar'), ('Alto Sax', '14_MELODIC/winds/alto_sax'),
            ('Pluggnb Bell', '14_MELODIC/synths/pluggnb_bell'), ('Dub Siren', '15_FX/dub_sirens'),
            ('Afrobeats Loop', '16_LOOPS/drum_loops/afrobeats'), ('Dembow Fill', '19_FILLS_ROLLS/fill_reggaeton_dembow'),
        ],
        '20_reggae_dub_roots': [
            ('Roots Kick', '01_KICKS/jazz'), ('Warm Kick', '01_KICKS/rnb_neosoul'),
            ('Rim Click', '02_SNARES/rnb_rim_snare'), ('Ghost Snare', '02_SNARES/ghost_notes'),
            ('Brush Tap', '02_SNARES/jazz_brush_tap'), ('Closed Hat', '05_HATS_CLOSED/jazz_foot_chick'),
            ('Open Hat', '06_HATS_OPEN/rnb'), ('Dub Siren FX', '15_FX/dub_sirens'),
            ('Upright Sub', '13_BASS/upright_double_bass'), ('Moog Sub', '13_BASS/moog_fat_bass'),
            ('Dub Delay Chord', '14_MELODIC/chords_stabs/dub_techno_chord'), ('Clavinet Skank', '14_MELODIC/keys/clavinet'),
            ('Pipe Organ', '14_MELODIC/keys/pipe_organ'), ('Trombone Horn', '14_MELODIC/brass/trombone'),
            ('One-Drop Loop', '16_LOOPS/drum_loops/reggae_onedrop'), ('Vinyl Crackle', '15_FX/atmos_loops/vinyl'),
        ],
        '21_uk_ny_drill_pro': [
            ('Drill Punch Kick', '01_KICKS/modern_pop'), ('Baile Sub Kick', '01_KICKS/baile_funk'),
            ('Counter Snare', '02_SNARES/reggaeton_dembow'), ('Rim Snare', '02_SNARES/rnb_rim_snare'),
            ('Clap', '03_CLAPS/modern_pop'), ('Tight Hat', '05_HATS_CLOSED/rnb_tight'),
            ('Open Hat', '06_HATS_OPEN/rnb'), ('Church Bell', '20_TONAL_PERC/church_bell'),
            ('808 Drill Slide 1', '12_808_SUB/808_drill_slide_long'), ('808 Spinz Pro', '12_808_SUB/808_spinz_pro'),
            ('Felt Piano', '14_MELODIC/keys/felt_upright'), ('Mellotron Strings', '14_MELODIC/keys/mellotron_strings'),
            ('French Horn', '14_MELODIC/brass/french_horn'), ('Dark Cinema Drone', '14_MELODIC/pads/drone_dark_cinema'),
            ('Braaam Hit', '15_FX/cinema_braaam'), ('Drill Fill', '19_FILLS_ROLLS/fill_drill_countersnare'),
        ],
        '22_cinematic_orchestral_epic': [
            ('Taiko Low', '20_TONAL_PERC/orchestral_taiko'), ('Taiko High', '20_TONAL_PERC/orchestral_taiko'),
            ('Epic Snare', '02_SNARES/synthwave_gated'), ('Wide Impact Clap', '03_CLAPS/disco_layered'),
            ('Church Bell', '20_TONAL_PERC/church_bell'), ('Ride Cymbal', '07_CYMBALS/jazz_sizzle_ride'),
            ('Sub Drop', '15_FX/sub_drops'), ('Braaam Horn', '15_FX/cinema_braaam'),
            ('Tuba Low', '14_MELODIC/brass/tuba_stab'), ('French Horn', '14_MELODIC/brass/french_horn'),
            ('Trombone', '14_MELODIC/brass/trombone'), ('Oboe', '14_MELODIC/winds/oboe'),
            ('Bassoon', '14_MELODIC/winds/bassoon'), ('Duduk', '14_MELODIC/winds/duduk'),
            ('Erhu Bowed', '14_MELODIC/world/erhu'), ('Dark Drone', '14_MELODIC/pads/drone_dark_cinema'),
        ],
        '23_chiptune_8bit_arcade': [
            ('Pop Kick', '01_KICKS/modern_pop'), ('Psy Kick', '01_KICKS/psytrance'),
            ('Snare', '02_SNARES/postpunk'), ('Clap', '03_CLAPS/baile_clap'),
            ('Simmons Tom', '08_TOMS/simmons_80s'), ('Hat Tight', '05_HATS_CLOSED/rnb_tight'),
            ('Open Hat', '06_HATS_OPEN/postpunk'), ('Automotivo Blip', '10_PERC_ELECTRONIC/automotivo_stab'),
            ('Moog Bass', '13_BASS/moog_fat_bass'), ('Hardbass Donk', '13_BASS/hardbass_donk'),
            ('8-Bit Pulse Lead', '14_MELODIC/synths/chiptune_duty'), ('8-Bit Chord Arp', '14_MELODIC/synths/chiptune_arp'),
            ('Hyperpop Lead', '14_MELODIC/synths/hyperpop_lead'), ('DX Crystal Bell', '14_MELODIC/synths/dx_crystal_bell'),
            ('Tape Stop', '15_FX/tape_stops'), ('Cyber Riser', '15_FX/cyber_risers'),
        ],
        '24_modern_pop_kpop_hyperpop': [
            ('Pop Kick', '01_KICKS/modern_pop'), ('Disco Kick', '01_KICKS/disco'),
            ('Pop Snare', '02_SNARES/modern_pop'), ('Pop Clap', '03_CLAPS/modern_pop'),
            ('Finger Clap', '03_CLAPS/rnb_finger_clap'), ('Crisp Hat', '05_HATS_CLOSED/disco_crisp'),
            ('Open Hat', '06_HATS_OPEN/disco_sizzle'), ('Reverse Swell', '15_FX/reverse_swells'),
            ('Slap Bass', '13_BASS/slap_bass'), ('808 Spinz Pro', '12_808_SUB/808_spinz_pro'),
            ('Hyperpop Lead', '14_MELODIC/synths/hyperpop_lead'), ('Concert Grand', '14_MELODIC/keys/concert_grand'),
            ('Steel Acoustic', '14_MELODIC/guitars/steel_acoustic'), ('Funk Brass', '14_MELODIC/brass/funk_brass_section'),
            ('Shimmer Pad', '14_MELODIC/pads/pad_shimmer_stereo'), ('Cyber Riser', '15_FX/cyber_risers'),
        ],
    }

    drum_sfz_dir = os.path.join(out_root, '18_KIT_MAPS', 'drum_kits_v3')
    for kit_name, pad_defs in GENRE_PAD_SPECS.items():
        pad_entries = [(role, pick(pref, idx=(i % 3))) for i, (role, pref) in enumerate(pad_defs)]
        write_drum_kit_sfz_and_txt(drum_sfz_dir, out_root, kit_name, pad_entries)

    # Build 6-segment multi-genre full-arrangement showcase demo (drums + melodic/bass layered!)
    import soundfile as sf

    def to_stereo(arr):
        return np.repeat(arr, 2, axis=1) if arr.shape[1] == 1 else arr[:, :2]

    segs = []
    DEMO_PAIRS = [
        ('16_LOOPS/drum_loops/bossa_nova_116bpm.wav', '16_LOOPS/melodic_loops/bossa_nylon_chords_116bpm_Gm.wav'),
        ('16_LOOPS/drum_loops/postpunk_148bpm.wav', '16_LOOPS/melodic_loops/postpunk_bass_riff_148bpm_Em.wav'),
        ('16_LOOPS/drum_loops/rnb_neosoul_86bpm.wav', '16_LOOPS/melodic_loops/neosoul_rhodes_loop_86bpm_Dm.wav'),
        ('16_LOOPS/drum_loops/disco_funk_118bpm.wav', '16_LOOPS/melodic_loops/funk_slap_groove_118bpm_Em.wav'),
        ('16_LOOPS/drum_loops/rage_opium_152bpm.wav', '16_LOOPS/melodic_loops/rage_synths_152bpm_Fm.wav'),
        ('16_LOOPS/drum_loops/synthwave_108bpm.wav', '16_LOOPS/melodic_loops/synthwave_arp_108bpm_Am.wav'),
    ]
    for d_rel, m_rel in DEMO_PAIRS:
        d_wav = to_stereo(sf.read(os.path.join(out_root, d_rel), always_2d=True)[0])
        m_wav = to_stereo(sf.read(os.path.join(out_root, m_rel), always_2d=True)[0])
        L = min(len(d_wav), len(m_wav))
        mixed = d_wav[:L] * 0.82 + m_wav[:L] * 0.62
        segs.append(fade(normalize(mixed, -1.2), 0.012, 0.08))
        segs.append(np.zeros((int(0.18 * FS), 2)))

    demo = np.concatenate(segs, axis=0)
    kio.emit('00_START_HERE/DEMO_v3_6_zhanrov.wav', demo, 'DEMO', 'showcase', trim=False)


def main():
    t0 = time.time()
    out_root = sys.argv[1] if len(sys.argv) > 1 else 'build_v3'
    kio.set_root(out_root)
    rng = np.random.default_rng(20261122)

    build_drums_and_perc(rng)
    build_basses(rng)
    build_melodic_and_chords(rng)
    build_fx_and_fills(rng)
    build_loops(rng)
    build_midi_library(out_root)
    build_kit_maps_and_demo(out_root, rng)

    kio.save_index(os.path.join(out_root, 'KIT_INDEX_v3.csv'))
    elapsed = time.time() - t0
    tot_s = sum(r['seconds'] for r in kio.INDEX)
    print(f'DONE in {elapsed:.1f}s! WAV count: {len(kio.INDEX)} ({tot_s/60.0:.1f} min audio)')


if __name__ == '__main__':
    main()
