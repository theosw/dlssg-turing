"""Check the pinned extraction and optionally its canonical TRP Git objects."""
import argparse, hashlib, json, pathlib, subprocess, sys
root = pathlib.Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--trp', type=pathlib.Path, help='local TRP Git checkout containing the pinned commit')
args = parser.parse_args()
manifest = json.loads((root / 'SOURCE-MANIFEST.json').read_text())
errors = []
for entry in manifest['files']:
    path = root / entry['path']
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
        errors.append('extraction differs: ' + entry['path'])
    if args.trp:
        result = subprocess.run(['git', '-C', str(args.trp), 'show', manifest['commit'] + ':' + entry['sourcePath']], capture_output=True)
        if result.returncode or hashlib.sha256(result.stdout).hexdigest() != entry['sha256']:
            errors.append('TRP source differs/unavailable: ' + entry['sourcePath'])
if errors:
    print('\n'.join(errors), file=sys.stderr)
    sys.exit(1)
print(f"Verified {len(manifest['files'])} files from {manifest['commit']}")
