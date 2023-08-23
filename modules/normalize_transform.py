import re
# import logging

class NormalizeText:
    # Required
    input: object = None

    # Default
    names: list[str] = [
        "becky",
        "prim",
        "mastodon",
        "alexis",
        "mia",
        "firefish",
        "iceshrimp",
        "misskey",
        "akkoma",
        "pleroma",
        "pixelfed",
        "hometown",
        "calckey",
        "foundkey",
        "lemmy"
    ]

    # Non-Configurable
    capitalize_i_pattern: re.Pattern = re.compile(pattern=r'(\s)i(\W)', flags=re.IGNORECASE|re.MULTILINE)
    capitalize_sentence_pattern: re.Pattern = re.compile(pattern=r'[.!?]([\s\n]*)(\w)', flags=re.IGNORECASE|re.MULTILINE)

    def __init__(self):
        """
            Initialize this module
        """

        pass

    def set_settings(self, settings: dict):
        """
            Configure the settings for this module
        """

        if "names" in settings:
            self.names = settings["names"]

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
            return self._get_normalized_text(text=self.input)
        
        if type(self.input) is not list:
            return

        notes: list = []
        for note in self.input:
            if "text" not in note:
                continue

            note["text"] = self._get_normalized_text(text=note["text"])
            notes.append(note)

        return notes

    def _get_normalized_text(self, text: str):
        # Validate text
        if text is None:
            text: str = ""

        text: str = text.capitalize()
        text: str = text.replace("Hmmmmmmm", "hmmmmmmm...")
        text: str = text.replace(" uwu ", " UwU ")
        text: str = text.replace(" owo ", " OwO ")
        text: str = re.sub(pattern=self.capitalize_i_pattern, repl=r'\1I\2', string=text)
        text: str = re.sub(pattern=self.capitalize_sentence_pattern, repl=lambda m: f".{m.group(1)}{m.group(2).upper()}", string=text)
        
        for name in self.names:
            text: str = text.replace(f" {name.lower()}", f" {name.capitalize()}")

        return text