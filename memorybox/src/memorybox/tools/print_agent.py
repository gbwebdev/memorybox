import socketio
import peripage

from PIL import Image
import io

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
    
    printer = peripage.Printer(data['printer']['mac_address'], peripage.PrinterType[data['printer']['model']])
    printer.connect()
    printer.reset()

    image_data = data['image_data'] # byte values of the image
    image = Image.open(io.BytesIO(image_data))
    image.show()

    printer.setConcentration(1)

    printer.printImage(image)
    printer.printBreak(150)



def run(server: str):
    """Run the agent"""
    # Connect to the Flask-SocketIO server
    sio.connect(server, transports=['websocket'])

    # Keep the client running to listen for events
    sio.wait()
