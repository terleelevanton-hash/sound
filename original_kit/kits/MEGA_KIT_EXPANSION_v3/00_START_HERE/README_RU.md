# MEGA KIT EXPANSION v3 — Полное всежанровое студийное дополнение

Эта папка достраивает `Dkits` + `MEGA_KIT_EXPANSION_v2` до полноценной студийной библиотеки, на которой можно написать трек **в абсолютно любом жанре**: от Jazz, Bossanova, Funk/Disco и Классики/Кино до Drift Phonk, Baile Funk, Rage/Opium, Pluggnb, Post-Punk/Doomer Wave, Synthwave, Metal/Djent, Русского фолка/СНГ-сцены, House/UKG, Psytrance, Hardbass и Gabber.

## Что нового и что исправлено по сравнению с v2

1. **Новый DSP-движок без алиасинга и фальши в верхних регистрах (`kitlib_v3`):**
   - Осцилляторы с **PolyBLEP anti-aliasing** и настоящим стерео-унисоном (моно-совместимым, без фазовой гребёнки Haas-эффекта).
   - Физическое моделирование струн **Karplus-Strong с дробной задержкой Thiran Allpass** — точность строя гитар и щипковых инструментов **в пределах ±1 цента** по всем октавам (`C1..C6`).
   - Исправлена ошибка v2 с укорачиванием нот в цикле и ошибка относительных путей в `.sfz` (`../../` проверены автоматически для всех 84 SFZ-патчей, диапазон покрывает всю клавиатуру `A0..C8` / MIDI `21..108` без наложений зон).
2. **Мультиоктавная мелодика (`14_MELODIC`, 45 новых инструментов на 3–4 октавы `C2..C6`):**
   - **Клавишные (`keys`):** `concert_grand`, `felt_upright` (Lo-Fi / неоклассика), `wurli_ep` (Wurlitzer 200A), `clavinet` (Funk D6), `pipe_organ` (соборный орган), `mellotron_flute`, `mellotron_strings`.
   - **Саксофоны, духовые и медь (`winds`, `brass`):** `tenor_sax`, `alto_sax`, `trombone`, `french_horn`, `tuba_stab`, `funk_brass_section`, `oboe`, `bassoon`, `duduk`.
   - **Гитары (`guitars`):** `nylon_guitar`, `steel_acoustic`, `funk_wah_guitar`, `jazz_guitar`, `metal_chug_8str` (8-струнный Djent от `F#1`!), `shimmer_guitar` (Shoegaze / Post-Rock).
   - **Народные и СНГ-инструменты (`world`, `mallets`):** `balalaika`, `bayan`, `gusli`, `ukulele`, `mandolin`, `erhu`, `kalimba_stereo`.
   - **Современные синты и лиды (`synths`):** `rage_lead` (Opium / Yeat / Carti), `pluggnb_lead`, `pluggnb_bell`, `retro_poly80` (Synthwave), `gfunk_whistle_lead` (West Coast), `hyperpop_lead`, `rave_hoover` (90s Rave), `dx_crystal_bell`, `psy_fm_lead`, `chiptune_duty`, `chiptune_arp`.
   - **Длинные стерео-пэды и дроны (`pads`):** `pad_shimmer_stereo`, `pad_cs80_dark`, `pad_glass_ambient`, `pad_tape_strings`, `drone_dark_cinema`.
3. **72 готовых аккорда и гитарного боя во всех 12 тональностях (`14_MELODIC/chords_stabs`):**
   - Живой чёс 6-струнной акустики (`acoustic_strum_major` и `acoustic_strum_minor`, `C..B`), рок/метал квинт-аккорды (`rock_power_chord`, `C2..B2`), House M1/Wurli стабы (`house_organ_chord`), Dub Techno аккорды с пинг-понг дилеем (`dub_techno_chord`), Neo-Soul Rhodes min9 (`neosoul_rhodes_chord`).
4. **Басы для любых жанров (`12_808_SUB`, `13_BASS`):**
   - `upright_double_bass` (джазовый контрабас), `slap_bass` (фанк слэп), `picked_rock_bass` (рок/пост-панк бас медиатором), `fretless_bass`, `donk_organ_bass` (легендарный House/UKG M1 Organ Bass), `hardbass_donk` (рейв/хардбасс донк), `moog_fat_bass`, `neuro_bass` (DnB Neurofunk Reese), `808_spinz_pro`, `808_opium_buzz`, `808_drill_slide_long`.
5. **Хроматический 808 Drift Phonk Cowbell (`C4..B5` — 24 ноты!) и новые жанры ударных:**
   - Джазовые щётки (`jazz_brush_tap`, `jazz_brush_sweep`, `ghost_notes`, `jazz_foot_chick`, `jazz_sizzle_ride`, `jazz_ride_bell`), 80s Synthwave Gated Snare и томы Simmons SDS-V, Baile Funk / Automotivo (кики, снейры, куика, стабы), Post-Punk / Doomer Wave, Reggaeton Dembow, R&B / Neo-Soul, Disco / Funk, Psytrance, Gabber / Hardcore, House Snare, Modern Pop.
6. **24 по-сэмпльно точных лупа (`16_LOOPS`) + 84 MIDI-файла (`17_MIDI`) + 24 жанровых раскладки 16 пэдов (`18_KIT_MAPS`).**
   - Все лупы сведены с бесшовным переносом хвоста реверберации на начало 1-го такта — длина файла **до одного сэмпла** совпадает с сеткой BPM в FL Studio и Ableton Live!

## Сборка единой папки со всеми тремя китами

Из корня репозитория запустите:
```bash
python3 tools/unify_kits.py
```
Скрипт за пару секунд соберёт `Dkits` + `v2` + `v3` в единую структуру `ALL_IN_ONE_KIT/` и автоматически исправит пути во всех `.sfz` из `v2`.
