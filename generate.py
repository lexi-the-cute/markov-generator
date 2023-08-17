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

def create_note(api_key: str, text: str, content_warning: str = "markov generated post", visibility: str = "followers", session: requests.Session = requests.Session()):
    base_url: str = "https://catgirl.land/api/notes/create"

    params: dict = {
        "i": api_key,
        "text": text,
        "cw": content_warning,
        "visibility": visibility
    }

    response: requests.Response = session.post(url=base_url, json=params)
    return response, session

def get_notes(api_key: str, user_id: str, until_id: str = None, limit: int = 100, session: requests.Session = requests.Session()):
    base_url: str = "https://catgirl.land/api/users/notes"

    # select text from note where "userId" = '9h5znfmoxj3nldm4' and "renoteId" is null and "replyId" is null and mentions = '{}'; 
    params: dict = {
        "i": api_key,
        "userId": user_id,
        "includeMyRenotes": False,
        "includeReplies": False,
        "limit": limit
    }

    if until_id is not None:
        params["untilId"] = until_id

    response: requests.Response = session.post(url=base_url, json=params)
    return response, session

def update_corpus(api_key: str, user_id: str, until_id: str = None, limit: int = 100, corpus_path: str = "corpus.txt"):
    corpus = open(file=corpus_path, mode="a")

    # Setup Session
    session: requests.Session = requests.Session()
    pattern: re.Pattern = re.compile(pattern=r"(@)([A-Za-z0-9_]+@[A-Za-z0-9_.]+)\w+")

    count: int = 0
    loop: bool = True
    while loop:
        response, session = get_notes(api_key=api_key, user_id=user_id, until_id=until_id, session=session)

        status = response.status_code
        results = response.json()

        if status != 200:
            print(f"get_notes(...) status code is {status}... exiting...")
            exit(1)
        
        print(f"Results: {len(results)}")
        if len(results) <= 0:
            loop: bool = False

        print(f"{humanize.intcomma(count)} notes processed....")
        for note in results:
            until_id: str = note['id']

            # "public" "home" "followers" "specified" "hidden"
            # We don't want to process private notes
            if note["visibility"] == "specified" or note["visibility"] == "hidden":
                # print(note["text"])
                continue

            # We don't want to handle renotes
            if note["renoteId"] is not None:
                continue

            # We don't want to handle replies
            if note["replyId"] is not None:
                continue

            # Filter out more serious notes
            if note["cw"] is not None:
                continue

            # We don't want to handle mentions
            if "mentions" in note and len(note["mentions"]) > 0:
                continue

            # We don't want to process notes with ZWS in them (e.g. MiCECo)
            if "\u200B" in note["text"]:
                # print(note["text"])
                continue

            # We want to be sure to sanitize out mentions
            if re.search(pattern, note["text"]) is not None:
                # print(note["text"])
                continue

            # Revert nyaized text
            text: str = get_reverted_nyaized_text(text=note["text"].strip())

            # Clean text
            text: str = get_cleaned_text(text=text)

            # Split text for model
            text_split_len: int = 512
            split: list = [text[i:i+text_split_len] for i in range(0, len(text), text_split_len)]
            
            # Process text
            text: str = ""
            for piece in split:
                text: str = text + get_processed_text(doc=nlp(piece))

            # Write corpus
            corpus.write(f"{text}\n")
        
            # Count number of notes processed
            count += 1

    return until_id

def create_markov_texts(sentiment_analyzer: SentimentIntensityAnalyzer, sentiment_score_minimum: float = 1.0, max_chars: int = 3000, state_size: int = 3, corpus_path: str = "corpus.txt"):
    corpus: str = None
    with open(corpus_path) as f:
        corpus: str = f.read()

    # Build the model from the corpus
    model: markovify.Text = markovify.Text(input_text=corpus, state_size=state_size)

    # Keep looping until high quality text is generated
    while True:
        text: str = model.make_short_sentence(max_chars=max_chars)

        # We want to keep the notes more positive
        positive_score, negative_score = get_sentiment(text=text, sid=sentiment_analyzer)
        if positive_score < sentiment_score_minimum:
            # print(f"{positive_score} - Negative: {note['text']}")
            continue

        break

    # Nyaize the text
    text: str = get_nyaized_text(text=text)

    # Generate the text
    return text

def get_reverted_nyaized_text(text: str):
    text: str = re.sub(pattern=r"(nyan)(?=[bcdfghjklmnpqrstvwxyz])", repl="non", string=text, flags=re.IGNORECASE|re.MULTILINE)
    text: str = re.sub(pattern=r"(?<=every)(nyan)", repl="one", string=text, flags=re.IGNORECASE|re.MULTILINE)
    text: str = re.sub(pattern=r"(?<=morn)(yan)", repl="ing", string=text, flags=re.IGNORECASE|re.MULTILINE)
    text: str = re.sub(pattern=r"(?<=n)(ya)", repl="a", string=text, flags=re.IGNORECASE|re.MULTILINE)

    return text

def get_nyaized_text(text: str):
    text: str = re.sub(pattern=r"(?<=n)(a)", repl="ya", string=text, flags=re.IGNORECASE|re.MULTILINE)
    text: str = re.sub(pattern=r"(?<=morn)(ing)", repl="yan", string=text, flags=re.IGNORECASE|re.MULTILINE)
    text: str = re.sub(pattern=r"(?<=every)(one)", repl="nyan", string=text, flags=re.IGNORECASE|re.MULTILINE)
    text: str = re.sub(pattern=r"(non)(?=[bcdfghjklmnpqrstvwxyz])", repl="nyan", string=text, flags=re.IGNORECASE|re.MULTILINE)

    return text

def get_cleaned_text(text: str):
    text: str = re.sub(pattern=r'http\S+', repl='', string=text, flags=re.IGNORECASE|re.MULTILINE)

    return text

def get_processed_text(doc: spacy.tokens.doc.Doc):
    return " ".join([sent.text for sent in doc.sents if len(sent.text) > 1])

def get_sentiment(text: str, sid: SentimentIntensityAnalyzer):
    score: dict = sid.polarity_scores(text)
    
    positive: float = round((score['pos'] * 10), 2)
    negative: float = round((score['neg'] * 10), 2)

    return positive, negative

# Built in boolean parsing does not work as expected, so use this custom parser instead
def parse_boolean_from_string(string: str):
    if string.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif string.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

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

    # NLTK Lexicon
    nltk_lexicon: str = "vader_lexicon"
    nltk_lexicon_path: str = "sentiment/vader_lexicon.zip"

    # Spacy Model
    spacy_model: str = "en_core_web_trf"  # en_core_web_sm is less accurate, en_core_web_trf is more accurate

    # Markov Model
    state_size: int = 3

    # Download VADER lexicon for sentiment analysis
    # VADER is designed for short, social media posts
    try:
        nltk.data.find(nltk_lexicon_path)
    except LookupError:
        print(f"Failed to find {nltk_lexicon}. Downloading for you...")
        nltk.download(nltk_lexicon)

    # Open text parser
    if spacy.util.is_package(spacy_model):
        nlp = spacy.load(spacy_model)  # spacy.lang.en.English
    else:
        print(f"Failed to find {spacy_model}. Downloading for you...")
        spacy.cli.download(spacy_model)
        nlp = spacy.load(spacy_model)  # spacy.lang.en.English

    # Initialize Sentiment Score Analysis
    sentiment_analyzer: SentimentIntensityAnalyzer = SentimentIntensityAnalyzer()

    # Get Saved Latest ID If Exists
    if os.path.exists(id_tracker_path):
        with open(file=id_tracker_path, mode="r") as f:
            human_until_id: str = f.read().strip()

    # Update Corpus
    until_id: str = update_corpus(api_key=human_api_key, user_id=human_user_id, until_id=human_until_id)

    # Save Latest ID
    with open(file=id_tracker_path, mode="w") as f:
        f.write(until_id)

    # Generate Markov Posts
    count = 0
    while count < num_notes:
        markov_text: str = create_markov_texts(sentiment_score_minimum=sentiment_score_minimum, sentiment_analyzer=sentiment_analyzer, state_size=state_size)

        if args.dry_run is not None and args.dry_run != True:
            response, session = create_note(api_key=bot_api_key, text=markov_text, visibility="home")

            # Display post
            print(f"Generated note: `{markov_text}`")
        else:
            # Display dry run
            print(f"Dry run... Generated note: `{markov_text}`")

        count += 1