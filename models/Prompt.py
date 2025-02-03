import re

class Prompt:
    def __init__(self, text="", webflag=False,imgflag=False):
        self.prompt_text = text
        self.webflag = webflag
        self.imgflag = imgflag

    def get_prompt(self):
        return self.prompt_text

    def get_flags(self):
        return self.webflag,self.imgflag

    def tokenize(self):
        return re.findall(r'\b\w+\b', self.prompt_text.lower())