# [WIP]lrcparser

A simple parser to parse lrc files.

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
[ar:283375]
[al:TEST ~エラーを回避するための最良の方法~]
[by:283375]
[OFFset:250]

[00:00.02]Line 1
[00:00.28]Line 2
[00:02.83]Line 3
[00:28.33]Line 4 with TRANSLATION! COOL!!!
[00:28.33]这行有翻译！真他妈的酷！！！
[03:23.37]Sad because secs < 60
[02:83.37]But we can change the rules :)
[03:23.37]我只是来凑数的
[28:33.75]Line 6
```

```py
from lrcparser import LrcParser
from datetime import timedelta

with open('example.lrc', 'r', encoding='utf-8') as lrc_file:
    parsed = LrcParser.parse(lrc_file.read(), parse_translations=True)
    global_offset, lrc_lines, attributes = parsed.values()

>>> global_offset
250

>>> lrc_lines
[
    LrcLine(
        start_timedelta=datetime.timedelta(microseconds=20000),
        text="Line 1", translations=None,
    ),
    LrcLine(
        start_timedelta=datetime.timedelta(microseconds=280000),
        text="Line 2", translations=None,
    ),
    LrcLine(
        start_timedelta=datetime.timedelta(seconds=2, microseconds=830000),
        text="Line 3", translations=None,
    ),
    LrcLine(
        start_timedelta=datetime.timedelta(seconds=28, microseconds=330000),
        text="Line 4 with TRANSLATION! COOL!!!", translations=["这行有翻译！真他妈的酷！！！"],
    ),
    LrcLine(
        start_timedelta=datetime.timedelta(seconds=203, microseconds=370000),
        text="Sad because secs < 60", translations=["But we can change the rules :)", "我只是来凑数的"],
    ),
    LrcLine(
        start_timedelta=datetime.timedelta(seconds=1713, microseconds=750000),
        text="Line 6", translations=None,
    ),
]

>>> attributes
[
    {'name': 'ti', 'value': 'test_lyric'},
    {'name': 'ar', 'value': '283375'},
    {'name': 'al', 'value': 'TEST ~エラーを回避するための最良の方法~'},
    {'name': 'by', 'value': '283375'}
]

```
