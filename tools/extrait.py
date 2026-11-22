"""Extrait le texte japonais de VOTRE ROM dans out/jp.tsv (+ police d'origine dans out/police_jp.bin).

    python tools/extrait.py "Party Mail (Japan).ngc"


Colonnes : id, lieu, limite_px, japonais (octets bruts entre {} pour FF n et codes inconnus).
  C.xxxxx  = chaîne du code (adresse fichier), lieux = sites « pushw seg ; pushw lo » (fichier).
  Lnn.ii   = liste nn de l'archive (entrée 4, 24, 31, 32, 33, 34, 35), chaîne ii.
Limite : 8 px par caractère japonais (le cadre a été dessiné pour le japonais), sauf bulles (136 px).
"""
import os
import re
import struct
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from table import T  # noqa: E402

PROJET = os.path.dirname(ICI)
LISTES = (4, 24, 31, 32, 33, 34, 35)
BULLE = 136


def dec(b):
    out, i = [], 0
    while i < len(b):
        if b[i] == 0xFF and i + 1 < len(b):
            out.append('{FF %02X}' % b[i + 1]); i += 2; continue
        out.append(T.get(b[i], '{%02X}' % b[i])); i += 1
    return ''.join(out)


def chaine(rom, a):
    """Octets jusqu'au 00 final (FF 00 = variable, pas une fin)."""
    i = a
    while True:
        if rom[i] == 0xFF:
            i += 2; continue
        if rom[i] == 0:
            return rom[a:i]
        i += 1


def chaines_code(rom):
    cibles = {}
    for m in re.finditer(rb'\x0b([\x20-\x2f])\x00\x0b(..)', rom, re.S):
        a = (m.group(1)[0] << 16 | m.group(2)[0] | m.group(2)[1] << 8) - 0x200000
        if 0x21E00 <= a < 0x22040 or 0x21370 <= a < 0x21380:
            cibles.setdefault(a, []).append(m.start())
    return cibles


def listes(rom):
    B = 0x60000
    top = [struct.unpack_from('<I', rom, B + 4 * i)[0] for i in range(37)]
    for e in LISTES:
        s = B + top[e]
        n = struct.unpack_from('<I', rom, s)[0] // 4
        for j in range(n):
            yield e, j, s + struct.unpack_from('<I', rom, s + 4 * j)[0]


def textes_jp(rom):
    """-> {id: (lieu, limite_px, japonais)}"""
    d = {}
    for a, sites in sorted(chaines_code(rom).items()):
        b = chaine(rom, a)
        d['C.%05X' % a] = (','.join('%05X' % s for s in sites), 8 * len(b), dec(b))
    for e, j, a in listes(rom):
        b = chaine(rom, a)
        d['L%02d.%02d' % (e, j)] = ('%05X' % a, BULLE if e != 4 else 8 * len(b), dec(b))
    return d


def main():
    rom = open(sys.argv[1], 'rb').read()
    os.makedirs(os.path.join(PROJET, 'out'), exist_ok=True)
    import police
    open(os.path.join(PROJET, 'out', 'police_jp.bin'), 'wb').write(rom[police.POLICE_JP:police.POLICE_JP + 4096])
    lignes = ['id\tlieu\tlimite_px\tjaponais']
    for a, sites in sorted(chaines_code(rom).items()):
        b = chaine(rom, a)
        lignes.append('C.%05X\t%s\t%d\t%s' % (a, ','.join('%05X' % s for s in sites), 8 * len(b), dec(b)))
    for e, j, a in listes(rom):
        b = chaine(rom, a)
        lim = BULLE if e != 4 else 8 * len(b)
        lignes.append('L%02d.%02d\t%05X\t%d\t%s' % (e, j, a, lim, dec(b)))
    open(os.path.join(PROJET, 'out', 'jp.tsv'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lignes) + '\n')
    print(len(lignes) - 1, 'chaînes')


if __name__ == '__main__':
    main()
