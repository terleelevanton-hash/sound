#!/usr/bin/env python3
"""
unify_kits.py — Склейка Dkits + MEGA_KIT_EXPANSION_v2 + MEGA_KIT_EXPANSION_v3
в единый всежанровый мастер-кит `ALL_IN_ONE_KIT/` + автоматическая починка SFZ-путей v2.

Запуск из корня репозитория (не требует сторонних библиотек):
    python3 tools/unify_kits.py
    python3 tools/unify_kits.py --out /путь/к/папке/FL_Studio_Packs/ALL_IN_ONE_KIT
"""
import argparse
import csv
import os
import re
import shutil
from pathlib import Path


DKITS_FALLBACK_MAP = {
    '808s': '12_808_SUB/dkits_808s',
    'claps': '03_CLAPS/dkits_claps',
    'claps and snares': '02_SNARES/dkits_claps_and_snares',
    'crashes': '07_CYMBALS/dkits_crashes',
    'fx': '15_FX/dkits_fx',
    'sfx': '15_FX/dkits_sfx',
    'hh': '05_HATS_CLOSED/dkits_hh',
    'hi hats': '05_HATS_CLOSED/dkits_hi_hats',
    'kicks': '01_KICKS/dkits_kicks',
    'oh': '06_HATS_OPEN/dkits_oh',
    'open hats': '06_HATS_OPEN/dkits_open_hats',
    'percloops': '16_LOOPS/perc_loops/dkits_percloops',
    'percs': '09_PERC_ACOUSTIC/dkits_percs',
    'snares': '02_SNARES/dkits_snares',
    'stomps': '11_STOMPS_BODY/dkits_stomps',
    'vox': '14_MELODIC/vox/dkits_vox',
}


def fix_v2_sfz_content(sfz_text: str) -> str:
    """Fix v2 relative paths (`sample=../01_` -> `sample=../../01_`) and widen narrow 1-octave ranges."""
    lines = []
    regions = []
    for line in sfz_text.splitlines():
        fixed = re.sub(r'sample=\.\./(?=\d\d_)', 'sample=../../', line)
        m = re.search(r'pitch_keycenter=(\d+)\s+lokey=(\d+)\s+hikey=(\d+)', fixed)
        if m:
            regions.append((len(lines), int(m.group(1)), fixed))
        lines.append(fixed)

    if regions:
        regions_sorted = sorted(regions, key=lambda t: t[1])
        midis = [r[1] for r in regions_sorted]
        for idx, (line_i, mid, orig_line) in enumerate(regions_sorted):
            lo = min(21, mid) if idx == 0 else ((midis[idx - 1] + mid) // 2 + 1)
            hi = max(108, mid) if idx == len(regions_sorted) - 1 else ((mid + midis[idx + 1]) // 2)
            lines[line_i] = re.sub(
                r'lokey=\d+\s+hikey=\d+',
                f'lokey={lo} hikey={hi}',
                orig_line,
            )
    return '\n'.join(lines) + '\n'


def copy_unique(src: Path, dst: Path, dry_run: bool = False) -> Path:
    if dst.exists():
        stem, suf = dst.stem, dst.suffix
        k = 2
        while dst.exists():
            dst = dst.with_name(f'{stem}_dup{k}{suf}')
            k += 1
    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return dst


def main():
    parser = argparse.ArgumentParser(description='Unify Dkits + MEGA_KIT v2 + MEGA_KIT v3 into one folder.')
    parser.add_argument('--kits-root', default='original_kit/kits', help='Path to original_kit/kits')
    parser.add_argument('--out', default='ALL_IN_ONE_KIT', help='Target unified kit folder')
    parser.add_argument('--dry-run', action='store_true', help='Only count files without copying')
    args = parser.parse_args()

    kits_root = Path(args.kits_root)
    out_root = Path(args.out)

    dkits_dir = kits_root / 'Dkits'
    v2_dir = kits_root / 'MEGA_KIT_EXPANSION_v2'
    v3_dir = kits_root / 'MEGA_KIT_EXPANSION_v3'

    counts = {'dkits': 0, 'v2': 0, 'v3': 0, 'v2_sfz_fixed': 0}

    # 1. Load CSV mapping for Dkits if available
    csv_map = {}
    map_csv = v2_dir / '00_START_HERE' / 'original_kit_to_new_folders.csv'
    if map_csv.is_file():
        with open(map_csv, encoding='utf-8', errors='replace') as fh:
            reader = csv.reader(fh, delimiter=';')
            header = next(reader, None)
            for row in reader:
                if len(row) >= 2:
                    csv_map[row[0].strip().replace('\\', '/')] = row[1].strip().replace('\\', '/')

    if dkits_dir.is_dir():
        for src in sorted(dkits_dir.rglob('*')):
            if not src.is_file():
                continue
            rel = src.relative_to(dkits_dir).as_posix()
            target_folder = csv_map.get(rel)
            if not target_folder:
                parent_lower = src.parent.name.lower()
                target_folder = DKITS_FALLBACK_MAP.get(parent_lower, '00_DKITS_EXTRAS')
            copy_unique(src, out_root / target_folder / src.name, dry_run=args.dry_run)
            counts['dkits'] += 1

    # 2. Merge MEGA_KIT_EXPANSION_v2 (fixing SFZ relative paths & key ranges on the fly)
    if v2_dir.is_dir():
        for src in sorted(v2_dir.rglob('*')):
            if not src.is_file() or '__pycache__' in src.parts:
                continue
            rel = src.relative_to(v2_dir)
            if rel.parts[0] == '00_START_HERE':
                dst = out_root / '00_START_HERE' / 'v2_docs_and_generator' / Path(*rel.parts[1:])
            elif rel.name == 'KIT_INDEX.csv':
                dst = out_root / 'KIT_INDEX_v2.csv'
            else:
                dst = out_root / rel

            if src.suffix.lower() == '.sfz':
                counts['v2_sfz_fixed'] += 1
                if not args.dry_run:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    txt = src.read_text(encoding='utf-8', errors='replace')
                    dst.write_text(fix_v2_sfz_content(txt), encoding='utf-8')
            else:
                copy_unique(src, dst, dry_run=args.dry_run)
            counts['v2'] += 1

    # 3. Merge MEGA_KIT_EXPANSION_v3
    if v3_dir.is_dir():
        for src in sorted(v3_dir.rglob('*')):
            if not src.is_file() or '__pycache__' in src.parts:
                continue
            rel = src.relative_to(v3_dir)
            if rel.parts[0] == '00_START_HERE':
                dst = out_root / '00_START_HERE' / 'v3_docs_and_generator' / Path(*rel.parts[1:])
            else:
                dst = out_root / rel
            copy_unique(src, dst, dry_run=args.dry_run)
            counts['v3'] += 1

    total = counts['dkits'] + counts['v2'] + counts['v3']
    mode_lbl = '[DRY RUN] ' if args.dry_run else ''
    print(f'{mode_lbl}Unified kit ready at: {out_root}')
    print(f"  Dkits files:        {counts['dkits']}")
    print(f"  Expansion v2 files: {counts['v2']} (auto-fixed SFZs: {counts['v2_sfz_fixed']})")
    print(f"  Expansion v3 files: {counts['v3']}")
    print(f'  TOTAL FILES:        {total}')


if __name__ == '__main__':
    main()
