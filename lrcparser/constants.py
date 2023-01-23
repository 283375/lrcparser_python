import re

LRC_TIMESTAMP = re.compile(r"(?P<min>\d{2}):(?P<sec>\d{2}).(?P<ms>\d{2,6})")
LRC_LINE = re.compile(r"(?P<time>\[\d{2}:\d{2}\.\d{2,6}\])(?P<content>.*)")
LRC_WORD = re.compile(r"(?P<time><\d{2}:\d{2}\.\d{2,6}>)(?P<content>.*?)(?=<|\n|$){1}")
LRC_ATTRIBUTE = re.compile(r"\[(?P<name>[^\d]+):[\x20]*(?P<value>.+)\]")

MS_DIGITS = 2
TRANSLATION_DIVIDER = " | "
