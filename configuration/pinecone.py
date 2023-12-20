import os

import pinecone


def init_pinecone():
    pinecone_key = os.environ["PINECONE_API_KEY"]
    pinecone_env = os.environ["PINECONE_ENVIRONMENT"]

    pinecone.init(
        api_key=pinecone_key,
        environment=pinecone_env,
    )
