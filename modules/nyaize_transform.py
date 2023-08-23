import re
# import logging

class NyaizeText:
    # Required
    input: object = None

    # Non-Configurable
    banyanya_pattern: re.Pattern = re.compile(pattern=r"(?<=n)(a)", flags=re.IGNORECASE|re.MULTILINE)  # banyanya
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
            return self._get_nyaized_text(text=self.input)
        
        if type(self.input) is not list:
            return

        notes: list = []
        for note in self.input:
            if "text" not in note:
                continue

            if "meta" not in note:
                continue

            notes.append({
                "text": self._get_nyaized_text(text=note["text"]),
                "meta": note["meta"]
            })

        return notes

    def _get_nyaized_text(self, text: str):
        # Validate text
        if text is None:
            text: str = ""

        text: str = re.sub(pattern=self.banyanya_pattern, repl="ya", string=text)
        text: str = re.sub(pattern=self.mornyan_pattern, repl="yan", string=text)
        text: str = re.sub(pattern=self.everynyan_pattern, repl="nyan", string=text)
        text: str = re.sub(pattern=self.nyansense_pattern, repl="nyan", string=text)

        return text

class RevertNyaizeText:
    # Required
    input: object = None

    # Non-Configurable
    nonsense_pattern: re.Pattern = re.compile(pattern=r"(nyan)(?=[bcdfghjklmnpqrstvwxyz])", flags=re.IGNORECASE|re.MULTILINE)  # nonsense
    everyone_pattern: re.Pattern = re.compile(pattern=r"(?<=every)(nyan)", flags=re.IGNORECASE|re.MULTILINE)  # everyone
    morning_pattern: re.Pattern = re.compile(pattern=r"(?<=morn)(yan)", flags=re.IGNORECASE|re.MULTILINE)  # morning
    banana_pattern: re.Pattern = re.compile(pattern=r"(?<=n)(ya)", flags=re.IGNORECASE|re.MULTILINE)  # banana

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
            return self._get_reverted_nyaized_text(text=self.input)
        
        if type(self.input) is not list:
            return

        notes: list = []
        for note in self.input:
            if "text" not in note:
                continue

            if "meta" not in note:
                continue

            notes.append({
                "text": self._get_reverted_nyaized_text(text=note["text"]),
                "meta": note["meta"]
            })

        return notes

    def _get_reverted_nyaized_text(self, text: str):
        # Validate text
        if text is None:
            text: str = ""

        text: str = re.sub(pattern=self.nonsense_pattern, repl="non", string=text)
        text: str = re.sub(pattern=self.everyone_pattern, repl="one", string=text)
        text: str = re.sub(pattern=self.morning_pattern, repl="ing", string=text)
        text: str = re.sub(pattern=self.banana_pattern, repl="a", string=text)

        return text