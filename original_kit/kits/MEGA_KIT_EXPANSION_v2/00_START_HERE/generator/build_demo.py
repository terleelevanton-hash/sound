import sys, os, glob; sys.path.insert(0, 'work')
import numpy as np, soundfile as sf
from kitlib import dsp
from kitlib.dsp import FS, n_of, midi_to_freq, note_filename

KIT = 'build/kit'
rng = np.random.default_rng(5)

def load(rel):
    x, sr = sf.read(os.path.join(KIT, rel), dtype='float64')
    return x if x.ndim == 1 else x.mean(axis=1)

def find_note(instr_glob, midi):
    """pick closest sampled note and pitch-shift it to the target midi"""
    cands = glob.glob(os.path.join(KIT, instr_glob + '/*.wav'))
    if not cands:
        return np.zeros(10)
    def note_of(p):
        b = os.path.basename(p)[:-4]
        n = b.split('_')[-1].replace('s', '#')
        names = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
        import re
        m = re.match(r'([A-G]#?)(-?\d+)', n)
        return names[m.group(1)] + (int(m.group(2)) + 1) * 12
    best = min(cands, key=lambda p: abs(note_of(p) - midi))
    x = load(os.path.relpath(best, KIT))
    src = note_of(best)
    if src != midi:
        r = 2 ** ((midi - src) / 12)
        idx = np.arange(0, len(x) - 1, r)
        x = np.interp(idx, np.arange(len(x)), x)
    return x

def place(buf, x, t, gain=1.0):
    i = n_of(t)
    m = min(len(x), len(buf) - i)
    if m > 0:
        buf[i:i + m] += x[:m] * gain

total = 24.0
n = n_of(total)
mix = np.zeros(n)
beat1 = 60 / 140
beat2 = 60 / 90
beat3 = 60 / 128
trap = load('16_LOOPS/drum_loops/trap_140bpm.wav')
boom = load('16_LOOPS/drum_loops/boombap_90bpm.wav')
house = load('16_LOOPS/drum_loops/house_128bpm.wav')
len_trap, len_boom, len_house = len(trap) / FS, len(boom) / FS, len(house) / FS

# ------------------------------------------------------------ A: trap 140
secA = 0.0
for k in range(3):
    place(mix, trap, secA + k * len_trap, 0.9)
place(mix, load('15_FX/risers/riser_02.wav'), secA, 0.45)
place(mix, load('15_FX/impacts/impact_01.wav'), secA, 0.65)
riff = [(24, 0), (24, 1.5), (27, 2.0), (24, 3.0), (22, 4.0), (24, 4.5), (27, 5.5), (24, 6.0), (31, 6.5)]
for k in range(3):
    for (m, b) in riff:
        place(mix, find_note('12_808_SUB/808_tuned_hard', m), secA + k * len_trap + b * beat1, 0.5)
melA = [(72, 0.0), (75, 0.5), (77, 1.0), (79, 2.0), (77, 2.5), (75, 3.0), (72, 4.0), (70, 5.0), (72, 5.5)]
for k in range(3):
    for (m, b) in melA:
        place(mix, find_note('14_MELODIC/synths/pluck_synth', m), secA + k * len_trap + b * beat1 * 0.5, 0.26)
place(mix, load('14_MELODIC/vox/vocal_chop/vocal_chop_C4.wav'), 1.6, 0.22)
place(mix, load('14_MELODIC/vox/vocal_chop/vocal_chop_A4.wav'), 6.9, 0.2)
place(mix, load('14_MELODIC/vox/vocal_chop/vocal_chop_C4.wav'), 8.4, 0.2)

# ------------------------------------------------------------ B: boombap 90
secB = 3 * len_trap
place(mix, load('15_FX/transitions/tape_stop_01.wav'), secB - 1.2, 0.45)
place(mix, boom, secB, 0.85)
chords = [(60, 0.0, 63, 67, 70), (56, 2.0, 60, 63, 67)]
for root, b, *rest in chords:
    for m in [root] + list(rest):
        place(mix, find_note('14_MELODIC/keys/rhodes', m), secB + b * beat2, 0.2)
for (m, b) in [(36, 0.0), (36, 1.5), (43, 2.0), (36, 3.0), (41, 4.0)]:
    place(mix, find_note('13_BASS/bass_guitar', m), secB + b * beat2, 0.38)

# ------------------------------------------------------------ C: house 128
secC = secB + len_boom
place(mix, load('15_FX/risers/riser_04.wav'), secC - 1.5, 0.38)
for k in range(2):
    place(mix, house, secC + k * len_house, 0.9)
for k in range(2):
    for i, m in enumerate([72, 75, 79, 82, 84, 82, 79, 75]):
        place(mix, find_note('14_MELODIC/synths/pluck_synth', m), secC + k * len_house + i * beat3 * 0.5, 0.18)
for m in [48, 55]:
    place(mix, find_note('14_MELODIC/pads/pad_warm', m), secC, 0.2)
for k in range(4):
    for (m, b) in [(36, 0), (36, 1), (38, 2), (36, 3)]:
        place(mix, find_note('13_BASS/synth_bass_saw', m), secC + k * len_house + b * beat3, 0.4)
place(mix, load('15_FX/reverses/reverse_cymbal_01.wav'), total - 2.2, 0.4)
mix = dsp.hp(mix, 25, 2)
mix = dsp.sat(mix, 1.25, 'tanh')
mix = mix / max(np.max(np.abs(mix)), 1e-9) * 0.95
mix = dsp.limiter_soft(mix, 0.95)
mix = dsp.fade(mix, 0.01, 0.6)
st = dsp.stereo(mix, 0.25)
sf.write('DEMO_megakit_24s.wav', st.astype(np.float32), FS, subtype='PCM_16')
print('demo written', len(mix) / FS, 'sec')
