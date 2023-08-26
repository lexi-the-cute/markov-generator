import re
import random
import logging

class CleanText:
    # Required
    input: object = None

    # Default
    chance_execute: float = 1.0
    show_tag: bool = False
    hard_skip: bool = False

    # Non-Configurable
    skipped: bool = False
    markdown_link_pattern: re.Pattern = re.compile(pattern=r"\[.*\]\(http.+\)", flags=re.IGNORECASE|re.MULTILINE)
    url_pattern: re.Pattern = re.compile(pattern=r"http\S+", flags=re.IGNORECASE|re.MULTILINE)
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
            self.logger.log(level=self.LESSERDEBUG, msg="Hit random chance of skipping cleaning notes...")

            if self.hard_skip:
                return self.input

            self.skipped: bool = True
        else:
            self.logger.info("Cleaning notes...")

        if type(self.input) is str:
            return self._get_cleaned_text(text=self.input)
        
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
                "name": "CleanText",
                "operation": "modify",
                "show": self.show_tag
            }

            text: str = note["text"]
            if not self.skipped:
                text: str = self._get_cleaned_text(text=note["text"])

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