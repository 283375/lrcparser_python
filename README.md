# [WIP]lrcparser

A simple lyric file parser.

## Why this parser?

Pros:

- ...
- Well, to be honest, there's no strong reasons.

Cons:

- Lack of tests
- Potential bugs that may screw your files up
- ...

...But if you have tried this library and think it useful...

then just keep using it, thank you for your support :)

## Usage

```lrc
[ti:test_lyric]
[al:TEST ~AVOIDING ERRORS~]
[by:283375]
[offset:250]

[00:00.02]Line 1
[00:00.28]Line 2
[00:02.83]Line 3
[00:28.33]Line 4 with translation | 一般大家都这么打翻译
[00:28.33]可惜我更喜欢换行
[00:28.33]你说得对，但是《lrcparser》是由……
[28:33.75]Line 6
```

```py
from lrcparser import *

with open('example.lrc', 'r', encoding='utf-8') as lrc_file:
    parsed = LrcParser.parse(lrc_file.read(), parse_translations=True)
    offset, lrc_lines, attributes = parsed.values()

>>> offset
250

>>> lrc_lines
[
    LrcLine(
        start_time=LrcTime(0, 0, 20),
        text=LrcText(LrcTextSegment(LrcTime(0, 0, 20), "Line 1")),
        translations=None,
    ),
    LrcLine(
        start_time=LrcTime(0, 0, 280),
        text=LrcText(LrcTextSegment(LrcTime(0, 0, 280), "Line 2")),
        translations=None,
    ),
    LrcLine(
        start_time=LrcTime(0, 2, 830),
        text=LrcText(LrcTextSegment(LrcTime(0, 2, 830), "Line 3")),
        translations=None,
    ),
    LrcLine(
        start_time=LrcTime(0, 28, 330),
        text=LrcText(
            LrcTextSegment(LrcTime(0, 28, 330), "Line 4 with translation")
        ),
        translations=[
            LrcText(LrcTextSegment(LrcTime(0, 28, 330), "一般大家都这么打翻译")),
            LrcText(LrcTextSegment(LrcTime(0, 28, 330), "可惜我更喜欢换行")),
            LrcText(LrcTextSegment(LrcTime(0, 28, 330), "你说得对，但是《lrcparser》是由……")),
        ],
    ),
    LrcLine(
        start_time=LrcTime(28, 33, 750),
        text=LrcText(LrcTextSegment(LrcTime(28, 33, 750), "Line 6")),
        translations=None,
    ),
]

>>> attributes
{
    "ti": "test_lyric",
    "al": "TEST ~AVOIDING ERRORS~",
    "by": "283375",
    "offset": "250",
}
```
