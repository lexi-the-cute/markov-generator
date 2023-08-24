# import re
import logging

try:
    import markovify
except ImportError:
    raise ImportError("Failed to import markovify, please run `pip3 install markovify`")

try:
    import nltk
except ImportError:
    raise ImportError("Failed to import nltk, please run `pip3 install nltk`")

class GenerateMarkov:
    # Required
    input: object = None

    # Default
    number_of_posts_to_generate: int = 1
    sentimental_score_minimum: float = 1.0
    show_tag: bool = True
    state_size: int = 3
    words: dict = {
        # Gay Speak
        'UwU': 0.2,
        'OwO': 0.2,
        'awawawa': 0.5,
        'mew': 0.2,
        'mrrp': 0.6,
        'miau': 0.4,
        'eepy': 0.7,
        ':3': 0.3,
        'catgirl': 0.5,
        'catboy': 0.5,
        'doggirl': 0.5,
        'dogboy': 0.5,
        'foxgirl': 0.5,
        'foxboy': 0.5,
        'demongirl': 0.5,
        'demonboy': 0.5,
        'trans': 0.3,
        'gay': 0.3,

        # Emojis
        ':blobfox_mlem:': 0.8,
        ':blobfox_pleading:': 0.8,

        # Negative Sentiment
        ':blobfox_sad:': -0.3,  # Mark emoji as sad
        ':neocat_sad:': -0.3,  # Mark emoji as sad
        ':neofox_sad:': -0.3,  # Mark emoji as sad
        ':blobfox_pat_sad:': -0.4,  # Mark emoji as sad
        ':blobcat_very_sad:': -0.6,  # Mark emoji as sad
        ':blobcat_sad_reach:': -0.6,  # Mark emoji as sad
        ':neocat_sad_reach:': -0.6,  # Mark emoji as sad
        ':blobfox_sad_reach:': -0.6,  # Mark emoji as sad
        ':neofox_sad_reach:': -0.6,  # Mark emoji as sad
        ':blobcat_sad_huggies:': -0.6,  # Mark emoji as sad
        'spam': -0.5,  # Hate spam
        'jeez': -0.5,  # Complaint
        'ISPs': -0.3,  # Internet Service Providers
        'lie': -0.5    # Shows up way too much, and negative
    }

    # Non-Configurable
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
        if "number_of_posts_to_generate" in settings:
            self.number_of_posts_to_generate = settings["number_of_posts_to_generate"]

        if "sentimental_score_minimum" in settings:
            self.sentimental_score_minimum = settings["sentimental_score_minimum"]

        if "state_size" in settings:
            self.state_size = settings["state_size"]

        if "words" in settings:
            self.words = settings["words"]

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