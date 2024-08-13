"""
Find duplicate files based on hashes.
"""
__version__ = "0.0.1"
import sys

import os
import hashlib
import sys


def compute_md5(file_path):
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        md5_hash.update(f.read())
    return md5_hash.hexdigest()


def _ig(full, ignores):
    for ig in ignores:
        if ig in full:
            return True
    return False


def iter_files(dir_path, ignores):
    for root, _, files in os.walk(dir_path):
        for file in files:
            full = os.path.relpath(os.path.join(root, file))
            if _ig(full, ignores):
                continue
            yield full


def find_hashes(dir_path, hash_dict=None):
    if hash_dict is None:
        hash_dict = {}
    for file_path in iter_files(dir_path, [".git", ".mypy_cache"]):
        file_hash = compute_md5(file_path)
        print(file_hash, file_path)
        if file_hash in hash_dict:
            hash_dict[file_hash].append(file_path)
        else:
            hash_dict[file_hash] = [file_path]
    return hash_dict


from typing import List, Optional
import typer
from typing_extensions import Annotated


def main(where, safe: Annotated[Optional[List[str]], typer.Option()] = []):
    hd = {}
    candidates = find_hashes(where)
    for safe_x in safe:
        find_hashes(safe_x, hd)

    # files that have a copy in a safe location:

    common_hashes = set(candidates.keys()).intersection(set(hd.keys()))

    print("common hashes:")
    for c in common_hashes:
        print("  duplicates:")
        for cx in candidates[c]:
            print("    ", cx)
        print("  corresponding:")
        for cx in hd[c]:
            print("    ", cx)

    dups = {k: v for k, v in candidates.items() if len(v) > 1}
    for paths in dups.values():
        print("May be duplicates:")
        for p in paths:
            print(" ", repr(p))
    sys.exit()

    print("safes:")
    for s in safes:
        print("  ", s)

    print("duplicates:")
    for k, v in dups.items():
        print("   ", k)
        for vv in v:
            print("       ", vv)

    s_dups = {
        k: (list(set(v) - safes), set(v).intersection(safes))
        for k, v in dups.items()
        if len(set(v).intersection(safes)) > 0 and len(list(set(v) - safes)) > 0
    }

    dups = {
        k: list(set(v) - safes)
        for k, v in dups.items()
        if len(list(set(v) - safes)) > 0
    }

    removables = set()
    for rr, keep in s_dups.values():
        for r in rr:
            removables.add(r)

    print(f"Sdups {len(removables)}:")
    for file in sorted(removables):
        print("   ", file)

    removeall = input("remove all?")
    if removeall == "y":
        for file in sorted(removables):
            os.unlink(file)
    else:
        print("skipping")
    import questionary
    import os

    to_del = []
    i = 0
    for paths in dups.values():
        if len(paths) > 1:
            i += 1
            print(f"{i}/{n} May be duplicates:")
            res = questionary.select(
                "Which do you want to delete",
                choices=paths + ["None", "doit"],
                use_shortcuts=True,
            ).ask()
            print(repr(res))
            if res == "doit":
                break
            if not res:
                sys.exit(1)
            if res == "None":
                pass
            else:
                print("will unlinking", res)
                to_del.append(res)

    for r in to_del:
        print(r)
    input("press any keys to continue")
    for r in to_del:
        os.unlink(r)
