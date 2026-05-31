import os

# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_answer(
    question: str,
    context_chunks: list[str],
    chat_history: list[dict] | None = None
) -> str:
    context = "\n\n".join(context_chunks)

    history_text = ""

    if chat_history:
        for message in chat_history:
            history_text += f"{message['role']}: {message['content']}\n"

    prompt = f"""
    You are an AI assistant answering questions using only the provided document context.

    Use chat history only to understand follow-up questions.
    Do not use chat history as factual evidence unless it is supported by the document context.

    If the answer is not in the context, say:
    "I don't know based on the provided document."

    Chat History:
    {history_text}

    Document Context:
    {context}

    User Question:
    {question}

    Answer:
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content