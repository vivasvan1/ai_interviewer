from datetime import datetime, timezone
from typing import List
from langchain.schema import BaseMessage, SystemMessage, AIMessage, HumanMessage
from langchain.memory import ChatMessageHistory
import json


class ChatMessageHistoryWithJSON(ChatMessageHistory):
    timestamps: List[str]

    def clear(self) -> None:
        self.timestamps.clear()
        return super().clear()

    def add_message(self, message: BaseMessage) -> None:
        self.timestamps.append(datetime.now(timezone.utc).astimezone().isoformat())
        return super().add_message(message)

    def add_ai_message(self, message: str) -> None:
        self.timestamps.append(datetime.now(timezone.utc).astimezone().isoformat())
        return super().add_ai_message(message)

    def add_user_message(self, message: str) -> None:
        self.timestamps.append(datetime.now(timezone.utc).astimezone().isoformat())
        return super().add_user_message(message)

    def to_json(self):
        final_json = {"messages": []}
        for index, message in enumerate(self.messages):
            if isinstance(message, SystemMessage):
                final_json["messages"].append(
                    {
                        "type": "system",
                        "content": message.content,
                        "timestamp": self.timestamps[index],
                    }
                )
            elif isinstance(message, AIMessage):
                final_json["messages"].append(
                    {
                        "type": "ai",
                        "content": message.content,
                        "timestamp": self.timestamps[index],
                    }
                )
            else:
                final_json["messages"].append(
                    {
                        "type": "human",
                        "content": message.content,
                        "timestamp": self.timestamps[index],
                    }
                )
        return json.dumps(final_json)

    def from_json(self, json_string: str):
        self.clear()
        json_dict = json.loads(json_string)
        for message in json_dict["messages"]:
            self.timestamps.append(message["timestamp"])
            if message["type"] == "system":
                self.messages.append(SystemMessage(content=message["content"]))
            elif message["type"] == "ai":
                self.messages.append(AIMessage(content=message["content"]))
            else:
                self.messages.append(HumanMessage(content=message["content"]))
        return self
