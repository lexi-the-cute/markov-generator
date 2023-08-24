import re
import random
import logging

try:
    import nltk
except ImportError:
    raise ImportError("Failed to import nltk, please run `pip3 install nltk`")

try:
    # This was designed for spanish, but seems to mostly work on english from what I've tested
    import pylabeador
except ImportError:
    raise ImportError("Failed to import pylabeador, please run `pip3 install pylabeador`")

try:
    from pylabeador.errors import HyphenatorError
except ImportError:
    raise ImportError("Failed to import pylabeador.errors.HyphenatorError, please run `pip3 install pylabeador`")   

class GibberishText:
    # Required
    input: object = None

    # Default
    chance_execute: float = 1.0
    show_tag: bool = True
    tokenizer_language: str = "english"
    word_pattern: re.Pattern = re.compile(pattern=r'^[a-zñáéíóúü]+$', flags=re.IGNORECASE|re.MULTILINE)
    vowels: list = ["a", "e", "i", "o", "u"]

    # Non-Configurable
    nltk_tokenizer_lexicon: str = "punkt"
    nltk_tokenizer_lexicon_path: str = "tokenizers/punkt"
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

        if "tokenizer_language" in settings:
            self.tokenizer_language = settings["tokenizer_language"]

        if "word_pattern" in settings:
            self.word_pattern = settings["word_pattern"]

        if "vowels" in settings:
            self.vowels = settings["vowels"]

        if "chance_execute" in settings:
            self.chance_execute = settings["chance_execute"]

        # Download PUNKT lexicon for rebuilding sentences
        # PUNKT is designed for tokenizing words
        try:
            nltk.data.find(self.nltk_tokenizer_lexicon_path)
        except LookupError:
            self.logger.log(level=self.LESSERDEBUG, msg=f"Failed to find {self.nltk_tokenizer_lexicon}. Downloading for you...")
            nltk.download(self.nltk_tokenizer_lexicon)

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
            self.logger.log(level=self.LESSERDEBUG, msg="Hit random chance of skipping gibberishifying notes...")
            return self.input

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
            if text is False:
                text: str = note["text"]

            # If modification did not take effect, then remove tag
            if self.show_tag and note["text"] == text:
                tag["show"] = False

            note["text"] = text
            note["tags"] = note["tags"] + [tag] if "tags" in note else [tag]
            notes.append(note)

        return notes

    def _get_gibberishified_word_from_syllables(self, syllables: list):
        if len(syllables) == 0:
            return

        word: list = []
        for syllable in syllables:
            count: int = -1
            for character in syllable:
                count += 1
                if character in self.vowels:
                    break
            
            syllable = syllable[:count] + "othag" + syllable[count:].lower()
            word.append(syllable)

        word: str = ''.join(word)
        if syllables[0][0] == syllables[0][0].upper():
            word: str = word[0].upper() + word[1:]

        return word

    def _get_gibberishified_text(self, text: str):
        # Validate text
        if text is None:
            text: str = ""

        sentences: list[str] = []
        for sentence in nltk.sent_tokenize(text=text, language=self.tokenizer_language):
            # Breaks on `I'm` or `Cute!`
            words: list[str] = nltk.word_tokenize(text=sentence, language=self.tokenizer_language)
            # words: list[str] = sentence.split()

            word_pos: int = 0
            for word in words:
                if self.word_pattern.match(string=word):
                    # Breaks on `everything`
                    try:
                        syllables: list = pylabeador.syllabify(word)
                    except HyphenatorError as e:
                        self.logger.error(msg=f"pylabeador couldn't handle the word, `{e.word}`. Skipping gibberishifying this text...")
                        return False

                    word: str = self._get_gibberishified_word_from_syllables(syllables=syllables)
                elif any(c.isalpha() for c in word):
                    # When a word contains both letters and something else
                    self.logger.log(level=self.LESSERDEBUG, msg=f"The word, `{word}`, contains characters which can't be processed right now. Skipping gibberishifying this text...")
                    return False

                words[word_pos] = word
                word_pos += 1
            sentences += words

        self.logger.log(level=self.VERBOSE, msg=f"Original: `{text}`, Gibberishified: `{' '.join(sentences)}`")
        return ' '.join(sentences)