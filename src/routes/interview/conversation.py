
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.utils.conversation import Conversation

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
                voice = msg.get('voice')
                history = msg.get('history')
                ai_reply =conversation.inititateConversation(voice,history)
                await websocket.send_json(ai_reply)
            elif type == "reply":
                print("recieved reply")
                audio_binary = await websocket.receive_bytes()
                reply = conversation.process_reply(audio_binary)
                await websocket.send_json(reply)
    
    except WebSocketDisconnect: 
        websocket.close(websocket)
        print(f"Client {client_id} disconnected")


    
    

        