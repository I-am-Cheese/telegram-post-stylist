#!/usr/bin/env python3
"""Verify the delivery contract, parser, footer and mobile output without Telegram."""
import json
from pathlib import Path
import tempfile
from PIL import Image
from render_post import PACKAGE, parse, plain_text, load_profile, prepare_scheme, generate


def main():
    assert plain_text(parse('<жирный>Тест</жирный>\n\n<курсив>Пример</курсив>'))=='Тест\n\nПример'
    sample='<цитата>\n<жирный>Важно.</жирный>\nОбычная строка.\n</цитата>'
    cells=parse(sample)
    assert plain_text(cells)=='Важно.\nОбычная строка.'
    assert all(c.quote for c in cells if c.text!='\n')
    assert any(c.bold for c in cells) and any(not c.bold for c in cells)
    for invalid in [
        '<b>HTML запрещён</b>', '<жирный>Незакрытый',
        '<ссылка "https://one.example"> Текст </ссылка "https://two.example">',
        '<ссылка "https://one.example"> Текст </ссылка>',
        '<жирный><курсив>Текст</жирный></курсив>']:
        try:parse(invalid);raise AssertionError('Invalid scheme accepted: '+invalid)
        except ValueError:pass
    with tempfile.TemporaryDirectory(prefix="пост's-test-") as temp:
        folder=Path(temp)
        for name in ['giveaway','developer-notice']:
            original=PACKAGE/'examples'/f'{name}.json'
            result=generate(original,folder/name)
            plain=Path(result['txt']).read_text(encoding='utf-8-sig')
            assert plain==plain_text(parse(result['formatting_scheme']))
            assert '**' not in plain and '<жирный>' not in plain and '<ссылка ' not in plain
            assert plain.endswith('Подписаться на ExitDLC\nКупить приватный чит ExitDLC')
            assert plain.count('Купить приватный чит ExitDLC')==1
            assert len(list((folder/name).iterdir()))==2
            with Image.open(result['png']) as image:
                assert image.width==840 and image.height>=1680
            assert result['layout']['rightmost_text_pixel']<840-35
            profile=load_profile(json.loads(original.read_text(encoding='utf-8')),original)
            already={'scheme':result['formatting_scheme'],'include_footer':True}
            _,once=prepare_scheme(already,profile)
            assert plain_text(once).count('Купить приватный чит ExitDLC')==1
            optout=json.loads(original.read_text(encoding='utf-8'));optout['include_footer']=False
            _,without=prepare_scheme(optout,profile)
            assert 'Подписаться на ExitDLC' not in plain_text(without)
        longspec={'scheme':'<жирный>Переносы</жирный>\n\n<моно>'+('оченьдлинноеимя'*15)+'</моно>','include_footer':False,'width':720}
        job=folder/'long.json';job.write_text(json.dumps(longspec),encoding='utf-8')
        result=generate(job,folder/'long')
        assert result['layout']['rightmost_text_pixel']<720-30
        try:generate(job,folder/'long');raise AssertionError('Existing outputs overwritten')
        except ValueError:pass
    print('PASS: Russian tags, nested quote/style, exact closing-link URLs, plain TXT equality, 2-file delivery, default footer/opt-out/dedup, Unicode paths, long-word wrapping and overwrite refusal.')


if __name__=='__main__':main()
