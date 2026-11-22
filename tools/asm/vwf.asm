; Party Mail FR : chasse variable dans sub_2110DD (affichage d'une chaîne, 1 tuile par caractère).
;
; Cadre de pile de sub_2110DD (son XSP) : +6 compteur de caractères (octet), +7 libre -> décalage en
; pixels dans la tuile ouverte (0 = aucune ; bit 7 = mode « monospace » d'origine), +20 ptr vers le
; pointeur de carte (mots), +24 ptr vers le pointeur de tuiles, +28 ptr de chaîne, +32 numéro de tuile
; (mot, attributs compris), +34 octet d'attribut (OR sur les pixels).
;
; Points d'appel posés par tools/build.py :
;   0x2110E3 : call INIT        (à la place de « ld (xsp+6),0 »)
;   0x2112E7 : call APRES_FF ; jr 0x211332   (après l'appel récursif des variables FF n)
;   0x2112ED : call CAR ; jr 0x211332        (caractère ordinaire ; le jrl de 0x2110F2 y pointe)
;
; Code 0x7F en tête de chaîne : passe en monospace (glyphes d'origine, 1 tuile par caractère).
;
; Assemblage : asl -cpu 96C141 vwf.asm ; p2bin vwf.p   (tools/build.py)

        cpu     96C141
        maxmode on
        org     300000h

POLICE  equ     300400h         ; 256 x 8 octets (1 bpp)
LARG    equ     300C00h         ; 256 octets
EXPAND  equ     300D00h         ; 256 mots
RESS    equ     218213h         ; sub_218213(n) -> XHL = ressource n (2 = police d'origine)

INIT:   ldw     (xsp+10),0      ; compteur = 0, décalage = 0
        ret

APRES_FF:
        add     (xsp+10),a      ; ce que faisait le jeu
        ldb     (xsp+11),0      ; la variable a fermé sa dernière tuile
        ret

; ---------------------------------------------------------------- caractère ordinaire
CAR:    push    xiy
        push    xiz
        lda     xiy,(xsp+12)    ; cadre de sub_2110DD
        ; octet de fond = 1re ligne du glyphe espace d'origine | attribut
        pushw   2
        call    RESS
        inc     2,xsp
        ld      xiz,xhl         ; XIZ = police d'origine
        ld      xix,(xiy+28)
        ld      a,(xix)
        cp      a,7Fh
        jr      nz,PAS_MARQ
        ldb     (xiy+7),80h     ; marqueur : monospace, rien à dessiner
        jp      FIN
PAS_MARQ:
        bit     7,(xiy+7)
        jp      nz,MONO
        extz    wa
        extz    xwa
        ld      xbc,xwa
        add     xbc,LARG
        ld      d,(xbc)         ; D = avance
        sll     3,xwa
        add     xwa,POLICE
        ld      xix,xwa         ; XIX = lignes du glyphe
        ld      b,(xiy+7)       ; B = décalage
        ld      a,b
        add     a,d             ; (pas de « add A,C » : CB 81 suspect sur console)
        ld      c,a             ; C = décalage + avance
        cp      b,0
        jr      nz,V1
        call    NOUVELLE        ; garde B et C
V1:     ld      xhl,(xiy+24)
        ld      xhl,(xhl)
        lda     xhl,(xhl-16)    ; tuile ouverte
        ld      a,c
        cp      a,8
        jr      c,V2
        jr      z,V3
        sub     a,8             ; déborde sur une 2e tuile
        ld      (xiy+7),a
        push    xhl
        call    NOUVELLE
        pop     xhl
        jr      V4
V3:     ld      a,0
V2:     ld      (xiy+7),a
V4:     ld      a,b
        add     a,a
        ld      e,a             ; E = décalage x 2 (bits)
        ld      a,16
        sub     a,e
        ld      d,a             ; D = 16 - E
        ld      xiz,xix
        add     xiz,8           ; fin du glyphe
LIGNE:  ld      a,(xix+)
        extz    wa
        add     wa,wa
        extz    xwa
        add     xwa,EXPAND
        ld      bc,(xwa)        ; BC = masque 2 bpp (pixel 0 en bits 15-14)
        ld      iy,bc
        ld      a,e
        cp      a,0
        jr      z,SANS
        srl     a,bc            ; partie gauche -> tuile ouverte
        ld      a,d
        sll     a,iy            ; partie qui déborde -> tuile suivante
        jr      ECRIT
SANS:   ld      iy,0
ECRIT:  or      (xhl),bc
        or      (xhl+16),iy
        inc     2,xhl
        cp      xix,xiz
        jr      nz,LIGNE
        jp      FIN

; ---------------------------------------------------------------- monospace d'origine
MONO:   extz    wa
        sll     4,wa
        extz    xwa
        add     xwa,xiz
        ld      xix,xwa         ; glyphe d'origine (16 octets 2 bpp)
        call    NOUVELLE
        ld      xhl,(xiy+24)
        ld      xhl,(xhl)
        lda     xhl,(xhl-16)
        ld      b,16
M1:     ld      a,(xix+)
        or      a,(xiy+34)
        ld      (xhl+),a
        djnz    b,M1

FIN:    pop     xiz
        pop     xiy
        ret

; ---------------------------------------------------------------- ouvre une tuile
; XIY = cadre ; XIZ = police d'origine. Garde B, C, XIX, XIY, XIZ.
NOUVELLE:
        ld      xde,(xiy+24)
        ld      xhl,(xde)
        ld      a,(xiz+200h)    ; fond du glyphe espace
        or      a,(xiy+34)
        ld      w,a
        ld      (xhl+),wa
        ld      (xhl+),wa
        ld      (xhl+),wa
        ld      (xhl+),wa
        ld      (xhl+),wa
        ld      (xhl+),wa
        ld      (xhl+),wa
        ld      (xhl+),wa
        ld      (xde),xhl
        ld      xde,(xiy+20)
        ld      xhl,(xde)
        ld      wa,(xiy+32)
        ld      (xhl+),wa
        ld      (xde),xhl
        inc     1,wa
        ld      (xiy+32),wa
        ret
