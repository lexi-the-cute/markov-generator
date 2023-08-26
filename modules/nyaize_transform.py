import re
import random
import logging

class NyaizeText:
    # Required
    input: object = None

    # Default
    chance_execute: float = 1.0
    show_tag: bool = True
    hard_skip: bool = False

    # Non-Configurable
    skipped: bool = False
    snyack_pattern: re.Pattern = re.compile(pattern=r"(?<=n)(a)", flags=re.IGNORECASE|re.MULTILINE)  # snyack
    mornyan_pattern: re.Pattern = re.compile(pattern=r"(?<=morn)(ing)", flags=re.IGNORECASE|re.MULTILINE)  # mornyan
    everynyan_pattern: re.Pattern = re.compile(pattern=r"(?<=every)(one)", flags=re.IGNORECASE|re.MULTILINE)  # everynyan
    nyansense_pattern: re.Pattern = re.compile(pattern=r"(non)(?=[bcdfghjklmnpqrstvwxyz])", flags=re.IGNORECASE|re.MULTILINE)  # nyansense
    logger: logging.Logger = None
    LESSERDEBUG: int = 15
    VERBOSE: int = 5

    def __init__(self):
        """
            Initialize this module
        """

        self.logger: logging.Logger = logging.getLogger(type(self).__name__)

    def set_settings(self, settings: dict):
        """
            Configure the settings for this module
        """

        if "show_tag" in settings:
            self.show_tag = settings["show_tag"]

        if "chance_execute" in settings:
            self.chance_execute = settings["chance_execute"]

        if "hard_skip" in settings:
            self.hard_skip = settings["hard_skip"]

    def set_input(self, input: object):
        """
            Set the input used by this module
        """
        
        self.input: object = input

    def run(self):
        """
            Execute this module as part of a chain of modules
        """

        # Gives probability of executing module
        if self.chance_execute < random.random():
            self.logger.log(level=self.LESSERDEBUG, msg="Hit random chance of skipping nyaizing notes...")

            if self.hard_skip:
                return self.input

            self.skipped: bool = True
        else:
            self.logger.info("Nyaizing notes...")

        if type(self.input) is str:
            return self._get_nyaized_text(text=self.input)
        
        if type(self.input) is not list:
            return

        notes: list = []
        for note_data in self.input:
            if "note" not in note_data:
                continue

            if "tags" not in note_data:
                continue

            note: dict = note_data["note"][-1].copy()

            if "text" not in note:
                continue

            # Create Operation Tag
            tag: dict = {
                "name": "NyaizeText",
                "operation": "modify",
                "show": self.show_tag
            }

            if not self.skipped:
                text: str = self._get_nyaized_text(text=note["text"])

            # If modification did not take effect, then remove tag
            if self.show_tag and note["text"] == text:
                tag["show"] = False

            note["text"] = text.strip()
            note_data["tags"] = note_data["tags"] + [tag] if "tags" in note_data else [tag]

            # Add Note To List
            note_data["note"].append(note)

            notes.append({
                "note": note_data["note"],
                "tags": note_data["tags"]
            })

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
    chance_execute: float = 1.0
    show_tag: bool = False
    hard_skip: bool = False

    # Non-Configurable
    skipped: bool = False
    banana_pattern: re.Pattern = re.compile(pattern=r"(?<=n)(yanya)", flags=re.IGNORECASE|re.MULTILINE)  # banana
    nonsense_pattern: re.Pattern = re.compile(pattern=r"(nyan)(?=[bcdfghjklmnpqrstvwxyz])", flags=re.IGNORECASE|re.MULTILINE)  # nonsense
    everyone_pattern: re.Pattern = re.compile(pattern=r"(?<=every)(nyan)", flags=re.IGNORECASE|re.MULTILINE)  # everyone
    morning_pattern: re.Pattern = re.compile(pattern=r"(?<=morn)(yan)", flags=re.IGNORECASE|re.MULTILINE)  # morning
    snack_pattern: re.Pattern = re.compile(pattern=r"(?<=n)(ya)", flags=re.IGNORECASE|re.MULTILINE)  # snack
    logger: logging.Logger = None

    def __init__(self):
        """
            Initialize this module
        """

        self.logger: logging.Logger = logging.getLogger(type(self).__name__)

    def set_settings(self, settings: dict):
        """
            Configure the settings for this module
        """

        if "show_tag" in settings:
            self.show_tag = settings["show_tag"]

        if "chance_execute" in settings:
            self.chance_execute = settings["chance_execute"]

        if "hard_skip" in settings:
            self.hard_skip = settings["hard_skip"]

    def set_input(self, input: object):
        """
            Set the input used by this module
        """
        
        self.input: object = input

    def run(self):
        """
            Execute this module as part of a chain of modules
        """

        # Gives probability of executing module
        if self.chance_execute < random.random():
            self.logger.log(level=self.LESSERDEBUG, msg="Hit random chance of skipping reverting nyaizing notes...")

            if self.hard_skip:
                return self.input

            self.skipped: bool = True
        else:
            self.logger.info("Revert Nyaizing notes...")

        if type(self.input) is str:
            return self._get_reverted_nyaized_text(text=self.input)
        
        if type(self.input) is not list:
            return

        notes: list = []
        for note_data in self.input:
            if "note" not in note_data:
                continue

            if "tags" not in note_data:
                continue

            note: dict = note_data["note"][-1].copy()

            if "text" not in note:
                continue

            # Create Operation Tag
            tag: dict = {
                "name": "RevertNyaizeText",
                "operation": "modify",
                "show": self.show_tag
            }

            text: str = note["text"]
            if not self.skipped:
                text: str = self._get_reverted_nyaized_text(text=note["text"])

            # If modification did not take effect, then remove tag
            if self.show_tag and note["text"] == text:
                tag["show"] = False

            note["text"] = text.strip()
            note_data["tags"] = note_data["tags"] + [tag] if "tags" in note_data else [tag]

            # Add Note To List
            note_data["note"].append(note)

            notes.append({
                "note": note_data["note"],
                "tags": note_data["tags"]
            })

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