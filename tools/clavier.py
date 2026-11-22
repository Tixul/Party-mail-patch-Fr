"""Clavier, police 8x8 d'origine et dictionnaire de mots.

- Police 8x8 (glyphe = base + code*16) : 0x27A9B6 (fond 0) et 0x27B9B6 (fond 1), encre 3. Les codes des
  lettres accentuées (police.CODE_ACCENT, 0x01-0x1C) y reçoivent une version 8x8 du glyphe à chasse
  variable, centrée ; 0x2D devient un trait d'union court.
- Clavier des messages : table 0x220EDE, 3 pages x 7 rangées x 16 octets ; pointeurs en 0x221030 :
  page 0 (hiragana) = 0x220EDE, page 1 (katakana) = 0x220FBE, page 2 (latin) = 0x220F4E.
  Grille : colonnes 0-4, 6-10, 12 (rangée 3 : 0-4, 6, 8, 10, 12). Codes 0xB7/0xB8 = touches ゛/゜
  (conversion des kana voisés) : supprimées. Étiquettes des commandes en 0x220CDC, 4 octets chacune :
  « か な » (-> hiragana) « カ ナ » (-> katakana) « えいご » (-> latin) « じしょ » « セット ».
  Français : page 0 = MAJ (capitales + accents), page 1 = min, page 2 = ABC d'origine.
- Dictionnaire de mots par défaut : 80 pointeurs u32 en 0x2211F6 (objets, salutations, lieux, moments).
"""
import os
import struct
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import police  # noqa: E402

POLICES = ((0x7A9B6, 0), (0x7B9B6, 1))   # (adresse fichier, fond)
TABLE = {0: 0x20EDE, 1: 0x20FBE}          # pages refaites (la page latine 0x20F4E est gardée)
ETIQ = 0x20CDC
DICO = 0x211F6

PAGES = {
    0: ['ABCDE FGHIJ !', 'KLMNO PQRST ?', "UVWXY Z ' - .", 'ÉÈÊËÀ ÇÔÎŒ« ,',
        '():;/ «»…"~ +', "<=>+- ♡',.! ?", '01234 56789'],
    1: ['abcde fghij !', 'klmno pqrst ?', "uvwxy z ' - .", 'éèêëà çôîœû ,',
        'ùüâïî «»…"~ +', '():;/ <=>+- ♡', '01234 56789'],
}
ETIQUETTES = ['MAJ', 'min', 'ABC', 'Mot', 'OK ']    # か な / カ ナ / えいご / じしょ / セット

MOTS = [
    # objets (どうぐ)
    'Sac', 'Portable', 'Mobile', 'Bipeur', 'Boisson', 'Repas', 'Cassette', 'Téléphone', 'CD', 'MD',
    'Montre', 'Jeu vidéo', 'Manuel', 'Portefeuille', 'Crayon', 'Gomme', 'Stylo', 'Télé', 'Vidéo', 'Mail',
    # salutations (あいさつ)
    'Bonjour', 'Salut', 'Bonsoir', 'Enchanté', 'Yo !', 'La forme ?', 'Ça fait un bail !', 'Bon courage',
    'Bonne nuit', 'Coucou !', 'Je t\'envoie un mail', 'Envoie-moi un mail', 'J\'ai eu ton mail',
    'Bye bye', 'Namasté', 'Ça faisait longtemps', 'Dodo', 'D\'accord', 'Ouais', 'Quoi ?',
    # lieux (ばしょ)
    'École', 'Gare', 'Maison', 'Parc', 'Salle d\'arcade', 'Bureau', 'Petit boulot', 'Salle de classe',
    'Arrêt de bus', 'Supérette', 'Librairie', 'Toilettes', 'Là où d\'habitude', 'Train', 'Cabine tél.',
    'Grand magasin', 'Ski', 'Piscine', 'Cour de récré', 'Resto',
    # moments (じかん)
    'Matin', 'Midi', 'Soir', 'Après les cours', 'Ce matin', 'Aujourd\'hui', 'Demain', 'Après-demain',
    'Hier', 'Avant-hier', 'Jour de repos', 'Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi',
    'Vendredi', 'Samedi', 'En cours', 'La prochaine fois',
]


def glyphe_8x8(font, larg, code, fond):
    w = max(larg[code] - 1, 1)
    dx = max((8 - w) // 2, 0)
    o = bytearray()
    for y in range(8):
        v = font[code * 8 + y]
        w16 = 0
        for x in range(8):
            c = fond
            xs = x - dx
            if 0 <= xs < 8 and v & (0x80 >> xs):
                c = 3
            w16 |= c << (14 - 2 * x)
        o += w16.to_bytes(2, 'little')
    return bytes(o)


def ligne(texte):
    b = police.encode(texte)
    return (b + b' ' * 16)[:16]


def applique(rom, zone):
    font, larg, _ = police.construit()
    codes = sorted(set(police.CODE_ACCENT.values()) | {0x2D} | set(range(0x61, 0x7B)))
    for base, fond in POLICES:
        for c in codes:
            rom[base + c * 16: base + c * 16 + 16] = glyphe_8x8(font, larg, c, fond)
    for p, rangs in PAGES.items():
        for r, t in enumerate(rangs):
            rom[TABLE[p] + 16 * r: TABLE[p] + 16 * r + 16] = ligne(t)
    for i, t in enumerate(ETIQUETTES):
        b = police.encode(t)
        assert len(b) == 3
        rom[ETIQ + 4 * i: ETIQ + 4 * i + 3] = b
    if len(MOTS) != 80:
        raise SystemExit('dictionnaire : %d mots (80 attendus)' % len(MOTS))
    for i, t in enumerate(MOTS):
        a = zone.met(police.encode(t) + b'\0')
        struct.pack_into('<I', rom, DICO + 4 * i, a)
