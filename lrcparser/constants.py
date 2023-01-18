LRC_REGEX = r"(?P<time>\[(?P<minutes>\d{2}):(?P<seconds>\d{2})\.(?P<milliseconds>\d{2,3})\])(?P<text>.*)"
ATTR_REGEX = r"\[(?P<name>[^\d]+):[\x20]*(?P<value>.+)\]"
TRANSLATION_DIVIDER = " | "
