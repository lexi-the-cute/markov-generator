import logging

try:
    import modules
except ImportError as e:
    logging.error(e)
    exit(1)

class ChatBot:
    def __init__(self):
        pass

if __name__ == "__main__":
    # Download Notes Settings
    download_host: str = "https://catgirl.land"
    download_api_key: str = "REDACTED"
    user_id: str = "9h5znfmoxj3nldm4"

    # Post Notes Settings
    post_host: str = "https://catgirl.land"
    post_api_key: str = "REDACTED"
    content_warning: str = "markov generated post"
    dry_run: bool = True

    # Filter Notes Settings
    toss_text: list = [
        "nagifur", "donate", "paid", "u.s", "cmakecache.txt",
        "cpu", "chatgpt", "perception of me", "twitter",
        ".actor@", "..onion", "urls:", "digitalocean"
    ]

    STEPS: list = [
        {"module": modules.DownloadNotes, "settings": {"host": download_host, "api_key": download_api_key, "user_id": user_id}},
        {"module": modules.FilterNotes, "settings": {"toss_text": toss_text}},
        {"module": modules.RevertNyaizeText, "settings": {}},
        {"module": modules.CleanText, "settings": {}},
        # TODO: Markov stuff here...
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
    print(output)