
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.agent.simple import process_user_response
from src.history.ChatMessageHistory import ChatMessageHistoryWithJSON
from src.processing.tts import do_text_to_speech
from src.utils.audio import convert_audio_to_base64
from src.utils.conversation import Conversation
from src.utils.websocketManager import WebSocketManager

# Create a new APIRouter instance for the conversation
router = APIRouter()

@router.websocket("/ws")
async def conversation_endpoint(websocket: WebSocket):

    await websocket.accept()
    
    client_id = str(websocket.client)
    conversation = Conversation()
    try:
        while True:
            
            msg = await websocket.receive_json()
            type = msg.get('type')
            if type == 'initial':
                print("Recieved initiate call")
                voice = msg.get('voice')
                history = msg.get('history')
                conversation.inititateConversation(voice,history)
                welcome_message = conversation.getWelcomeMessage()
                await websocket.send_json(welcome_message)
            elif type == "reply":
                print("recieved reply")
                audio_binary = await websocket.receive_bytes()
                reply = conversation.process_reply(audio_binary)
                await websocket.send_json(reply)
    
    except WebSocketDisconnect: 
        websocket.close(websocket)
        print(f"Client {client_id} disconnected")


    
    

        
