"""Gros lettrage du menu principal (carte 22.0) : « JEU », « MAIL », « PROFIL » à la place de
ゲーム / メール / 設定, dans le style d'origine : remplissage couleur 2, contour couleur 1 (2 px),
liseré clair couleur 3 (bord haut/gauche intérieur), ombre tramée couleur 1 décalée en bas à droite,
fond 0 (transparent).

Les palettes (vert / bleu / rose) sont posées par zone de cases : chaque mot reste dans les cases
NON VIDES du mot japonais (contrôlé) ; les cases du mot japonais non utilisées deviennent vides.
"""
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import police  # noqa: E402
from carte_dec import decode  # noqa: E402

CARTE = 0x63CFA       # carte 22.0 (fichier)
# mot -> (texte, échelle x, échelle y, rectangle de cases autorisé (col0, lig0, col1, lig1) inclus)
BLOCS = {
    'A': ['###', '#.#', '###', '#.#', '#.#'], 'E': ['###', '#..', '###', '#..', '###'],
    'F': ['###', '#..', '###', '#..', '#..'], 'I': ['#', '#', '#', '#', '#'],
    'J': ['..#', '..#', '..#', '#.#', '###'], 'L': ['#..', '#..', '#..', '#..', '###'],
    'M': ['##.##', '#.#.#', '#.#.#', '#...#', '#...#'], 'O': ['###', '#.#', '#.#', '#.#', '###'],
    'P': ['###', '#.#', '###', '#..', '#..'], 'R': ['###', '#.#', '##.', '#.#', '#.#'],
    'U': ['#.#', '#.#', '#.#', '#.#', '###'],
}
# mot -> (texte, bloc x, bloc y, écart (px), rectangle des cases du mot, rectangle de centrage)
MOTS = [
    ('JEU', 4, 6, 2, (2, 3, 9, 8), (2, 3, 8, 7)),
    ('MAIL', 3, 5, 2, (9, 3, 17, 8), (10, 4, 16, 7)),
    ('PROFIL', 3, 5, 1, (6, 10, 13, 15), (6, 10, 13, 15)),
]


def masque_mot(texte, bx, by, g):
    cols = []
    for i, c in enumerate(texte):
        rows = BLOCS[c]
        for x in range(len(rows[0])):
            for _ in range(bx):
                cols.append([1 if rows[y][x] == '#' else 0 for y in range(5)])
        if i < len(texte) - 1:
            cols += [[0] * 5] * g
    W, H = len(cols), 5 * by
    return [[cols[x][y // by] for x in range(W)] for y in range(H)], W, H


def style(m, W, H, marge=2, ombre=True):
    """-> image (liste de lignes) des couleurs 0-3, avec marge de 2 px (contour) + 3 px (ombre)."""
    M = marge
    O = 3 if ombre else 0
    Wt, Ht = W + 2 * M + O, H + 2 * M + O
    fill = [[0] * Wt for _ in range(Ht)]
    for y in range(H):
        for x in range(W):
            if m[y][x]:
                fill[y + M][x + M] = 1
    def dil(a, r):
        o = [[0] * Wt for _ in range(Ht)]
        for y in range(Ht):
            for x in range(Wt):
                if a[y][x]:
                    for dy in range(-r, r + 1):
                        for dx in range(-r, r + 1):
                            if 0 <= y + dy < Ht and 0 <= x + dx < Wt:
                                o[y + dy][x + dx] = 1
        return o
    cont = dil(fill, M)
    img = [[0] * Wt for _ in range(Ht)]
    for y in range(Ht):
        for x in range(Wt):
            if cont[y][x] and not fill[y][x]:
                img[y][x] = 1
            elif fill[y][x]:
                bord = (y > 0 and not fill[y - 1][x]) or (x > 0 and not fill[y][x - 1])
                img[y][x] = 3 if bord else 2
    for y in range(Ht if ombre else 0):
        for x in range(Wt):
            if img[y][x] == 0 and y >= 3 and x >= 3 and cont[y - 3][x - 3] and (x + y) % 2 == 0:
                img[y][x] = 1
    return img, Wt, Ht


def tuile(img, x0, y0):
    o = bytearray()
    for y in range(8):
        w16 = 0
        for x in range(8):
            yy, xx = y0 + y, x0 + x
            c = img[yy][xx] if 0 <= yy < len(img) and 0 <= xx < len(img[0]) else 0
            w16 |= c << (14 - 2 * x)
        o += w16.to_bytes(2, 'little')
    return bytes(o)


def cellules(rom):
    """-> {(mot, col, lig): tuile 16 octets} et la liste des cases japonaises à vider."""
    L, H, cells, _ = decode(rom, CARTE, 3)
    neuves, a_vider = {}, []
    for texte, bx, by, g, (c0, l0, c1, l1), (k0, m0, k1, m1) in MOTS:
        orig = {(x, y) for y in range(l0, l1 + 1) for x in range(c0, c1 + 1) if cells[y * L + x] is not None}
        m, W, Hm = masque_mot(texte, bx, by, g)
        img, Wt, Ht = style(m, W, Hm)
        # centrage dans le rectangle des cases d'origine
        px0 = k0 * 8 + ((k1 - k0 + 1) * 8 - Wt) // 2
        py0 = m0 * 8 + ((m1 - m0 + 1) * 8 - Ht) // 2
        pris = set()
        for y in range(Ht):
            for x in range(Wt):
                if img[y][x]:
                    pris.add(((px0 + x) // 8, (py0 + y) // 8))
        hors = pris - orig
        if hors:
            raise SystemExit('%s sort des cases d\'origine : %s' % (texte, sorted(hors)))
        for (cx, cy) in orig:
            if (cx, cy) in pris:
                neuves[(texte, cx, cy)] = tuile(img, cx * 8 - px0, cy * 8 - py0)
            else:
                a_vider.append((cx, cy))
    return neuves, a_vider



# --- Panneau « スタート » du début de partie : 8 x 2 tuiles en 0x71D16 (fichier), réécrites sur place.
PANNEAU = 0x71D16
BLOCS.update({'G': ['###', '#..', '#.#', '#.#', '###'], '!': ['#', '#', '#', '.', '#'], ' ': ['.', '.', '.', '.', '.']})


def panneau(texte='GO !', bx=5, by=2, g=3):

    m, W, H = masque_mot(texte, bx, by, g)
    img, Wt, Ht = style(m, W, H, marge=1, ombre=False)
    x0, y0 = (64 - Wt) // 2, (16 - Ht) // 2
    out = bytearray()
    for ty in range(2):
        for tx in range(8):
            out += tuile(img, tx * 8 - x0, ty * 8 - y0)
    return bytes(out)


BLOCS.update({'S': ['###', '#..', '###', '..#', '###'], 'T': ['###', '.#.', '.#.', '.#.', '.#.'],
              'e': ['###', '#.#', '###', '#..', '###'], 'r': ['###', '#..', '#..', '#..', '#..']})


def image_bloc(texte, bx, by, g, larg, haut, marge=1, ax='c', ay='c'):
    """Texte en blocs stylé, posé dans une image larg x haut (couleurs 0-3)."""
    m, W, H = masque_mot(texte, bx, by, g)
    img, Wt, Ht = style(m, W, H, marge=marge, ombre=False)
    if Wt > larg or Ht > haut:
        raise SystemExit('%s : %dx%d > %dx%d' % (texte, Wt, Ht, larg, haut))
    x0 = {'g': 0, 'c': (larg - Wt) // 2, 'd': larg - Wt}[ax]
    y0 = {'h': 0, 'c': (haut - Ht) // 2, 'b': haut - Ht}[ay]
    out = [[0] * larg for _ in range(haut)]
    for y in range(Ht):
        for x in range(Wt):
            out[y0 + y][x0 + x] = img[y][x]
    return out


def tuiles_de(img, nx, ny):
    return [tuile(img, tx * 8, ty * 8) for ty in range(ny) for tx in range(nx)]


# Panneaux rouges (objet 31 de la 2e table) : carte 0 « スタート », carte 1 « ストップ » (8 x 2 tuiles)
PANNEAUX_ROUGES = {0: ('GO !', 5, 2, 3), 1: ('STOP !', 3, 2, 3)}
# Classements « n位 » (objets 13-20 de la 2e table) : « 位 » = colonnes 4-7, lignes 0-5 (tuiles communes)
SUFFIXE = ('e', 5, 4, 2)
SUFFIXE_1 = ('er', 4, 4, 2)


# --- Sous-titre du logo « パーティーメール » (bandeau, carte 6.0 ligne 9, tuiles 0x0335-0x033C) ---
BANDEAU_TUILES = list(range(0x0335, 0x033D))   # colonnes 6-13 ; 0x0332-0x0334 et leurs miroirs gardés
BANDEAU_X0 = 24                                # x (depuis la colonne 3) de la 1re tuile réécrite
SOUS_TITRE = 'Mail en fête'


def bandeau(rom):
    """-> {code: 16 octets} : bandeau sans le katakana (pixels non symétriques effacés) + sous-titre."""
    from carte_dec import decode
    F = 0x66B86
    L, H, cells, _ = decode(rom, 0x62186, 3)
    pix = [[0] * (14 * 8) for _ in range(8)]
    for tx in range(14):
        c = cells[9 * L + 3 + tx]
        b = rom[F + c[0] * 16:F + c[0] * 16 + 16]
        for y in range(8):
            w = b[2 * y] | b[2 * y + 1] << 8
            px = [(w >> (14 - 2 * x)) & 3 for x in range(8)]
            if c[1]:
                px = px[::-1]
            pix[y][tx * 8:tx * 8 + 8] = px
    # axe de symétrie : plis du bandeau
    W = 14 * 8
    centre2 = None
    for s in range(90, 130):          # 2 x centre
        ok = sum(1 for y in range(8) for x in range(W) if 0 <= s - x < W and pix[y][x] == pix[y][s - x])
        if centre2 is None or ok > best:
            centre2, best = s, ok
    out = [r[:] for r in pix]
    for y in range(6):                 # entre les plis, lignes 0-5 = fond uni du bandeau
        for x in range(BANDEAU_X0, BANDEAU_X0 + 64):
            out[y][x] = 1
    # texte : encre 2, lignes 0-5 (lignes 1-6 du glyphe)
    font, larg, _ = police.construit()
    b = police.encode(SOUS_TITRE)
    w = police.largeur(b, larg)
    x = BANDEAU_X0 + (64 - w) // 2 + (centre2 // 2 - (BANDEAU_X0 + 32))
    for c in b:
        for gy in range(8):
            v = font[c * 8 + gy]
            for k in range(8):
                if v & (0x80 >> k) and 0 <= gy - 1 < 8:
                    out[gy - 1][x + k] = 2
        x += larg[c]
    res = {}
    for i, code in enumerate(BANDEAU_TUILES):
        o = bytearray()
        for y in range(8):
            w16 = 0
            for k in range(8):
                w16 |= out[y][BANDEAU_X0 + i * 8 + k] << (14 - 2 * k)
            o += w16.to_bytes(2, 'little')
        res[code] = bytes(o)
    return res, centre2, out
