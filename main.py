from fastapi import FastAPI
from configuration.database import init_database_migrations


from handlers import auth, tickets, chatbot, sos, community_chat, areas
from utils import sio, socketio
from configuration.pinecone import init_pinecone

# Apply all changes to DB
init_database_migrations()

# Initialize Pinecone
init_pinecone()

fast_api_app = FastAPI(swagger_ui_parameters={"syntaxHighlight": True})
fast_api_app.include_router(auth.router)
fast_api_app.include_router(tickets.router)
fast_api_app.include_router(chatbot.router)
fast_api_app.include_router(sos.router)
fast_api_app.include_router(community_chat.router)
fast_api_app.include_router(areas.router)

sio.register_namespace(community_chat.CommunityChatNamespace("/community_chat"))
sio.register_namespace(tickets.TicketChatNamespace("/tickets"))
sio.instrument(
    auth={"username": "admin", "password": "admin"}
)  # TODO: Conditionally add this in dev mode
app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=fast_api_app)
