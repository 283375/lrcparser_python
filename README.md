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

```py
import lrcparser

parser = lrcparser.LrcParser()

with open('your.lrc', 'r', encoding='utf-8') as lrcFile:
    parsedData = parser.parse(lrcFile.read())
    lyricLines, attributes = parsedData.values()

>>> lyricLines
[
    LyricLine(text="Line 1", startTimedelta=datetime.timedelta(microseconds=20000), ),
    LyricLine(text="Line 2", startTimedelta=datetime.timedelta(microseconds=280000), ),
    LyricLine(text="Line 3", startTimedelta=datetime.timedelta(seconds=2, microseconds=830000), ),
    LyricLine(text="Line 4 with TRANSLATION! COOL!!!", startTimedelta=datetime.timedelta(seconds=28, microseconds=330000), ),
    LyricLine(text="这行有翻译！真他妈的酷！！！", startTimedelta=datetime.timedelta(seconds=28, microseconds=330000), ),
    LyricLine(text="Sad because secs < 60", startTimedelta=datetime.timedelta(seconds=203, microseconds=370000), ),
    LyricLine(text="But we can change the rules :)", startTimedelta=datetime.timedelta(seconds=203, microseconds=370000), ),
    LyricLine(text="我只是来凑数的", startTimedelta=datetime.timedelta(seconds=203, microseconds=370000), ),
    LyricLine(text="Line 6", startTimedelta=datetime.timedelta(seconds=1713, microseconds=750000), )
]

>>> attributes
[
    {'name': 'ti', 'value': 'test_lyric'},
    {'name': 'ar', 'value': '283375'},
    {'name': 'al', 'value': 'TEST ~エラーを回避するための最良の方法~'},
    {'name': 'by', 'value': '283375'}
]

>>> parsedData
{'lyricLines': LyricLine[...],
 'attributes': [{'name': ..., 'value': ...}, ...]}

```
