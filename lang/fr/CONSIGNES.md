# Consignes de traduction (français)

## Principe
- Traduire depuis le **japonais** et **adapter** : chaque réplique doit avoir du sens seule, dite par ce
  personnage, comme un francophone la dirait.
- Tutoiement entre le joueur et ses bestioles. Seul le robot vouvoie.

## Les bestioles
| Liste | Bestiole | Ton |
|---|---|---|
| L24 | chien | crâneur, familier (« Laisse-moi faire ! », « j'suis ») |
| L31 | oiselle | enjouée, tête en l'air (« Trois pas, et j'oublie tout ! ») |
| L32 | chatte | coquette, indépendante (« Laisse-moi tranquille. ») |
| L33 | robot | MAJUSCULES, phrases de machine, vouvoie (« EN ATTENTE D'ORDRES. ») |
| L34 | petite bête timide | polie, peureuse, gourmande |

`COMMUN.00`-`COMMUN.29` : salutations et calendrier, communs aux listes 24, 31, 32 et 34. Fêtes
japonaises : un équivalent français quand il existe (Golden Week → ponts de mai), sinon le nom de la fête
dit simplement (« fête des poupées »).

Liste 35 (en partie), 11 événements par bestiole dans cet ordre : départ, ordre reçu, arrivée chez un
autre joueur, retour, mauvaise carte, bonne carte, grondé, félicité, oubli, devenu plus malin, perdu
puis retrouvé.

## Vocabulaire
- ペット → **bestiole** (jamais « pet »).
- えらぶ (menu de tour) → **Échanger** : on choisit un partenaire d'échange.
- あがり → **Gagner** (8 cartes identiques).
- てん → **pt**, 位 → **1er / 2e…**

## Variables
Une variable peut contenir n'importe quel mot tapé par le joueur (4 à 6 lettres) : construire la phrase
pour qu'elle reste correcte quel que soit le mot (« {FF 03}, j'en mangerais bien ! » plutôt que
« J'ai envie de {FF 03} »).

## Place
- Bulles des bestioles : 128 px ; aides : 96 px par ligne ; menus de partie : 40 px.
- Liste 4 (profil, clavier) : police fixe, 1 caractère = 8 px.
- `python tools/controle.py --lang fr` signale tout dépassement.
