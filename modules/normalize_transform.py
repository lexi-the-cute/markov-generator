import re
import random
import logging

class NormalizeText:
    # Required
    input: object = None

    # Default
    should_recase_sentence: bool = True
    chance_execute: float = 1.0
    show_tag: bool = False
    hard_skip: bool = False
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
    skipped: bool = False
    capitalize_i_pattern: re.Pattern = re.compile(pattern=r'(\s)i(\W)', flags=re.IGNORECASE|re.MULTILINE)
    capitalize_sentence_pattern: re.Pattern = re.compile(pattern=r'[.!?]([\s\n]*)(\w)', flags=re.IGNORECASE|re.MULTILINE)
    ending_punctuation_pattern: re.Pattern = re.compile(pattern=r'\s([,.?!;:\-)\]>]+)', flags=re.MULTILINE)
    starting_punctuation_pattern: re.Pattern = re.compile(pattern=r'([:\-(\[<]+)\s', flags=re.MULTILINE)
    emoji_pattern: re.Pattern = re.compile(pattern=r'(:)([a-z_\-]+)(:)', flags=re.IGNORECASE|re.MULTILINE)
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

        if "names" in settings:
            self.names = settings["names"]

        if "show_tag" in settings:
            self.show_tag = settings["show_tag"]

        if "chance_execute" in settings:
            self.chance_execute = settings["chance_execute"]

        if "should_recase_sentence" in settings:
            self.should_recase_sentence = settings["should_recase_sentence"]

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
            self.logger.log(level=self.LESSERDEBUG, msg="Hit random chance of skipping normalizing notes...")

            if self.hard_skip:
                return self.input

            self.skipped: bool = True
        else:
            self.logger.info("Normalizing notes...")

        if type(self.input) is str:
            return self._get_normalized_text(text=self.input)
        
        if type(self.input) is not list:
            return

        notes: list = []
        for note_data in self.input:
            if "note" not in note_data:
                continue

            note: dict = note_data["note"][-1].copy()

            if "text" not in note:
                continue

            # Create Operation Tag
            tag: dict = {
                "name": "NormalizeText",
                "operation": "modify",
                "show": self.show_tag
            }

            text: str = note["text"]
            if not self.skipped:
                text: str = self._get_normalized_text(text=note["text"])

            # If modification did not take effect, then remove tag
            if self.show_tag and note["text"] == text:
                tag["show"] = False

            note["text"] = text.strip()
            note["tag"] = tag

            # Add Note To List
            note_data["note"].append(note)

            notes.append({
                "note": note_data["note"]
            })

        return notes

    def _get_normalized_text(self, text: str):
        # Validate text
        if text is None:
            text: str = ""

        # Destroys old capitalization, not always desired
        if self.should_recase_sentence:
            text: str = text.capitalize()
        
        text: str = " ".join(text.split())  # Remove extra whitespace
        text: str = text.replace("Hmmmmmmm", "hmmmmmmm...")
        text: str = text.replace(" uwu ", " UwU ")
        text: str = text.replace(" owo ", " OwO ")
        text: str = text.replace(" ii ", " II ")
        text: str = text.replace(" iii ", " III ")
        text: str = re.sub(pattern=self.starting_punctuation_pattern, repl=r'\1', string=text)
        text: str = re.sub(pattern=self.ending_punctuation_pattern, repl=r'\1', string=text)
        text: str = re.sub(pattern=self.capitalize_i_pattern, repl=r'\1I\2', string=text)
        text: str = re.sub(pattern=self.capitalize_sentence_pattern, repl=lambda m: f".{m.group(1)}{m.group(2).upper()}", string=text)
        text: str = re.sub(pattern=self.emoji_pattern, repl=r' \1\2\3 ', string=text)

        for name in self.names:
            text: str = text.replace(f" {name.lower()}", f" {name.capitalize()}")

        return text.strip()