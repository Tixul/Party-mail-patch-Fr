"""Decodeur des cartes de tuiles compressees (routine 0x21C2F0).
Format : [L*H en 1 octet : L = bits 0-3, H = bits 4-7] (modes 3/4/8 : 2 octets L, H)
         octet fort de base, compteur ; puis ceil(L*H/4) octets de codes 2 bits (bits faibles d'abord),
         puis les donnees.  Code 0 = vide, 1 = base|compteur++, 2 = base|octet,
         3 = octet B : B>>6 = 0/1 : fort = base_fort + sext6(B), faible = octet ; 2/3 : fort, faible = 2 octets.
         (1 et 3 : drapeau d'inversion (XSP+20) pour les sous-codes 01/11).
   python -I -B tools/carte_dec.py ROM ADRESSE_HEX [MODE]"""
import sys


def decode(rom, a, mode=0):
    p = a
    if mode in (3, 4, 8):
        L, H = rom[p], rom[p + 1]; p += 2
    else:
        L, H = rom[p] & 15, rom[p] >> 4; p += 1
    fort, cpt = rom[p], rom[p + 1]; p += 2
    n = L * H
    codes_deb = p
    q = p + (n + 3) // 4
    cells = []
    for i in range(n):
        c = rom[codes_deb + i // 4] >> (2 * (i % 4)) & 3
        if c == 0:
            cells.append(None)
        elif c == 1:
            cells.append((fort << 8 | cpt, 0)); cpt = (cpt + 1) & 255
        elif c == 2:
            cells.append((fort << 8 | rom[q], 0)); q += 1
        else:
            b = rom[q]; q += 1
            t = b >> 6
            if t < 2:
                d = b & 0x3F
                if d & 0x20: d |= 0xC0
                d = (d + fort) & 255
                cells.append((d << 8 | rom[q], t)); q += 1
            else:
                cells.append((rom[q] << 8 | rom[q + 1], t - 2)); q += 2
    return L, H, cells, q


if __name__ == '__main__':
    rom = open(sys.argv[1], 'rb').read()
    a = int(sys.argv[2], 16) & 0xFFFFF
    mode = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    L, H, cells, fin = decode(rom, a, mode)
    print('L=%d H=%d fin=%06X' % (L, H, fin + 0x200000))
    for y in range(H):
        print(' '.join('----' if c is None else '%04X%s' % (c[0], '*' if c[1] else '') for c in cells[y * L:(y + 1) * L]))
