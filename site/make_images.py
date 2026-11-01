#!/usr/bin/env python3
"""Makes favicon, apple-touch-icon, the developer mark and the OG share images. Run once; outputs are committed.
Needs Pillow and the DejaVu fonts (any bold sans works, set FONT)."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'assets', 'img')
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_R = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
NIGHT, ACC, ACC2 = (17, 24, 39), (99, 132, 255), (148, 163, 255)


def mark(size):
    s = size * 4
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * .23), fill=(59, 91, 219))
    # accent bar
    d.rounded_rectangle([int(s * .22), int(s * .74), int(s * .78), int(s * .80)], radius=int(s * .03), fill=(255, 255, 255))
    f = ImageFont.truetype(FONT, int(s * .42))
    d.text((s / 2, s * .45), 'PY', font=f, fill=(255, 255, 255), anchor='mm')
    return im.resize((size, size), Image.LANCZOS)


def flat(im, bg=(255, 255, 255)):
    b = Image.new('RGB', im.size, bg); b.paste(im, mask=im.split()[3]); return b


m = mark(512)
m.save(os.path.join(IMG, 'mark-512.png'))
mark(192).save(os.path.join(IMG, 'mark-192.webp'), quality=90)
flat(mark(180), NIGHT).save(os.path.join(HERE, 'apple-touch-icon.png'))
mark(64).save(os.path.join(HERE, 'favicon.png'))
mark(48).save(os.path.join(HERE, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])

TXT = {'en': ('Pavel Yakimenko', 'Indie developer of mobile apps', ['Fridge Pick', 'Jewelers Handbook']),
       'ru': ('Pavel Yakimenko', 'Инди-разработчик мобильных приложений', ['Fridge Pick', 'Справочник ювелира'])}
for lang, (name, sub, apps) in TXT.items():
    W, H = 1200, 630
    im = Image.new('RGB', (W, H), NIGHT)
    glow = Image.new('RGB', (W, H), NIGHT); g = ImageDraw.Draw(glow)
    g.ellipse([700, -300, 1500, 400], fill=(45, 62, 140)); glow = glow.filter(ImageFilter.GaussianBlur(120))
    im = Image.blend(im, glow, .9)
    d = ImageDraw.Draw(im)
    im.paste(mark(120), (80, 80), mark(120))
    d.text((80, 250), name, font=ImageFont.truetype(FONT, 72), fill=(240, 243, 255))
    d.text((82, 340), sub, font=ImageFont.truetype(FONT_R, 34), fill=(190, 199, 230))
    x = 80
    for i, (icon, label) in enumerate(zip(['fridge-pick-512.jpg', 'jewelers-handbook-512.jpg'], apps)):
        ic = Image.open(os.path.join(IMG, icon)).convert('RGB').resize((96, 96), Image.LANCZOS)
        msk = Image.new('L', (96, 96), 0); ImageDraw.Draw(msk).rounded_rectangle([0, 0, 95, 95], 22, fill=255)
        im.paste(ic, (x, 450), msk)
        f = ImageFont.truetype(FONT, 32)
        d.text((x + 116, 498), label, font=f, fill=(240, 243, 255), anchor='lm')
        x += 116 + int(d.textlength(label, font=f)) + 70
    d.rounded_rectangle([80, 400, 200, 408], 4, fill=ACC)
    im.save(os.path.join(IMG, f'og-{lang}.jpg'), quality=88)
print('ok')
