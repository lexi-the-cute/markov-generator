# import re
import logging

class GenerateMarkov:
    # Required
    input: object = None

    # Default
    show_tag: bool = True

    # Non-Configurable
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

    def set_input(self, input: object):
        """
            Set the input used by this module
        """
        
        self.input: object = input

    def run(self):
        """
            Execute this module as part of a chain of modules
        """

        self.logger.info("Markovifying notes...")

        if type(self.input) is str:
            return self._get_markov_text(text=self.input)
        
        if type(self.input) is not list:
            return

        notes: list = []
        for note in self.input:
            if "text" not in note:
                continue

            # Create Operation Tag
            tag: dict = {
                "name": "GenerateMarkov",
                "operation": "create",
                "show": self.show_tag
            }

            text: str = self._get_markov_text(text=note["text"])

            # If modification did not take effect, then remove tag
            if self.show_tag and note["text"] == text:
                tag["show"] = False

            note["text"] = text
            note["tags"] = note["tags"] + [tag] if "tags" in note else [tag]
            notes.append(note)

        return notes

    def _get_markov_text(self, text: str):
        # Validate text
        if text is None:
            text: str = ""

        # ...

        return text