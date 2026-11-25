#!/usr/bin/env python3
"""Generate plain TXT and a Telegram phone mockup from Russian explanatory tags."""
import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

PACKAGE = Path(__file__).resolve().parent.parent
TAG = re.compile(r'<(/?)(жирный|курсив|моно|цитата|ссылка)(?:\s+"([^"\r\n]+)")?\s*>')
TAGLIKE = re.compile(r'</?[A-Za-zА-Яа-яЁё][^>\n]*>')


@dataclass(frozen=True)
class Cell:
    text: str
    bold: bool = False
    italic: bool = False
    mono: bool = False
    quote: bool = False
    url: str = ''


def valid_url(url):
    parsed = urlsplit(url)
    return bool(parsed.scheme in ('http', 'https', 'tg') and (parsed.netloc or parsed.path) and not any(c in url for c in '\r\n"<>'))


def parse(scheme):
    """Parse the owner's custom notation, never HTML or Telegram Markdown."""
    stack, cells, cursor = [], [], 0
    def emit(text):
        names = [name for name, _ in stack]
        url = next((value for name, value in reversed(stack) if name == 'ссылка'), '')
        for char in text:
            cells.append(Cell(char, 'жирный' in names, 'курсив' in names,
                              'моно' in names, 'цитата' in names, url))
    for match in TAG.finditer(scheme):
        literal = scheme[cursor:match.start()]
        if TAGLIKE.search(literal):
            raise ValueError('Unknown tag; use Russian explanatory tags only.')
        emit(literal)
        closing, name, value = match.groups(); value = value or ''
        if name == 'ссылка':
            if not value or not valid_url(value):
                raise ValueError('Both link tags require the same quoted valid URL.')
        elif value:
            raise ValueError('Only ссылка accepts a quoted URL.')
        if closing:
            if not stack or stack[-1] != (name, value):
                raise ValueError('Mismatched closing tag: ' + match.group())
            stack.pop()
        else:
            if name in [item[0] for item in stack]:
                raise ValueError('Repeated nested tag: ' + name)
            if name == 'ссылка' and any(item[0] == 'ссылка' for item in stack):
                raise ValueError('Nested links are not allowed.')
            stack.append((name, value))
        cursor = match.end()
    if TAGLIKE.search(scheme[cursor:]):
        raise ValueError('Unknown tag; use Russian explanatory tags only.')
    emit(scheme[cursor:])
    if stack:
        raise ValueError('Unclosed tag: ' + stack[-1][0])
    # Trim line-only wrapper whitespace, retain meaningful explicit line breaks.
    lines, line = [], []
    for cell in cells + [Cell('\n')]:
        if cell.text == '\n':
            while line and line[0].text in ' \t\r': line.pop(0)
            while line and line[-1].text in ' \t\r': line.pop()
            flags = {cell.quote for cell in line if not cell.text.isspace()}
            if len(flags) > 1:
                raise ValueError('A quote must occupy its own line/block.')
            if line or (lines and lines[-1]): lines.append(line)
            line = []
        else:
            line.append(cell)
    while lines and not lines[0]: lines.pop(0)
    while lines and not lines[-1]: lines.pop()
    normalized = []
    for index, row in enumerate(lines):
        if index: normalized.append(Cell('\n'))
        normalized.extend(row)
    if not normalized:
        raise ValueError('Post is empty.')
    return normalized


def plain_text(cells):
    return ''.join(cell.text for cell in cells)


def footer_scheme(profile):
    result = []
    for link in profile.get('footer', []):
        text, url = link['text'], link['url']
        if not text.strip() or not valid_url(url) or TAGLIKE.search(text):
            raise ValueError('Invalid footer entry.')
        result.append(f'<ссылка "{url}"> {text} </ссылка "{url}">')
    return '\n'.join(result)


def prepare_scheme(spec, profile):
    scheme = spec['scheme'].strip()
    cells = parse(scheme)
    include = spec.get('include_footer', profile.get('footer_default', True))
    if not isinstance(include, bool):
        raise ValueError('include_footer must be true/false.')
    footer = profile.get('footer', [])
    if include and footer:
        suffix = '\n'.join(row['text'] for row in footer)
        if plain_text(cells).endswith(suffix):
            # Already linked footer is accepted once; plain duplicate is a spec error.
            for row in footer:
                if not any(c.url == row['url'] for c in cells):
                    raise ValueError('Remove the unlinked footer from the body; generator adds it.')
        else:
            scheme += '\n\n' + footer_scheme(profile)
            cells = parse(scheme)
    return scheme, cells


def load_profile(spec, spec_path):
    path = Path(spec.get('profile', PACKAGE / 'assets/channel-profile.json'))
    if not path.is_absolute(): path = spec_path.parent / path
    profile = json.loads(path.read_text(encoding='utf-8-sig'))
    profile['_base'] = str(path.resolve().parent)
    return profile


def font_paths(profile):
    windir = Path('C:/Windows/Fonts')
    linux = Path('/usr/share/fonts/truetype/dejavu')
    candidates = {
        'regular': [windir/'segoeui.ttf', linux/'DejaVuSans.ttf', Path('/System/Library/Fonts/Supplemental/Arial.ttf')],
        'bold': [windir/'seguisb.ttf', linux/'DejaVuSans-Bold.ttf', Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf')],
        'italic': [windir/'segoeuii.ttf', linux/'DejaVuSans-Oblique.ttf', Path('/System/Library/Fonts/Supplemental/Arial Italic.ttf')],
        'bold_italic': [windir/'segoeuiz.ttf', linux/'DejaVuSans-BoldOblique.ttf'],
        'mono': [windir/'consola.ttf', linux/'DejaVuSansMono.ttf'],
        'emoji': [windir/'seguiemj.ttf', Path('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf')]
    }
    result = {}
    for kind, paths in candidates.items():
        custom = profile.get('fonts', {}).get(kind)
        if custom:
            value = Path(custom)
            if not value.is_absolute(): value = Path(profile['_base']) / value
            paths = [value]
        result[kind] = next((p for p in paths if p.is_file()), None)
    if not result['regular']:
        raise ValueError('No Cyrillic-capable regular font found; configure fonts.regular.')
    for kind in ['bold', 'italic', 'bold_italic', 'mono', 'emoji']:
        result[kind] = result[kind] or result['regular']
    return result


def clusters(cells):
    """Keep combining marks/emoji sequences together when breaking long words."""
    import unicodedata
    result = []
    for cell in cells:
        if result and (unicodedata.combining(cell.text) or cell.text in '\ufe0f\ufe0e\u200d\u20e3'
                       or 0x1f3fb <= ord(cell.text) <= 0x1f3ff or result[-1].text.endswith('\u200d')):
            old = result[-1]
            result[-1] = Cell(old.text + cell.text, old.bold, old.italic, old.mono, old.quote, old.url)
        else:
            result.append(cell)
    return result


def render_png(cells, profile, width, path):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as error:
        raise RuntimeError('Pillow is required for PNG rendering; reuse an existing installation.') from error
    if not 480 <= width <= 1600:
        raise ValueError('Preview width must be 480–1600 pixels.')
    scale = width / 840
    px = lambda n: round(n * scale)
    paths = font_paths(profile)
    fonts = {}
    def font(kind='regular', size=32):
        key = (kind, px(size))
        if key not in fonts:
            try:
                fonts[key] = ImageFont.truetype(str(paths[kind]), px(size))
            except OSError:
                if kind != 'emoji': raise
                fonts[key] = ImageFont.truetype(str(paths['regular']), px(size))
        return fonts[key]
    measurement = ImageDraw.Draw(Image.new('RGB', (1,1)))
    def is_emoji(cell):
        return any(ord(ch) >= 0x1f000 or ch in '⭐⚠❗▫' for ch in cell.text)
    def kind(cell):
        if is_emoji(cell) and not cell.mono: return 'emoji'
        if cell.mono: return 'mono'
        if cell.bold and cell.italic: return 'bold_italic'
        if cell.bold: return 'bold'
        if cell.italic: return 'italic'
        return 'regular'
    def visible(cell):
        # Segoe Emoji BASIC layout otherwise allocates a phantom advance for VS16.
        return cell.text.replace('\ufe0f','').replace('\ufe0e','')
    def length(cell): return measurement.textlength(visible(cell), font=font(kind(cell)))
    def tokens(row):
        items, token, whitespace = [], [], None
        for c in clusters(row):
            flag = c.text.isspace()
            if token and flag != whitespace: items.append(token); token=[]
            token.append(c); whitespace=flag
        if token: items.append(token)
        return items
    def wrap(row, maximum):
        lines, current, used = [], [], 0
        for token in tokens(row):
            spaces = all(c.text.isspace() for c in token)
            total = sum(length(c) for c in token)
            if spaces:
                if current: current.extend(token); used += total
                continue
            if current and used + total > maximum:
                while current and current[-1].text.isspace(): current.pop()
                lines.append(current);current=[];used=0
            for cell in token:
                advance = length(cell)
                if current and used + advance > maximum:
                    lines.append(current);current=[];used=0
                current.append(cell);used+=advance
        while current and current[-1].text.isspace(): current.pop()
        if current:lines.append(current)
        return lines
    raw_lines, row = [], []
    for cell in cells + [Cell('\n')]:
        if cell.text == '\n': raw_lines.append(row);row=[]
        else:row.append(cell)
    line_height = px(44)
    x, top, y = px(48), px(294), px(359)
    layouts, quote_ranges = [], []
    active_quote = None
    for row in raw_lines:
        if not row:
            if active_quote is not None:
                quote_ranges.append((active_quote,y+px(8)));active_quote=None
            y+=px(27);continue
        quoted = next(c.quote for c in row if not c.text.isspace())
        if quoted and active_quote is None: active_quote=y-px(7)
        if not quoted and active_quote is not None:
            quote_ranges.append((active_quote,y+px(8)));active_quote=None;y+=px(25)
        left = x+px(20) if quoted else x
        maximum=width-px(114)-(px(35) if quoted else 0)
        for laid_out in wrap(row,maximum):
            layouts.append((left,y,laid_out));y+=line_height
    if active_quote is not None: quote_ranges.append((active_quote,y+px(8)))
    y+=px(16)
    bubble_bottom=y+px(47)
    minimum=round(profile.get('preview',{}).get('minimum_height',1680)*scale)
    height=max(minimum,bubble_bottom+px(180))
    if height>12000:raise ValueError('Post too tall for a useful preview; shorten or split it deliberately.')
    image=Image.new('RGB',(width,height),'#0e1720');draw=ImageDraw.Draw(image)
    draw.rectangle((0,0,width,px(196)),fill='#182530')
    draw.text((px(28),px(15)),profile.get('preview',{}).get('clock','21:57'),font=font('bold',25),fill='white')
    draw.line([(width-px(135),px(35)),(width-px(125),px(25)),(width-px(115),px(35))],fill='white',width=px(3))
    draw.rounded_rectangle((width-px(91),px(24),width-px(34),px(47)),radius=px(5),outline='white',width=px(2))
    draw.rectangle((width-px(87),px(28),width-px(45),px(43)),fill='white')
    draw.line([(px(51),px(102)),(px(30),px(122)),(px(51),px(142))],fill='#f6f8fa',width=px(4))
    draw.ellipse((px(81),px(83),px(155),px(157)),fill='#314154')
    draw.text((px(101),px(96)),profile.get('avatar_letter','E')[:1],font=font('bold',36),fill='#d48aff')
    channel=profile.get('channel_name','Telegram channel')
    header=channel
    while measurement.textlength(header,font=font('bold',30))>width-px(245):
        header=header[:-2]+'…'
    draw.text((px(174),px(91)),header,font=font('bold',30),fill='#f2f5f7')
    draw.text((px(174),px(134)),'предпросмотр публикации',font=font('regular',24),fill='#8ea2b4')
    for yy in [108,123,138]:draw.ellipse((width-px(40),px(yy),width-px(34),px(yy+6)),fill='#b9c7d3')
    draw.rounded_rectangle((width//2-px(124),px(222),width//2+px(124),px(264)),radius=px(21),fill='#253a4b')
    label=profile.get('preview',{}).get('label','Тестовый макет')
    draw.text((width//2-measurement.textlength(label,font=font('regular',24))/2,px(226)),label,font=font('regular',24),fill='#d3dfe9')
    draw.rounded_rectangle((px(22),top,width-px(26),bubble_bottom),radius=px(27),fill='#192936')
    draw.text((x,top+px(22)),channel,font=font('bold',27),fill='#5cd8e9')
    for start,end in quote_ranges:
        draw.rounded_rectangle((x,start,width-px(50),end),radius=px(8),fill='#203d49')
        draw.rounded_rectangle((x,start,x+px(6),end),radius=px(3),fill='#64c9d9')
    max_right=0
    for left,yy,row in layouts:
        xx=left
        for cell in row:
            text=visible(cell);style=kind(cell);advance=length(cell)
            if cell.mono:
                draw.rectangle((xx,yy+px(2),xx+advance,yy+px(40)),fill='#263b49')
            draw.text((xx,yy),text,font=font(style),fill='#5cd8e9' if cell.url else '#f0f2f4',embedded_color=style=='emoji')
            xx+=advance
        max_right=max(max_right,xx)
    draw.text((width-px(225),y),'предпросмотр',font=font('regular',21),fill='#8097aa')
    bottom=height-px(120)
    draw.rectangle((0,bottom,width,height),fill='#182530')
    draw.rounded_rectangle((px(24),bottom+px(15),width-px(24),bottom+px(80)),radius=px(32),fill='#22333f')
    draw.text((px(51),bottom+px(26)),'Публикация…',font=font('regular',28),fill='#8299ac')
    draw.rounded_rectangle((width//2-px(90),height-px(20),width//2+px(90),height-px(12)),radius=px(4),fill='#d2d8de')
    image.save(path)
    return {'width':width,'height':height,'rightmost_text_pixel':round(max_right,2),'fonts':{k:str(v) for k,v in paths.items()}}


def generate(spec_path, output, scheme_out=None):
    spec_path=Path(spec_path).resolve()
    spec=json.loads(spec_path.read_text(encoding='utf-8-sig'))
    profile=load_profile(spec,spec_path)
    scheme,cells=prepare_scheme(spec,profile)
    output=Path(output).resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output folder is not empty; choose a new post/revision folder.')
    output.mkdir(parents=True,exist_ok=True)
    text_path=output/'Пост без форматирования.txt'
    image_path=output/'Предпросмотр.png'
    layout=render_png(cells,profile,int(spec.get('width',profile.get('preview',{}).get('width',840))),image_path)
    text_path.write_text(plain_text(cells),encoding='utf-8-sig')
    if scheme_out:
        target=Path(scheme_out);target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(scheme,encoding='utf-8')
    return {'txt':str(text_path),'png':str(image_path),'formatting_scheme':scheme,'layout':layout}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--spec',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--scheme-out',type=Path)
    args=ap.parse_args()
    try:result=generate(args.spec,args.out,args.scheme_out)
    except (ValueError,KeyError,OSError,RuntimeError) as error:ap.exit(2,'Generation failed: '+str(error)+'\n')
    print(json.dumps(result,ensure_ascii=True,indent=2))


if __name__=='__main__':main()
