"""Construit la ROM traduite de Party Mail (base : ROM japonaise d'origine, non modifiée).

    python tools/build.py --rom "Party Mail (Japan).ngc" [--lang fr] [--ips]
        ->  out/<code>.ngc (+ out/<code>.ips, revérifié)

ROM portée à 2 Mio : le code de sauvegarde du jeu gère les cartouches 16 Mbit (sauvegardes en
0x3F8000/0x3FA000, effacement par sa propre routine 0x21FF37), taille forcée à 16 Mbit.
Zone de sauvegarde livrée vierge.
Ajouts en CPU 0x300000+ (fichier 0x100000+) :
  0x300000 code VWF (tools/asm/vwf.asm)   0x300400 police 1 bpp   0x300C00 avances   0x300D00 EXPAND
  0x301000.. chaînes traduites, tuiles neuves, objets écran recopiés.
Le code assembleur est livré assemblé (tools/asm/vwf.bin). Pour le réassembler après modification,
installer AS (Macro Assembler AS, asl + p2bin) et donner son dossier dans la variable ASL_DIR.
"""
import hashlib
import os
import struct
import subprocess
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import police  # noqa: E402

PROJET = os.path.dirname(ICI)
CPU = 0x200000
# ROM japonaise attendue : SHA-1 du contenu hors zone de sauvegarde (0xF8000-0xFBFFF)
SHA1_JP = '2ff04fd5999c43e096f9cd4541d23ccd7b454643'
JP = None


def assemble(nom):
    d = os.path.join(ICI, 'asm')
    asl = os.environ.get('ASL_DIR')
    if asl:
        ext = '.exe' if os.name == 'nt' else ''
        subprocess.run([os.path.join(asl, 'asl' + ext), '-cpu', '96C141', '-q', nom + '.asm'], cwd=d,
                       check=True, stdout=subprocess.DEVNULL)
        subprocess.run([os.path.join(asl, 'p2bin' + ext), nom + '.p', nom + '.bin'], cwd=d, check=True,
                       stdout=subprocess.DEVNULL)
    return open(os.path.join(d, nom + '.bin'), 'rb').read()


def pose(rom, adr, avant, apres):
    a, b = bytes.fromhex(avant), bytes.fromhex(apres)
    if rom[adr:adr + len(a)] != a:
        raise SystemExit('octets inattendus en %06X : %s (attendu %s)' % (adr, rom[adr:adr + len(a)].hex(), avant))
    rom[adr:adr + len(b)] = b


class Zone:
    """Allocation linéaire dans la puce étendue (fichier 0x100000+)."""
    def __init__(self, rom, debut, fin):
        self.rom, self.p, self.fin = rom, debut, fin

    def met(self, octets, align=2):
        self.p = (self.p + align - 1) & ~(align - 1)
        if self.p + len(octets) > self.fin:
            raise SystemExit('zone pleine')
        a = self.p
        self.rom[a:a + len(octets)] = octets
        self.p += len(octets)
        return a + CPU


def base_rom():
    jp = JP
    rom = bytearray(jp) + bytearray(b'\xff' * 0x100000)
    # Sauvegarde vierge en 0x1F8000-0x1FBFFF : la sauvegarde du dump (profil d'un ancien joueur,
    # dictionnaire de mots japonais) n'est pas reprise ; au 1er lancement le jeu crée le profil.
    code = assemble('vwf')
    rom[0x100000:0x100000 + len(code)] = code
    font, larg, expand = police.construit()
    rom[0x100400:0x100C00] = font
    rom[0x100C00:0x100D00] = larg
    rom[0x100D00:0x100F00] = expand
    pose(rom, 0x0110E3, 'bf060000', '1d000030')
    pose(rom, 0x0110F2, '7ef701', '7ef801')
    pose(rom, 0x0112E7, '8f06896846', '1d06003068')   # call APRES_FF ; jr ...
    rom[0x0112EC] = 0x211332 - 0x2112ED                # ... 0x211332
    pose(rom, 0x0112ED, '02001d13', '1d0e0030')         # call CAR ; jr 0x211332
    rom[0x0112F1] = 0x68
    rom[0x0112F2] = 0x211332 - 0x2112F3
    pose(rom, 0x011345, '0d', '40')
    # Sauvegarde : le jeu passe la taille de cartouche EN DUR (8 Mbit) -> blocs 16/17 en 0x2F8000 ;
    # sur une puce 16 Mbit ces numéros effaceraient 0x300000-0x31FFFF (nos ajouts). 16 Mbit :
    # 0x3F8000/0x3FA000, blocs 32/33 (le jeu a le code pour).
    pose(rom, 0x018015, '0b0800', '0b1000')    # lecture (sub_21B739)
    pose(rom, 0x01803F, '0b0800', '0b1000')    # écriture (sub_21B5F2)
    # « てん » (points) écrit par le code après le score (0x2117CC / 0x2117D8) -> « pt »
    pose(rom, 0x0117CC, 'f307e0e40092', 'f307e0e40070')
    pose(rom, 0x0117D8, 'f307e0e400ad', 'f307e0e40074')
    # « てん » tracé caractère par caractère (sub_211353, pushw 0xFF92 / 0xFFAD) -> « pt »
    for a, c in ((0x2108DF, 0x70), (0x2108F4, 0x74), (0x211665, 0x70), (0x211677, 0x74)):
        f = a - CPU - 11
        if rom[f] != 0x0B or rom[f + 2] != 0xFF or rom[f + 1] not in (0x92, 0xAD):
            raise SystemExit('てん introuvable avant %06X' % a)
        rom[f + 1] = c
    # date du profil « 10月23日 » -> « 10/23 » (3 routines : ld (XBC+2),0xF7 / ld (XBC+5),0xF8)
    for motif, neuf in ((bytes.fromhex('b90200f7'), 0x2F), (bytes.fromhex('b90500f8'), 0x20)):
        n, i = 0, rom.find(motif, 0x16000, 0x17400)
        while i >= 0:
            rom[i + 3] = neuf
            n += 1
            i = rom.find(motif, i + 1, 0x17400)
        if n != 3:
            raise SystemExit('date : %d sites (3 attendus)' % n)
    # bulle « {joueur}のペット » : largeur 10 -> 12 (80 px utiles)
    pose(rom, 0x00A47E, '0b0a000b2200', '0b0c000b2200')
    return rom


def repointe_push(rom, site, cible):
    """site = adresse fichier de « 0B ss 00 0B ll hh » ; cible = adresse CPU."""
    if rom[site] != 0x0B or rom[site + 2] != 0 or rom[site + 3] != 0x0B:
        raise SystemExit('pas un pushw/pushw en %06X' % site)
    rom[site + 1] = cible >> 16
    rom[site + 4] = cible & 0xFF
    rom[site + 5] = (cible >> 8) & 0xFF


# Appels de sub_21139D (bulle centrée) dont la largeur 15 passe à 18 tuiles (128 px utiles) :
# répliques des bêtes (listes 24-35) et « grondé/félicité/a joué avec ».
BULLES_18 = (0x213596, 0x213755, 0x21382C, 0x213A67, 0x213EA7, 0x213FC9, 0x20C018, 0x20C8E3,
             0x20C95D, 0x20C402, 0x20CA0C, 0x20CAB8, 0x20CB10)
ARCHIVE = 0x60000
BOURRE = {'C.21ECE', 'C.21EDA'}   # liaison coupée : cases de la boîte = tuiles du texte japonais


def elargit_bulles(rom):
    # effacement des bulles : sub_219B85(0x44D6 = ligne 2 col 2, tuile 0x20, 15, 3) -> col 1, 18 tuiles
    motif = bytes.fromhex('0b03000b0f000b2000f1d64430')
    n, i = 0, rom.find(motif, 0, 0x100000)
    while i >= 0:
        rom[i + 4] = 0x12
        rom[i + 10] = 0xD4
        n += 1
        i = rom.find(motif, i + 1, 0x100000)
    if n != 11:
        raise SystemExit('effacements de bulle : %d trouvés (11 attendus)' % n)
    for a in BULLES_18:
        f = a - CPU
        i = rom.rfind(b'\x0b\x0f\x00', f - 45, f)
        if i < 0:
            raise SystemExit('largeur 15 introuvable avant %06X' % a)
        rom[i + 1] = 0x12


def menus(rom):
    """Menus de partie (えらぶ/メール/ペット, おくる, しかる/ほめる/あそぶ, あがり) : cadre 5 -> 7 tuiles,
    élargi vers la droite (bord gauche et curseur inchangés) : 5 tuiles utiles (40 px)."""
    for a in (0x2109D3, 0x210A57, 0x210AAC, 0x210ABE, 0x210B5F):
        pose(rom, a - CPU, '0b0500', '0b0700')
    # curseur des menus de partie (sub_210BF3, cas DE=0x1C codé en dur) : coins droits x 0x54 -> 0x64
    pose(rom, 0x010C32, 'f5f00054', 'f5f00064')
    pose(rom, 0x010C53, 'f5f00054', 'f5f00064')
    # effacements correspondants : sub_219B85(0x44E0, tuile 0x20, largeur 5, hauteur 3/6)
    motif = bytes.fromhex('0b05000b2000f1e04430')
    n, i = 0, rom.find(motif, 0, 0x100000)
    while i >= 0:
        rom[i + 1] = 7
        n += 1
        i = rom.find(motif, i + 1, 0x100000)
    if n != 9:
        raise SystemExit('effacements de menu : %d trouvés (9 attendus)' % n)


def boites_aide(rom):
    """La boîte « おなじまいすうで / トレードします » (10 tuiles) prend la taille et la place des
    autres boîtes d'aide (14 tuiles en 0x4618, lignes 0x465A / 0x469A)."""
    pose(rom, 0x01292D, '0b0a00f11c4630', '0b0e00f1184630')
    pose(rom, 0x012938, 'f15e4630', 'f15a4630')
    pose(rom, 0x012960, 'f19e4630', 'f19a4630')


def textes(rom, z, langue):
    import controle
    import extrait
    fr = controle.developpe(controle.charge_fr(langue))
    jp = extrait.textes_jp(JP)
    n = 0
    _, larg, _ = police.construit()
    for i, t in sorted(fr.items()):
        b = police.encode(t)
        if i in BOURRE:       # boîte toute faite : couvrir autant de tuiles que le japonais
            while police.largeur(b, larg) < 8 * len(jp[i][2]):
                b += b' '
        b += b'\0'
        if i.startswith('C.'):
            a = z.met(b)
            for site in jp[i][0].split(','):
                repointe_push(rom, int(site, 16), a)
        else:
            liste, j = int(i[1:3]), int(i[4:])
            base = ARCHIVE + struct.unpack_from('<I', rom, ARCHIVE + 4 * liste)[0]
            a = z.met(b)
            struct.pack_into('<I', rom, base + 4 * j, a - CPU - base)
        n += 1
    return n


def main():
    global JP
    args = sys.argv[1:]
    if '--rom' not in args:
        raise SystemExit(__doc__)
    rom_jp = args[args.index('--rom') + 1]
    langue = args[args.index('--lang') + 1] if '--lang' in args else 'fr'
    JP = open(rom_jp, 'rb').read()
    if len(JP) != 0x100000 or hashlib.sha1(JP[:0xF8000] + JP[0xFC000:]).hexdigest() != SHA1_JP:
        raise SystemExit('ROM inattendue : il faut « Party Mail (Japan) », 1 048 576 octets, non modifiée')
    police.ROM = JP
    rom = base_rom()
    z = Zone(rom, 0x101000, 0x1F0000)
    elargit_bulles(rom)
    boites_aide(rom)
    menus(rom)
    n = textes(rom, z, langue)
    import ecrans
    import clavier
    import lettrage
    clavier.applique(rom, z)
    rom[lettrage.PANNEAU:lettrage.PANNEAU + 256] = lettrage.panneau()   # « スタート » -> « GO ! »
    for code, t in lettrage.bandeau(rom)[0].items():                    # sous-titre du logo
        rom[0x66B86 + code * 16:0x66B86 + code * 16 + 16] = t
    ecrans.applique(rom, z)
    ecrans.graphismes(rom, z)
    os.makedirs(os.path.join(PROJET, 'out'), exist_ok=True)
    sortie = os.path.join(PROJET, 'out', langue + '.ngc')
    open(sortie, 'wb').write(bytes(rom))
    print(sortie, '-', n, 'chaînes')
    if '--ips' in args:
        import ips
        p = ips.fabrique(JP, bytes(rom))
        if ips.applique(JP, p) != bytes(rom):
            raise SystemExit('patch IPS faux')
        f = os.path.join(PROJET, 'out', langue + '.ips')
        open(f, 'wb').write(p)
        print(f, '-', len(p), 'octets, vérifié')


if __name__ == '__main__':
    main()
