
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
                language = msg.get('language')
                interview_type = msg.get('interview_type')
                ai_reply =conversation.inititateConversation(voice,history,language,interview_type)
                await websocket.send_json(ai_reply)
            elif type == "reply":
                audio_binary = await websocket.receive_bytes()
                reply = conversation.process_reply(audio_binary)
                await websocket.send_json(reply)
    
    except WebSocketDisconnect: 
        websocket.close(websocket)
        print(f"Client {client_id} disconnected")


    
    

        
