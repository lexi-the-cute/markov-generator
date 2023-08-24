import logging

try:
    import nltk
except ImportError:
    raise ImportError("Failed to import nltk, please run `pip3 install nltk`")

try:
    from nltk.corpus import cmudict
except ImportError:
    raise ImportError("Failed to import nltk.corpus.cmudict, please run `pip3 install nltk`")

class GibberishText:
    # Required
    input: object = None

    # Default
    nltk_pronunciation_lexicon: str = "cmudict"  # Carnegie Mellon University Pronunciation Dictionary
    nltk_pronunciation_lexicon_path: str = "corpora/cmudict"
    show_tag: bool = True
    pronunciation_dictionary: dict = {
        "pronounciation": [
            "P R OW0 N AW0 N S IY0 EY1 SH AH0 N",
            "P R AH0 N AW0 N S IY0 EY1 SH AH0 N"
        ]
    }

    # Non-Configurable
    cdict: dict = {}
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

        # Download Carnegie Mellon University Pronunciation Dictionary for Syllable analysis
        # CMUDict is designed for analyzing syllables and pronunciation
        try:
            nltk.data.find(self.nltk_pronunciation_lexicon_path)
        except LookupError:
            print(f"Failed to find {self.nltk_pronunciation_lexicon}. Downloading for you...")
            nltk.download(self.nltk_pronunciation_lexicon)

        self.cdict: dict = cmudict.dict()

    def set_input(self, input: object):
        """
            Set the input used by this module
        """
        
        self.input: object = input

    def run(self):
        """
            Execute this module as part of a chain of modules
        """

        self.logger.info("Gibberishifying notes...")

        if type(self.input) is str:
            return self._get_gibberishified_text(text=self.input)
        
        if type(self.input) is not list:
            return

        notes: list = []
        for note in self.input:
            if "text" not in note:
                continue

            # Create Operation Tag
            tag: dict = {
                "name": "GibberishText",
                "operation": "modify",
                "show": self.show_tag
            }

            text: str = self._get_gibberishified_text(text=note["text"])

            # If modification did not take effect, then remove tag
            if self.show_tag and note["text"] == text:
                tag["show"] = False

            note["text"] = text
            note["tags"] = note["tags"] + [tag] if "tags" in note else [tag]
            notes.append(note)

        return notes

    def _get_syllables(self, word: str):
        pronunciation_dictionary: dict = self.cdict | self.pronunciation_dictionary

        if word.lower() not in pronunciation_dictionary:
            self.logger.error(msg=f"Could not find the word, {word.lower()}, in the pronunciation lexicon...")
            return

        desired_syllables: list = []
        for syllables in pronunciation_dictionary[word.lower()]:
            numbered_syllables: list = []
            for syllable in syllables:
                if syllable[-1].isdigit():  # -1 means seek from end
                    numbered_syllables.append(syllable)

            desired_syllables.append(numbered_syllables)

        syllable_count: list = []
        for syllables in desired_syllables:
            syllable_count.append(len(syllables))

        print(syllable_count)

    def _get_gibberishified_text(self, text: str):
        # Validate text
        if text is None:
            text: str = ""

        # https://catgirl.land/notes/9iqfxd9wok9h5myh
        # ...

        self._get_syllables(word="Dictionary")