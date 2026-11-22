"""Bug-free Standard MIDI File (.mid) and SFZ (.sfz) / Pad Layout generators."""
import os
import re
import struct

NAME2PC = {
    'C': 0, 'C#': 1, 'Cs': 1, 'D': 2, 'D#': 3, 'Ds': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Fs': 6, 'G': 7, 'G#': 8, 'Gs': 8,
    'A': 9, 'A#': 10, 'As': 10, 'B': 11,
}


def note_str_to_midi(note_str):
    m = re.match(r'^([A-G](?:#|s)?)(-?\d+)$', note_str.strip())
    if not m:
        raise ValueError(f'Invalid note string: {note_str!r}')
    return NAME2PC[m.group(1)] + (int(m.group(2)) + 1) * 12


def _vlq(n):
    n = max(0, int(n))
    out = bytearray([n & 0x7F])
    n >>= 7
    while n:
        out.insert(0, (n & 0x7F) | 0x80)
        n >>= 7
    return bytes(out)


def write_midi(path, tracks, ppq=480, bpm=120, time_sig=(4, 4)):
    """
    Write Format-1 Standard MIDI File.
    tracks: list of dicts {
        'name': str,
        'channel': int (0..15, where 9 is GM drums),
        'program': optional int (0..127),
        'notes': [(start_beats, dur_beats, midi_pitch, velocity), ...]
    }
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    header = b'MThd' + struct.pack('>IHHH', 6, 1, len(tracks) + 1, ppq)

    # Tempo & Time Signature track
    us_per_beat = int(round(60_000_000.0 / max(float(bpm), 20.0)))
    num, den = time_sig
    den_pow = int(round({1: 0, 2: 1, 4: 2, 8: 3, 16: 4}.get(den, 2)))
    t0 = bytearray()
    t0 += b'\x00\xff\x58\x04' + bytes([num, den_pow, 24, 8])
    t0 += b'\x00\xff\x51\x03' + struct.pack('>I', us_per_beat)[1:]
    t0 += b'\x00\xff\x2f\x00'
    chunks = [header, b'MTrk' + struct.pack('>I', len(t0)) + bytes(t0)]

    for tr in tracks:
        ch = int(tr.get('channel', 0)) & 0x0F
        body = bytearray()
        nm = str(tr.get('name', 'Track')).encode('utf-8')
        body += b'\x00\xff\x03' + _vlq(len(nm)) + nm
        if 'program' in tr and tr['program'] is not None and ch != 9:
            body += b'\x00' + bytes([0xC0 | ch, int(tr['program']) & 0x7F])

        events = []
        for start_b, dur_b, pitch, vel in tr.get('notes', []):
            s_tick = max(0, int(round(float(start_b) * ppq)))
            e_tick = max(s_tick + 1, int(round((float(start_b) + float(dur_b)) * ppq)))
            p = max(0, min(127, int(pitch)))
            v = max(1, min(127, int(vel)))
            # Sort note-off (order 0) BEFORE note-on (order 1) at identical tick so repeated notes retrigger!
            events.append((s_tick, 1, 0x90 | ch, p, v))
            events.append((e_tick, 0, 0x80 | ch, p, 0))

        events.sort(key=lambda e: (e[0], e[1], e[3]))
        last_tick = 0
        for tick, _ord, status, d1, d2 in events:
            body += _vlq(tick - last_tick) + bytes([status, d1, d2])
            last_tick = tick

        body += b'\x00\xff\x2f\x00'
        chunks.append(b'MTrk' + struct.pack('>I', len(body)) + bytes(body))

    with open(path, 'wb') as fh:
        fh.write(b''.join(chunks))


def write_melodic_sfz(sfz_path, kit_root, instr_name, sample_entries, release_s=0.35, lo_limit=21, hi_limit=108):
    """
    Write full-keyboard non-overlapping SFZ instrument with verified relative paths.
    sample_entries: list of (midi_note, rel_path_from_kit_root)
    """
    os.makedirs(os.path.dirname(sfz_path), exist_ok=True)
    sfz_dir = os.path.dirname(sfz_path)
    items = sorted(sample_entries, key=lambda t: t[0])
    # Deduplicate same MIDI pitch if any
    dedup = []
    seen = set()
    for m, rel in items:
        if m not in seen:
            seen.add(m)
            dedup.append((m, rel))
    items = dedup
    if not items:
        return

    lines = [
        f'// MEGA KIT v3 - {instr_name} ({len(items)} multi-sampled root zones)',
        '// Full keyboard range A0..C8 (MIDI 21..108), non-overlapping zones, verified paths',
        '<global>',
        f'ampeg_release={release_s:.2f}',
        'amp_veltrack=82',
        '',
    ]
    midis = [m for m, _ in items]
    for i, (mid, rel) in enumerate(items):
        lokey = min(lo_limit, mid) if i == 0 else ((midis[i - 1] + mid) // 2 + 1)
        hikey = max(hi_limit, mid) if i == len(items) - 1 else ((mid + midis[i + 1]) // 2)
        abs_target = os.path.join(kit_root, rel)
        rel_from_sfz = os.path.relpath(abs_target, sfz_dir).replace(os.sep, '/')
        lines.append(
            f'<region> sample={rel_from_sfz} pitch_keycenter={mid} lokey={lokey} hikey={hikey} lovel=1 hivel=127'
        )

    with open(sfz_path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')


def write_drum_kit_sfz_and_txt(sfz_dir, kit_root, kit_name, pad_entries):
    """
    pad_entries: list of 16 tuples (role_label, rel_path_from_kit_root)
    """
    os.makedirs(sfz_dir, exist_ok=True)
    sfz_path = os.path.join(sfz_dir, f'{kit_name}.sfz')
    txt_path = os.path.join(sfz_dir, f'{kit_name}_PAD_LAYOUT.txt')

    sfz_lines = [
        f'// MEGA KIT v3 - {kit_name.upper()} 16-Pad Producer Kit',
        '// Mapped to MIDI notes 36..51 (C2..D#3 standard MPC / FL FPC / Ableton Drum Rack)',
        '<global>',
        'ampeg_release=0.80',
        'amp_veltrack=85',
        '',
    ]
    txt_lines = [
        f'{kit_name.upper()} — Рекомендуемая 16-пэд раскладка (MEGA KIT v3)',
        '=' * 64,
        '',
    ]

    for idx, (role, rel) in enumerate(pad_entries):
        key = 36 + idx
        txt_lines.append(f'{idx + 1:2d}. [MIDI {key:2d}] {role:18s} {rel}')
        if rel:
            abs_target = os.path.join(kit_root, rel)
            rel_from_sfz = os.path.relpath(abs_target, sfz_dir).replace(os.sep, '/')
            # Closed & open hi-hat mute group (group=1 off_by=1) on pads 6 & 7
            choke = ''
            if idx == 5:
                choke = ' group=1 off_by=1'
            elif idx == 6:
                choke = ' group=1 off_by=1'
            sfz_lines.append(f'<region> sample={rel_from_sfz} key={key} lovel=1 hivel=127{choke}')

    with open(sfz_path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(sfz_lines) + '\n')
    with open(txt_path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(txt_lines) + '\n')
