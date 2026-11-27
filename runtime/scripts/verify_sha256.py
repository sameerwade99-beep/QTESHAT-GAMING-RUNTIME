
#!/usr/bin/env python3

import argparse
import hashlib
import re
import sys
from pathlib import Path


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def verify_file(file_path, expected_hash):
    path = Path(file_path)

    if not path.is_file():
        print("ERROR: File does not exist.")
        return False

    if not expected_hash:
        print("ERROR: SHA-256 checksum is missing.")
        return False

    expected_hash = expected_hash.strip().lower()

    if not re.fullmatch(r"[a-f0-9]{64}", expected_hash):
        print("ERROR: Invalid SHA-256 format.")
        return False

    actual_hash = calculate_sha256(path)

    print(f"Expected: {expected_hash}")
    print(f"Actual:   {actual_hash}")

    if actual_hash == expected_hash:
        print("SUCCESS: File verification passed.")
        return True

    print("FAILED: SHA-256 mismatch.")
    return False


def main():
    parser = argparse.ArgumentParser(
        description="QTESHAT GAMING SHA-256 Verifier"
    )

    parser.add_argument("--file", required=True)
    parser.add_argument("--sha256", required=True)

    args = parser.parse_args()

    if not verify_file(args.file, args.sha256):
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
