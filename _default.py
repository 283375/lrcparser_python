LRCPARSER_LRC_REGEX = r"(?P<time>\[(?P<minutes>\d{2}):(?P<seconds>\d{2})\.(?P<milliseconds>\d{2,3})\])(?P<text>.*)"
LRCPARSER_ATTR_REGEX = r"\[(?P<name>[^\d]+):(?P<attr>.+)\]"
LRCPARSER_DEFAULT_TRANSLATION_DIVIDER = " | "
