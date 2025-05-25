import functools
import operator
import os
from datetime import timedelta, datetime

from openai import OpenAI


class GPTClient:
    client: OpenAI
    queries: dict
    last_message_id: str | None = None
    last_messaged_at: datetime
    base_model: str

    CONTEXT_DURATION_IN_HOURS = 2

    def __init__(self, base_model: str):
        self.client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
        self.queries = {datetime.now(): 0}
        self.last_message_id = None
        self.last_messaged_at = datetime.now()
        self.base_model = base_model

    def ask_question(self, content: str, instructions: str) -> (str, int):
        model = self.base_model

        # clean history if the last message was sent more than `CONTEXT_DURATION_IN_HOURS` ago
        if self.last_messaged_at < datetime.now() - timedelta(hours=self.CONTEXT_DURATION_IN_HOURS):
            self.last_message_id = None
            self.last_messaged_at = datetime.now()

        # send the query to OpenAI
        query = self.client.responses.create(
            model=model,
            input=content,
            previous_response_id=self.last_message_id,
            **({"instructions": instructions} if instructions else {}),
        )

        print(query.model_dump_json())
        # update the history with the response
        self.last_message_id = query.id
        self.last_messaged_at = datetime.now()

        for output in query.output:
            if output.type == "message":
                return output.content[0].text, query.usage.total_tokens

        return "This is a system message, no text response, contact your Discord admin", query.usage.total_tokens

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
        self.last_message_id = None
        self.last_messaged_at = datetime.now()
