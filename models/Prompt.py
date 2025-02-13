import re
from models import User


class Prompt:
    def __init__(self, text="", webflag=False,imgflag=False, fileflag=False):
        self.prompt_text = text
        self.webflag = webflag
        self.imgflag = imgflag
        self.fileflag = fileflag

    def get_prompt(self):
        return self.prompt_text

    def get_flags(self):
        return self.webflag,self.imgflag,self.fileflag

    def tokenize(self):
        return re.findall(r'\b\w+\b', self.prompt_text.lower())