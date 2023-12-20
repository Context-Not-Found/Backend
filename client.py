# Client to test socketio connection
import socketio

# url = [
#     "http://localhost:8000?ticket_id=1&user_id=5",
#     "/tickets",
# ]  # Ticket Chat room URL
url = [
    "http://localhost:8000?user_id=7",
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
sio.connect(url[0], namespaces=[url[1]])

# Keep the script running to handle events
sio.wait()
