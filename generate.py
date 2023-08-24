import os

import nltk
import spacy
from nltk.sentiment import SentimentIntensityAnalyzer
from mosestokenizer import MosesDetokenizer

def create_markov_texts(detokenize: MosesDetokenizer, sentiment_analyzer: SentimentIntensityAnalyzer, text_to_toss: list[str] = [], names: list[str] = [], stopwords: list[str] = [], sentiment_score_minimum: float = 1.0, max_chars: int = 3000, state_size: int = 3, reject_pattern: str = r"(^`)|(`$)|\s`|`\s|(^')|('$)|\s'|'\s|[\"(\(\)\[\])]", corpus_path: str = "corpus.txt"):
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

    # Initialize Sentiment Score Analysis
    sentiment_analyzer: SentimentIntensityAnalyzer = SentimentIntensityAnalyzer()
    sentiment_analyzer.lexicon.update(new_words)

    # Initialize detokenizer
    detokenize: MosesDetokenizer = MosesDetokenizer('en')