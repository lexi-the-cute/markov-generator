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
    host: str = "https://catgirl.land"
    api_key: str = "REDACTED"
    user_id: str = "9h5znfmoxj3nldm4"


    STEPS: list = [
        {"module": modules.DownloadPosts, "settings": {"host": host, "api_key": api_key, "user_id": user_id}},
        # Filter out unwanted posts here...
        {"module": modules.RevertNyaizeText, "settings": {}},
        {"module": modules.CleanText, "settings": {}}
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