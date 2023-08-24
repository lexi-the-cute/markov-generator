import os
import logging

# Setup Logger
logger = logging.getLogger(__name__)

try:
    import coloredlogs
except ImportError:
    logger.error("Failed to import coloredlogs, please run `pip3 install coloredlogs`")
    exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    logger.error("Failed to import dotenv, please run `pip3 install python-dotenv`")
    exit(1)

try:
    import modules
except ImportError as e:
    logger.error(e)
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
    # Load Environment Variables
    load_dotenv()

    # Set Logger Configuration
    LOG_LEVEL: int = parse_level_from_string(os.getenv("LOG_LEVEL", "INFO"))
    coloredlogs.install(level=LOG_LEVEL)

    # Download Notes Settings
    download_host: str = os.getenv("DOWNLOAD_HOST")
    download_api_key: str = os.getenv("DOWNLOAD_API_KEY")
    user_id: str = os.getenv("USER_ID")

    # Post Notes Settings
    post_host: str = os.getenv("POST_HOST")
    post_api_key: str = os.getenv("POST_API_KEY")
    content_warning: str = os.getenv("CONTENT_WARNING", "markov generated post")
    dry_run: bool = parse_boolean_from_string(string=os.getenv("DRY_RUN", "true"))

    STEPS: list = [
        # Require Meta
        {"module": modules.DownloadNotes, "settings": {"host": download_host, "api_key": download_api_key, "user_id": user_id}},
        {"module": modules.FilterNotes, "settings": {"toss_text": os.getenv("FILTER_TOSS_TEXT", [])}},

        # Support Text Only
        {"module": modules.RevertNyaizeText, "settings": {}},
        {"module": modules.CleanText, "settings": {}},
        {"module": modules.GenerateMarkov, "settings": {}},
        {"module": modules.NormalizeText, "settings": {}},
        {"module": modules.CleanText, "settings": {}},
        {"module": modules.GibberishText, "settings": {}},
        {"module": modules.NyaizeText, "settings": {}},
        {"module": modules.AddHashtags, "settings": {}},
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