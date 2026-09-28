#!/usr/bin/env python3
"""Stage only assets allowed by an exact, clean and successfully tested source checkout."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from verify import ROOT, digest, require, source_evidence, verify


def git(source, *args):
    return subprocess.check_output(["git", "-C", str(source), *args], text=True).strip()


def promote(source, commit, run_id, base_main_commit):
    source = Path(source).resolve(strict=True)
    require(source != ROOT and not ROOT.is_relative_to(source) and not source.is_relative_to(ROOT),
            "Use a separate authoritative source checkout.")
    require(git(source, "rev-parse", "HEAD") == commit, "Source checkout is not at the explicit commit.")
    require(not git(source, "status", "--porcelain", "--untracked-files=all"),
            "Source checkout must have no modified or untracked files.")
    evidence = source_evidence(run_id, commit, base_main_commit)
    validator = source / ".github/scripts/check_site.py"
    require(validator.is_file() and not validator.is_symlink(), "Source public-asset validator is missing.")
    with tempfile.TemporaryDirectory(prefix="savekewriverside-promotion-") as temporary:
        staging_root = Path(temporary)
        staged = staging_root / "public"
        # The authoritative validator supplies the allowlist; never copy the repository wholesale.
        subprocess.run([sys.executable, str(validator), "--stage", str(staged)], cwd=source, check=True)
        files = {}
        for path in sorted(staged.rglob("*")):
            require(not path.is_symlink(), "Source staging produced a symlink.")
            if path.is_file():
                files[path.relative_to(staged).as_posix()] = digest(path)
        manifest = {
            "schema_version": 2,
            "promoted_at_utc": datetime.now(timezone.utc).isoformat(),
            "source": evidence,
            "validator_sha256": digest(validator),
            "files": files,
        }
        (staging_root / "promotion.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        verify(staging_root, check_source_run=True)
        require(not git(source, "status", "--porcelain", "--untracked-files=all")
                and git(source, "rev-parse", "HEAD") == commit,
                "Source checkout changed during promotion.")
        destination = ROOT / "public"
        require(not destination.is_symlink(), "Public destination may not be a symlink.")
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(staged, destination)
        shutil.copyfile(staging_root / "promotion.json", ROOT / "promotion.json")
    return verify()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="Clean authoritative source checkout")
    parser.add_argument("--commit", required=True, help="Full source commit SHA")
    parser.add_argument("--run-id", required=True, type=int, help="Successful source Pages workflow run ID")
    parser.add_argument("--base-main", required=True, help="Full current main SHA included in the tested candidate")
    args = parser.parse_args()
    try:
        count = promote(args.source, args.commit, args.run_id, args.base_main)
        print(f"Promoted {count} allowlisted assets from {args.commit}. Review and commit public/ and promotion.json together.")
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Promotion failed: {error}\n")
