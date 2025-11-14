from groq import Groq
from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def main():
    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "user", "content": "Hello Groq! Test message."}
            ]
        )

        print("Groq Test Response:")
        print(response.choices[0].message.content)

    except Exception as e:
        print("ERROR:", str(e))


if __name__ == "__main__":
    main()
