"""Character-level scanner for LRC lines.

An explicit state machine (TEXT -> BRACKET / ANGLE) replacing the previous
regex-based scanning, so that loose real-world formats ([1:02], [00:12]
without milliseconds, single-digit fields) and malformed input
(unterminated brackets) all have well-defined behavior.

Timestamps are returned as ``(minutes, seconds, microseconds)`` tuples with
raw, non-normalized values (e.g. seconds > 59); :class:`lrcparser.LrcTime`
is responsible for normalization.
"""

from __future__ import annotations

from typing import NamedTuple

MAX_MS_DIGITS = 6


class LrcLineScan(NamedTuple):
    """Result of scanning one LRC line."""

    timestamps: tuple[tuple[int, int, int], ...]
    attributes: tuple[tuple[str, str], ...]
    content: str


def _is_digit(ch: str) -> bool:
    return ch.isascii() and ch.isdigit()


def _is_digits(text: str, min_len: int, max_len: int) -> bool:
    return min_len <= len(text) <= max_len and text.isascii() and text.isdigit()


def _parse_timestamp_at(
    text: str, start: int
) -> tuple[tuple[int, int, int], int] | None:
    """Try to parse ``mm:ss(.ms)`` from ``start``; return it with the end index."""
    i = start
    while i < len(text) and _is_digit(text[i]):
        i += 1
    minutes_str = text[start:i]
    if not _is_digits(minutes_str, 1, 3) or i >= len(text) or text[i] != ":":
        return None
    i += 1
    seconds_start = i
    while i < len(text) and _is_digit(text[i]):
        i += 1
    seconds_str = text[seconds_start:i]
    if not _is_digits(seconds_str, 1, 2):
        return None
    microseconds = 0
    if i < len(text) and text[i] == ".":
        i += 1
        ms_start = i
        while i < len(text) and _is_digit(text[i]):
            i += 1
        ms_str = text[ms_start:i]
        if not _is_digits(ms_str, 1, MAX_MS_DIGITS):
            return None
        microseconds = int(ms_str.ljust(MAX_MS_DIGITS, "0"))
    return (int(minutes_str), int(seconds_str), microseconds), i


def parse_timestamp(text: str) -> tuple[int, int, int] | None:
    """Parse a whole tag body as a timestamp.

    >>> parse_timestamp("00:12")
    (0, 12, 0)
    >>> parse_timestamp("1:02.5")
    (1, 2, 500000)
    >>> parse_timestamp("ti: test") is None
    True

    """
    minutes_str, sep, rest = text.strip().partition(":")
    if not sep or not _is_digits(minutes_str, 1, 3):
        return None
    seconds_str, dot, ms_str = rest.partition(".")
    if not _is_digits(seconds_str, 1, 2):
        return None
    if dot:
        if not _is_digits(ms_str, 1, MAX_MS_DIGITS):
            return None
        microseconds = int(ms_str.ljust(MAX_MS_DIGITS, "0"))
    else:
        microseconds = 0
    return (int(minutes_str), int(seconds_str), microseconds)


def find_timestamp(text: str) -> tuple[int, int, int] | None:
    """Find the first timestamp anywhere in ``text`` (search semantics).

    >>> find_timestamp("[00:03.750]")
    (0, 3, 750000)
    >>> find_timestamp("no timestamp here") is None
    True

    """
    for start, ch in enumerate(text):
        if _is_digit(ch):
            found = _parse_timestamp_at(text, start)
            if found is not None:
                return found[0]
    return None


def scan_line(line: str) -> LrcLineScan:
    """Scan one LRC line into leading timestamps, attributes and content."""
    if "[" not in line:
        # 快速通道：绝大多数行到这里就结束了
        return LrcLineScan((), (), line.lstrip("\ufeff"))
    line = line.lstrip("\ufeff")
    timestamps: list[tuple[int, int, int]] = []
    attributes: list[tuple[str, str]] = []
    i, length = 0, len(line)
    # 状态 BRACKET：吃掉行首连续的 [...] tag
    while i < length and line[i] == "[":
        end = line.find("]", i + 1)
        if end == -1:
            # 未闭合的 [：整体按字面内容处理
            break
        tag = line[i + 1 : end]
        timestamp = parse_timestamp(tag)
        if timestamp is not None:
            timestamps.append(timestamp)
        else:
            # 属性 tag：name: value；空值视为畸形，忽略
            name, sep, value = tag.partition(":")
            if sep and value.strip():
                attributes.append((name.strip(), value.strip()))
        i = end + 1
    # 状态 TEXT：剩下的部分是歌词内容
    return LrcLineScan(tuple(timestamps), tuple(attributes), line[i:])


def scan_word_segments(content: str) -> list[tuple[tuple[int, int, int] | None, str]]:
    """Split lyric content on ``<mm:ss.ms>`` word-timestamp tags.

    Returns ``(timestamp, text)`` pairs; text outside any tag gets a
    ``None`` timestamp (the caller attaches the line start time to it),
    and unterminated ``<`` is kept as literal text.

    >>> scan_word_segments("<00:01.00>a <00:02.00>b")
    [((0, 1, 0), 'a '), ((0, 2, 0), 'b')]
    >>> scan_word_segments("plain text")
    [(None, 'plain text')]

    """
    segments: list[tuple[tuple[int, int, int] | None, str]] = []
    if "<" not in content:
        # 快速通道：没有逐字时间戳的行占大多数
        return [(None, content)] if content else []
    buffer: list[str] = []
    i, length = 0, len(content)
    while i < length:
        # 状态 ANGLE：遇 < 尝试读一个 word 时间戳 tag
        if content[i] == "<":
            end = content.find(">", i + 1)
            if (
                end != -1
                and (timestamp := parse_timestamp(content[i + 1 : end])) is not None
            ):
                if buffer:
                    segments.append((None, "".join(buffer)))
                    buffer = []
                next_tag = content.find("<", end + 1)
                text_end = length if next_tag == -1 else next_tag
                segments.append((timestamp, content[end + 1 : text_end]))
                i = text_end
                continue
        buffer.append(content[i])
        i += 1
    if buffer:
        segments.append((None, "".join(buffer)))
    return segments
