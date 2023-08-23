import os
import re
import csv
import json
import logging

try:
    import requests
except ImportError:
    raise ImportError("Failed to import requests, please run `pip3 install requests`")

class DownloadPosts:
    # Required
    host: str
    api_key: str
    user_id: str

    # Default
    limit: int = 100
    session: requests.Session = requests.Session()
    file_path: str = "corpus.csv"
    tracker_file_path: str = "latest_id.txt"

    # Non-Configurable
    setup: bool = False
    include_my_renotes: bool = False
    include_replies: bool = False
    until_id: str = None
    processed_notes: int = 0

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
        
        if "user_id" in settings:
            self.user_id = settings["user_id"]
            count += 1

        if "limit" in settings:
            self.limit = settings["limit"]

        if "file_path" in settings:
            self.file_path = settings["file_path"]

        if "session" in settings:
            self.session = settings["session"]

        if count == 3:
            self.setup = True

    def set_input(self, input: object):
        """
            This operation is not implemented on this module
        """
        
        pass

    def run(self):
        """
            Execute this module as part of a chain of modules
        """

        if not self.setup:
            logging.error("DownloadPosts module not configured...")
            return

        # Get Saved Latest ID If Exists
        if os.path.exists(self.tracker_file_path):
            with open(file=tracker_file_path, mode="r") as f:
                self.until_id: str = f.read().strip()

        return self._update_corpus()

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
            "includeReplies": self.include_replies
        }

        if self.until_id is not None:
            params["untilId"] = self.until_id

        return self.session.post(url=base_url, json=params)

    def _update_corpus(self):
        # Setup
        corpus_writer = open(file=self.file_path, mode="a")
        corpus: csv.writer = csv.writer(corpus_writer)
        mentions_pattern: re.Pattern = re.compile(pattern=r"(@)([A-Za-z0-9_]+@[A-Za-z0-9_.]+)\w+")

        if not self._has_header():
            corpus.writerow(["text", "meta"])

        loop: bool = True
        while loop:
            response: requests.Response = self._get_notes()

            status: int = response.status_code
            notes: dict = response.json()

            if status != 200:
                logging.warning(f"DownloadPosts status code is {status}...")

            if len(notes) == 0:
                loop: bool = False

            for note in notes:
                self.until_id: str = note["id"]

                meta: dict = {
                    "visibility": note["visibility"],
                    "is_renote": True if note["renoteId"] is not None else False,
                    "is_reply": True if note["replyId"] is not None else False,
                    "has_cw": True if note["cw"] is not None else False,
                    "has_mentions": True if "mentions" in note and len(note["mentions"]) > 0 else False,
                    "has_zws": True if "\u200B" in note["text"] else False,
                }

                if meta["has_mentions"] == False and re.search(mentions_pattern, note["text"]) is not None:
                    meta["has_mentions"] = True

                self.processed_notes += 1
                corpus.writerow([note["text"], json.dumps(meta)])