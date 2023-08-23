# import json
import os
import re

import nltk
import spacy

import requests
import argparse
import humanize
import markovify

from nltk.sentiment import SentimentIntensityAnalyzer
from mosestokenizer import MosesDetokenizer

def create_markov_texts(detokenize: MosesDetokenizer, sentiment_analyzer: SentimentIntensityAnalyzer, text_to_toss: list[str] = [], names: list[str] = [], stopwords: list[str] = [], sentiment_score_minimum: float = 1.0, max_chars: int = 3000, state_size: int = 3, reject_pattern: str = r"(^`)|(`$)|\s`|`\s|(^')|('$)|\s'|'\s|[\"(\(\)\[\])]", corpus_path: str = "corpus.txt"):
    corpus_file_size: int = os.path.getsize(corpus_path)

    # Friendlier error
    if corpus_file_size <= 0:
        print("Corpus file is empty, please check your starting post id used for generating the corpus... exiting...")
        exit(1)

    corpus: str = None
    with open(corpus_path) as f:
        corpus: str = f.read()

    # Build the model from the corpus
    model: markovify.Text = markovify.Text(input_text=corpus, state_size=state_size, well_formed=True, reject_reg=reject_pattern)

    # Keep looping until high quality text is generated
    while True:
        text: str = model.make_short_sentence(max_chars=max_chars)

        # Toss text which shouldn't be included at all
        if get_should_toss_text(text=text, text_to_toss=text_to_toss):
            continue

        # Remove stopwords from text for analysis
        no_stopwords_text: str = remove_stopwords(text=text, stopwords=stopwords, detokenize=detokenize)

        # Rebuild sentences to fix grammar
        text: str = rebuild_sentences(text=text, detokenize=detokenize)

        # We want to keep the notes more positive
        positive_score, negative_score = get_sentiment(text=no_stopwords_text, sid=sentiment_analyzer)
        # print(f"Pos: {positive_score} - Neg: {negative_score} - Note: {text}")

        if positive_score < sentiment_score_minimum:
            continue

        break

    # Normalize text
    text: str = get_normalized_text(text=text, names=names)

    # Clean the text
    text: str = get_cleaned_text(text=text)

    # Nyaize the text
    text: str = get_nyaized_text(text=text)

    # Set text to null if zero length
    if isinstance(text, str) and len(text) <= 0:
        text = None

    # Generate the text
    return text

def remove_stopwords(text: str, detokenize: MosesDetokenizer, stopwords: list[str] = []):
    # Validate text
    if text is None:
        text: str = ""

    sentences: list[str] = []
    for sentence in nltk.sent_tokenize(text):
        words: list[str] = [w for w in nltk.word_tokenize(sentence) if w.lower() not in stopwords]
        sentence: str = detokenize(words)

        sentences.append(sentence)

    return ' '.join(sentences)

def rebuild_sentences(text: str, detokenize: MosesDetokenizer):
    # Validate text
    if text is None:
        text: str = ""

    sentences: list[str] = []
    for sentence in nltk.sent_tokenize(text):
        # words: list[str] = nltk.word_tokenize(sentence)
        words: list[str] = sentence.split()
        sentence: str = detokenize(words)

        sentences.append(sentence)

    return ' '.join(sentences)

def get_processed_text(doc: spacy.tokens.doc.Doc):
    return " ".join([sent.text for sent in doc.sents if len(sent.text) > 1])

def get_sentiment(text: str, sid: SentimentIntensityAnalyzer):
    # Validate text
    if text is None:
        text: str = ""

    score: dict = sid.polarity_scores(text)
    
    positive: float = round((score['pos'] * 10), 2)
    negative: float = round((score['neg'] * 10), 2)

    return positive, negative

if __name__ == "__main__":
    argParser: argparse.ArgumentParser = argparse.ArgumentParser()
    argParser.add_argument("-sa", "--source-api-key",
                           nargs="?",
                           type=str,
                           help="API key for source of texts (default: %(default)s)")
    
    argParser.add_argument("-da", "--destination-api-key",
                           nargs="?",
                           type=str,
                           help="API key for destination of Markov texts (default: %(default)s)")

    argParser.add_argument("-suid", "--source-user-id",
                           nargs="?",
                           type=str,
                           help="User ID for source of texts (default: %(default)s)")

    argParser.add_argument("-ssid", "--source-post-id",
                           nargs="?",
                           type=str,
                           help="First Post ID for source of texts; only necessary on first run (default: %(default)s)")

    argParser.add_argument("-dr", "--dry-run",
                           default=False,
                           nargs="?",
                           type=parse_boolean_from_string,
                           help="Disable posting Markov text; useful for debugging (default: %(default)s)")

    argParser.add_argument("-np", "--number-of-posts",
                           default=1,
                           nargs="?",
                           type=int,
                           help="The number of posts to generate (default: %(default)s)")

    argParser.add_argument("-ssm", "--sentiment-score-minimum",
                           default=1.0,
                           nargs="?",
                           type=float,
                           help="The minimum score needed to pass the sentiment check (default: %(default)s)")

    args = argParser.parse_args()

    # Retrieve from human account for updating corpus
    human_api_key: str = args.source_api_key
    human_user_id: str = args.source_user_id
    human_until_id: str = args.source_post_id  # Latest Note ID is `9ih79s19aa6v49fh`  # Original Note ID is `9h61mim7x5qg1szz`

    # Post to bot account from markov chain
    bot_api_key: str = args.destination_api_key

    id_tracker_path: str = "latest_id.txt"
    num_notes: int = args.number_of_posts
    sentiment_score_minimum: float = args.sentiment_score_minimum

    # NLTK PUNKT Lexicon
    nltk_punkt_lexicon: str = "punkt"
    nltk_punkt_lexicon_path: str = "tokenizers/punkt"

    # NLTK STOPWORDS Lexicon
    nltk_stopwords_lexicon: str = "stopwords"
    nltk_stopwords_lexicon_path: str = "corpora/stopwords.zip"

    # NLTK VADER Lexicon
    nltk_vader_lexicon: str = "vader_lexicon"
    nltk_vader_lexicon_path: str = "sentiment/vader_lexicon.zip"

    # Spacy Model
    spacy_model: str = "en_core_web_trf"  # en_core_web_sm is less accurate, en_core_web_trf is more accurate

    # Markov Model
    state_size: int = 3

    # Custom VADER lexicon additions
    new_words: dict = {
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

    # Download PUNKT lexicon for sentiment analysis
    # PUNKT is designed for removing tokenizing words
    try:
        nltk.data.find(nltk_punkt_lexicon_path)
    except LookupError:
        print(f"Failed to find {nltk_punkt_lexicon}. Downloading for you...")
        nltk.download(nltk_punkt_lexicon)

    # Download STOPWORDS lexicon for removing useless words
    # STOPWORDS is designed for removing useless words
    try:
        nltk.data.find(nltk_stopwords_lexicon_path)
    except LookupError:
        print(f"Failed to find {nltk_stopwords_lexicon}. Downloading for you...")
        nltk.download(nltk_stopwords_lexicon)

    # Download VADER lexicon for sentiment analysis
    # VADER is designed for short, social media posts
    try:
        nltk.data.find(nltk_vader_lexicon_path)
    except LookupError:
        print(f"Failed to find {nltk_vader_lexicon}. Downloading for you...")
        nltk.download(nltk_vader_lexicon)

    # Open text parser
    if spacy.util.is_package(spacy_model):
        nlp = spacy.load(spacy_model)  # spacy.lang.en.English
    else:
        print(f"Failed to find {spacy_model}. Downloading for you...")
        spacy.cli.download(spacy_model)
        nlp = spacy.load(spacy_model)  # spacy.lang.en.English

    # Initialize Stopwords
    stopwords: list = nltk.corpus.stopwords.words("english")

    # Initialize Names
    names: list = custom_names

    # Initialize Sentiment Score Analysis
    sentiment_analyzer: SentimentIntensityAnalyzer = SentimentIntensityAnalyzer()
    sentiment_analyzer.lexicon.update(new_words)

    # Initialize detokenizer
    detokenize: MosesDetokenizer = MosesDetokenizer('en')