#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Redact private libelf assertion source prefixes from ELF64 read-only strings.

Post-build privacy step. Preserves byte lengths, section layout and code; only
full absolute C-source filenames in .rodata are eligible. Run before hashing
and packaging. Rebuilding libelf with -ffile-prefix-map is preferred.
"""
import re
import struct
import sys
from pathlib import Path

def anonymize(data):
    if data[:6] != b'\x7fELF\x02\x01':
        raise ValueError('Expected little-endian ELF64')
    header=struct.unpack_from('<16sHHIQQQIHHHHHH',data)
    sections=[struct.unpack_from('<IIQQQQIIQQ',data,header[6]+i*header[11]) for i in range(header[12])]
    strings=sections[header[13]]
    names=data[strings[4]:strings[4]+strings[5]]
    output=bytearray(data); changes=[]
    pattern=re.compile(rb'/(?:home|Users)/[^/\x00\r\n]+/[^\x00\r\n]*?/libelf/(?P<file>elf(?:32|64)?_[A-Za-z0-9_]+\.c)\x00')
    for section in sections:
        if names[section[0]:].split(b'\x00',1)[0] != b'.rodata':continue
        start,size=section[4],section[5]
        for match in pattern.finditer(data[start:start+size]):
            prefix_len=match.start('file')-match.start()
            replacement=b'/build/'+b'_'*(prefix_len-8)+b'/'
            if len(replacement)!=prefix_len:raise ValueError('Invalid path length')
            at=start+match.start()
            output[at:at+prefix_len]=replacement
            changes.append((at,at+prefix_len))
    assert len(output)==len(data)
    for index,(old,new) in enumerate(zip(data,output)):
        if old!=new:assert any(a<=index<b for a,b in changes)
    return bytes(output),len(changes)

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('Usage: anonymize-build-paths.py ELF_FILE')
    path=Path(sys.argv[1]); data=path.read_bytes(); output,count=anonymize(data)
    if count:path.write_bytes(output)
    print(f'Anonymized {count} diagnostic source path(s); byte lengths preserved.')
