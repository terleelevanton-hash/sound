set -e
rm -rf build/kit
python3 work/build_drums.py build/kit
python3 work/build_bass.py build/kit
python3 work/build_melodic.py build/kit
python3 work/build_fx.py build/kit
python3 work/build_loops.py build/kit
