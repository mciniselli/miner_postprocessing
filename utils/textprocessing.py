import re

class TextProcessing:
    def __init__(self, text):
        self.text=text

    def remove_comments(self):

        text=self.text

        self.text = re.sub("(?s)<comment.*?</comment>", "", text);

    def remove_tags(self):

        text=self.text

        res = (re.sub(r'\<[^>]*\>', '|_|', text))

        res = res.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;",
                                                                    "&")  # these characters are replaced with HTML version => we replace them all
        while "|_||_|" in res:
            res=res.replace("|_||_|", "|_|")


        while "  " in res:
            res = res.replace("  ", " ")

        self.text=res
