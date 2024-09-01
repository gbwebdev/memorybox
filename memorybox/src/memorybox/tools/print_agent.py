import socketio

# Create a Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print('Connection established')

@sio.event
def disconnect():
    print('Disconnected from server')

@sio.on('notify_agent')
def on_notify_agent(data):
    print('Received notification from server:', data['message'])
    # Perform actions in response to the notification


@sio.on('request_print')
def on_button_clicked(data):
    print('Print request received')
    
    # Perform actions in response to the notification



def run(server: str):
    """Run the agent"""
    # Connect to the Flask-SocketIO server
    sio.connect(server, transports=['websocket'])

    # Keep the client running to listen for events
    sio.wait()
