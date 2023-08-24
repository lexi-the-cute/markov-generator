import re
# import logging

class NyaizeText:
    # Required
    input: object = None

    # Default
    show_tag: bool = True

    # Non-Configurable
    snyack_pattern: re.Pattern = re.compile(pattern=r"(?<=n)(a)", flags=re.IGNORECASE|re.MULTILINE)  # snyack
    mornyan_pattern: re.Pattern = re.compile(pattern=r"(?<=morn)(ing)", flags=re.IGNORECASE|re.MULTILINE)  # mornyan
    everynyan_pattern: re.Pattern = re.compile(pattern=r"(?<=every)(one)", flags=re.IGNORECASE|re.MULTILINE)  # everynyan
    nyansense_pattern: re.Pattern = re.compile(pattern=r"(non)(?=[bcdfghjklmnpqrstvwxyz])", flags=re.IGNORECASE|re.MULTILINE)  # nyansense

    def __init__(self):
        """
            Initialize this module
        """

        pass

    def set_settings(self, settings: dict):
        """
            Configure the settings for this module
        """

        if "show_tag" in settings:
            self.show_tag = settings["show_tag"]

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
            return self._get_nyaized_text(text=self.input)
        
        if type(self.input) is not list:
            return

        notes: list = []
        for note in self.input:
            if "text" not in note:
                continue

            # Create Operation Tag
            tag: dict = {
                "name": "NyaizeText",
                "operation": "modify",
                "show": self.show_tag
            }

            note["text"] = self._get_nyaized_text(text=note["text"])
            note["tags"] = note["tags"] + [tag] if "tags" in note else tag
            notes.append(note)

        return notes

    def _get_nyaized_text(self, text: str):
        # Validate text
        if text is None:
            text: str = ""

        text: str = re.sub(pattern=self.snyack_pattern, repl="ya", string=text)
        text: str = re.sub(pattern=self.mornyan_pattern, repl="yan", string=text)
        text: str = re.sub(pattern=self.everynyan_pattern, repl="nyan", string=text)
        text: str = re.sub(pattern=self.nyansense_pattern, repl="nyan", string=text)

        return text

class RevertNyaizeText:
    # Required
    input: object = None

    # Default
    show_tag: bool = False

    # Non-Configurable
    banana_pattern: re.Pattern = re.compile(pattern=r"(?<=n)(yanya)", flags=re.IGNORECASE|re.MULTILINE)  # banana
    nonsense_pattern: re.Pattern = re.compile(pattern=r"(nyan)(?=[bcdfghjklmnpqrstvwxyz])", flags=re.IGNORECASE|re.MULTILINE)  # nonsense
    everyone_pattern: re.Pattern = re.compile(pattern=r"(?<=every)(nyan)", flags=re.IGNORECASE|re.MULTILINE)  # everyone
    morning_pattern: re.Pattern = re.compile(pattern=r"(?<=morn)(yan)", flags=re.IGNORECASE|re.MULTILINE)  # morning
    snack_pattern: re.Pattern = re.compile(pattern=r"(?<=n)(ya)", flags=re.IGNORECASE|re.MULTILINE)  # snack

    def __init__(self):
        """
            Initialize this module
        """

        pass

    def set_settings(self, settings: dict):
        """
            Configure the settings for this module
        """

        if "show_tag" in settings:
            self.show_tag = settings["show_tag"]

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
            return self._get_reverted_nyaized_text(text=self.input)
        
        if type(self.input) is not list:
            return

        notes: list = []
        for note in self.input:
            if "text" not in note:
                continue

            # Create Operation Tag
            tag: dict = {
                "name": "RevertNyaizeText",
                "operation": "modify",
                "show": self.show_tag
            }

            note["text"] = self._get_reverted_nyaized_text(text=note["text"])
            note["tags"] = note["tags"] + [tag] if "tags" in note else tag
            notes.append(note)

        return notes

    def _get_reverted_nyaized_text(self, text: str):
        # Validate text
        if text is None:
            text: str = ""

        text: str = re.sub(pattern=self.banana_pattern, repl="ana", string=text)
        text: str = re.sub(pattern=self.nonsense_pattern, repl="non", string=text)
        text: str = re.sub(pattern=self.everyone_pattern, repl="one", string=text)
        text: str = re.sub(pattern=self.morning_pattern, repl="ing", string=text)
        text: str = re.sub(pattern=self.snack_pattern, repl="a", string=text)

        return text