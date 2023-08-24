import logging

try:
    import nltk
except ImportError:
    raise ImportError("Failed to import nltk, please run `pip3 install nltk`")

try:
    from mosestokenizer import MosesDetokenizer
except ImportError:
    raise ImportError("Failed to import mosestokenizer, please run `pip3 install mosestokenizer`")

class RebuildText:
    # Required
    input: object = None

    # Default
    show_tag: bool = False
    detokenizer_language: str = "en"

    # Non-Configurable
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

        # Download PUNKT lexicon for rebuilding sentences
        # PUNKT is designed for tokenizing words
        try:
            nltk.data.find(self.nltk_tokenizer_lexicon_path)
        except LookupError:
            print(f"Failed to find {self.nltk_tokenizer_lexicon}. Downloading for you...")
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

        self.logger.info("Rebuilding notes...")

        if type(self.input) is str:
            return self._get_nyaized_text(text=self.input)
        
        if type(self.input) is not list:
            return

        notes: list = []
        for note in self.input:
            if "text" not in note:
                continue

            # Create Operation Tag
            tag: dict = {
                "name": "RebuildText",
                "operation": "modify",
                "show": self.show_tag
            }

            text: str = self._get_rebuilt_text(text=note["text"])

            # If modification did not take effect, then remove tag
            if self.show_tag and note["text"] == text:
                tag["show"] = False

            note["text"] = text
            note["tags"] = note["tags"] + [tag] if "tags" in note else [tag]
            notes.append(note)

        return notes

    def _get_rebuilt_text(self, text: str):
        # Validate text
        if text is None:
            text: str = ""

        sentences: list[str] = []
        for sentence in nltk.sent_tokenize(text):
            # words: list[str] = nltk.word_tokenize(sentence)
            words: list[str] = sentence.split()
            sentence: str = self.detokenizer(words)

            sentences.append(sentence)

        return ' '.join(sentences)