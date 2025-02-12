import re
from models import Prompt

import re

SWEAR_WORDS = {"duck", "beach"}

def filter_swear_words(text):
    pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, SWEAR_WORDS)) + r')\b', re.IGNORECASE)
    return pattern.sub("[censored]", text)
