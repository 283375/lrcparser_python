# Usage

## Quick start

Parse a lyric file with `LrcParser.parse`.

```lrc
[ti:test_lyric]
[al:TEST ~AVOIDING ERRORS~]
[by:283375]
[offset:250]

[00:00.02]Line 1
[00:00.28]Line 2
[00:02.83]Line 3
[00:28.33]Line 4 with translation | translation after the divider
[00:28.33]可惜我更喜欢换行
[00:28.33]你说得对，但是《lrcparser》是由……
[28:33.75]Line 6
```

```py
from lrcparser import LrcParser

with open("example.lrc") as lrc_file:
    parse_result = LrcParser.parse(lrc_file.read(), parse_translations=True)
    offset, lrc_lines, attributes = parse_result.values()
```

> See the API docs for details on `LrcParser.parse()`: [LrcParser.parse](../api/parser.md)
