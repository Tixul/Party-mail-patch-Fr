"""Écrans fixes : remplace le texte japonais des cartes de tuiles (bloc 0 de l'archive) par du français
rendu en tuiles neuves avec la police à chasse variable.

Une carte = tools/carte_dec.py (mode 3). Réencodage : toute case non vide en code 3 forme longue
(0x80/0xC0, fort, faible) ; drapeau d'origine gardé. Objet écran (4 offsets u16 + cartes) recopié dans la
zone neuve, entrée u32 du bloc 0 (0x260094 + 4k) repointée.
Tuile neuve : code = (adresse - 0x266B86) / 16 (feuille), adresse < 0x366B86.

CHAMPS[(k, j)] = liste de champs : (ligne, colonne, nb_cases, texte, alignement 'g'|'c'|'d', style)
  style 'n' = encre 2 sur fond 1 (boîtes grises), 'i' = encre 1 sur fond 3 (boîte noire).
EFFACE[(k, j)] = cases (ligne, colonne, nb) remises à vide avant les champs.
"""
import os
import struct
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import police  # noqa: E402
from carte_dec import decode  # noqa: E402

FEUILLE_CPU = 0x266B86
BLOC0 = 0x60094
VIDE = {'n': 0x0003, 'i': 0x000D}
COULEURS = {'n': (2, 1), 'i': (1, 3)}       # (encre, fond)

CHAMPS = {
    # sauvegarde (choix : « はい » c6 / « いいえ » c11)
    (6, 2): [(6, 4, 12, 'Reprendre la partie', 'c', 'n'), (7, 4, 12, 'sauvegardée ?', 'c', 'n'),
             (9, 6, 3, 'Oui', 'g', 'n'), (9, 11, 3, 'Non', 'g', 'n')],
    # groupes de destinataires : « グループ♡ » c1, « へんこう » c10, « さくじょ » c15
    (10, 0): [(1, 1, 8, 'Groupe ♡', 'g', 'n'), (1, 10, 4, 'Modif.', 'g', 'n'),
              (1, 15, 4, 'Suppr.', 'g', 'n')],
    # dictionnaire de mots : c2 / c11 puis deux colonnes c4 / c12
    (11, 0): [(1, 2, 8, 'Lexiques', 'g', 'n'), (1, 11, 7, 'Mes mots', 'g', 'n'),
              (3, 4, 7, 'Noms', 'g', 'n'), (3, 12, 6, 'Objets', 'g', 'n'),
              (5, 4, 7, 'Salutations', 'g', 'n'), (5, 12, 6, 'Divers 1', 'g', 'n'),
              (7, 4, 7, 'Lieux', 'g', 'n'), (7, 12, 6, 'Divers 2', 'g', 'n'),
              (9, 4, 7, 'Moments', 'g', 'n'), (9, 12, 6, 'Divers 3', 'g', 'n')],
    # saisie de message : « メッセージ入力 » c2, « ペット » c14
    (15, 0): [(1, 2, 11, 'Écrire un message', 'g', 'n'), (1, 14, 5, 'Bestiole', 'g', 'n')],
    (20, 0): [(1, 4, 8, 'Tout le monde', 'g', 'n')],
    # liaison
    (21, 1): [(7, 4, 12, 'Liaison par câble ?', 'c', 'n'), (9, 6, 3, 'Oui', 'g', 'n'),
              (9, 11, 3, 'Non', 'g', 'n')],
    # choix de la bestiole (boîte noire)
    (24, 0): [(13, 4, 12, 'Choisis ta', 'c', 'i'), (15, 4, 12, 'bestiole.', 'c', 'i')],
    (24, 1): [(13, 4, 12, 'Choisis ta', 'c', 'i'), (15, 4, 12, 'bestiole.', 'c', 'i')],
    # ID de la console
    (31, 1): [(8, 1, 18, 'Entre le numéro à 7 chiffres', 'g', 'n'),
              (10, 1, 18, 'écrit au dos de ta console.', 'g', 'n')],
    # nombre d'adversaires ordinateur (chiffres c4 / c8 / c12 gardés, « にん » effacés)
    (32, 1): [(13, 4, 12, 'Combien de joueurs', 'c', 'n'), (15, 4, 12, 'ordinateur ?', 'c', 'n')],
    # points à atteindre (« てん » c10-11)
    (32, 2): [(6, 7, 5, '100 pts', 'g', 'n'), (7, 7, 5, '300 pts', 'g', 'n'), (8, 7, 5, '500 pts', 'g', 'n'),
              (13, 4, 12, 'En combien', 'c', 'n'), (15, 4, 12, 'de points ?', 'c', 'n')],
    # recherche de partenaire
    (32, 3): [(8, 4, 12, 'Recherche en cours…', 'c', 'n'),
              (10, 4, 12, 'Patiente un instant.', 'c', 'n')],
}
for _k in range(26, 31):
    CHAMPS[(_k, 0)] = [(13, 4, 12, 'Choisis la couleur', 'c', 'n'), (15, 4, 12, 'de ta bestiole.', 'c', 'n')]

EFFACE = {
    (32, 1): [(7, 5, 2), (7, 9, 2), (7, 13, 2), (8, 5, 2), (8, 9, 2), (8, 13, 2)],   # « にん »
}

_FONT = None


def _police():
    global _FONT
    if _FONT is None:
        _FONT = police.construit()
    return _FONT


def rend(texte, n, align, style):
    """-> liste de n tuiles (16 octets, 2 bpp NGPC)."""
    font, larg, _ = _police()
    encre, fond = COULEURS[style]
    b = police.encode(texte)
    w = police.largeur(b, larg)
    if w > n * 8:
        raise SystemExit('trop long (%d > %d px) : %s' % (w, n * 8, texte))
    x0 = {'g': 0, 'c': (n * 8 - w) // 2, 'd': n * 8 - w}[align]
    pix = [[fond] * (n * 8) for _ in range(8)]
    x = x0
    for c in b:
        for y in range(8):
            v = font[c * 8 + y]
            for k in range(8):
                if v & (0x80 >> k) and x + k < n * 8:
                    pix[y][x + k] = encre
        x += larg[c]
    tuiles = []
    for t in range(n):
        o = bytearray()
        for y in range(8):
            w16 = 0
            for k in range(8):
                w16 |= pix[y][t * 8 + k] << (14 - 2 * k)
            o += w16.to_bytes(2, 'little')
        tuiles.append(bytes(o))
    return tuiles


def encode_carte(L, H, cells, fort, cpt):
    n = L * H
    codes = bytearray((n + 3) // 4)
    data = bytearray()
    for i, c in enumerate(cells):
        if c is None:
            continue
        codes[i // 4] |= 3 << (2 * (i % 4))
        v, t = c
        data += bytes([0xC0 if t else 0x80, v >> 8, v & 0xFF])
    return bytes([L, H, fort, cpt]) + bytes(codes) + bytes(data)


class Tuiles:
    """Tuiles neuves, placées dans la zone (adresse alignée sur la feuille), dédoublonnées."""
    def __init__(self, rom, zone):
        self.rom, self.zone, self.vus = rom, zone, {}

    def code(self, t, style):
        if t == bytes(rend('', 1, 'g', style)[0]):
            return VIDE[style]
        if t in self.vus:
            return self.vus[t]
        z = self.zone
        while (z.p + 0x200000 - FEUILLE_CPU) % 16:
            z.p += 1
        a = z.met(t, align=1)
        c = (a - FEUILLE_CPU) // 16
        if c > 0xFFFF:
            raise SystemExit('tuile hors de portée de la feuille')
        self.vus[t] = c
        return c


def lettrage_menu(rom, tu):
    """Carte 22.0 (menu principal) : cases -> {(col, lig): code} pour JEU / MAIL / PROFIL."""
    import lettrage
    neuves, vides = lettrage.cellules(rom)
    res = {}
    for (_, cx, cy), t in neuves.items():
        if t in tu.vus:
            res[(cx, cy)] = tu.vus[t]
        else:
            z = tu.zone
            while (z.p + 0x200000 - FEUILLE_CPU) % 16:
                z.p += 1
            a = z.met(t, align=1)
            tu.vus[t] = (a - FEUILLE_CPU) // 16
            res[(cx, cy)] = tu.vus[t]
    for c in vides:
        res[c] = None
    return res


def applique(rom, zone):
    tu = Tuiles(rom, zone)
    menu = lettrage_menu(rom, tu)
    objets = sorted({k for k, _ in CHAMPS} | {22})
    for k in objets:
        obj = BLOC0 + struct.unpack_from('<I', rom, BLOC0 + 4 * k)[0]
        offs = [struct.unpack_from('<H', rom, obj + 2 * j)[0] for j in range(4)]
        cartes = []
        for j, o in enumerate(offs):
            if not o:
                cartes.append(None)
                continue
            a = obj + o
            L, H, cells, fin = decode(rom, a, 3)
            fort, cpt = rom[a + 2], rom[a + 3]
            if (k, j) == (22, 0):
                for (cx, cy), code in menu.items():
                    cells[cy * L + cx] = None if code is None else (code, cells[cy * L + cx][1])
                cartes.append(encode_carte(L, H, cells, fort, cpt))
                continue
            if (k, j) not in CHAMPS:
                cartes.append(rom[a:fin])
                continue
            for (y, x, n) in EFFACE.get((k, j), []):
                for i in range(n):
                    if cells[y * L + x + i] is not None:
                        cells[y * L + x + i] = (VIDE['n'], 0)
            for (y, x, n, texte, al, st) in CHAMPS[(k, j)]:
                for i, t in enumerate(rend(texte, n, al, st)):
                    cells[y * L + x + i] = (tu.code(t, st), 0)
            cartes.append(encode_carte(L, H, cells, fort, cpt))
        tete = bytearray(8)
        corps = bytearray()
        for j, c in enumerate(cartes):
            if c is None:
                continue
            struct.pack_into('<H', tete, 2 * j, 8 + len(corps))
            corps += c
        a = zone.met(bytes(tete) + bytes(corps))
        struct.pack_into('<I', rom, BLOC0 + 4 * k, a - 0x200000 - BLOC0)
    return len(tu.vus)


TABLE2 = 0x60198      # 2e table d'objets (cartes, WIN/LOSE, classements, panneaux) ; offsets / 0x60094


def encode_carte0(L, H, cells):
    """Carte « mode 0 » (en-tête 1 octet L | H << 4), cases en forme longue."""
    return bytes([L | H << 4]) + encode_carte(L, H, cells, 0, 0)[2:]


def objet2(rom, zone, k, cartes_neuves):
    """Recopie l'objet k de la 2e table ; cartes_neuves = {j: octets de carte}."""
    obj = BLOC0 + struct.unpack_from('<I', rom, TABLE2 + 4 * k)[0]
    offs = [struct.unpack_from('<H', rom, obj + 2 * j)[0] for j in range(4)]
    tete, corps = bytearray(8), bytearray()
    for j, o in enumerate(offs):
        if not o:
            continue
        if j in cartes_neuves:
            c = cartes_neuves[j]
        else:
            _, _, _, fin = decode(rom, obj + o, 0)
            c = rom[obj + o:fin]
        struct.pack_into('<H', tete, 2 * j, 8 + len(corps))
        corps += c
    a = zone.met(bytes(tete) + bytes(corps))
    struct.pack_into('<I', rom, TABLE2 + 4 * k, a - 0x200000 - BLOC0)


def graphismes(rom, zone):
    import lettrage
    tu = Tuiles(rom, zone)

    def code_de(t):
        if t not in tu.vus:
            z = tu.zone
            while (z.p + 0x200000 - FEUILLE_CPU) % 16:
                z.p += 1
            tu.vus[t] = (z.met(t, align=1) - FEUILLE_CPU) // 16
        return tu.vus[t]

    # panneaux rouges
    neuves = {}
    for j, (t, bx, by, g) in lettrage.PANNEAUX_ROUGES.items():
        ts = lettrage.tuiles_de(lettrage.image_bloc(t, bx, by, g, 64, 16), 8, 2)
        neuves[j] = encode_carte0(8, 2, [(code_de(x), 0) for x in ts])
    objet2(rom, zone, 31, neuves)
    # classements : « 位 » commun (objet 13, colonnes 4-7) réécrit sur place en « e »
    obj = BLOC0 + struct.unpack_from('<I', rom, TABLE2 + 4 * 13)[0]
    a = obj + struct.unpack_from('<H', rom, obj)[0]
    L, H, cells, _ = decode(rom, a, 0)
    t, bx, by, g = lettrage.SUFFIXE
    ts = lettrage.tuiles_de(lettrage.image_bloc(t, bx, by, g, 32, 48, marge=2, ay='h'), 4, 6)
    for ty in range(6):
        for tx in range(4):
            c = cells[ty * L + 4 + tx][0]
            f = FEUILLE_CPU - 0x200000 + c * 16
            rom[f:f + 16] = ts[ty * 4 + tx]
    # 1er : tuiles propres « er »
    t, bx, by, g = lettrage.SUFFIXE_1
    ts = lettrage.tuiles_de(lettrage.image_bloc(t, bx, by, g, 32, 48, marge=2, ay='h'), 4, 6)
    for ty in range(6):
        for tx in range(4):
            cells[ty * L + 4 + tx] = (code_de(ts[ty * 4 + tx]), cells[ty * L + 4 + tx][1])
    objet2(rom, zone, 13, {0: encode_carte0(L, H, cells)})
