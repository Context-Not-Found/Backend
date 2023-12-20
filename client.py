# Client to test socketio connection
import socketio

# url = [
#     "http://localhost:8000?ticket_id=5",
#     "/tickets",
# ]  # Ticket Chat room URL
url = [
    "http://localhost:8000",
    "/community_chat",
]  # Community_chat URL

sio = socketio.Client()


# Event handler for connection established
@sio.event
def connect():
    print(f"Connected to {url[1]} namespace")

    # Send the message when connected
    message = "Hey!"
    sio.send(message, namespace=url[1])
    print(f"Sent message: {message}")


# Event handler for message
@sio.event
def message(data):
    print(f"Received message from server: {data}")


# Event handler for disconnection
@sio.event
def disconnect():
    print(f"Disconnected from {url[1]} namespace")


# Connect to the server
sio.connect(
    url[0],
    namespaces=[url[1]],
    auth={
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiZXhwIjoxNzAzNzE4NzY1fQ._u_wUOl42c3FkHlGW9WWLC2_2fkLuWq88yLE37p1CUU"
    },
)

# Keep the script running to handle events
sio.wait()
