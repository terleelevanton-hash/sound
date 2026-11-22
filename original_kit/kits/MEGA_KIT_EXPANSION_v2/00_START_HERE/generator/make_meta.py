"""Build index CSV, SFZ maps and recommended-kit pad layouts."""
import os, glob, csv, re, numpy as np, soundfile as sf
from sys import path; path.insert(0, 'work')

ROOT = 'build/kit'
CAT_TAG = {
    '01_KICKS': 'KICK', '02_SNARES': 'SNARE', '03_CLAPS': 'CLAP', '04_SNAPS_RIMS_STICKS': 'SNAP/RIM',
    '05_HATS_CLOSED': 'HAT', '06_HATS_OPEN': 'OPEN HAT', '07_CYMBALS': 'CYMBAL', '08_TOMS': 'TOM',
    '09_PERC_ACOUSTIC': 'PERC (acoustic)', '10_PERC_ELECTRONIC': 'PERC (electronic)',
    '11_STOMPS_BODY': 'STOMP/BODY', '12_808_SUB': '808/SUB', '13_BASS': 'BASS',
    '14_MELODIC': 'MELODIC', '15_FX': 'FX', '16_LOOPS': 'LOOP',
    '19_FILLS_ROLLS': 'FILL', '20_TONAL_PERC': 'TONAL PERC',
}
files = sorted(glob.glob(ROOT + '/**/*.wav', recursive=True))
rows = []
for f in files:
    rel = os.path.relpath(f, ROOT).replace(os.sep, '/')
    parts = rel.split('/')
    cat = parts[0]
    sub = parts[1] if len(parts) > 2 else ''
    x, sr = sf.read(f)
    m = x if x.ndim == 1 else x.mean(axis=1)
    note = ''
    mm = re.search(r'_([A-G]s?-?\d)\.wav$', parts[-1])
    if mm:
        note = mm.group(1).replace('s', '#')
    XX = np.abs(np.fft.rfft(m * np.hanning(len(m))))
    fr = np.fft.rfftfreq(len(m), 1 / sr)
    cen = (XX * fr).sum() / max(XX.sum(), 1e-9)
    rows.append([rel, CAT_TAG.get(cat, cat), sub, note, round(len(m) / sr, 2),
                 round(20 * np.log10(max(np.max(np.abs(m)), 1e-9)), 1),
                 round(20 * np.log10(np.sqrt(np.mean(m ** 2) + 1e-12)), 1),
                 int(cen), 2 if x.ndim == 2 else 1])
with open(ROOT + '/KIT_INDEX.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, delimiter=';')
    w.writerow(['file', 'type', 'style', 'root_note', 'seconds', 'peak_dB', 'rms_dB', 'centroid_Hz', 'ch'])
    w.writerows(rows)
print('index rows', len(rows))

# ---------------------------------------------------------------- recommended kits
def pick(sub_prefix, n, contains=None, style=None):
    out = []
    for r in rows:
        rel = r[0]
        if not rel.startswith(sub_prefix):
            continue
        if contains and contains not in rel.lower():
            continue
        if style and ('/' + style + '/') not in rel:
            continue
        out.append(rel)
    step = max(1, len(out) // max(n, 1))
    return out[::step][:n] if out else []

KITS = {
    'trap': dict(k1='01_KICKS/trap', k2='01_KICKS/808', sn='02_SNARES/trap', cl='03_CLAPS/trap',
                 ht='05_HATS_CLOSED/trap', oh='06_HATS_OPEN/trap', pr='10_PERC_ELECTRONIC/blip',
                 b1='12_808_SUB/808_tuned_hard', b2='12_808_SUB/808_glide', cr='07_CYMBALS/crash',
                 fx='15_FX/risers', mel='14_MELODIC/synths/pluck_synth', vx='14_MELODIC/vox/vocal_chop'),
    'drill': dict(k1='01_KICKS/drill', k2='01_KICKS/trap', sn='02_SNARES/drill', cl='03_CLAPS/drill',
                  ht='05_HATS_CLOSED/tight', oh='06_HATS_OPEN/dnb', pr='10_PERC_ELECTRONIC/laser',
                  b1='12_808_SUB/808_tuned_hard', b2='12_808_SUB/808_glide', cr='07_CYMBALS/crash',
                  fx='15_FX/impacts', mel='14_MELODIC/synths/saw_lead', vx='14_MELODIC/vox/vocal_aah'),
    'phonk': dict(k1='01_KICKS/phonk', k2='01_KICKS/techno', sn='02_SNARES/phonk', cl='03_CLAPS/phonk',
                  ht='05_HATS_CLOSED/phonk', oh='06_HATS_OPEN/phonk', pr='09_PERC_ACOUSTIC/cowbell',
                  b1='12_808_SUB/808_tuned_reese', b2='12_808_SUB/808_oneshots', cr='07_CYMBALS/china',
                  fx='15_FX/sirens', mel='14_MELODIC/mallets/kalimba', vx='14_MELODIC/vox/vocal_chop'),
    'boombap_lofi': dict(k1='01_KICKS/boombap', k2='01_KICKS/lofi', sn='02_SNARES/boombap',
                         cl='03_CLAPS/boombap', ht='05_HATS_CLOSED/analog', oh='06_HATS_OPEN/analog',
                         pr='09_PERC_ACOUSTIC/shaker', b1='13_BASS/bass_guitar', b2='13_BASS/synth_bass_saw',
                         cr='07_CYMBALS/ride', fx='15_FX/textures', mel='14_MELODIC/keys/rhodes',
                         vx='14_MELODIC/strings/pizz'),
    'house_techno': dict(k1='01_KICKS/house', k2='01_KICKS/techno', sn='02_SNARES/house',
                         cl='03_CLAPS/house', ht='05_HATS_CLOSED/house', oh='06_HATS_OPEN/house',
                         pr='09_PERC_ACOUSTIC/conga', b1='13_BASS/synth_bass_saw', b2='13_BASS/sub',
                         cr='07_CYMBALS/crash', fx='15_FX/risers', mel='14_MELODIC/synths/pluck_synth',
                         vx='14_MELODIC/pads/pad_warm'),
    'dnb': dict(k1='01_KICKS/dnb', k2='01_KICKS/techno', sn='02_SNARES/dnb', cl='03_CLAPS/wide',
                ht='05_HATS_CLOSED/dnb', oh='06_HATS_OPEN/dnb', pr='09_PERC_ACOUSTIC/tambourine',
                b1='13_BASS/synth_bass_square', b2='13_BASS/sub', cr='07_CYMBALS/ride',
                fx='15_FX/transitions', mel='14_MELODIC/synths/supersaw', vx='14_MELODIC/vox/vocal_aah'),
    'rock_acoustic': dict(k1='01_KICKS/rock', k2='01_KICKS/funk', sn='02_SNARES/rock', cl='03_CLAPS/boombap',
                          ht='05_HATS_CLOSED/analog', oh='06_HATS_OPEN/analog', pr='09_PERC_ACOUSTIC/tambourine',
                          b1='13_BASS/bass_guitar', b2='13_BASS/bass_guitar', cr='07_CYMBALS/crash',
                          fx='15_FX/impacts', mel='14_MELODIC/guitars/guitar_dist', vx='14_MELODIC/strings/strings'),
    'amapiano': dict(k1='01_KICKS/amapiano', k2='01_KICKS/afrobeat', sn='02_SNARES/amapiano', cl='03_CLAPS/amapiano',
                     ht='05_HATS_CLOSED/amapiano', oh='06_HATS_OPEN/amapiano', pr='09_PERC_ACOUSTIC/afro_shaker',
                     b1='13_BASS/log_drum_soft', b2='13_BASS/log_drum_hard', cr='07_CYMBALS/crash',
                     fx='19_FILLS_ROLLS', mel='14_MELODIC/mallets/kalimba', vx='14_MELODIC/vox/shout'),
    'ukg_garage': dict(k1='01_KICKS/ukg', k2='01_KICKS/house', sn='02_SNARES/ukg', cl='03_CLAPS/ukg',
                       ht='05_HATS_CLOSED/ukg', oh='06_HATS_OPEN/ukg', pr='10_PERC_ELECTRONIC/blip',
                       b1='13_BASS/sub', b2='13_BASS/wobble', cr='07_CYMBALS/splash',
                       fx='15_FX/scratches', mel='14_MELODIC/keys/organ', vx='14_MELODIC/vox/shout'),
    'dubstep_breakbeat': dict(k1='01_KICKS/dubstep', k2='01_KICKS/breakbeat', sn='02_SNARES/dubstep', cl='03_CLAPS/breakbeat',
                              ht='05_HATS_CLOSED/breakbeat', oh='06_HATS_OPEN/dnb', pr='09_PERC_ACOUSTIC/tambourine',
                              b1='13_BASS/wobble', b2='13_BASS/sub', cr='07_CYMBALS/china',
                              fx='15_FX/impacts', mel='14_MELODIC/synths/saw_lead', vx='14_MELODIC/vox/shout'),
    'orchestral_cinematic': dict(k1='20_TONAL_PERC/timpani', k2='01_KICKS/rock', sn='02_SNARES/rock', cl='03_CLAPS/wide',
                                 ht='05_HATS_CLOSED/analog', oh='06_HATS_OPEN/ridey', pr='09_PERC_ACOUSTIC/anvil',
                                 b1='20_TONAL_PERC/gong', b2='13_BASS/sub', cr='20_TONAL_PERC/cymbal_swell',
                                 fx='20_TONAL_PERC/gong_swell', mel='14_MELODIC/strings/strings', vx='14_MELODIC/vox/vocal_aah'),
    'melodic_any': dict(k1='14_MELODIC/keys/piano_soft', k2='14_MELODIC/keys/rhodes', sn='14_MELODIC/mallets/marimba',
                        cl='14_MELODIC/mallets/glockenspiel', ht='14_MELODIC/synths/pluck_synth',
                        oh='14_MELODIC/synths/pad_warm', pr='14_MELODIC/winds/flute', b1='13_BASS/sub',
                        b2='12_808_SUB/808_tuned_soft', cr='14_MELODIC/strings/strings',
                        fx='15_FX/risers', mel='14_MELODIC/keys/music_box', vx='14_MELODIC/vox/vocal_aah'),
}
LAYOUT = ['kick1', 'kick2', 'snare1', 'clap1', 'snap/rim', 'hat closed', 'hat open', 'perc',
          'bass/808 A', 'bass/808 B', 'crash/ride', 'fx', 'melodic 1', 'melodic 2', 'vocal', 'tom']
mapdir = ROOT + '/18_KIT_MAPS'
os.makedirs(mapdir + '/drum_kits', exist_ok=True)
os.makedirs(mapdir + '/melodic_kits', exist_ok=True)
rows_pad = []
def allin(prefix):
    return [r[0] for r in rows if r[0].startswith(prefix)]

for kit, m in KITS.items():
    def one(*prefixes, idx=0):
        for p_ in prefixes:
            got = allin(p_)
            if got:
                return got[min(idx, len(got) - 1)]
        return ''

    def pair(*prefixes):
        for p_ in prefixes:
            got = allin(p_)
            if len(got) >= 2:
                return got[0], got[1]
        return (one(prefixes[0]), one(prefixes[0]))
    k1a, k1b = pair(m['k1'], m['k2'])
    sna, _ = pair(m['sn'])
    cla, _ = pair(m['cl'])
    htc = one(m['ht'])
    oht = one(m['oh'])
    prc = one(m['pr'])
    bas = one(m['b1'])
    bas2 = one(m['b2'])
    crs = one(m['cr'])
    fxs = one(m['fx'])
    melpool = allin(m['mel'])
    mel1 = next((p_ for p_ in melpool if p_.endswith('_C4.wav')), melpool[0] if melpool else '')
    mel2 = next((p_ for p_ in melpool if p_.endswith('_A4.wav')), melpool[1] if len(melpool) > 1 else mel1)
    vxx = one(m['vx'])
    tom = one('08_TOMS/acoustic', '08_TOMS/trap')
    snaporrim = tom  # placeholder replaced below by snap/rim pool
    snr2 = ''
    extra = allin('04_SNAPS_RIMS_STICKS/snap') or allin('04_SNAPS_RIMS_STICKS/rim')
    if extra:
        snr2 = extra[0]
    padlist = [k1a, k1b, sna, cla, snr2 or k1b, htc, oht, prc, bas, bas2, crs, fxs, mel1, mel2, vxx, tom]
    lines = ['// Mega Kit expansion - recommended ' + kit + ' layout',
             '// pads 1-16 mapped to MIDI notes 36-51 (GM-ish)', '']
    for i, pth in enumerate(padlist):
        if pth:
            lines.append(f'<region> sample=../{pth} key={36 + i} lovel=1 hivel=127')
    open(f'{mapdir}/drum_kits/{kit}.sfz', 'w').write('\n'.join(lines) + '\n')
    for i, (lbl, pth) in enumerate(zip(LAYOUT, padlist)):
        rows_pad.append([kit, i + 1, lbl, pth])
    txt = [f'{kit.upper()} - recommended 16 pads (drag in this order)', '']
    for i, (lbl, pth) in enumerate(zip(LAYOUT, padlist)):
        txt.append(f'{i + 1:2d}. {lbl:14s} {pth}')
    open(f'{mapdir}/drum_kits/{kit}_PAD_LAYOUT.txt', 'w', encoding='utf-8').write('\n'.join(txt) + '\n')

with open(ROOT + '/18_KIT_MAPS/recommended_kits.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh, delimiter=';')
    w.writerow(['kit', 'pad', 'role', 'file'])
    w.writerows(rows_pad)

# ---------------------------------------------------------------- melodic sfz (key-mapped)
mel = [r for r in rows if r[0].startswith('14_MELODIC/') and r[3]]
byinstr = {}
for r in mel:
    rel = r[0]
    instr = rel.split('/')[2] if len(rel.split('/')) > 3 else rel.split('/')[-1].rsplit('_', 1)[0]
    byinstr.setdefault(instr, []).append((r[3], rel))
NAME2PC = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
def note_to_midi(n):
    m = re.match(r'([A-G]#?)(-?\d+)', n)
    return NAME2PC[m.group(1)] + (int(m.group(2)) + 1) * 12
for instr, lst in sorted(byinstr.items()):
    lst = sorted(lst, key=lambda t: note_to_midi(t[0]))
    midis = [note_to_midi(n) for n, _ in lst]
    lines = [f'// {instr} - synthesized melodic instrument, {len(lst)} sampled notes',
             '// zones stretch to neighbouring notes and keep the tuning', '']
    for (n, rel), mid in zip(lst, midis):
        # zone = halfway to neighbours, one octave range outward
        i = midis.index(mid)
        lo = mid - 1 if i == 0 else (mid - (mid - midis[i - 1]) // 2)
        hi = mid + int(round(12 * np.log2(2 ** (1/12)))) if i == len(midis) - 1 else mid + (midis[i + 1] - mid) // 2
        lines.append(f'<region> sample=../{rel} pitch_keycenter={mid} lokey={lo} hikey={hi} lovel=1 hivel=127')
    open(f'{mapdir}/melodic_kits/{instr}.sfz', 'w').write('\n'.join(lines) + '\n')
print('sfz maps:', len(glob.glob(mapdir + '/*/*.sfz')))
