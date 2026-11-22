"""Police à chasse variable (VWF) pour le texte en octets de Party Mail.

Sortie : FONT (256 x 8 octets, 1 bit par pixel, bit 7 = colonne de gauche),
         LARG (256 octets : avance en pixels, espace compris),
         EXPAND (256 x mot : 1 bit -> 2 bits « 11 », pixel 0 dans les bits 15-14).
Les codes non redessinés ici reprennent le glyphe d'origine (police 0x27A9B6), rogné à gauche,
avance = largeur d'encre + 1.
Lignes : 0 = accent des capitales, 1-6 = capitales / chiffres, 3-6 = minuscules, 7 = jambage.

Codes des lettres accentuées (à la place des kana voisés 0x01-0x1A, inutiles en français) :
"""
import os
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROM = None          # ROM japonaise d'origine (octets), posée par build.py ; sinon out/police_jp.bin
POLICE_JP = 0x7A9B6

ACCENTS = 'éèêëàâîïôûùüçœÉÈÊÀÇÔÎ«»…"~ËŒ'
CODE_ACCENT = {c: 0x01 + i for i, c in enumerate(ACCENTS)}

G = {}


def _g(c, *lignes, haut=1):
    """lignes à partir de la ligne `haut` ; '#' = encre."""
    rows = ['' for _ in range(8)]
    for i, l in enumerate(lignes):
        rows[haut + i] = l
    G[c] = rows


# --- capitales (lignes 1-6) ---
_g('A', '.##.', '#..#', '#..#', '####', '#..#', '#..#')
_g('B', '###.', '#..#', '###.', '#..#', '#..#', '###.')
_g('C', '.###', '#...', '#...', '#...', '#...', '.###')
_g('D', '###.', '#..#', '#..#', '#..#', '#..#', '###.')
_g('E', '####', '#...', '###.', '#...', '#...', '####')
_g('F', '####', '#...', '###.', '#...', '#...', '#...')
_g('G', '.###', '#...', '#...', '#.##', '#..#', '.###')
_g('H', '#..#', '#..#', '####', '#..#', '#..#', '#..#')
_g('I', '###', '.#.', '.#.', '.#.', '.#.', '###')
_g('J', '..##', '...#', '...#', '...#', '#..#', '.##.')
_g('K', '#..#', '#.#.', '##..', '#.#.', '#..#', '#..#')
_g('L', '#...', '#...', '#...', '#...', '#...', '####')
_g('M', '#...#', '##.##', '#.#.#', '#...#', '#...#', '#...#')
_g('N', '#..#', '##.#', '#.##', '#..#', '#..#', '#..#')
_g('O', '.##.', '#..#', '#..#', '#..#', '#..#', '.##.')
_g('P', '###.', '#..#', '#..#', '###.', '#...', '#...')
_g('Q', '.##.', '#..#', '#..#', '#..#', '#.#.', '.#.#')
_g('R', '###.', '#..#', '#..#', '###.', '#.#.', '#..#')
_g('S', '.###', '#...', '.##.', '...#', '...#', '###.')
_g('T', '###', '.#.', '.#.', '.#.', '.#.', '.#.')
_g('U', '#..#', '#..#', '#..#', '#..#', '#..#', '.##.')
_g('V', '#...#', '#...#', '#...#', '.#.#.', '.#.#.', '..#..')
_g('W', '#...#', '#...#', '#.#.#', '#.#.#', '##.##', '#...#')
_g('X', '#..#', '#..#', '.##.', '.##.', '#..#', '#..#')
_g('Y', '#.#', '#.#', '#.#', '.#.', '.#.', '.#.')
_g('Z', '####', '...#', '..#.', '.#..', '#...', '####')
# --- minuscules (x = lignes 3-6) ---
_g('a', '.###', '#..#', '#..#', '.###', haut=3)
_g('b', '#...', '#...', '###.', '#..#', '#..#', '###.')
_g('c', '.##', '#..', '#..', '.##', haut=3)
_g('d', '...#', '...#', '.###', '#..#', '#..#', '.###')
_g('e', '.##.', '####', '#...', '.###', haut=3)
_g('f', '.##', '#..', '###', '#..', '#..', '#..')
_g('g', '.###', '#..#', '.###', '...#', '###.', haut=3)
_g('h', '#...', '#...', '###.', '#..#', '#..#', '#..#')
_g('i', '#', '.', '#', '#', '#', '#')
_g('j', '.#', '..', '.#', '.#', '.#', '.#', '#.')
_g('k', '#..', '#..', '#.#', '##.', '#.#', '#.#')
_g('l', '#', '#', '#', '#', '#', '#')
_g('m', '##.#.', '#.#.#', '#.#.#', '#.#.#', haut=3)
_g('n', '###.', '#..#', '#..#', '#..#', haut=3)
_g('o', '.##.', '#..#', '#..#', '.##.', haut=3)
_g('p', '###.', '#..#', '###.', '#...', '#...', haut=3)
_g('q', '.###', '#..#', '.###', '...#', '...#', haut=3)
_g('r', '#.#', '##.', '#..', '#..', haut=3)
_g('s', '.###', '##..', '..##', '###.', haut=3)
_g('t', '#..', '###', '#..', '#..', '.##', haut=2)
_g('u', '#..#', '#..#', '#..#', '.###', haut=3)
_g('v', '#.#', '#.#', '#.#', '.#.', haut=3)
_g('w', '#...#', '#.#.#', '#.#.#', '.#.#.', haut=3)
_g('x', '#..#', '.##.', '.##.', '#..#', haut=3)
_g('y', '#..#', '#..#', '.###', '...#', '###.', haut=3)
_g('z', '####', '..#.', '.#..', '####', haut=3)
# --- chiffres ---
_g('0', '.##.', '#..#', '#..#', '#..#', '#..#', '.##.')
_g('1', '.#.', '##.', '.#.', '.#.', '.#.', '###')
_g('2', '.##.', '#..#', '..#.', '.#..', '#...', '####')
_g('3', '###.', '...#', '.##.', '...#', '...#', '###.')
_g('4', '..#.', '.##.', '#.#.', '####', '..#.', '..#.')
_g('5', '####', '#...', '###.', '...#', '...#', '###.')
_g('6', '.##.', '#...', '###.', '#..#', '#..#', '.##.')
_g('7', '####', '...#', '..#.', '.#..', '.#..', '.#..')
_g('8', '.##.', '#..#', '.##.', '#..#', '#..#', '.##.')
_g('9', '.##.', '#..#', '#..#', '.###', '...#', '.##.')
# --- ponctuation ---
_g('!', '#', '#', '#', '#', '.', '#')
_g('?', '.##.', '#..#', '..#.', '.#..', '....', '.#..')
_g('.', '#', haut=6)
_g(',', '.#', '#.', haut=6)
_g(':', '#', '.', '.', '#', haut=3)
_g(';', '.#', '..', '..', '.#', '#.', haut=3)
_g("'", '#', '#', haut=1)
_g('-', '###', haut=4)
_g('(', '.#', '#.', '#.', '#.', '#.', '.#')
_g(')', '#.', '.#', '.#', '.#', '.#', '#.')
_g('/', '..#', '..#', '.#.', '.#.', '#..', '#..')
_g('+', '.#.', '###', '.#.', haut=3)
_g('«', '.#.#', '#.#.', '.#.#', haut=3)
_g('»', '#.#.', '.#.#', '#.#.', haut=3)
_g('…', '#.#.#', haut=6)
_g('"', '#.#', '#.#', haut=1)
_g('~', '.#.#', '#.#.', haut=3)
# --- accents ---
def _acc(c, base, accent, ligne=1):
    rows = list(G[base])
    w = max(len(r) for r in rows)
    for i, l in enumerate(accent):
        rows[ligne + i] = l.ljust(w, '.')
    G[c] = rows


AIGU, GRAVE, CIRC, TREMA = ['..#.', '.#..'], ['.#..', '..#.'], ['.##.', '#..#'], ['....', '#..#']
_acc('é', 'e', AIGU); _acc('è', 'e', GRAVE); _acc('ê', 'e', CIRC); _acc('ë', 'e', TREMA)
_acc('à', 'a', GRAVE); _acc('â', 'a', CIRC)
_acc('ô', 'o', CIRC); _acc('û', 'u', CIRC); _acc('ù', 'u', GRAVE); _acc('ü', 'u', TREMA)
G['î'] = ['', '.#.', '#.#', '.#.', '.#.', '.#.', '.#.', '']
G['ï'] = ['', '', '#.#', '.#.', '.#.', '.#.', '.#.', '']
G['ç'] = ['', '', '', '.##', '#..', '#..', '.##', '.#.']
G['œ'] = ['', '', '', '.#.##.', '#.####', '#.#...', '.#.###', '']
G['É'] = ['..#.'] + G['E'][1:]
G['È'] = ['.#..'] + G['E'][1:]
G['Ê'] = ['.##.'] + G['E'][1:]
G['À'] = ['.#..'] + G['A'][1:]
G['Ô'] = ['.##.'] + G['O'][1:]
G['Î'] = ['.#.'] + G['I'][1:]
G['Ç'] = G['C'][:7] + ['.#..']

ESPACE = 3


def code_de(c):
    if c in CODE_ACCENT:
        return CODE_ACCENT[c]
    if c == ' ':
        return 0x20
    if c == '♡':
        return 0xFE
    if c == '+':                 # dans la police du jeu, 0x2B = ゼ ; le + est en 0x7B
        return 0x7B
    o = ord(c)
    if 0x21 <= o <= 0x7A:
        return o
    raise KeyError(c)


def _glyphe_jp(rom, code):
    b = rom[POLICE_JP + code * 16: POLICE_JP + code * 16 + 16]
    rows = []
    for y in range(8):
        w = b[2 * y] | b[2 * y + 1] << 8
        rows.append(''.join('#' if (w >> (14 - 2 * x)) & 3 == 3 else '.' for x in range(8)))
    return rows


def _rogne(rows):
    cols = [x for x in range(8) if any(len(r) > x and r[x] == '#' for r in rows)]
    if not cols:
        return ['' for _ in rows], 0
    a, b = min(cols), max(cols)
    return [r[a:b + 1] if len(r) > a else '' for r in rows], b - a + 1


def construit():
    if ROM is not None:
        rom = ROM
    else:
        f = os.path.join(RACINE, 'out', 'police_jp.bin')
        if not os.path.exists(f):
            raise SystemExit("lancer d'abord : python tools/extrait.py <ROM japonaise>")
        rom = bytes(POLICE_JP) + open(f, 'rb').read()
    font = bytearray(256 * 8)
    larg = bytearray(256)
    for code in range(256):
        rows, w = _rogne(_glyphe_jp(rom, code))
        for y, r in enumerate(rows):
            v = 0
            for x, ch in enumerate(r[:8]):
                if ch == '#':
                    v |= 0x80 >> x
            font[code * 8 + y] = v
        larg[code] = w + 1 if w else ESPACE
    for c, rows in G.items():
        code = code_de(c)
        w = max(len(r) for r in rows)
        for y in range(8):
            v = 0
            for x, ch in enumerate(rows[y] if y < len(rows) else ''):
                if ch == '#':
                    v |= 0x80 >> x
            font[code * 8 + y] = v
        larg[code] = w + 1
    larg[0x20] = ESPACE
    expand = bytearray()
    for v in range(256):
        m = 0
        for x in range(8):
            if v & (0x80 >> x):
                m |= 3 << (14 - 2 * x)
        expand += m.to_bytes(2, 'little')
    return bytes(font), bytes(larg), bytes(expand)


def encode(texte):
    """Texte français -> octets du jeu. {FF xx} / {xx} = octets bruts."""
    out = bytearray()
    i = 0
    while i < len(texte):
        c = texte[i]
        if c == '{':
            j = texte.index('}', i)
            out += bytes(int(h, 16) for h in texte[i + 1:j].split())
            i = j + 1
            continue
        out.append(code_de(c))
        i += 1
    return bytes(out)


def largeur(octets, larg=None):
    """Largeur en pixels d'une chaîne (variables FF n comptées à part)."""
    if larg is None:
        larg = construit()[1]
    w = 0
    i = 0
    while i < len(octets):
        if octets[i] == 0xFF:
            i += 2
            continue
        w += larg[octets[i]]
        i += 1
    return w


if __name__ == '__main__':
    import sys
    from PIL import Image
    font, larg, _ = construit()
    txt = sys.argv[1] if len(sys.argv) > 1 else 'Voilà ! Ça marche, élève : « œuf » ? Ô Îles 0123456789'
    b = encode(txt)
    W = largeur(b, larg)
    im = Image.new('RGB', (W + 4, 12), (200, 200, 200))
    x = 2
    for c in b:
        for y in range(8):
            for k in range(8):
                if font[c * 8 + y] & (0x80 >> k):
                    im.putpixel((x + k, 2 + y), (0, 0, 0))
        x += larg[c]
    im = im.resize((im.width * 4, im.height * 4), 0)
    im.save(sys.argv[2] if len(sys.argv) > 2 else 'out/apercu_police.png')
    print(W, 'px')


G['Ë'] = ['#..#'] + G['E'][1:]
G['Œ'] = ['', '.#####', '#.#...', '#.###.', '#.#...', '#.#...', '.#####', '']
