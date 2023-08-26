import re
import random
import logging

class AddHashtags:
    # Required
    input: object = None

    # Default
    chance_execute: float = 1.0
    show_tag: bool = False

    # Non-Configurable
    skipped: bool = False
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
            self.logger.log(level=self.LESSERDEBUG, msg="Hit random chance of skipping adding hashtags to notes...")
            self.skipped: bool = True
        else:
            self.logger.info("Adding hashtags to notes...")

        # Create Operation Tag
        tag: dict = {
            "name": "AddHashtags",
            "operation": "modify",
            "show": self.show_tag
        }

        if type(self.input) is str:
            return self._get_tagged_text(text=self.input, tags=[tag])
        
        if type(self.input) is not list:
            return

        notes: list = []
        for note_data in self.input:
            if "note" not in note_data:
                continue

            if "tags" not in note_data:
                note_data["tags"] = []

            note: dict = note_data["note"][-1].copy()

            if "text" not in note:
                continue

            # We only want to add our tag if we add other tags
            modifies_text: bool = False
            for note_tag in note_data["tags"]:
                if "show" in note_tag and note_tag["show"] == True:
                    modifies_text: bool = True

            tag["show"] = self.show_tag
            if tag["show"] and not modifies_text:
                tag["show"] = False

            note_data["tags"] = note_data["tags"] + [tag] if "tags" in note_data else [tag]

            if not self.skipped:
                note["text"] = self._get_tagged_text(text=note["text"], tags=note_data["tags"]).strip()

            # Add Note To List
            note_data["note"].append(note)

            notes.append(note_data)

        return notes

    def _get_tagged_text(self, text: str, tags: list):
        # Validate text
        if text is None:
            text: str = ""

        if tags is None:
            tags: list = []

        for tag in tags:
            if "show" in tag and tag["show"] == True:
                text = text.strip() + f" #{tag['name']}"

        # self.logger.log(level=self.VERBOSE, msg=f"Text: `{text}`, Tags: `{tags}`")

        return text