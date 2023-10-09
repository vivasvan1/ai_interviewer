
from langchain.schema import BaseMessage, SystemMessage, AIMessage, HumanMessage
from langchain.memory import ChatMessageHistory
import json

class ChatMessageHistoryWithJSON(ChatMessageHistory):
    def to_json(self):
        final_json = {"messages": []}
        for message in self.messages:
            if isinstance(message, SystemMessage):
                final_json["messages"].append(
                    {"type": "system", "content": message.content}
                )
            elif isinstance(message, AIMessage):
                final_json["messages"].append(
                    {"type": "ai", "content": message.content}
                )
            else:
                final_json["messages"].append(
                    {"type": "human", "content": message.content}
                )
        return json.dumps(final_json)

    def from_json(self, json_string: str):
        json_dict = json.loads(json_string)
        for message in json_dict["messages"]:
            if message["type"] == "system":
                self.messages.append(SystemMessage(content=message["content"]))
            elif message["type"] == "ai":
                self.messages.append(AIMessage(content=message["content"]))
            else:
                self.messages.append(HumanMessage(content=message["content"]))
        return self

