#!/usr/bin/env python3
"""
extract_zips.py
Recursively find .zip files under a base directory and extract each into a subfolder
next to the zip (folder named after the zip file without .zip).
Corrupted / unreadable ZIPs are skipped.
"""

import zipfile
from pathlib import Path
import argparse
import logging
import sys

def main(base_dir: Path, extract_into_subfolder: bool = True):
    if not base_dir.exists():
        print(f"Error: base directory does not exist: {base_dir}")
        sys.exit(1)

    # Find all .zip files recursively
    zip_paths = list(base_dir.rglob("*.zip"))

    if not zip_paths:
        print(f"No .zip files found under: {base_dir}")
        return

    total = len(zip_paths)
    extracted_count = 0
    skipped_count = 0

    for zpath in zip_paths:
        # Decide where to extract:
        # if extract_into_subfolder -> /path/to/zipname/  (keeps things neat)
        # else -> extract directly into zpath.parent
        if extract_into_subfolder:
            extract_dir = zpath.with_suffix("")  # same dir, folder named like file (no .zip)
        else:
            extract_dir = zpath.parent

        extract_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(zpath, 'r') as zf:
                # testzip() returns the name of the first bad file or None if OK
                bad_file = zf.testzip()
                if bad_file is not None:
                    logging.warning(f"Corrupted member '{bad_file}' inside {zpath}. Skipping.")
                    skipped_count += 1
                    continue

                # Extract all members
                zf.extractall(path=extract_dir)

            logging.info(f"Extracted: {zpath} -> {extract_dir}")
            extracted_count += 1

        except zipfile.BadZipFile:
            logging.warning(f"Bad/corrupted zip file (BadZipFile): {zpath}. Skipping.")
            skipped_count += 1
        except RuntimeError as e:
            # sometimes encryption or other runtime issues surface here
            logging.warning(f"RuntimeError with {zpath}: {e}. Skipping.")
            skipped_count += 1
        except PermissionError as e:
            logging.error(f"PermissionError extracting {zpath}: {e}. Skipping.")
            skipped_count += 1
        except Exception as e:
            logging.error(f"Unexpected error with {zpath}: {e}. Skipping.")
            skipped_count += 1

    print()
    print(f"Scanned {total} .zip files.")
    print(f"Successfully extracted: {extracted_count}")
    print(f"Skipped / failed: {skipped_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recursively extract .zip files.")
    parser.add_argument(
        "base_dir",
        nargs="?",
        default="/home/vsysuser/workspace/ASSIGNMENTS/Assignment2",
        help="Base directory to search (default: your Assignment2 folder)."
    )
    parser.add_argument(
        "--no-subfolder",
        action="store_true",
        help="If provided, extract files directly into the zip's parent directory (not a new subfolder)."
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show more logging.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(levelname)s: %(message)s")

    main(Path(args.base_dir), extract_into_subfolder=not args.no_subfolder)
