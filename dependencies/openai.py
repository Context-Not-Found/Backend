import os


def get_openai_key():
    try:
        openai_key = os.environ["OPENAI_API_KEY"]
        yield openai_key
    except Exception as e:
        raise e
