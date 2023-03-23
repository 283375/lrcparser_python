from .constants import TRANSLATION_DIVIDER
from .line import LrcLine

from typing import List, Dict, Protocol, Literal, Any, Optional


class SupportsWrite(Protocol):
    def write(self, s: str) -> Any:
        ...


class LrcFile:
    def __init__(
        self,
        lrc_lines: List[LrcLine],
        attributes: Optional[Dict[str, str]] = None,
        offset: Optional[int] = None,
    ):
        if attributes is None:
            attributes = {}
        self.lrc_lines = lrc_lines
        self.attributes = attributes

        if offset is None:
            for key in attributes.keys():
                if key.lower() == "offset":
                    self.offset = int(attributes[key])
        else:
            self.offset = offset or 0

    def to_str(
        self,
        ms_digits: Literal[2, 3] = 2,
        translations: bool = True,
        translation_divider: str = TRANSLATION_DIVIDER,
    ):
        lrc_lines = sorted(self.lrc_lines)

        return "{}\n{}".format(
            "\n".join(f"[{key}:{value}]" for key, value in self.attributes.items()),
            "\n".join(
                line.to_str(
                    ms_digits=ms_digits,
                    translations=translations,
                    translation_divider=translation_divider,
                )
                for line in lrc_lines
            ),
        )

    def write_to(self, fp: SupportsWrite):
        pass
