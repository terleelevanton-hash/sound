import sys, os, glob, re; sys.path.insert(0, 'work')
import numpy as np, soundfile as sf
from kitlib import dsp
from kitlib.dsp import FS, n_of

KIT = 'build/kit'
rng = np.random.default_rng(11)
NAME2PC = {'C':0,'C#':1,'D':2,'D#':3,'E':4,'F':5,'F#':6,'G':7,'G#':8,'A':9,'A#':10,'B':11}

def load(rel, stereo=False):
    x, sr = sf.read(os.path.join(KIT, rel), dtype='float64')
    if stereo and x.ndim == 2:
        return x
    return x if x.ndim == 1 else x.mean(axis=1)

def note_of(p):
    n = os.path.basename(p)[:-4].rsplit('_', 1)[-1].replace('s', '#')
    m = re.match(r'([A-G]#?)(-?\d+)', n)
    return NAME2PC[m.group(1)] + (int(m.group(2)) + 1) * 12

_cache = {}
def note_sample(glob_pat, midi):
    key = (glob_pat, midi)
    if key in _cache:
        return _cache[key]
    cands = glob.glob(os.path.join(KIT, glob_pat, '*.wav'))
    best = min(cands, key=lambda p: abs(note_of(p) - midi))
    x = load(os.path.relpath(best, KIT))
    src = note_of(best)
    if src != midi:
        r = 2 ** ((midi - src) / 12)
        x = np.interp(np.arange(0, len(x) - 1, r), np.arange(len(x)), x)
    _cache[key] = x
    return x

def place(buf, x, t, gain=1.0):
    i = n_of(t)
    if i >= len(buf):
        return
    m = min(len(x), len(buf) - i)
    if m > 0:
        buf[i:i + m] += x[:m] * gain

mix = np.zeros(n_of(26.0))

def dur(rel): return len(load(rel)) / FS

# ---------------- A: trap 140 (2 bars x2)
trap = load('16_LOOPS/drum_loops/trap_140bpm.wav'); Lt = len(trap)/FS; b1 = 60/140
place(mix, trap, 0, 0.9); place(mix, trap, Lt, 0.9)
place(mix, load('15_FX/risers/riser_01.wav'), 0, 0.4)
place(mix, load('15_FX/impacts/impact_02.wav'), 0, 0.6)
for k in range(2):
    for (m, b) in [(24,0),(24,1.5),(27,2),(24,3),(22,4),(24,4.5),(27,5.5),(31,6.5)]:
        place(mix, note_sample('12_808_SUB/808_tuned_hard', m), k*Lt + b*b1, 0.5)
    for (m, b) in [(72,0),(75,0.5),(77,1),(79,2),(77,2.5),(75,3),(72,4),(70,5),(72,5.5)]:
        place(mix, note_sample('14_MELODIC/synths/pluck_synth', m), k*Lt + b*b1*0.5, 0.24)
place(mix, load('14_MELODIC/vox/vocal_chop/vocal_chop_C4.wav'), 1.7, 0.2)

# ---------------- B: boombap 90
secB = 2 * Lt
boom = load('16_LOOPS/drum_loops/boombap_90bpm.wav'); Lb = len(boom)/FS; b2 = 60/90
place(mix, load('15_FX/transitions/tape_stop_02.wav'), secB - 1.0, 0.4)
place(mix, boom, secB, 0.85)
for (root, t0, iv) in [(60, 0, [0,3,7,10]), (56, 2, [0,4,7,11])]:
    for j in iv:
        place(mix, note_sample('14_MELODIC/keys/rhodes', root + j), secB + t0*b2, 0.18)
for (m, b) in [(36,0),(36,1.5),(43,2),(36,3),(41,4)]:
    place(mix, note_sample('13_BASS/bass_guitar', m), secB + b*b2, 0.36)

# ---------------- C: house 128
secC = secB + Lb
house = load('16_LOOPS/drum_loops/house_128bpm.wav'); Lh = len(house)/FS; b3 = 60/128
place(mix, load('15_FX/transitions/uplifter_01.wav'), secC - 1.4, 0.35)
for k in range(2):
    place(mix, house, secC + k*Lh, 0.9)
    for i, m in enumerate([72,75,79,82,84,82,79,75]):
        place(mix, note_sample('14_MELODIC/synths/pluck_synth', m), secC + k*Lh + i*b3*0.5, 0.17)
    for (m, b) in [(36,0),(36,1),(38,2),(36,3)]:
        place(mix, note_sample('13_BASS/synth_bass_saw', m), secC + k*Lh + b*b3, 0.4)
for m in [48, 55]:
    place(mix, note_sample('14_MELODIC/pads/pad_warm', m), secC, 0.18)

# ---------------- D: amapiano 112
secD = secC + 2 * Lh
amap = load('16_LOOPS/drum_loops/amapiano_112bpm.wav'); La = len(amap)/FS; b4 = 60/112
place(mix, load('19_FILLS_ROLLS/fill_snare_roll_8th_1bar_120bpm.wav'), secD - 1.6, 0.35)
place(mix, load('20_TONAL_PERC/gong_swell/gong_swell_01.wav'), secD - 1.2, 0.3)
place(mix, amap, secD, 0.9)
for (m, b) in [(33,0),(36,0.75),(33,1.5),(40,1.75),(33,2),(36,2.75),(38,3.0),(33,3.5)]:
    place(mix, note_sample('13_BASS/log_drum_soft', m), secD + b*b4, 0.5)
for (m, b) in [(72,0),(75,1),(79,2),(72,3)]:
    place(mix, note_sample('14_MELODIC/mallets/kalimba', m), secD + b*b4, 0.22)
place(mix, load('14_MELODIC/vox/shout/shout_e_1.wav'), secD + 2*b4, 0.16)
place(mix, load('20_TONAL_PERC/timpani/timpani_C2.wav'), secD + 4*b4 - 0.25, 0.3)
place(mix, load('15_FX/scratches/scratch_02.wav'), secD + 1.2, 0.2)

mix = dsp.hp(mix, 25, 2)
mix = dsp.sat(mix, 1.2, 'tanh')
mix = mix / max(np.max(np.abs(mix)), 1e-9) * 0.92
mix = dsp.limiter_soft(mix, 0.95)
mix = dsp.fade(mix, 0.01, 0.8)
st = dsp.stereo(mix, 0.25)
sf.write('DEMO_megakit_4_zhanra.wav', st.astype(np.float32), FS, subtype='PCM_16')
print('demo', round(len(mix)/FS, 1), 'sec, peak', round(dsp.peak_db(mix), 1))
