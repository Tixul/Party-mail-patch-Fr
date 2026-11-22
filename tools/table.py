"""Table du texte 1 octet (police 0x27B9B6 / 0x27A9B6, glyphe = base + code*16)."""
T = {}
def _r(debut, s):
    for i, c in enumerate(s):
        if c != '□':
            T[debut + i] = c
_r(0x00, '□ジじパドどぐばグプ入力ごがぎげ')
_r(0x10, 'ざずぜぞだぢづでびぶべぼぱぴぷぺ')
_r(0x20, ' !ガギゲゴザ\'()ズゼ,ー./')
_r(0x30, '0123456789:;<=>?')
_r(0x40, 'ゾABCDEFGHIJKLMNO')
_r(0x50, 'PQRSTUVWXYZぽ¥ブ・ダ')
_r(0x60, 'ヂabcdefghijklmno')
_r(0x70, 'pqrstuvwxyz+ヅデバビ')
_r(0x80, 'あいうえおかきくけこさしすせそた')
_r(0x90, 'ちつてとなにぬねのはひふへほまみ')
_r(0xA0, 'むめもやゆよらりるれろわをんぁぃ')
_r(0xB0, 'ぅぇぉゃゅょっ、・～。」…^_ペ')
_r(0xC0, 'アイウエオカキクケコサシスセソタ')
_r(0xD0, 'チツテトナニヌネノハヒフヘホマミ')
_r(0xE0, 'ムメモヤユヨラリルレロワヲンァィ')
_r(0xF0, 'ゥェォャュョッ月日ベボピポ■♡%')
INV = {v: k for k, v in T.items()}


def dec(b):
    return ''.join(T.get(x, '{%02X}' % x) for x in b)
