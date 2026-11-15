"""Content addressing shared by acquisition, export, and verification."""
import hashlib
import json
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def write_checksums(root):
    root = Path(root)
    checksums = {str(p.relative_to(root)): sha256(p) for p in sorted(root.rglob('*'))
                 if p.is_file() and p.name != 'checksums.json' and '__pycache__' not in p.parts}
    (root / 'checksums.json').write_text(json.dumps(checksums, indent=2) + '\n')
    return checksums


def verify_checksums(root):
    root = Path(root)
    expected = json.loads((root / 'checksums.json').read_text())
    if not expected:
        raise ValueError('Checksum manifest cannot be empty')
    for name, digest in expected.items():
        target = (root / name).resolve()
        if not target.is_relative_to(root.resolve()):
            raise ValueError('Unsafe checksum path')
        if sha256(target) != digest:
            raise ValueError(f'Checksum mismatch: {name}')
    return len(expected)
