"""Contrôle de lang/<code>/textes.tsv : caractères hors police, largeur (px) contre la limite du contexte.

    python tools/controle.py [--lang fr]     (après tools/extrait.py)
Variables comptées au pire : FF 02..06 = 4 lettres (24 px), FF 07 = 6 lettres (36 px),
FF 00/01 = 2 chiffres (10 px), FF 10 = 5 caractères (30 px).
"""
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import police  # noqa: E402

PROJET = os.path.dirname(ICI)
VAR = {0x00: 10, 0x01: 10, 0x02: 24, 0x03: 24, 0x04: 24, 0x05: 24, 0x06: 24, 0x07: 36, 0x10: 30}
BULLE = 128
MONO = {'L04.24': 56, 'L04.48': 56, 'L04.27': 56, 'L04.30': 56, 'L04.33': 72, 'L04.36': 56,
        'L04.39': 72, 'L04.42': 64, 'L04.45': 72, 'L04.32': 72, 'L04.35': 72, 'L04.38': 80,
        'L04.41': 72, 'L04.44': 80, 'L04.23': 72, 'L04.47': 72, 'L04.54': 88, 'L04.55': 112,
        'L04.26': 88, 'L04.29': 88, 'L04.31': 32, 'L04.34': 32, 'L04.37': 32, 'L04.40': 32,
        'L04.43': 32}
TUTO = 96
LIMITES = {
    'C.21E36': 80, 'C.2202A': 32, 'C.22030': 40, 'C.22036': 32,
    'C.21372': 48, 'C.2137A': 48, 'C.21E20': 80, 'C.21E2A': 80, 'C.21E44': 64,
    'C.21E4C': 104, 'C.21E56': 104, 'C.21E60': 104, 'C.21E6A': 96, 'C.21E78': 96,
    'C.21EC8': 40, 'C.21E00': 40, 'C.21E04': 40, 'C.21E08': 40, 'C.21E0C': 40, 'C.21E10': 40,
    'C.21E14': 40, 'C.21E18': 40, 'C.21E1C': 40, 'C.21ECE': 80, 'C.21EDA': 80,
}


LANGUE = 'fr'


def charge_fr(langue=None):
    d = {}
    for l in open(os.path.join(PROJET, 'lang', langue or LANGUE, 'textes.tsv'), encoding='utf-8'):
        l = l.rstrip('\n')
        if not l or l.startswith('#') or l.startswith('id\t'):
            continue
        i, t = l.split('\t', 1)
        d[i] = t
    return d


def charge_jp():
    d = {}
    f = os.path.join(PROJET, 'out', 'jp.tsv')
    if not os.path.exists(f):
        raise SystemExit("lancer d'abord : python tools/extrait.py <ROM japonaise>")
    for l in open(f, encoding='utf-8').read().splitlines()[1:]:
        i, lieu, lim, jp = l.split('\t')
        d[i] = (lieu, int(lim), jp)
    return d


def developpe(fr):
    """COMMUN.nn -> L24/L31/L32/L34.nn (si absent)."""
    out = dict(fr)
    for k, v in fr.items():
        if k.startswith('COMMUN.'):
            n = k.split('.')[1]
            for l in ('L24', 'L31', 'L32', 'L34'):
                out.setdefault('%s.%s' % (l, n), v)
            del out[k]
    return out


def limite(i, jp):
    if i in LIMITES:
        return LIMITES[i]
    if i.startswith('L') and not i.startswith('L04'):
        return BULLE
    if 'C.21EE6' <= i <= 'C.21F64':
        return TUTO
    return jp[1]


def largeur(b, larg):
    w, i = 0, 0
    while i < len(b):
        if b[i] == 0xFF:
            w += VAR.get(b[i + 1], 30)
            i += 2
            continue
        w += larg[b[i]]
        i += 1
    return w


def main():
    global LANGUE
    if '--lang' in sys.argv:
        LANGUE = sys.argv[sys.argv.index('--lang') + 1]
    _, larg, _ = police.construit()
    fr = developpe(charge_fr())
    jp = charge_jp()
    err = 0
    for i, t in sorted(fr.items()):
        if i not in jp:
            print('?? id inconnu', i); err += 1; continue
        try:
            b = police.encode(t)
        except KeyError as e:
            print('%-8s caractère hors police %r : %s' % (i, e.args[0], t)); err += 1; continue
        if i.startswith('L04.'):     # monospace : 1 caractère = 8 px
            w, lim = 8 * len(b), MONO.get(i, jp[i][1])
        else:
            w, lim = largeur(b, larg), limite(i, jp[i])
        if w > lim:
            print('%-8s %3d > %3d px : %s' % (i, w, lim, t)); err += 1
    manque = [i for i in jp if i not in fr and i not in ('L04.17', 'L04.19', 'L04.20', 'L04.21',
                                                          'L04.50', 'L04.51', 'L04.52', 'L04.53')]
    print('%d traduites, %d erreurs, %d non traduites (hors L04)' % (len(fr), err, len(manque)))
    if manque:
        print('  ', ' '.join(manque))


if __name__ == '__main__':
    main()
