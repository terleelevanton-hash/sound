"""Minimal Standard MIDI File writer."""
import struct


def _vlq(n):
    out = bytearray([n & 0x7F])
    n >>= 7
    while n:
        out.insert(0, (n & 0x7F) | 0x80)
        n >>= 7
    return bytes(out)


def write_midi(path, tracks, ppq=480, bpm=120):
    """tracks: list of dicts {name, channel, notes:[(start_beats, dur_beats, pitch, vel)]}"""
    data = b'MThd' + struct.pack('>IHHH', 6, 1, len(tracks) + 1, ppq)
    # tempo track
    t0 = b'\x00\xff\x51\x03' + struct.pack('>I', int(60_000_000 / bpm))[1:]
    t0 += b'\x00\xff\x2f\x00'
    data += b'MTrk' + struct.pack('>I', len(t0)) + t0
    for tr in tracks:
        ch = tr.get('channel', 0) - 1  # 0-indexed
        ev = []
        for (start, dur, pitch, vel) in tr['notes']:
            ev.append((int(round(start * ppq)), 0x90 | ch, pitch, vel))
            ev.append((int(round((start + dur) * ppq)), 0x80 | ch, pitch, 0))
        ev.sort(key=lambda e: (e[0], e[1] & 0xF0 == 0x90))
        body = bytearray()
        # track name
        nm = tr.get('name', 'track').encode()
        body += b'\x00\xff\x03' + _vlq(len(nm)) + nm
        last = 0
        for (tick, status, d1, d2) in ev:
            body += _vlq(tick - last) + bytes([status, d1, d2])
            last = tick
        body += b'\x00\xff\x2f\x00'
        data += b'MTrk' + struct.pack('>I', len(body)) + bytes(body)
    with open(path, 'wb') as fh:
        fh.write(data)
