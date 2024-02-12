from datetime import datetime, timezone
from typing import List
from langchain.schema import BaseMessage, SystemMessage, AIMessage, HumanMessage
from langchain.memory import ChatMessageHistory
import json


class ChatMessageHistoryWithJSON(ChatMessageHistory):
    timestamps: List[str] = []
    feedbacks: List[str] = []

    def __init__(self, timestamps: List[str] = None, feedbacks: List[str] = None):
        super().__init__()
        self.timestamps = timestamps if timestamps is not None else []
        self.feedbacks = feedbacks if feedbacks is not None else []

    def clear(self) -> None:
        self.timestamps.clear()
        self.feedbacks.clear()
        return super().clear()

    def add_message(self, message: BaseMessage) -> None:
        self.timestamps.append(datetime.now(timezone.utc).astimezone().isoformat())
        self.feedbacks.append(None)
        return super().add_message(message)

    def add_ai_message(self, message: str) -> None:
        self.timestamps.append(datetime.now(timezone.utc).astimezone().isoformat())
        self.feedbacks.append(None)
        return super().add_ai_message(message)

    def add_user_message(self, message: str) -> None:
        self.timestamps.append(datetime.now(timezone.utc).astimezone().isoformat())
        self.feedbacks.append(None)
        return super().add_user_message(message)

    def add_feedback_to_message(self, index: int, feedback: str) -> None:
        if index < -len(self.feedbacks) or index >= len(self.feedbacks):
            raise IndexError(
                "index out of range: index = "
                + str(index)
                + ", len = "
                + str(len(self.feedbacks))
            )

        self.feedbacks[index] = feedback
        return

    def to_json(self):
        """Convert the chat history to a JSON-formatted string.

        This method organizes the chat history into a structured JSON format, including message content, type, and timestamp.

        Returns:
            str: A JSON-formatted string representing the chat history.
        """
        # Initialize a dictionary to hold the final JSON structure
        final_json = {"messages": []}
        # Loop through each message and its index in the chat history
        for index, message in enumerate(self.messages):
            # Create a dictionary for each message's details
            message_details = {
                "content": message.content,  # Message content
                "timestamp": self.timestamps[index],  # Corresponding timestamp
                "feedback": self.feedbacks[index],  # Feedback for the user
            }
            # Classify the message type based on its instance
            if isinstance(message, SystemMessage):
                message_details["type"] = "system"
            elif isinstance(message, AIMessage):
                message_details["type"] = "ai"
            else:
                message_details["type"] = "human"

            # Append each message's details to the final JSON's "messages" list
            final_json["messages"].append(message_details)
        # Convert the final JSON dictionary to a JSON-formatted string and return it
        return json.dumps(final_json)

    def from_json(self, json_string: str):
        self.clear()
        json_dict = json.loads(json_string)
        for message in json_dict["messages"]:
            self.timestamps.append(message["timestamp"])
            self.feedbacks.append(
                message.get("feedback", None)
            )  # Use get with a default value

            if message["type"] == "system":
                self.messages.append(SystemMessage(content=message["content"]))
            elif message["type"] == "ai":
                self.messages.append(AIMessage(content=message["content"]))
            else:
                self.messages.append(HumanMessage(content=message["content"]))
        return self
