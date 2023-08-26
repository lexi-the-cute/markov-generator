import os
import re
import csv
import json
import random
import logging

try:
    import requests
except ImportError:
    raise ImportError("Failed to import requests, please run `pip3 install requests`")

class DownloadNotes:
    # Required
    input: object = None
    host: str
    api_key: str
    user_id: str

    # Default
    chance_execute: float = 1.0
    limit: int = 100
    session: requests.Session = requests.Session()
    file_path: str = "corpus.csv"
    show_tag: bool = False

    # Non-Configurable
    setup: bool = False
    include_my_renotes: bool = False
    include_replies: bool = False
    include_files: bool = False
    include_nsfw: bool = False
    since_id: str = None
    processed_notes: int = 0
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
        
        if "user_id" in settings:
            self.user_id = settings["user_id"]
            count += 1

        if "limit" in settings:
            self.limit = settings["limit"]

        if "file_path" in settings:
            self.file_path = settings["file_path"]

        if "session" in settings:
            self.session = settings["session"]

        if "show_tag" in settings:
            self.show_tag = settings["show_tag"]

        if "chance_execute" in settings:
            self.chance_execute = settings["chance_execute"]

        if count == 3:
            self.setup = True

    def set_input(self, input: object):
        """
            Set the input used by this module
        """
        
        self.input = input

    def run(self):
        """
            Execute this module as part of a chain of modules
        """

        if not self.setup:
            self.logger.error("Module not configured...")
            return

        # Gives probability of executing module
        if self.chance_execute < random.random():
            self.logger.log(level=self.LESSERDEBUG, msg="Hit random chance of skipping downloading notes...")
            return self.input    # This is a special case, if this was skipped the way other modules are, there would be no data

        self.logger.info("Downloading notes...")

        # Import Existing Notes
        notes: list = []
        if os.path.exists(self.file_path):
            with open(file=self.file_path, mode="r") as f:
                corpus: csv.reader = csv.reader(f)

                first_loop: bool = True
                for note_data in corpus:
                    if first_loop:
                        first_loop: bool = False
                        continue

                    self.since_id: str = note_data[0].strip()

                    # Create Operation Tag
                    tag: dict = {
                        "name": "DownloadNotes",
                        "operation": "create",
                        "show": self.show_tag
                    }

                    note: dict = {
                        "text": note_data[1].strip(),
                        "meta": json.loads(note_data[2])
                    }

                    notes.append({
                        "note": [note],  # The list is so versions can be tracked
                        "tags": [tag]
                    })

        # Import New Notes
        new_notes: list = []
        for note in self._update_corpus():
            new_notes.append(note)

        # Combine New and Existing Notes
        notes: list = notes + new_notes

        return notes

    def _has_header(self):
        reader = open(file=self.file_path, mode="r")
        if not reader.readline():
            return False

        return True

    def _get_notes(self):
        base_url: str = f"{self.host}/api/users/notes"

        params: dict = {
            "i": self.api_key,
            "userId": self.user_id,
            "limit": self.limit,
            "includeMyRenotes": self.include_my_renotes,
            "includeReplies": self.include_replies,
            "withFiles": self.include_files,
            "excludeNsfw": not self.include_nsfw,
        }

        if self.since_id is not None:
            params["sinceId"] = self.since_id
        else:
            # To force loading from beginning
            params["sinceId"] = "0"

        return self.session.post(url=base_url, json=params)

    def _update_corpus(self):
        # Setup
        corpus_writer = open(file=self.file_path, mode="a")
        corpus: csv.writer = csv.writer(corpus_writer)
        mentions_pattern: re.Pattern = re.compile(pattern=r"(@)([A-Za-z0-9_]+@[A-Za-z0-9_.]+)\w+")

        if not self._has_header():
            corpus.writerow(["id", "text", "meta"])

        loop: bool = True
        while loop:
            response: requests.Response = self._get_notes()

            status: int = response.status_code
            notes: dict = response.json()

            if status == 429:
                self.logger.error(f"Hit rate limit... returning...")
                return

            if status == 403:
                self.logger.error(f"Downloading notes is unauthorized... returning...")
                return

            if status == 500:
                self.logger.error(f"Hit server with internal error... returning...")
                return

            if status != 200:
                self.logger.warning(f"Status code is {status}...")
                continue

            if len(notes) == 0:
                loop: bool = False

            for note_data in notes:
                self.since_id: str = note_data["id"]

                meta: dict = {
                    "visibility": note_data["visibility"],
                    "is_renote": True if note_data["renoteId"] is not None else False,
                    "is_reply": True if note_data["replyId"] is not None else False,
                    "has_cw": True if note_data["cw"] is not None else False,
                    "has_mentions": True if "mentions" in note_data and len(note_data["mentions"]) > 0 else False,
                    "has_zws": True if "\u200B" in note_data["text"].strip() else False,
                }

                if meta["has_mentions"] == False and re.search(mentions_pattern, note_data["text"].strip()) is not None:
                    meta["has_mentions"] = True

                self.processed_notes += 1
                corpus.writerow([note_data["id"], note_data["text"], json.dumps(meta)])  # Intentionally leaving unstripped here

                # Create Operation Tag
                tag: dict = {
                    "name": "DownloadNotes",
                    "operation": "create",
                    "show": self.show_tag
                }

                note: dict = {
                    "text": note_data["text"].strip(),
                    "meta": meta
                }

                yield {
                    "note": [note],  # The list is so versions can be tracked
                    "tags": [tag]
                }