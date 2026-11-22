# Universal Producer Sound Kit (`sound`) — Всежанровый студийный саунд-кит

Полная коллекция ваншотов, мультиоктавных инструментов, ударных, басов, аккордов, бесшовных лупов, FX, MIDI-паттернов и SFZ-патчей для создания музыки **в любом жанре** (FL Studio, Ableton Live, Logic Pro, Reaper, Bitwig, MPC и любые сэмплеры с поддержкой WAV / SFZ).

---

## Состав репозитория (~2 825 файлов)

| Раздел | Путь | Файлов | Описание |
|---|---|---:|---|
| **Оригинальный драм-кит (`Dkits`)** | `original_kit/kits/Dkits/` | 320 | `!mylancore drumkit @StarBeats` + `treit1 kit`: плотные Trap / Phonk / Underground 808, кики, клэпы, снейры, хэты, перки, SFX и вокальные ваншоты |
| **Расширение `MEGA_KIT_EXPANSION_v2`** | `original_kit/kits/MEGA_KIT_EXPANSION_v2/` | 1 415 | Базовые электронные и акустические ударные (29 стилей киков), лог-драмы Amapiano, Acid 303, Wobble, базовая мелодика, оркестровая перкуссия, лупы и MIDI |
| **Новое студийное расширение `MEGA_KIT_EXPANSION_v3`** | `original_kit/kits/MEGA_KIT_EXPANSION_v3/` | 1 090 | **Мультиоктавные инструменты (`C2..C6`)**, саксофоны, духовые, живые/метал гитары, чёс акустики и павер-аккорды во всех 12 тональностях, джазовые щётки, хроматический 808 Drift Phonk Cowbell (24 ноты), контрабас, слэп-бас, M1 House Organ Bass, Hardbass Donk, Neuro Reese, Rage/Pluggnb/Synthwave синты, народные инструменты (балалайка, баян, гусли, дудук), длинные стерео-пэды, 24 идеальных по BPM лупа, 84 MIDI и 84 проверенных SFZ-мапы |
| **Инструменты сборки и склейки** | `tools/unify_kits.py` | 1 | Скрипт слияния `Dkits` + `v2` + `v3` в единую папку `ALL_IN_ONE_KIT/` в одну команду (плюс авто-починка SFZ из `v2`) |

---

## Какие жанры полностью закрыты

- **Hip-Hop & Urban:** Trap, UK / NY Drill, Boom-Bap, Lo-Fi, West Coast G-Funk, Memphis, Rage / Opium, Plugg / Pluggnb, Cloud Rap, R&B / Neo-Soul, Reggaeton / Dembow, Afrobeats, Amapiano, Baile Funk / Automotivo
- **Electronic & Club:** House, Deep / Organ House, UK Garage / 2-Step, Techno, Dub Techno, Acid 303, Drum & Bass / Neurofunk / Jungle, Dubstep / Halftime, Breakbeat, Footwork, Synthwave / Retrowave, Hyperpop, Trance / Psytrance, Hardstyle, Hardbass, Gabber / Rave, Chiptune / 8-Bit
- **Live, Band & Acoustic:** Rock, Punk, Post-Punk / Doomer Wave, Metal / 8-String Djent, Shoegaze / Midwest Emo, Indie / Pop / K-Pop, Funk / Disco / City Pop, Jazz (Swing / Quartet / Brushes), Bossanova / Latin / Salsa, Reggae / Dub, Country / Folk
- **World, Folk & Cinematic:** Русский и СНГ фолк-фьюжн (балалайка, баян, гусли, дудук), восточные и этнические инструменты (ситар, кото, уд, эрху, калимба), Оркестр / Саундтреки / Трейлеры (литавры, тайко, гонги, церковные колокола, валторны, тромбоны, туба, деревянные духовые, BRAAAM-импакты и тёмные дроны)

---

## Быстрый старт

### Вариант 1: Собрать всё в одну единую папку `ALL_IN_ONE_KIT` (рекомендуется)
Склонируйте репозиторий и выполните:
```bash
git clone https://github.com/terleelevanton-hash/sound.git
cd sound
python3 tools/unify_kits.py
```
В корне появится папка **`ALL_IN_ONE_KIT/`**, где все сэмплы из `Dkits`, `v2` и `v3` аккуратно разложены по единым категориям `01_KICKS` … `20_TONAL_PERC`, а все `.sfz`-карты готовы к загрузке. Добавьте эту папку в браузер **FL Studio** (*Options → File settings → Browser extra search folders*) или **Ableton Live** (*Places → Add Folder*).

### Вариант 2: Использовать папки напрямую
Все три набора уже лежат в распакованном виде внутри `original_kit/kits/`:
- `original_kit/kits/Dkits`
- `original_kit/kits/MEGA_KIT_EXPANSION_v2`
- `original_kit/kits/MEGA_KIT_EXPANSION_v3`

### Как играть мелодическими инструментами и басами
- **Через бесплатный SFZ-плеер (Sforzando / Sfizz / FL DirectWave):** откройте любой файл из `18_KIT_MAPS/melodic_and_bass_sfz/*.sfz` — инструмент сразу разложен по всей MIDI-клавиатуре (`A0..C8`) в точном строю.
- **Через обычный сэмплер DAW:** закиньте сэмпл с нужной опорной нотой (например `..._C4.wav` или `808_spinz_C1.wav`) и выставите эту Root Note в сэмплере.
- **Готовые наборы на 16 пэдов (FPC / Drum Rack / MPC):** смотрите `original_kit/kits/MEGA_KIT_EXPANSION_v3/18_KIT_MAPS/drum_kits_v3/` — там лежат 24 жанровых пресета (`.sfz` + текстовая шпаргалка `*_PAD_LAYOUT.txt`).
- **Готовые MIDI (аккорды, басовые линии, хэт-роллы, грувы):** перетаскивайте файлы из `17_MIDI/` прямо в Piano Roll.

---

## Пересборка синтезаторного пака `v3` с нуля
Весь код DSP-синтезатора находится в `original_kit/kits/MEGA_KIT_EXPANSION_v3/00_START_HERE/generator/`:
```bash
pip install numpy scipy soundfile
python3 original_kit/kits/MEGA_KIT_EXPANSION_v3/00_START_HERE/generator/build_all_v3.py build_v3
```
