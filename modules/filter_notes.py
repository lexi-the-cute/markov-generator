import re
# import logging

class FilterNotes:
    # Required
    input: object = None
    toss_text: list = None

    # Default
    show_tag: bool = False

    # Non-Configurable
    setup: bool = False
    banned_visibilities: list = ["specified", "hidden"]
    banned_renote: bool = True
    banned_reply: bool = True
    banned_cw: bool = True
    banned_mentions: bool = True
    banned_zws: bool = True

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
        if "toss_text" in settings:
            self.toss_text = settings["toss_text"]
            count += 1

        if "show_tag" in settings:
            self.show_tag = settings["show_tag"]

        if count == 1:
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
            logging.error("FilterNotes module not configured...")
            return

        if type(self.input) is str:
            return self._get_should_filter_note_text(text=self.input)
        
        if type(self.input) is not list:
            return

        notes: list = []
        for note in self.input:
            if "text" not in note:
                continue

            if "meta" not in note:
                continue

            if self._get_should_filter_note_meta(meta=note["meta"]):
                continue

            if self._get_should_filter_note_text(text=note["text"]):
                continue

            # Create Operation Tag
            tag: dict = {
                "name": "FilterNotes",
                "operation": "filter",
                "show": self.show_tag
            }

            # Add Tag To List
            note["tags"] = note["tags"] + [tag] if "tags" in note else tag

            notes.append({
                "text": note["text"],
                "meta": note["meta"],
                "tags": note["tags"]
            })

        return notes

    def _get_should_filter_note_meta(self, meta: dict):
        # Validate meta
        if meta is None:
            meta: dict = {}

        # "public" "home" "followers" "specified" "hidden"
        # We don't want to process private notes
        if "visibility" in meta:
            for banned_visibility in self.banned_visibilities:
                if meta["visibility"] == banned_visibility:
                    return True

        # We don't want to handle renotes
        if "is_renote" in meta and meta["is_renote"] == True:
            if self.banned_renote:
                return True

        # We don't want to handle replies
        if "is_reply" in meta and meta["is_reply"] == True:
            if self.banned_reply:
                return True

        # Filter out more serious notes
        if "has_cw" in meta and meta["has_cw"] == True:
            if self.banned_cw:
                return True

        # We don't want to handle mentions
        if "has_mentions" in meta and meta["has_mentions"] == True:
            if self.banned_mentions:
                return True

        # We don't want to process notes with ZWS in them (e.g. MiCECo)
        if "has_zws" in meta and meta["has_zws"] == True:
            if self.banned_zws:
                return True

        return False

    def _get_should_filter_note_text(self, text: str):
        # Validate text
        if text is None:
            text: str = ""

        # Check if toss word in text
        for w in text.split():
            for toss_word in self.toss_text:
                if toss_word.lower() in w.lower():
                    # print(f"W: `{w}` - Toss Word: `{toss_word}`")
                    return True

        return False