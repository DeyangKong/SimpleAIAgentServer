from typing import List, Optional, Union

from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI
from llama_index.llms.openai_like import OpenAILike


class Agent():
    def __init__(
            self,
            llm: Union[OpenAI, OpenAILike],
            memory: List[ChatMessage]=None,
            system_prompt: Optional[str]=None,
    ) -> None:
        """init the agent"""
        if memory is None:
            memory = []
        if system_prompt is not None:
            memory.append(ChatMessage(role="system", content=system_prompt))

        self.memory = memory
        self.llm = llm

    def chat(self, query):
        self.memory.append(ChatMessage(role="user", content=query))

        response = self.llm.chat(messages=self.memory)
        self.memory.append(response.message)

        return response.message.content

    def stream_chat(self, query):
        self.memory.append(ChatMessage(role="user", content=query))

        response = self.llm.stream_chat(messages=self.memory)
        complete_message = ""

        for chunk in response:
            complete_message += chunk.delta
            yield chunk.delta

        self.memory.append(ChatMessage(role="assistant", content=complete_message))
