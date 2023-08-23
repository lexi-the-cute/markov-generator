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
    dry_run: bool = True
    content_warning: str = None
    visibility: str = "followers"
    session: requests.Session = requests.Session()

    # Non-Configurable
    setup: bool = False

    def __init__(self):
        """
            Initialize this module
        """

        pass

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
            logging.error("PostNotes module not configured...")
            return

        if type(self.input) is str:
            return self._post_note(text=self.input)
        
        if type(self.input) is not list:
            return

        notes: list = []
        for note in self.input:
            if "text" not in note:
                continue

            if "meta" not in note:
                continue

            response: requests.Response = self._post_note(text=note["text"])

            notes.append({
                "text": note["text"],
                "meta": note["meta"],
                "response": response
            })

            if response is not None and response.status_code == 429:
                logging.error(f"PostNotes hit rate limit... returning...")
                return

            if response is not None and status == 403:
                logging.error(f"PostNotes is unauthorized... returning...")
                return

            if response is not None and status == 500:
                logging.error(f"PostNotes hit server with internal error... returning...")
                return

            if response is not None and status != 200:
                logging.warning(f"PostNotes status code is {status}...")

        return notes

    def _post_note(self, text: str):
        # Validate text
        if text is None:
            text: str = ""

        if self.dry_run:
            logging.debug(f"PostNotes dry run: {text}")
            return

        base_url: str = f"{self.host}/api/notes/create"

        params: dict = {
            "i": api_key,
            "text": text,
            "visibility": visibility
        }

        # Add Content Warning
        if self.content_warning is not None:
            params["cw"] = self.content_warning

        return self.session.post(url=base_url, json=params)