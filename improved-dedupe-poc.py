import os
import hashlib
import json
import argparse  # Replaces fire
from datetime import datetime
import logging
from typing import Dict, List, Optional

# Global datestamp for default filenames
datestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Set up logging to a time-stamped file
logging.basicConfig(
    filename=f'duplicate_scan_{datestamp}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def calculate_partial_hash(filepath: str) -> Optional[str]:
    """Calculates a partial SHA-256 hash of a file for fast duplicate checking."""
    hasher = hashlib.sha256()
    START_CHUNK_SIZE = 4 * 1024 * 1024  # 4MB
    END_CHUNK_SIZE = 1 * 1024 * 1024    # 1MB

    try:
        filesize = os.path.getsize(filepath)
        with open(filepath, 'rb') as f:
            first_chunk = f.read(START_CHUNK_SIZE)
            hasher.update(first_chunk)
            if filesize > START_CHUNK_SIZE:
                seek_position = max(START_CHUNK_SIZE, filesize - END_CHUNK_SIZE)
                f.seek(seek_position)
                last_chunk = f.read()
                hasher.update(last_chunk)
        return hasher.hexdigest()
    except (IOError, PermissionError) as e:
        logging.error(f"Could not access or read file '{filepath}': {e}")
        return None

def find_duplicates(root_path: str) -> Dict[str, List[str]]:
    """Finds duplicate files by first checking size, then partial hash."""
    size_groups: Dict[int, Dict[str, List[str]]] = {}
    total_files = 0
    duplicate_sets = 0
    logging.info(f"Starting duplicate file scan in '{root_path}'")
    print(f"Scanning '{root_path}'... Logs will be saved to duplicate_scan_{datestamp}.log")

    try:
        for root, _, filenames in os.walk(root_path):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                total_files += 1

                try:
                    filesize = os.path.getsize(filepath)
                except OSError as e:
                    logging.warning(f"Skipping {filepath}: {e}")
                    continue

                if filesize < 1:  # Skip zero-byte files
                    continue

                # Lazily initialize dictionaries
                if filesize not in size_groups:
                    size_groups[filesize] = {}
                
                partial_hash = calculate_partial_hash(filepath)
                if not partial_hash:
                    continue

                if partial_hash not in size_groups[filesize]:
                    size_groups[filesize][partial_hash] = []
                
                size_groups[filesize][partial_hash].append(filepath)

    except KeyboardInterrupt:
        logging.warning("Scan interrupted by user.")
        print("\nScan interrupted.")

    # Filter results to find actual duplicates and calculate wasted space
    duplicates = {}
    wasted_space = 0
    for size, hash_map in size_groups.items():
        for file_hash, paths in hash_map.items():
            if len(paths) > 1:
                duplicates[file_hash] = paths
                duplicate_sets += 1
                wasted_space += size * (len(paths) - 1)

    gb_wasted = wasted_space / (1024**3)
    logging.info(f"Scan complete. Processed {total_files} files.")
    logging.info(f"Found {duplicate_sets} sets of duplicates, wasting {gb_wasted:.2f} GB.")
    print(f"Scan complete. Found {duplicate_sets} duplicate sets wasting {gb_wasted:.2f} GB.")
    return duplicates

def save_results(duplicates: Dict[str, List[str]], output_file: str):
    """Saves duplicate file information to a JSON file."""
    output_data = {
        'scan_time': datetime.now().isoformat(),
        'duplicate_groups': len(duplicates),
        'duplicates': duplicates
    }
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    logging.info(f"Results saved to {output_file}")
    print(f"Detailed results saved to {output_file}")

def main(path: str, output: Optional[str] = None):
    """
    Finds and reports duplicate files within a specified directory.

    :param path: The directory to scan for duplicate files.
    :param output: Optional path to save the JSON results file.
                   Defaults to 'dedupe-results-YYYYMMDD_HHMMSS.json'.
    """
    if not os.path.isdir(path):
        print(f"Error: Path '{path}' is not a valid directory.")
        logging.error(f"Invalid path provided: {path}")
        return

    # If no output file is specified, create the default name
    if output is None:
        output = f"dedupe-results-{datestamp}.json"

    duplicates = find_duplicates(path)
    if duplicates:
        save_results(duplicates, output)
    else:
        logging.info("No duplicate files were found.")
        print("No duplicate files were found.")

if __name__ == "__main__":
    # Use argparse to handle command-line arguments instead of fire
    parser = argparse.ArgumentParser(
        description="Finds and reports duplicate files within a specified directory."
    )
    parser.add_argument(
        "path",
        help="The directory to scan for duplicate files."
    )
    parser.add_argument(
        "-o", "--output",
        help="Optional path to save the JSON results file. "
             "Defaults to 'dedupe-results-YYYYMMDD_HHMMSS.json'."
    )
    
    args = parser.parse_args()
    
    # Call the main function with the parsed arguments
    main(path=args.path, output=args.output)