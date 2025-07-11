

from dotenv import load_dotenv
import os

load_dotenv()  

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError("Missing GROQ_API_KEY environment variable.")

from groq import Groq

client = Groq(api_key=GROQ_API_KEY)

def ask_groq(question: str, context: str, role: str = "default"):
    # Inject role and context into the prompt
    prompt = f"""As a {role}, answer the following question using the provided document context.

Question: {question}

Context:
{context}

Only use the context above to generate your answer. If not found, say "Answer not available in the provided documents."
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
