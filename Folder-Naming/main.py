#!/usr/bin/env python3
"""
rename_files.py

Recursively renames all files in a folder to a chosen naming convention,
based on the words found in each file's current base name.

Supported conventions:
  kebab   -> "Whatever-This-Is"   (capitalized words, hyphen-separated)
  title   -> "Whatever This Is"   (capitalized words, space-separated)
  pascal_underscore -> "Whatever_This_Is" (capitalized words, underscore-separated)
  snake   -> "whatever_this_is"   (lowercase words, underscore-separated)

Usage:
  python rename_files.py /path/to/folder --style kebab
  python rename_files.py /path/to/folder --style title --dry-run
  python rename_files.py /path/to/folder --style snake --extensions .txt .md
"""

import argparse
import os
import re
import sys
from pathlib import Path


# --- Word splitting -----------------------------------------------------

# Splits a filename stem into individual "words", handling:
#   - existing hyphens, underscores, and spaces as separators
#   - camelCase / PascalCase boundaries (e.g. "myFileName" -> ["my", "File", "Name"])
#   - runs of digits treated as their own word
_WORD_SPLIT_RE = re.compile(
    r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+"
)


def split_into_words(stem: str) -> list[str]:
    """Break a filename stem (no extension) into a list of lowercase-agnostic words."""
    # Normalize existing separators to spaces first
    normalized = re.sub(r"[-_]+", " ", stem)
    words: list[str] = []
    for chunk in normalized.split(" "):
        if not chunk:
            continue
        found = _WORD_SPLIT_RE.findall(chunk)
        words.extend(found if found else [chunk])
    return [w for w in words if w]


# --- Naming convention formatters ---------------------------------------

def to_kebab(words: list[str]) -> str:
    return "-".join(w.capitalize() for w in words)


def to_title(words: list[str]) -> str:
    return " ".join(w.capitalize() for w in words)


def to_pascal_underscore(words: list[str]) -> str:
    return "_".join(w.capitalize() for w in words)


def to_snake(words: list[str]) -> str:
    return "_".join(w.lower() for w in words)


STYLE_FORMATTERS = {
    "kebab": to_kebab,               # Whatever-This-Is
    "title": to_title,               # Whatever This Is
    "pascal_underscore": to_pascal_underscore,  # Whatever_This_Is
    "snake": to_snake,               # whatever_this_is
}


# --- Core renaming logic --------------------------------------------------

def build_new_name(filename: str, style: str) -> str:
    """Given an original filename (with extension), return the renamed version."""
    path = Path(filename)
    stem, ext = path.stem, path.suffix  # ext includes the leading dot, e.g. ".txt"
    words = split_into_words(stem)
    if not words:
        return filename  # nothing sensible to rename
    formatter = STYLE_FORMATTERS[style]
    new_stem = formatter(words)
    return f"{new_stem}{ext}"


def unique_path(target: Path) -> Path:
    """If target already exists, append -1, -2, etc. before the extension until unique."""
    if not target.exists():
        return target
    stem, ext, parent = target.stem, target.suffix, target.parent
    counter = 1
    while True:
        candidate = parent / f"{stem}-{counter}{ext}"
        if not candidate.exists():
            return candidate
        counter += 1


def rename_files(
    root: Path,
    style: str,
    extensions: list[str] | None,
    dry_run: bool,
) -> None:
    ext_filter = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in extensions} if extensions else None

    renamed_count = 0
    skipped_count = 0

    # os.walk lets us go bottom-up if needed, but top-down is fine since we
    # are only renaming files, not directories.
    for dirpath, _dirnames, filenames in os.walk(root):
        dirpath = Path(dirpath)
        for filename in filenames:
            if ext_filter and Path(filename).suffix.lower() not in ext_filter:
                continue

            new_name = build_new_name(filename, style)
            if new_name == filename:
                skipped_count += 1
                continue

            old_path = dirpath / filename
            new_path = unique_path(dirpath / new_name)

            rel_old = old_path.relative_to(root)
            rel_new = new_path.relative_to(root)

            if dry_run:
                print(f"[dry-run] {rel_old}  ->  {rel_new}")
            else:
                try:
                    old_path.rename(new_path)
                    print(f"{rel_old}  ->  {rel_new}")
                except OSError as e:
                    print(f"ERROR renaming {rel_old}: {e}", file=sys.stderr)
                    continue

            renamed_count += 1

    action = "Would rename" if dry_run else "Renamed"
    print(f"\n{action} {renamed_count} file(s). Skipped {skipped_count} (already matched or no words found).")


# --- CLI -------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recursively rename files in a folder to a chosen naming convention."
    )
    parser.add_argument("folder", type=str, help="Path to the folder to process recursively.")
    parser.add_argument(
        "--style",
        required=True,
        choices=list(STYLE_FORMATTERS.keys()),
        help=(
            "Naming convention to apply:\n"
            "  kebab              -> Whatever-This-Is\n"
            "  title              -> Whatever This Is\n"
            "  pascal_underscore  -> Whatever_This_Is\n"
            "  snake              -> whatever_this_is"
        ),
    )
    parser.add_argument(
        "--extensions",
        nargs="*",
        default=None,
        help="Optional list of extensions to limit renaming to, e.g. --extensions .txt .md",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be renamed without actually renaming anything.",
    )

    args = parser.parse_args()
    root = Path(args.folder).expanduser().resolve()

    if not root.is_dir():
        print(f"Error: '{root}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    rename_files(root, args.style, args.extensions, args.dry_run)


# --- Interactive mode --------------------------------------------------

STYLE_MENU = {
    "1": ("kebab", "Whatever-This-Is"),
    "2": ("title", "Whatever This Is"),
    "3": ("pascal_underscore", "Whatever_This_Is"),
    "4": ("snake", "whatever_this_is"),
}


def prompt_for_folder() -> Path:
    while True:
        raw = input("Paste the folder path to process: ").strip().strip('"').strip("'")
        root = Path(raw).expanduser().resolve()
        if root.is_dir():
            return root
        print(f"'{root}' is not a valid directory. Try again.\n")


def prompt_for_style() -> str:
    print("\nChoose a naming convention:")
    for key, (_style, example) in STYLE_MENU.items():
        print(f"  {key}) {example}")
    while True:
        choice = input("Enter 1-4: ").strip()
        if choice in STYLE_MENU:
            return STYLE_MENU[choice][0]
        print("Invalid choice. Try again.")


def prompt_for_extensions() -> list[str] | None:
    raw = input(
        "\nLimit to specific extensions? (e.g. .txt .md) "
        "Leave blank for all files: "
    ).strip()
    if not raw:
        return None
    return raw.split()


def prompt_for_dry_run() -> bool:
    choice = input("\nDo a dry run first (no files actually renamed)? [y/n]: ").strip().lower()
    return choice in ("", "y", "yes")


def run_interactive() -> None:
    print("=== Recursive File Renamer ===\n")
    root = prompt_for_folder()
    style = prompt_for_style()
    extensions = prompt_for_extensions()
    dry_run = prompt_for_dry_run()

    print()
    rename_files(root, style, extensions, dry_run)

    # If they dry-ran first, offer to actually apply it right after.
    if dry_run:
        confirm = input("\nApply these renames for real now? [y/n]: ").strip().lower()
        if confirm in ("y", "yes"):
            print()
            rename_files(root, style, extensions, dry_run=False)
        else:
            print("No files were changed.")


if __name__ == "__main__":
    # If run with no command-line arguments, drop into interactive prompt
    # mode so the folder path (and options) can just be typed/pasted in.
    # If arguments ARE provided, fall back to the normal argparse CLI.
    if len(sys.argv) == 1:
        run_interactive()
    else:
        main()