#!/usr/bin/env python3
"""Chạy check thưởng độc lập, không thay orchestrator/cấu hình cố định của đề.

python scripts/run_extra_qc.py --src work/run/ds --max-ratio 15
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline.checks import aspect_ratio
from pipeline.common import Dataset, load_config, write_issues_csv


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--src', default='work/run/ds')
    parser.add_argument('--max-ratio', type=float, default=15)
    parser.add_argument('--out', default='submission/evidence/aspect_ratio.csv')
    args = parser.parse_args()
    cfg = load_config()
    cfg['aspect_ratio'] = {'max_ratio': args.max_ratio}
    ds = Dataset(ROOT / args.src, cfg['classes'])
    issues = aspect_ratio.run(ds, cfg)
    write_issues_csv(issues, ROOT / args.out)
    print(f'Đã quét {len(ds.image_files())} ảnh; {len(issues)} cảnh báo tỉ lệ cạnh > {args.max_ratio}; {args.out}')


if __name__ == '__main__':
    main()
