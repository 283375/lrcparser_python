# LrcParser

## class `ParseResult`

```py
class ParseResult(TypedDict):
        offset: int
        lrc_lines: List[LrcLine]
        attributes: Dict[str, str]
```

[`parse()`](#def_parse) 的函数返回值。

## def `parse`

```py
@classmethod
def parse(
    cls,
    s: str,
    parse_translations: bool = False,
    translation_divider: str = TRANSLATION_DIVIDER,
) -> ParseResult:
```

从传入的字符串 `s` 中解析歌词文件的歌词 `lrc_lines`、延迟 `offset` 及属性 `attributes`，以字典形式返回。

|                       | 说明               |
| --------------------: | :----------------- |
|                   `s` | 要解析的歌词字符串 |
|  `parse_translations` | 是否解析翻译       |
| `translation_divider` | 111                |

```py
>>> s = '''[ti: TEST]
... [ar: 283375]
... [al: TEST ~AN EXAMPLE FOR YOU~]
... [by: 283375]
... [offset: 375]
...
... [00:05.26]Line 1 example
... [00:07.36]Line 2 example | 翻译示例
... [00:09.54]Line 3 divider example /// 分隔符示例'''

>>> LrcParser.parse(s) == {
...     'offset': 375,
...     'lrc_lines': [
...         LrcLine(text="Line 1 example", start_time=LrcTime(0, 5, 260)),
...         LrcLine(text="Line 2 example | 翻译示例", start_time=LrcTime(0, 7, 360)),
...         LrcLine(text="Line 3 divider example /// 分隔符示例", start_time=LrcTime(0, 9, 540))
...     ],
...     'attributes': {
...         'ti': 'TEST',
...         'ar': '283375',
...         'al': 'TEST ~AN EXAMPLE FOR YOU~',
...         'by': '283375',
...         'offset': '375',
...     }
... }
True

>>> LrcParser.parse(s, parse_translations=True)['lrc_lines'] == [
...     LrcLine(text="Line 1 example", start_time=LrcTime(0, 5, 260)),
...     LrcLine(text="Line 2 example", translations=['翻译示例'], start_time=LrcTime(0, 7, 360)),
...     LrcLine(text="Line 3 divider example /// 分隔符示例", start_time=LrcTime(0, 9, 540))
... ]
True

>>> LrcParser.parse(s, parse_translations=True, translation_divider=' /// ')['lrc_lines'] == [
...     LrcLine(text="Line 1 example", start_time=LrcTime(0, 5, 260)),
...     LrcLine(text="Line 2 example | 翻译示例", start_time=LrcTime(0, 7, 360)),
...     LrcLine(text="Line 3 divider example", translations=['分隔符示例'], start_time=LrcTime(0, 9, 540))
... ]
True
```

## def `find_duplicate`

```py
@classmethod
def find_duplicate(cls, lrc_lines: List[LrcLine]) -> List[List[LrcLine]]:
```

find_duplicate finds duplicate lyrics.

```py
>>> LrcParser.find_duplicate([
...     LrcLine(start_time=LrcTime(0, 1, 589), text='Line 1'),
...     LrcLine(start_time=LrcTime(0, 1, 589), text='Line 2'),
...     LrcLine(start_time=LrcTime(0, 1, 589), text='Line 3'),
...     LrcLine(start_time=LrcTime(0, 2, 589), text='Line 4'),
...     LrcLine(start_time=LrcTime(0, 2, 589), text='Line 5'),
...     LrcLine(start_time=LrcTime(0, 2, 589), text='Line 6'),
... ]) == [
...      [
...          LrcLine(start_time=LrcTime(0, 1, 589), text='Line 1'),
...          LrcLine(start_time=LrcTime(0, 1, 589), text='Line 2'),
...          LrcLine(start_time=LrcTime(0, 1, 589), text='Line 3'),
...      ],
...      [
...          LrcLine(start_time=LrcTime(0, 2, 589), text='Line 4'),
...          LrcLine(start_time=LrcTime(0, 2, 589), text='Line 5'),
...          LrcLine(start_time=LrcTime(0, 2, 589), text='Line 6'),
...      ]
...  ]
True
```

## def `combine_translation`

```py
@classmethod
def combine_translation(cls, lrc_lines: List[LrcLine]) -> List[LrcLine]:
```

combine_translation analyzes the translation of the lyric.

```py
>>> LrcParser.combine_translation([
...     LrcLine(start_time=LrcTime(0, 1, 589), text='Line 1'),
...     LrcLine(start_time=LrcTime(0, 1, 589), text='翻译 1'),
...     LrcLine(start_time=LrcTime(0, 2, 589), text='Line 2'),
...     LrcLine(start_time=LrcTime(0, 2, 589), text='翻译 2'),
...     LrcLine(start_time=LrcTime(0, 2, 589), text='これは2行目です'),
... ]) == [
...     LrcLine(
...         start_time=LrcTime(0, 1, 589),
...         text='Line 1',
...         translations=['翻译 1']),
...     LrcLine(
...         start_time=LrcTime(0, 2, 589),
...         text='Line 2',
...         translations=['翻译 2', 'これは2行目です'])
... ]
True
```
