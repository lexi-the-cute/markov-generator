import os
import logging

try:
    import modules
except ImportError as e:
    logging.error(e)
    exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    logging.error("Failed to import dotenv, please run `pip3 install python-dotenv`")
    exit(1)

def parse_boolean_from_string(string: str):
    if string.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif string.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def parse_level_from_string(string: str):
    if string.lower() in ('critical', 'crit'):
        return logging.CRITICAL
    elif string.lower() in ('fatal'):
        return logging.FATAL
    elif string.lower() in ('error'):
        return logging.ERROR
    elif string.lower() in ('warn', 'warning'):
        return logging.WARNING
    elif string.lower() in ('info', 'information'):
        return logging.INFO
    elif string.lower() in ('debug'):
        return logging.DEBUG
    else:
        return logging.NOTSET

if __name__ == "__main__":
    load_dotenv()

    # Download Notes Settings
    download_host: str = os.getenv("DOWNLOAD_HOST")
    download_api_key: str = os.getenv("DOWNLOAD_API_KEY")
    user_id: str = os.getenv("USER_ID")

    # Post Notes Settings
    post_host: str = os.getenv("POST_HOST")
    post_api_key: str = os.getenv("POST_API_KEY")
    content_warning: str = os.getenv("CONTENT_WARNING", "markov generated post")
    dry_run: bool = parse_boolean_from_string(string=os.getenv("DRY_RUN", "true"))

    # Filter Notes Settings
    toss_text: list = [
        "nagifur", "donate", "paid", "u.s", "cmakecache.txt",
        "cpu", "chatgpt", "perception of me", "twitter",
        ".actor@", "..onion", "urls:", "digitalocean"
    ]

    # Set Logger Configuration
    LOG_LEVEL: int = parse_level_from_string(os.getenv("LOG_LEVEL", "INFO"))
    logging.basicConfig(level=LOG_LEVEL)

    STEPS: list = [
        # Require Meta
        {"module": modules.DownloadNotes, "settings": {"host": download_host, "api_key": download_api_key, "user_id": user_id}},
        {"module": modules.FilterNotes, "settings": {"toss_text": toss_text}},

        # Support Text Only
        {"module": modules.RevertNyaizeText, "settings": {}},
        {"module": modules.CleanText, "settings": {}},
        # TODO: Markov stuff here...
        {"module": modules.NormalizeText, "settings": {}},
        {"module": modules.CleanText, "settings": {}},
        # TODO: Gibberish text stuff here... (https://catgirl.land/notes/9iqfxd9wok9h5myh)
        {"module": modules.NyaizeText, "settings": {}},
        # TODO: Add a processing tag to each note on each module, then convert to hashtags here
        {"module": modules.PostNotes, "settings": {"host": post_host, "api_key": post_api_key, "content_warning": content_warning, "dry_run": dry_run}}
    ]

    output = None
    for STEP in STEPS:
        # Instantiate Module
        MODULE: object = STEP["module"]()

        # Set Settings
        MODULE.set_settings(settings=STEP["settings"])

        # Set Input
        MODULE.set_input(input=output)

        # Run
        output = MODULE.run()