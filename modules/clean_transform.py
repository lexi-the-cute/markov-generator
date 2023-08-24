import re
import logging

class CleanText:
    # Required
    input: object = None

    # Default
    show_tag: bool = False

    # Non-Configurable
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

    def set_input(self, input: object):
        """
            Set the input used by this module
        """
        
        self.input: object = input

    def run(self):
        """
            Execute this module as part of a chain of modules
        """

        self.logger.info("Cleaning notes...")

        if type(self.input) is str:
            return self._get_cleaned_text(text=self.input)
        
        if type(self.input) is not list:
            return

        notes: list = []
        for note in self.input:
            if "text" not in note:
                continue

            # Create Operation Tag
            tag: dict = {
                "name": "CleanText",
                "operation": "modify",
                "show": self.show_tag
            }

            text: str = self._get_cleaned_text(text=note["text"])

            # If modification did not take effect, then remove tag
            if self.show_tag and note["text"] == text:
                tag["show"] = False

            note["text"] = text
            note["tags"] = note["tags"] + [tag] if "tags" in note else [tag]
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