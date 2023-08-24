import re
import logging

try:
    import markovify
except ImportError:
    raise ImportError("Failed to import markovify, please run `pip3 install markovify`")

try:
    import nltk
except ImportError:
    raise ImportError("Failed to import nltk, please run `pip3 install nltk`")

try:
    from nltk.sentiment import SentimentIntensityAnalyzer
except ImportError:
    raise ImportError("Failed to import nltk.sentiment.SentimentIntensityAnalyzer, please run `pip3 install nltk`")

class GenerateMarkov:
    # Required
    input: object = None

    # Default
    max_characters: int = 3000
    nltk_sentiment_lexicon: str = "vader_lexicon"
    nltk_sentiment_lexicon_path: str = "sentiment/vader_lexicon.zip"
    rejection_pattern: str = re.compile(pattern=r"(^`)|(`$)|\s`|`\s|(^')|('$)|\s'|'\s|[\"(\(\)\[\])]", flags=re.IGNORECASE|re.MULTILINE)
    well_formed: bool = True
    number_of_posts_to_generate: int = 1
    sentiment_score_minimum: float = 1.0
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
    model: markovify.Text = None
    sentiment_analyzer: SentimentIntensityAnalyzer = None

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

        if "sentiment_score_minimum" in settings:
            self.sentiment_score_minimum = settings["sentiment_score_minimum"]

        if "state_size" in settings:
            self.state_size = settings["state_size"]

        if "words" in settings:
            self.words = settings["words"]

        if "show_tag" in settings:
            self.show_tag = settings["show_tag"]

        if "well_formed" in settings:
            self.well_formed = settings["well_formed"]

        if "rejection_pattern" in settings:
            self.rejection_pattern = settings["rejection_pattern"]
        
        if "nltk_sentiment_lexicon_path" in settings:
            self.nltk_sentiment_lexicon_path = settings["nltk_sentiment_lexicon_path"]

        if "nltk_sentiment_lexicon" in settings:
            self.nltk_sentiment_lexicon = settings["nltk_sentiment_lexicon"]

        if "max_characters" in settings:
            self.max_characters = settings["max_characters"]

        # Download VADER lexicon for sentiment analysis
        # VADER is designed for short, social media posts
        try:
            nltk.data.find(self.nltk_sentiment_lexicon_path)
        except LookupError:
            self.logger.log(level=self.LESSERDEBUG, msg=f"Failed to find {self.nltk_sentiment_lexicon}. Downloading for you...")
            nltk.download(self.nltk_sentiment_lexicon)

        # Initialize Sentiment Analyzer
        self.sentiment_analyzer: SentimentIntensityAnalyzer = SentimentIntensityAnalyzer()
        self.sentiment_analyzer.lexicon.update(self.words)

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

        corpus: str = None
        if type(self.input) is str:
            corpus: str = self.input
        
        # Turn list of notes into a single text corpus
        texts: list = []
        if type(self.input) is list:
            for note in self.input:
                if "text" not in note:
                    continue

                texts.append(note["text"])
        corpus: str = '\n'.join(texts)

        # Build the model from the corpus
        self.model: markovify.Text = markovify.Text(
            input_text=corpus, state_size=self.state_size,
            well_formed=self.well_formed, reject_reg=self.rejection_pattern
        )

        notes: list = []
        for count in range(self.number_of_posts_to_generate):
            # Create Operation Tag
            tag: dict = {
                "name": "GenerateMarkov",
                "operation": "create",
                "show": self.show_tag
            }

            notes.append({
                "text": self._get_markov_text(),
                "tags": [tag]
            })

        return notes

    def _get_sentiment(self, text: str):
        # Validate text
        if text is None:
            text: str = ""

        score: dict = self.sentiment_analyzer.polarity_scores(text)
        
        positive: float = round((score['pos'] * 10), 2)
        negative: float = round((score['neg'] * 10), 2)

        return positive, negative

    def _get_markov_text(self):
        while True:
            text: str = self.model.make_short_sentence(max_chars=self.max_characters)

            # We want to keep the notes more positive
            positive_score, negative_score = self._get_sentiment(text=text)
            self.logger.log(level=self.VERBOSE, msg=f"Positive: {positive_score} - Negative: {negative_score} - Note: `{text}`")

            # Check the sentiment score
            if positive_score >= self.sentiment_score_minimum:
                break

        return text