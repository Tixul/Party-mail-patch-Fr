# Party Mail — notes techniques (ROM, texte, police, écrans, sauvegarde)

Tout ce qui suit a été mesuré sur la ROM japonaise d'origine (1 Mio). Adresses **fichier** sauf mention ;
la cartouche est vue en CPU 0x200000 (fichier 0 = CPU 0x200000). La ROM traduite fait 2 Mio : les ajouts
sont en fichier 0x100000+ = CPU 0x300000+.

## Chaîne de construction
`tools/build.py` : ROM d'origine (contrôlée hors zone de sauvegarde) → ROM de 2 Mio, zone de sauvegarde
vierge → routine à chasse variable (`asm/vwf.asm`) et sa police (`police.py`) → correctifs du code
(sauvegarde, cadres, menus, curseur, « てん », date) → chaînes traduites (`lang/<code>/textes.tsv`) →
clavier, police 8×8, dictionnaire (`clavier.py`) → panneaux, logo (`lettrage.py`) → écrans fixes et
graphismes (`ecrans.py`) → patch IPS depuis la ROM d'origine, revérifié.

## Texte en octets
- Police 8×8, 2 bits/pixel, 256 glyphes : **0x7A9B6** (fond 0) et **0x7B9B6** (fond 1), glyphe =
  base + code × 16, encre couleur 3. Codes : 0x20 espace, 0x30 chiffres, 0x41 A-Z, 0x61 a-z, 0x80 あ…
  (ordre あいうえお), 0xC0 ア…, kana voisés dans les trous ASCII (0x01-0x1F, 0x22-0x2B…). Le `+` est en
  0x7B (0x2B = ゼ). 0xB7 / 0xB8 = touches ゛ / ゜ du clavier.
- `00` fin ; `FF n` variable : 00 mois, 01 jour, 02 nom de la bestiole, 03-06 plat aimé / détesté,
  personne aimée / détestée, 07 envie du moment, 10 joueur.
- Chaînes du code : `pushw 0x0022 ; pushw lo` (`0B 22 00 0B ll hh`), chaînes alignées sur une adresse
  paire. Archive **0x60000** : table u32 de 37 entrées (offsets / 0x60000) ; listes de chaînes = table
  u32 d'offsets relatifs au début de la liste. Liste 4 (= 5) : titre, rangées du clavier de profil,
  invites du profil (champ n : 22 + 3n, 23 + 3n, 24 + 3n), tables de voisement 50-53 ; listes 24-30
  (une seule), 31, 32, 33, 34 : répliques des bestioles ; 35 : répliques de partie (5 × 11).
- Bestiole → liste : table **0x221DDC** (type 0 chatte → 32, 1 chien → 30, 2 oiselle → 31, 3 timide →
  34, 4 robot → 33) ; groupe de la liste 35 : table **0x22138E**.

## Affichage et chasse variable
- sub_2110DD affiche une chaîne, **1 tuile par caractère**, 13 caractères au plus. Cadre de pile : +6
  compteur, +7 libre, +20 / +24 pointeurs vers les pointeurs de carte et de tuiles, +28 chaîne,
  +32 numéro de tuile, +34 attribut.
- `asm/vwf.asm` (CPU 0x300000) s'y greffe : 0x2110E3 `call INIT`, 0x2110F2 → 0x2112ED `call CAR`,
  0x2112E7 `call APRES_FF` (variables : appel récursif, tuile neuve), limite portée à 64 caractères.
  L'octet +7 du cadre garde le décalage en pixels dans la tuile ouverte. Code 0x7F en tête de chaîne :
  monospace d'origine. Police 1 bit/pixel en 0x300400, avances en 0x300C00, table 1 → 2 bits en 0x300D00.
- Autres routines, monospace (code + base = numéro de tuile, police chargée en tuiles 0-255) :
  sub_219999 (titre, clavier), sub_218091 (invites du profil), sub_2180CA (multi-lignes), sub_211353
  (un caractère).

## Cadres, menus, curseur
- Bulle centrée sub_21139D(chaîne, largeur, y) : largeur poussée par l'appelant. Bulles des bestioles
  15 → 18 tuiles (13 appels) ; effacement sub_219B85(0x44D6, 0x20, 15, 3) → (0x44D4, 18).
- Menus de partie (0x2109CE, 0x210A52, 0x210A9B, 0x210B5A) : cadre 5 → 7 tuiles vers la droite et leurs
  9 effacements ; curseur sub_210BF3 (cas DE = 0x1C codé en dur) : coins droits x 0x54 → 0x64.
- Boîtes d'aide sub_211024(tampon, 14, 4) ; celle de 0x21292D passe de 10 à 14 tuiles.
- Boîtes toutes faites (liaison coupée) : la chaîne doit couvrir autant de tuiles que le japonais.

## Écrans fixes (cartes de tuiles)
- Décodeur `carte_dec.py` (routine 0x21C2F0) : en-tête L, H (2 octets en mode 3/4/8, sinon 1 octet
  L | H << 4), octet fort, compteur, codes 2 bits (0 vide, 1 suite, 2 octet, 3 forme longue).
- Tuile = feuille **0x266B86** + code × 16 (CPU). 1er bloc de l'archive (0x60094) : objets écran = 4
  offsets u16 de cartes. 2e table **0x60198** (offsets / 0x60094) : cartes à jouer, WIN, LOSE,
  classements, panneaux.
- ⚠ Les **palettes** sont liées aux cases d'origine : une case ajoutée reçoit la palette 0. Le texte
  neuf reste dans les cases non vides du japonais.

## Clavier et dictionnaire
- Clavier des messages : table **0x220EDE**, 3 pages × 7 rangées × 16 octets (pointeurs en 0x221030 :
  hiragana 0x220EDE, katakana 0x220FBE, latin 0x220F4E). Étiquettes en 0x220CDC (4 octets chacune).
- Dictionnaire par défaut : 80 pointeurs u32 en **0x2211F6**. Il est **recopié dans la sauvegarde** à sa
  création : une ancienne sauvegarde garde ses mots.

## Sauvegarde
- 2 copies de 0x900 octets. Le jeu passe la taille de cartouche **en dur** (8 Mbit : `pushw 8` en
  0x218015 lecture et 0x21803F écriture) → 0x2F8000 / 0x2FA000, blocs 16 / 17. Sur une puce de 2 Mio ces
  numéros de bloc tomberaient sur 0x300000-0x31FFFF (les ajouts) : taille passée à 16 Mbit, sauvegardes
  en **0x3F8000 / 0x3FA000**, blocs 32 / 33, effacement par la routine du jeu 0x21FF37.

## Divers
- « てん » (points) : écrit après le score en 0x2117CC / 0x2117D8, et tracé caractère par caractère
  (sub_211353, 4 appels) → « pt ». Date du profil « 10月23日 » : 0xF7 / 0xF8 écrits par 3 routines →
  « 10/23 ».
- État du jeu : octet RAM 0x42AC (0x1E / 0x1F résultats, 0x5A liaison coupée, 0x64 saisie de message).
