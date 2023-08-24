import re
# import logging

class AddHashtags:
    # Required
    input: object = None

    # Default
    show_tag: bool = False

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
        for note in self.input:
            if "text" not in note:
                continue

            if "tags" not in note:
                note["tags"] = []

            note["tags"] = note["tags"] + [tag] if "tags" in note else tag
            note["text"] = self._get_tagged_text(text=note["text"], tags=note["tags"])
            notes.append(note)

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

        # print(f"Text: `{text}`, Tags: `{tags}`")

        return text