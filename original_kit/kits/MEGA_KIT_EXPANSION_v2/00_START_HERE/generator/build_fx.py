import sys; sys.path.insert(0, 'work')
import numpy as np
from kitlib import fx as X, drums as D, dsp
from kitlib.io import emit, set_root

set_root(sys.argv[1] if len(sys.argv) > 1 else 'build/kit')
rng = np.random.default_rng(9091)
U = lambda a, b: float(rng.uniform(a, b))

# risers (stereo for width)
for i in range(8):
    x = X.riser(rng, dur=U(1.0, 3.0), lo=U(200, 500), hi=U(6000, 12000), tone=bool(i % 2), noise_amt=U(0.7, 1.2))
    emit(f'15_FX/risers/riser_{i+1:02d}.wav', dsp.stereo(x, 0.4), 'FX', 'riser', stereo=True)
for i in range(5):
    x = X.downlifter(rng, dur=U(0.8, 2.2), lo=U(150, 400), hi=U(5000, 10000))
    emit(f'15_FX/downlifters/downlifter_{i+1:02d}.wav', dsp.stereo(x, 0.4), 'FX', 'downlifter', stereo=True)
for i in range(8):
    x = X.impact(rng, decay=U(0.6, 1.5), f0=U(40, 70), boom=U(0.7, 1.2), noise_amt=U(0.5, 1.0))
    emit(f'15_FX/impacts/impact_{i+1:02d}.wav', dsp.stereo(x, 0.3), 'FX', 'impact', stereo=True)
for i in range(6):
    x = X.sweep(rng, dur=U(0.5, 1.6), f_from=U(250, 600), f_to=U(4000, 10000), rise=bool(i % 2))
    emit(f'15_FX/sweeps/sweep_{i+1:02d}.wav', x, 'FX', 'sweep')
for i in range(6):
    src = ['pluck', 'cymbal', 'snare', 'pluck', 'cymbal', 'pluck'][i]
    x = X.reverse_reverb(rng, dur=U(1.2, 2.6), src=src)
    emit(f'15_FX/reverses/reverse_reverb_{i+1:02d}.wav', dsp.stereo(x, 0.3), 'FX', 'reverse', stereo=True)
for i in range(4):
    x = X.reverse_cymbal(rng, dur=U(1.2, 2.2))
    emit(f'15_FX/reverses/reverse_cymbal_{i+1:02d}.wav', dsp.stereo(x, 0.3), 'FX', 'reverse', stereo=True)
for i in range(4):
    x = X.sub_drop(rng, dur=U(1.0, 2.2), f0=U(70, 110), f1=U(20, 32))
    emit(f'15_FX/transitions/sub_drop_{i+1:02d}.wav', x, 'FX', 'sub_drop')
for i in range(3):
    x = X.tape_stop(rng, dur=U(0.8, 1.8), f0=U(160, 300), kind=['saw', 'square', 'sine'][i % 3])
    emit(f'15_FX/transitions/tape_stop_{i+1:02d}.wav', x, 'FX', 'tape_stop')
for i in range(3):
    x = X.snare_roll(rng, dur=U(1.5, 3.0), start_rate=U(6, 10), end_rate=U(28, 45), tone=U(180, 240))
    emit(f'15_FX/transitions/snare_roll_{i+1:02d}.wav', x, 'FX', 'roll')
for i in range(2):
    x = X.sub_blast(rng, dur=U(0.6, 1.2))
    emit(f'15_FX/transitions/sub_blast_{i+1:02d}.wav', x, 'FX', 'blast')
for i in range(4):
    x = X.siren(rng, dur=U(1.5, 3.0), f_lo=U(400, 700), f_hi=U(1100, 1800), rate=U(1.5, 3.5),
                kind=['sine', 'square', 'saw', 'sine'][i])
    emit(f'15_FX/sirens/siren_{i+1:02d}.wav', x, 'FX', 'siren')
for i in range(3):
    x = X.glitch(rng, dur=U(0.6, 1.6))
    emit(f'15_FX/glitch/glitch_{i+1:02d}.wav', x, 'FX', 'glitch')
# textures (stereo, longer)
emit('15_FX/textures/vinyl_crackle_01.wav', dsp.stereo(X.vinyl(rng, 3.0, pop_rate=5.0), 0.5), 'FX', 'texture', stereo=True)
emit('15_FX/textures/vinyl_crackle_02.wav', dsp.stereo(X.vinyl(rng, 3.0, pop_rate=14.0, tone=6000), 0.5), 'FX', 'texture', stereo=True)
emit('15_FX/textures/tape_hiss_01.wav', dsp.stereo(X.tape_hiss(rng, 3.0), 0.4), 'FX', 'texture', stereo=True)
emit('15_FX/textures/rain_01.wav', dsp.stereo(X.rain(rng, 3.0), 0.5), 'FX', 'texture', stereo=True)
emit('15_FX/textures/wind_01.wav', dsp.stereo(X.wind(rng, 3.0), 0.5), 'FX', 'texture', stereo=True)
emit('15_FX/textures/fire_01.wav', dsp.stereo(X.fire(rng, 3.0), 0.4), 'FX', 'texture', stereo=True)
emit('15_FX/textures/static_01.wav', X.static_noise(rng, 2.0), 'FX', 'texture')
emit('15_FX/textures/underwater_01.wav', dsp.stereo(X.underwater(rng, 2.5), 0.4), 'FX', 'texture', stereo=True)
# foley
emit('15_FX/foley/knock_door_01.wav', X.knock(rng, hits=3, decay=0.1, low=170), 'FOLEY', 'knock')
emit('15_FX/foley/knock_table_01.wav', X.knock(rng, hits=2, decay=0.06, low=320), 'FOLEY', 'knock')
emit('15_FX/foley/glass_break_01.wav', X.glass_break(rng, 0.6), 'FOLEY', 'glass')
emit('15_FX/foley/glass_break_02.wav', X.glass_break(rng, 0.8), 'FOLEY', 'glass')
emit('15_FX/foley/water_drop_01.wav', X.water_drop(rng, 0.4), 'FOLEY', 'water')
emit('15_FX/foley/camera_shutter_01.wav', X.camera_shutter(rng), 'FOLEY', 'camera')
emit('15_FX/foley/switch_click_01.wav', X.switch_click(rng), 'FOLEY', 'click')
emit('15_FX/foley/lighter_01.wav', X.lighter(rng, 1.0), 'FOLEY', 'lighter')
emit('15_FX/foley/paper_01.wav', X.paper(rng, 0.6), 'FOLEY', 'paper')
emit('15_FX/foley/whoosh_bang_01.wav', X.whoosh_bang(rng, 1.4), 'FOLEY', 'whoosh')
print('fx done')
