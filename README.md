# Duplicate File Scanner

A command-line Python script to efficiently find and report duplicate files within a specified directory.

This script identifies duplicates by first comparing file sizes and then comparing a partial hash (the first 4MB and last 1MB of the file). This method is significantly faster than performing a full-file hash on every file, especially in directories with many large files.

## Summary of Operations

1.  **Scans Recursively:** Walks through the entire directory tree from the starting path you provide.
2.  **Groups by Size:** First identifies files that have the exact same size, as files with different sizes cannot be duplicates.
3.  **Calculates Partial Hashes:** For files of the same size, it calculates a unique SHA-256 hash from the beginning and end portions of the file.
4.  **Identifies Duplicates:** Files that have both the same size and the same partial hash are flagged as a duplicate set.
5.  **Reports Findings:** Prints a summary to the console and saves a detailed report in JSON format, along with a log file of the operation.

---

## Example Usage

The script is run from the command line and takes one required argument (the path to scan) and one optional argument (the name of the output file).

#### Basic Scan
This command will scan the specified directory and create default log and report files in the current working directory.

```bash
python improved-dedupe-poc.py "/path/to/your/photos"
```

#### View results
```bash
cat duplicate_scan_20250720_152540.log
2025-07-20 15:25:40,779 - INFO - Starting duplicate file scan in '/Users/p/Downloads'
2025-07-20 15:25:45,087 - INFO - Scan complete. Processed 26502 files.
2025-07-20 15:25:45,087 - INFO - Found 566 sets of duplicates, wasting 0.03 GB.
2025-07-20 15:25:45,091 - INFO - Results saved to dedupe-results-20250720_152540.json
```
```bash
cat dedupe-results-20250720_152540.json
{
  "scan_time": "2025-07-20T15:25:45.089538",
  "duplicate_groups": 566,
  "duplicates": {
    "f07d5b2759899b8c7adaeb58d26c8270f7c050dafbbe28a243131afd69a468cb": [
...
```