from copy import deepcopy
from .constants import (
    LRC_LINE,
    LRC_WORD,
    LRC_ATTRIBUTE,
    TRANSLATION_DIVIDER,
)
from .line import LrcLine
from .time import LrcTime
from .text import LrcTextSegment, LrcText

from typing import TypedDict


class LrcParser:
    class ParseResult(TypedDict):
        offset: int
        lrc_lines: list[LrcLine]
        attributes: dict[str, str]

    @classmethod
    def parse(
        cls,
        s: str,
        parse_translations: bool = False,
        translation_divider: str = TRANSLATION_DIVIDER,
    ) -> ParseResult:
        """
        Parse lyrics from a string.

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

        """
        lines = s.splitlines()
        lrc_lines: list[LrcLine] = []
        attributes = {}
        offset = 0

        def __get_lrc_text_from_content(content: str, time: LrcTime):
            text = LrcText()
            if word_match := LRC_WORD.findall(content):
                for _time, _text in word_match:
                    text.append(LrcTextSegment(LrcTime(_time), _text))
            else:
                text.append(LrcTextSegment(time, content))
            return text

        for line in lines:
            if attribute_match := LRC_ATTRIBUTE.match(line):
                attr_name = attribute_match["name"].lower()
                attr_value = attribute_match["value"]

                if attr_name == "offset":
                    offset = int(attr_value)

                attributes[attr_name] = attr_value

            if lrc_line_match := LRC_LINE.match(line):
                start_time = [LrcTime(lrc_line_match["time"])]
                content = lrc_line_match["content"]

                # for lyrics like `[01:02.03][02:03.04][03:07.75]Same lyrics`
                while extra_match := LRC_LINE.match(content):
                    start_time.append(LrcTime(extra_match["time"]))
                    content = extra_match["content"]

                for time in start_time:
                    text = LrcText()
                    translations = []

                    if parse_translations:
                        splited_content = content.split(translation_divider)

                        for i, content in enumerate(splited_content):
                            _list = __get_lrc_text_from_content(content, time)
                            if i == 0:
                                text = _list
                            else:
                                translations.append(_list)

                    else:
                        text = __get_lrc_text_from_content(content, time)

                    lrc_lines.append(
                        LrcLine(
                            start_time=time,
                            text=text,
                            translations=translations or None,
                        )
                    )

        if parse_translations:
            duplicate_lines = cls.find_duplicate(lrc_lines)
            combined_lines = cls.combine_translation(lrc_lines)

            if combined_lines:
                [lrc_lines.remove(line) for group in duplicate_lines for line in group]
                lrc_lines += combined_lines

        return {
            "offset": offset,
            "lrc_lines": sorted(lrc_lines),
            "attributes": attributes,
        }

    @classmethod
    def find_duplicate(cls, lrc_lines: list[LrcLine]) -> list[list[LrcLine]]:
        """
        find_duplicate finds duplicate lyrics.

        :param lrc_lines: A list of LyricLine.
        :type lrc_lines: list
        :return: A list of duplicate groups, see example for details.
        :rtype: list

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

        """

        timedelta_dict: dict[LrcTime, list[LrcLine]] = {}

        for lrc_line in lrc_lines:
            if timedelta_dict.get(lrc_line.start_time) is None:
                timedelta_dict[lrc_line.start_time] = [lrc_line]
            else:
                timedelta_dict[lrc_line.start_time].append(lrc_line)

        timedelta_dict = dict(filter(lambda x: len(x[1]) > 1, timedelta_dict.items()))
        return list(dict(sorted(timedelta_dict.items(), key=lambda i: i[0])).values())

    @classmethod
    def combine_translation(cls, lrc_lines: list[LrcLine]) -> list[LrcLine]:
        """
        combine_translation analyzes the translation of the lyric.

        :param lrc_lines: A list of LyricLine.
        :type lrc_lines: list
        :return: Processed list of LyricLine, see example for details.
        :rtype: list

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

        """
        duplicates = cls.find_duplicate(lrc_lines)
        if len(duplicates) == 0:
            return []

        combined_lrcs = []
        for duplicate in duplicates:
            main_lrc_line = duplicate[0]

            if main_lrc_line.translations:
                translations = deepcopy(main_lrc_line.translations)
                translations.extend([lrc_line.text for lrc_line in duplicate[1:]])
            else:
                translations = [lrc_line.text for lrc_line in duplicate[1:]]

            lrc_line = LrcLine(
                start_time=main_lrc_line.start_time,
                text=main_lrc_line.text,
                translations=translations,
            )
            combined_lrcs.append(lrc_line)

        return combined_lrcs
