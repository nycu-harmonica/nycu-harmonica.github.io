#!/usr/bin/env python3
"""Unblind one saved review and append its scores to results/scores.json.

  python3 docs/design-review/tools/score.py ROUND REVIEWER RESULT_MD

Reads the reviewer's raw output (the last ```json block), maps A/B/C back to
baseline/new/reference with /tmp/bmhc-review/private/rROUND.json, and prints
overall scores, the 12-category means and new − baseline.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path('/tmp/bmhc-review')
RESULTS = Path(__file__).resolve().parents[1] / 'results'


def main():
    number, reviewer, path = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    text = path.read_text()
    blocks = re.findall(r'```json\s*(\{.*?\})\s*```', text, re.S)
    data = json.loads(blocks[-1])
    mapping = json.loads((ROOT / 'private' / f'r{number}.json').read_text())['mapping']
    row = {'round': number, 'reviewer': reviewer, 'file': path.name, 'mapping': mapping}
    for label, name in mapping.items():
        group = data[label]
        scores = [float(v) for v in group.get('scores', {}).values()]
        row[name] = {
            'overall': float(group.get('overall', 0)),
            'mean': round(sum(scores) / len(scores), 2) if scores else None,
            'scores': group.get('scores', {}),
            'issues': group.get('issues', []),
        }
    row['delta_overall'] = round(row['new']['overall'] - row['baseline']['overall'], 2)
    row['delta_mean'] = round(row['new']['mean'] - row['baseline']['mean'], 2)
    store = RESULTS / 'scores.json'
    rows = json.loads(store.read_text()) if store.exists() else []
    rows = [r for r in rows if not (r['round'] == number and r['reviewer'] == reviewer)] + [row]
    store.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
    for name in ('baseline', 'new', 'reference'):
        print(f"{name:9} overall {row[name]['overall']:>4}  mean {row[name]['mean']}")
    print(f"new - baseline: overall {row['delta_overall']:+}, mean {row['delta_mean']:+}")
    print('new issues:')
    for issue in row['new']['issues']:
        print(' -', issue)


if __name__ == '__main__':
    main()
