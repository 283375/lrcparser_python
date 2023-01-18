import re
from datetime import timedelta
from .constants import LRC_REGEX, ATTR_REGEX, TRANSLATION_DIVIDER
from .line import LrcLine

from typing import TypedDict


class LrcParser:
    class ParseResult(TypedDict):
        global_offset: int
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

        :param s: The lyric string, e.g.'[00:01.25]Lyric'.
        :type s: str
        :param parse_translations: Defaults to False, see examples for details
        :type parse_translations: bool, optional
        :param translation_divider: Defaults to TRANSLATION_DIVIDER, see examples for details
        :type translation_divider: str, optional
        :return: A dict contains `global_offset`, `lrc_lines` and `attributes` of the lyric.
        :rtype: dict

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
        ...     'global_offset': 375,
        ...     'lrc_lines': [
        ...         LrcLine(text="Line 1 example", start_timedelta=timedelta(seconds=5, milliseconds=260), ),
        ...         LrcLine(text="Line 2 example | 翻译示例", start_timedelta=timedelta(seconds=7, milliseconds=360), ),
        ...         LrcLine(text="Line 3 divider example /// 分隔符示例", start_timedelta=timedelta(seconds=9, milliseconds=540), )
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
        ...     LrcLine(text="Line 1 example", start_timedelta=timedelta(seconds=5, milliseconds=260)),
        ...     LrcLine(text="Line 2 example", translations=['翻译示例'], start_timedelta=timedelta(seconds=7, milliseconds=360)),
        ...     LrcLine(text="Line 3 divider example /// 分隔符示例", start_timedelta=timedelta(seconds=9, milliseconds=540))
        ... ]
        True

        >>> LrcParser.parse(s, parse_translations=True, translation_divider=' /// ')['lrc_lines'] == [
        ...     LrcLine(text="Line 1 example", start_timedelta=timedelta(seconds=5, milliseconds=260)),
        ...     LrcLine(text="Line 2 example | 翻译示例", start_timedelta=timedelta(seconds=7, milliseconds=360)),
        ...     LrcLine(text="Line 3 divider example", translations=['分隔符示例'], start_timedelta=timedelta(seconds=9, milliseconds=540))
        ... ]
        True

        """
        lines = s.splitlines()
        lrc_lines: list[LrcLine] = []
        attributes = {}
        global_offset = 0

        for line in lines:
            attribute_re_result = re.match(ATTR_REGEX, line)
            lrc_re_result = re.match(LRC_REGEX, line)

            if attribute_re_result:
                attr_name = attribute_re_result["name"].lower()
                attr_value = attribute_re_result["value"]

                if attr_name == "offset":
                    global_offset = int(attr_value)

                attributes[attr_name] = attr_value

            if lrc_re_result:
                # adapt lyrics like [01:02.345678]
                milliseconds = lrc_re_result["milliseconds"]
                microseconds = milliseconds.ljust(6, "0")

                start_timedelta = timedelta(
                    minutes=int(lrc_re_result["minutes"]),
                    seconds=int(lrc_re_result["seconds"]),
                    microseconds=int(microseconds),
                )
                orig_text = lrc_re_result["text"]

                if parse_translations:
                    splited_text = orig_text.split(translation_divider)
                    lrc_lines.append(
                        LrcLine(
                            start_timedelta=start_timedelta,
                            text=splited_text[0],
                            translations=splited_text[1:] or None,
                        )
                    )
                else:
                    lrc_lines.append(
                        LrcLine(
                            start_timedelta=start_timedelta,
                            text=orig_text,
                        )
                    )

        if parse_translations:
            original_texts: dict[timedelta, str] = {}
            translation_texts: dict[timedelta, list[str]] = {}
            combined_lines = cls.combine_translation(lrc_lines)
            for line in combined_lines:
                if line.translations:
                    original_texts[line.start_timedelta] = line.text
                    translation_texts[line.start_timedelta] = line.translations

            for line in lrc_lines.copy():
                if line.start_timedelta in original_texts:
                    if line.text == original_texts[line.start_timedelta]:
                        lrc_lines.append(
                            LrcLine(
                                start_timedelta=line.start_timedelta,
                                text=line.text,
                                translations=translation_texts[line.start_timedelta],
                            )
                        )
                    if line in lrc_lines:
                        lrc_lines.remove(line)

        return {
            "global_offset": global_offset,
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
        ...     LrcLine(start_timedelta=timedelta(seconds=1, milliseconds=589), text='Line 1'),
        ...     LrcLine(start_timedelta=timedelta(seconds=1, milliseconds=589), text='Line 2'),
        ...     LrcLine(start_timedelta=timedelta(seconds=1, milliseconds=589), text='Line 3'),
        ...     LrcLine(start_timedelta=timedelta(seconds=2, milliseconds=589), text='Line 4'),
        ...     LrcLine(start_timedelta=timedelta(seconds=2, milliseconds=589), text='Line 5'),
        ...     LrcLine(start_timedelta=timedelta(seconds=2, milliseconds=589), text='Line 6'),
        ... ]) == [
        ...      [
        ...          LrcLine(start_timedelta=timedelta(seconds=1, milliseconds=589), text='Line 1'),
        ...          LrcLine(start_timedelta=timedelta(seconds=1, milliseconds=589), text='Line 2'),
        ...          LrcLine(start_timedelta=timedelta(seconds=1, milliseconds=589), text='Line 3'),
        ...      ],
        ...      [
        ...          LrcLine(start_timedelta=timedelta(seconds=2, milliseconds=589), text='Line 4'),
        ...          LrcLine(start_timedelta=timedelta(seconds=2, milliseconds=589), text='Line 5'),
        ...          LrcLine(start_timedelta=timedelta(seconds=2, milliseconds=589), text='Line 6'),
        ...      ]
        ...  ]
        True

        """

        timedelta_dict: dict[timedelta, list[LrcLine]] = {}

        for lrc_line in lrc_lines:
            if timedelta_dict.get(lrc_line.start_timedelta) is None:
                timedelta_dict[lrc_line.start_timedelta] = [lrc_line]
            else:
                timedelta_dict[lrc_line.start_timedelta].append(lrc_line)

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
        ...     LrcLine(start_timedelta=timedelta(seconds=1, milliseconds=589), text='Line 1'),
        ...     LrcLine(start_timedelta=timedelta(seconds=1, milliseconds=589), text='翻译 1'),
        ...     LrcLine(start_timedelta=timedelta(seconds=2, milliseconds=589), text='Line 2'),
        ...     LrcLine(start_timedelta=timedelta(seconds=2, milliseconds=589), text='翻译 2'),
        ...     LrcLine(start_timedelta=timedelta(seconds=2, milliseconds=589), text='これは2行目です'),
        ... ]) == [
        ...     LrcLine(
        ...         start_timedelta=timedelta(seconds=1, milliseconds=589),
        ...         text='Line 1',
        ...         translations=['翻译 1']),
        ...     LrcLine(
        ...         start_timedelta=timedelta(seconds=2,milliseconds=589),
        ...         text='Line 2',
        ...         translations=['翻译 2', 'これは2行目です'])
        ... ]
        True

        """
        duplicates = cls.find_duplicate(lrc_lines)
        if len(duplicates) == 0:
            return lrc_lines

        combined_lrcs = []
        for duplicate in duplicates:
            main_lrc_line = duplicate[0]
            lrc_line = LrcLine(
                start_timedelta=main_lrc_line.start_timedelta,
                text=main_lrc_line.text,
                translations=[lrc_line.text for lrc_line in duplicate[1:]],
            )
            combined_lrcs.append(lrc_line)

        return combined_lrcs
