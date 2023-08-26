import json
import random
import logging

try:
    import requests
except ImportError:
    raise ImportError("Failed to import requests, please run `pip3 install requests`")

class PostNotes:
    # Required
    input: object = None
    host: str
    api_key: str

    # Default
    chance_execute: float = 1.0
    show_tag: bool = False
    dry_run: bool = True
    hard_skip: bool = False
    content_warning: str = None
    visibility: str = "public"  # public, home, followers, specified, hidden
    session: requests.Session = requests.Session()

    # Non-Configurable
    skipped: bool = False
    setup: bool = False
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

        count: int = 0
        if "host" in settings:
            self.host = settings["host"]
            count += 1
        
        if "api_key" in settings:
            self.api_key = settings["api_key"]
            count += 1

        if "dry_run" in settings:
            self.dry_run = settings["dry_run"]

        if "content_warning" in settings:
            self.content_warning = settings["content_warning"]

        if "visibility" in settings:
            self.visibility = settings["visibility"]

        if "session" in settings:
            self.session = settings["session"]

        if "chance_execute" in settings:
            self.chance_execute = settings["chance_execute"]

        if "hard_skip" in settings:
            self.hard_skip = settings["hard_skip"]

        if "show_tag" in settings:
            self.show_tag = settings["show_tag"]

        if count == 2:
            self.setup = True

    def set_input(self, input: object):
        """
            Set the input used by this module
        """
        
        self.input: object = input

    def run(self):
        """
            Execute this module as part of a chain of modules
        """

        if not self.setup:
            self.logger.error("Module not configured...")
            return

        # Gives probability of executing module
        if self.chance_execute < random.random():
            self.logger.log(level=self.LESSERDEBUG, msg="Hit random chance of skipping posting notes...")

            if self.hard_skip:
                return self.input

            self.skipped: bool = True
        else:
            self.logger.info("Posting notes...")

        if type(self.input) is str:
            return self._post_note(text=self.input)
        
        if type(self.input) is not list:
            return

        tag: dict = {
            "name": "PostNotes",
            "operation": "publish",
            "show": self.show_tag
        }

        notes: list = []
        for note_data in self.input:
            if "note" not in note_data:
                continue

            note: dict = note_data["note"][-1].copy()
            note["tag"] = tag

            if not self.skipped:
                response: requests.Response = self._post_note(text=note["text"])

                # Not JSON Serializable
                # if "meta" in note:
                #     note["meta"]["response"] = response
                # else:
                #     note["meta"] = {"response": response}

            note_data["note"].append(note)
            notes.append(note_data)

            if response is not None and response.status_code == 429:
                self.logger.error(f"Hit rate limit... returning...")
                return

            if response is not None and response.status_code == 403:
                self.logger.error(f"Posting notes is unauthorized... returning...")
                return

            if response is not None and response.status_code == 500:
                self.logger.error(f"Hit server with internal error... returning...")
                return

            if response is not None and response.status_code != 200:
                self.logger.warning(f"Status code is {status}...")

        self.logger.log(level=self.VERBOSE, msg=f"Post Notes Data: `{json.dumps(notes)}`")
        return notes

    def _post_note(self, text: str):
        # Validate text
        if text is None:
            text: str = ""

        if self.dry_run:
            self.logger.log(level=self.VERBOSE, msg=f"Dry run: `{text}`")
            return

        base_url: str = f"{self.host}/api/notes/create"

        params: dict = {
            "i": self.api_key,
            "text": text,
            "visibility": self.visibility
        }

        # Add Content Warning
        if self.content_warning is not None:
            params["cw"] = self.content_warning

        return self.session.post(url=base_url, json=params)