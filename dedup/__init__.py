#!/Users/bussonniermatthias/miniconda3/envs/arm64/bin/python

import os
import hashlib
import sys


def compute_md5(file_path):
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()

def find_duplicates(dir_path, hash_dict):
    i = 0
    for root, _, files in os.walk(dir_path):
        for file in files:
            #if (i %10) == 0:
            #    print('.', end='')
            sys.stdout.flush()
            file_path = os.path.relpath(os.path.join(root, file))
            print(file_path)
            if '.git' in file_path:
                continue
            if '.index.html' in file_path:
                continue
            #i+=1
            file_hash = compute_md5(file_path)
            if file_hash in hash_dict:
                hash_dict[file_hash].append(file_path)
            else:
                hash_dict[file_hash] = [file_path]

if len(sys.argv)> 1:

    safe_dirs = sys.argv[0:]
else:
    safe_dirs = []

safes = set()
for d in safe_dirs:
    for root, _, files in os.walk(d):
        for file in files:
            file_path = os.path.join(root,file)
            safes.add(os.path.relpath(file_path))



hash_dict = {}
find_duplicates('.', hash_dict)
print()
n=0

dups = {k:v for k,v in hash_dict.items() if len(v) > 1}
for paths in dups.values():
    if len(paths) > 1:
        n+=1
        print('May be duplicates:')
        for p in paths:
            print(' ', repr(p))

print('safes:')
for s in safes:
    print('  ', s)

print('duplicates:')
for k,v in dups.items():
    print('   ', k)
    for vv in v:
        print('       ', vv)

s_dups = {k:(list(set(v) - safes), set(v).intersection(safes)) for k,v in dups.items() if
          len(set(v).intersection(safes)) > 0 and len(list(set(v) - safes))>0}

dups = {k:list(set(v) - safes) for k,v in dups.items() if len(list(set(v) - safes))>0}

removables = set()
for rr,keep in s_dups.values():
    for r in rr:
        removables.add(r)



print(f'Sdups {len(removables)}:')
for file in sorted(removables):
    print('   ', file)

removeall = input('remove all?')
if removeall == 'y':
    for file in sorted(removables):
        os.unlink(file)
else:
    print('skipping')
import questionary
import os
to_del = []
i = 0
for paths in dups.values():
    if len(paths) > 1:
        i+=1
        print(f'{i}/{n} May be duplicates:')
        res = questionary.select(
            "Which do you want to delete",
            choices=paths +['None','doit'], use_shortcuts=True
            ).ask()
        print(repr(res))
        if res == 'doit':
            break
        if not res:
            sys.exit(1)
        if res == 'None':
            pass
        else:
            print('will unlinking', res)
            to_del.append(res)

for r in to_del:
    print(r)
input('press any keys to continue')
for r in to_del:
    os.unlink(r)

