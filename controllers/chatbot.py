from fastapi import HTTPException, status
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone


def get_answer_from_chatbot(question: str, openai_api_key: str):
    try:
        query = f"""
You are a chatbot personalized for answering questions, now answer the
question: {question} 
Do not go out of context in any circumstance or hallucinate or fabricate information.
"""

        # select the chat model and temperature
        llm = ChatOpenAI(temperature=0.6, openai_api_key=openai_api_key)
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

        # index_name -> index vector name in Pinecone
        index_name = "woman-safety-embeddings"

        # question and answer chain
        qa_chain = load_qa_chain(llm, chain_type="stuff")

        docsearch = Pinecone.from_existing_index(index_name, embeddings)

        docs = docsearch.similarity_search(query)
        answer = qa_chain.run(input_documents=docs, question=query, max_tokens=150)

        return answer
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
