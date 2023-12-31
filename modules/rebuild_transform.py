import re
import random
import logging

try:
    import nltk
except ImportError:
    raise ImportError("Failed to import nltk, please run `pip3 install nltk`")

try:
    from mosestokenizer import MosesDetokenizer
except ImportError:
    # Look at opus-fast-mosestokenizer
    raise ImportError("Failed to import mosestokenizer, please run `pip3 install mosestokenizer`")

class RebuildText:
    # Required
    input: object = None

    # Default
    chance_execute: float = 1.0
    show_tag: bool = False
    detokenizer_language: str = "en"
    tokenizer_language: str = "english"
    hard_skip: bool = False

    # Non-Configurable
    skipped: bool = False
    dont_pattern: re.Pattern = re.compile(pattern=r'(do) (n\'t)', flags=re.IGNORECASE|re.MULTILINE)
    nltk_tokenizer_lexicon: str = "punkt"
    nltk_tokenizer_lexicon_path: str = "tokenizers/punkt"
    detokenizer: MosesDetokenizer = None
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

        if "detokenizer_language" in settings:
            self.detokenizer_language = settings["detokenizer_language"]

        if "tokenizer_language" in settings:
            self.tokenizer_language = settings["tokenizer_language"]

        if "chance_execute" in settings:
            self.chance_execute = settings["chance_execute"]

        if "hard_skip" in settings:
            self.hard_skip = settings["hard_skip"]

        # Download PUNKT lexicon for rebuilding sentences
        # PUNKT is designed for tokenizing words
        try:
            nltk.data.find(self.nltk_tokenizer_lexicon_path)
        except LookupError:
            self.logger.log(level=self.LESSERDEBUG, msg="Failed to find {self.nltk_tokenizer_lexicon}. Downloading for you...")
            nltk.download(self.nltk_tokenizer_lexicon)

        self.detokenizer: MosesDetokenizer = MosesDetokenizer(self.detokenizer_language)

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
            self.logger.log(level=self.LESSERDEBUG, msg="Hit random chance of skipping rebuilding notes...")

            if self.hard_skip:
                return self.input

            self.skipped: bool = True
        else:
            self.logger.info("Rebuilding notes...")

        if type(self.input) is str:
            return self._get_nyaized_text(text=self.input)
        
        if type(self.input) is not list:
            return

        notes: list = []
        for note_data in self.input:
            if "note" not in note_data:
                continue

            note: dict = note_data["note"][-1].copy()

            if "text" not in note:
                continue

            # Create Operation Tag
            tag: dict = {
                "name": "RebuildText",
                "operation": "modify",
                "show": self.show_tag,
                "skipped": self.skipped
            }

            text: str = note["text"]
            if not self.skipped:
                text: str = self._get_rebuilt_text(text=note["text"])

            # If modification did not take effect, then remove tag
            if self.show_tag and note["text"] == text:
                tag["show"] = False

            note["text"] = text.strip()
            note["tag"] = tag

            # Add Note To List
            note_data["note"].append(note)

            notes.append({
                "note": note_data["note"]
            })

        return notes

    def _get_fixed_words(self, text: str):
        text: str = re.sub(pattern=self.dont_pattern, repl=r'\1\2', string=text)

        return text

    def _get_rebuilt_text(self, text: str):
        # Validate text
        if text is None:
            text: str = ""

        # Breaks word, `don't` as `do n't`
        sentences: list[str] = []
        for sentence in nltk.sent_tokenize(text=text, language=self.tokenizer_language):
            words: list[str] = nltk.word_tokenize(sentence)
            # words: list[str] = sentence.split()
            sentence: str = self.detokenizer(words)
            sentence: str = self._get_fixed_words(text=sentence)

            sentences.append(sentence)

        self.logger.log(level=self.VERBOSE, msg=f"OG Text: {text}, New Text: {' '.join(sentences)}")

        return ' '.join(sentences)