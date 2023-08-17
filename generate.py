# import json
import os
import re

import nltk

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

def get_notes(api_key: str, user_id: str, since_id: str = None, limit: int = 100, session: requests.Session = requests.Session()):
    base_url: str = "https://catgirl.land/api/users/notes"

    # select text from note where "userId" = '9h5znfmoxj3nldm4' and "renoteId" is null and "replyId" is null and mentions = '{}'; 
    params: dict = {
        "i": api_key,
        "userId": user_id,
        "includeMyRenotes": False,
        "includeReplies": False,
        "limit": limit
    }

    if since_id is not None:
        params["sinceId"] = since_id

    response: requests.Response = session.post(url=base_url, json=params)
    return response, session

def update_corpus(api_key: str, user_id: str, sentiment_analyzer: SentimentIntensityAnalyzer, sentiment_score_minimum: float = 1.0, since_id: str = None, limit: int = 100, corpus_path: str = "corpus.txt"):
    corpus = open(file=corpus_path, mode="a")

    # Setup Session
    session: requests.Session = requests.Session()
    pattern: re.Pattern = re.compile(pattern="(@)([A-Za-z0-9_]+@[A-Za-z0-9_.]+)\w+")

    count: int = 0
    loop: bool = True
    while loop:
        response, session = get_notes(api_key=api_key, user_id=user_id, since_id=since_id, session=session)

        status = response.status_code
        results = response.json()

        if status != 200:
            print(f"get_notes(...) status code is {status}... exiting...")
            exit(1)
        
        if len(results) <= 0:
            loop: bool = False

        print(f"{humanize.intcomma(count)} notes processed....")
        for note in results:
            since_id: str = note['id']

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

            # We want to keep the notes more positive
            positive_score, negative_score = get_sentiment(text=note["text"], sid=sentiment_analyzer)
            if positive_score < sentiment_score_minimum:
                # print(f"{positive_score} - Negative: {note['text']}")
                continue

            # Write corpus
            text: str = note["text"].strip()
            corpus.write(f"{text}\n")
        
            # Count number of notes processed
            count += 1

    return since_id

def create_markov_texts(sentiment_analyzer: SentimentIntensityAnalyzer, sentiment_score_minimum: float = 1.0, max_chars: int = 3000, corpus_path: str = "corpus.txt"):
    corpus: str = None
    with open(corpus_path) as f:
        corpus: str = f.read()

    # Build the model from the corpus
    model: markovify.Text = markovify.Text(input_text=corpus)

    # Keep looping until high quality text is generated
    while True:
        text: str = model.make_short_sentence(max_chars=max_chars)

        # We want to keep the notes more positive
        positive_score, negative_score = get_sentiment(text=text, sid=sentiment_analyzer)
        if positive_score < sentiment_score_minimum:
            # print(f"{positive_score} - Negative: {note['text']}")
            continue

        break

    # Generate the text
    return text

# Built in boolean parsing does not work as expected, so use this custom parser instead
def parse_boolean_from_string(string: str):
    if string.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif string.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def get_sentiment(text: str, sid: SentimentIntensityAnalyzer = SentimentIntensityAnalyzer()):
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
                           help="API key for destionation of Markov texts (default: %(default)s)")

    argParser.add_argument("-suid", "--source-user-id",
                           nargs="?",
                           type=str,
                           help="User ID for source of texts (default: %(default)s)")

    argParser.add_argument("-ssid", "--source-since-id",
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
    human_since_id: str = args.source_since_id  # Latest Note ID is `9ih79s19aa6v49fh`  # Original Note ID is `9h61mim7x5qg1szz`

    # Post to bot account from markov chain
    bot_api_key: str = args.destination_api_key

    id_tracker_path: str = "latest_id.txt"
    num_notes: int = args.number_of_posts
    sentiment_score_minimum: float = args.sentiment_score_minimum

    # Download VADER lexicon for sentiment analysis
    # VADER is designed for short, social media posts
    if not nltk.data.find('sentiment/vader_lexicon.zip'):
        nltk.download('vader_lexicon')

    # Initialize Sentiment Score Analysis
    sentiment_analyzer: SentimentIntensityAnalyzer = SentimentIntensityAnalyzer()

    # Get Saved Latest ID If Exists
    if os.path.exists(id_tracker_path):
        with open(file=id_tracker_path, mode="r") as f:
            human_since_id: str = f.read().strip()

    # Update Corpus
    since_id: str = update_corpus(sentiment_score_minimum=sentiment_score_minimum, api_key=human_api_key, user_id=human_user_id, since_id=human_since_id, sentiment_analyzer=sentiment_analyzer)

    # Save Latest ID
    with open(file=id_tracker_path, mode="w") as f:
        f.write(since_id)

    # Generate Markov Posts
    count = 0
    while count < num_notes:
        markov_text: str = create_markov_texts(sentiment_score_minimum=sentiment_score_minimum, sentiment_analyzer=sentiment_analyzer)

        if args.dry_run is not None and args.dry_run != True:
            response, session = create_note(api_key=bot_api_key, text=markov_text, visibility="home")
        else:
            print("Dry run...")

        # Display Post
        print(f"Generated note: `{markov_text}`")
        count += 1