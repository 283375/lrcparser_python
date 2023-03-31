# 使用

## 快速上手

使用 `LrcParser.parse` 解析歌词文件。

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
from lrcparser import LrcParser

with open("example.lrc") as lrc_rs:
    parse_result = LrcParser.parse(lrc_rs.read(), parse_translations=True)
    offset, lrc_lines, attributes = parse_result.values()
```

> 有关 LrcParser.parse() 的详细使用说明，参见 API 文档：[LrcParser.parse](/api/parser)
