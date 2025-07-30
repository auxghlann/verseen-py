import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

class VerseenAI:

    SYSTEM_BASE_PROMPT = """
    - Give interpretation to the song lyrics provided by the user.
    - Receive song lyrics and title and provide an interpretation of the lyrics.
    - Give interpretation of the song lyrics not exceeding 500 tokens.
    """


    INTERPRET_FUNCTION = {
        "type":"function",
        "function": {
            "name":"interpret_lyrics",
            "description": "Interpret the song lyrics provided by the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "interpretation": {
                        "type": "string",
                        "description": "The interpretation of the song lyrics."
                    }
                },
                "required": ["interpretation"]
            }
        }
    }       

    @staticmethod
    def get_response(lyrics: str) -> str | None:
        response = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[
                {"role": "system", "content": VerseenAI.SYSTEM_BASE_PROMPT},
                {"role": "user", "content": lyrics}
            ],
            max_tokens=500,
            tools=[VerseenAI.INTERPRET_FUNCTION],
            tool_choice="auto",
        )
        
        return response.choices[0].message.tool_calls[0].function.arguments if response.choices and response.choices[0].message.tool_calls else None


if __name__ == "__main__":
    prompt = """"I had a thought, dear\r\nHowever scary,\r\nAbout that night,\r\nThe bugs and the dirt\r\nWhy were you digging?\r\nWhat did you bury,\n\nBefore those hands pulled me\n\nFrom the earth?\n\n\n\nI will not ask you where you came from,\n\nI will not ask you and neither should you.\n\n\n\nHoney just put your sweet lips on my lips\n\nWe should just kiss like real people do.\n\n\n\nI knew that look dear,\n\nEyes always seeking\n\nWas there in someone\n\nThat dug long ago,\n\nSo I will not ask you\n\nWhy you were creeping,\n\nIn some sad way I already know.\n\n\n\nSo I will not ask you where you came from,\n\nI would not ask and neither would you.\n\n\n\nHoney just put your sweet lips on my lips\n\nWe should just kiss like real people do.\n\n\n\nI could not ask you where you came from,\n\nI could not ask and neither could you.\n\n\n\nHoney just put your sweet lips on my lips\n\nWe could just kiss like real people do."""
    response = VerseenAI.get_response(prompt)
    print(type(response))
    print(f"Response: {response}")
