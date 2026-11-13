# -*- coding: utf-8 -*-
"""把TTF字体base64内嵌进模板，生成单文件离线HTML。"""
import base64
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# TTF文件名前缀 -> (字体id, @font-face family名)
# family约定须与模板JS的familyOf()一致：'WW ' + id.slice(5)
MAPPING = [
    ('SolarisUniversal', 'font-Solaris',     'WW Solaris'),
    ('Ragunna',          'font-Ragunna',     'WW Ragunna'),
    ('Septimont',        'font-Septimont',   'WW Septimont'),
    ('Lahai-Roi',        'font-LahaiRoi',    'WW LahaiRoi'),
    ('Federation',       'font-Federation',  'WW Federation'),
    ('DigitalTube',      'font-DigitalTube', 'WW DigitalTube'),
    ('OldFont',          'font-OldFont',     'WW OldFont'),
    ('RinascitaRibbon',  'font-RRibbon',     'WW RRibbon'),
]


def find_ttf(prefix):
    for p in sorted(ROOT.glob('*.ttf')):
        if p.name.startswith(prefix):
            return p
    raise FileNotFoundError('找不到前缀为%s的ttf' % prefix)


def main():
    face_rules = []
    class_rules = []
    total = 0
    for prefix, fid, family in MAPPING:
        p = find_ttf(prefix)
        data = p.read_bytes()
        total += len(data)
        b64 = base64.b64encode(data).decode('ascii')
        face_rules.append(
            "@font-face{font-family:'%s';font-style:normal;font-weight:normal;"
            "font-display:block;src:url(data:font/ttf;base64,%s) format('truetype');}"
            % (family, b64)
        )
        class_rules.append(".%s{font-family:'%s',sans-serif;}" % (fid, family))
        print('内嵌 %-32s %6d bytes -> %s' % (p.name, len(data), family))

    font_css = '\n'.join(face_rules) + '\n' + '\n'.join(class_rules) + '\n'

    tpl_path = ROOT / 'app.template.html'
    template = tpl_path.read_text(encoding='utf-8')
    if '@@FONT_FACE@@' not in template:
        print('错误：模板缺少 @@FONT_FACE@@ 占位符')
        sys.exit(1)

    html = template.replace('@@FONT_FACE@@', font_css)
    out = ROOT / '鸣潮文字转换器.html'
    out.write_text(html, encoding='utf-8')

    print('-' * 60)
    print('TTF原始合计: %d bytes (%.1f KB)' % (total, total / 1024))
    print('输出文件: %s' % out)
    print('输出大小: %d bytes (%.1f KB)' % (out.stat().st_size, out.stat().st_size / 1024))
    print('占位符残留: %s' % ('@@FONT_FACE@@' in html))


if __name__ == '__main__':
    main()