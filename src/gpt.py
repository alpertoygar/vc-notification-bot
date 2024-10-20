import functools
import operator
import os
from datetime import timedelta, datetime

from openai import OpenAI


class GPTClient:
    client: OpenAI
    queries: dict

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
        self.queries = {datetime.now(): 0}

    def ask_when_taken(self, url: str, model="gpt-4o-mini"):
        query = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Tell me which city, country and year do you think this image taken? And what is your reasoning"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": url
                            }
                        }
                    ]
                }
            ]
        )
        return query.choices[0].message.content

    def ask_question(self, content: str, history=None, model="gpt-4o-mini"):
        if not history:
            history = []

        history.extend([
            {
                "role": "user",
                "content": content
            }
        ])

        query = self.client.chat.completions.create(
            model=model,
            messages=history
        )

        return query.choices[0].message.content

    def total_queries_length(self):
        return functools.reduce(operator.add, self.queries.values())

    def clean_queries(self):
        result = {}
        for timestamp, char_len in self.queries.items():
            if timestamp > datetime.now() - timedelta(hours=1):
                result[timestamp] = char_len
        self.queries = result
        print(self.queries)
