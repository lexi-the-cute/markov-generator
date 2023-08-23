import re
# import logging

class CleanText:
    # Required
    input: object = None

    # Non-Configurable
    markdown_link_pattern: re.Pattern = re.compile(pattern=r"\[.*\]\(http.+\)", flags=re.IGNORECASE|re.MULTILINE)
    url_pattern: re.Pattern = re.compile(pattern=r"http\S+", flags=re.IGNORECASE|re.MULTILINE)

    def __init__(self):
        """
            Initialize this module
        """

        pass

    def set_settings(self, settings: dict):
        """
            Configure the settings for this module
        """

        pass

    def set_input(self, input: object):
        """
            Set the input used by this module
        """
        
        self.input: object = input

    def run(self):
        """
            Execute this module as part of a chain of modules
        """

        if type(self.input) is str:
            return self._get_cleaned_text(text=self.input)
        
        if type(self.input) is not list:
            return

        notes: list = []
        for note in self.input:
            if "text" not in note:
                continue

            note["text"] = self._get_cleaned_text(text=note["text"])
            notes.append(note)

        return notes

    def _get_cleaned_text(self, text: str):
        # Validate text
        if text is None:
            text: str = ""

        text: str = text.strip()
        text: str = re.sub(pattern=self.markdown_link_pattern, repl='', string=text)
        text: str = re.sub(pattern=self.url_pattern, repl='', string=text)
        text: str = text.replace("UwU UwU", "UwU")
        text: str = text.replace("* * ", "")

        return text