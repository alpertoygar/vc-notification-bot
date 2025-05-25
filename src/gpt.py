import functools
import operator
import os
from datetime import timedelta, datetime

from openai import OpenAI


class GPTClient:
    client: OpenAI
    queries: dict
    history: list
    last_messaged_at: datetime
    base_model: str

    BASE_HISTORY = [
        {
            "role": "system",
            "content": "All answers must be shorter than 2000 characters.",
        }
    ]
    CONTEXT_DURATION_IN_HOURS = 2

    def __init__(self, base_model: str):
        self.client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
        self.queries = {datetime.now(): 0}
        self.history = self.BASE_HISTORY.copy()
        self.last_messaged_at = datetime.now()
        self.base_model = base_model

    def ask_when_taken(self, url: str, model=None):
        if model is None:
            model = self.base_model

        query = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Tell me which city, country and year do you think this image taken? And what is your reasoning",
                        },
                        {"type": "image_url", "image_url": {"url": url}},
                    ],
                }
            ],
        )
        return query.choices[0].message.content

    def ask_question(self, content: str, additional_context: list = [], model=None):
        if model is None:
            model = self.base_model

        # clean history if the last message was sent more than `CONTEXT_DURATION_IN_HOURS` ago
        if self.last_messaged_at < datetime.now() - timedelta(hours=self.CONTEXT_DURATION_IN_HOURS):
            self.history = self.BASE_HISTORY.copy()
            self.last_messaged_at = datetime.now()

        # add current message to history
        self.history.append({"role": "user", "content": content})

        # create a copy of the current history
        current_context = self.history.copy()

        # add additional context if provided
        if additional_context:
            for context in additional_context:
                current_context.append(context)

        # send the query to OpenAI
        query = self.client.chat.completions.create(model=model, messages=current_context)

        # update the history with the response
        self.history.append(query.choices[0].message)
        self.last_messaged_at = datetime.now()

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

    def reset_context(self):
        self.history = self.BASE_HISTORY.copy()
        self.last_messaged_at = datetime.now()
