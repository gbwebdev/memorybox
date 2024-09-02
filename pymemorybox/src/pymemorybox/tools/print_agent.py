import socketio
import peripage

from PIL import Image
import io

from bluetooth.btcommon import BluetoothError

# Create a Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print('Connection established')

@sio.event
def disconnect():
    print('Disconnected from server')

@sio.on('request_print')
def on_button_clicked(data):
    print('Print request received')
    sio.emit('agent_response', {
        'request_id': data['request_id'],
        'status': 100,
        'message': {
            'type': 'info',
            'message': 'Agent received the print request.'
        }
    })
    
    try:
        printer = peripage.Printer(data['printer']['mac_address'], peripage.PrinterType[data['printer']['model']])
        printer.connect()
        printer.reset()
        sio.emit('agent_response', {
            'request_id': data['request_id'],
            'status': 100,
            'message': {
                'type': 'info',
                'message': 'Connected to the printer.'
            }
        })
    except BluetoothError as e:
        sio.emit('agent_response', {
            'request_id': data['request_id'],
            'status': 500,
            'message': {
                'type': 'danger',
                'message': 'Could not connect to the printer.'
            }
        })
        return False
    except Exception as e:
        sio.emit('agent_response', {
            'request_id': data['request_id'],
            'status': 500,
            'message': {
                'type': 'danger',
                'message': f'Could not connect to the printer ({e})'
            }
        })
        return False

    try:
        image_data = data['image_data'] # byte values of the image
        image = Image.open(io.BytesIO(image_data))
        image.show()
        sio.emit('agent_response', {
            'request_id': data['request_id'],
            'status': 100,
            'message': {
                'type': 'info',
                'message': 'Picture processed.'
            }
        })
    except Exception as e:
        sio.emit('agent_response', {
            'request_id': data['request_id'],
            'status': 500,
            'message': {
                'type': 'danger',
                'message': f'Could not process the picture ({e})'
            }
        })
        return False
    
    try:
        printer.setConcentration(1)
        printer.printImage(image)
        printer.printBreak(150)
        sio.emit('agent_response', {
            'request_id': data['request_id'],
            'status': 200,
            'message': {
                'type': 'success',
                'message': 'Memory printed !'
            }
        })
    except Exception as e:
        sio.emit('agent_response', {
            'request_id': data['request_id'],
            'status': 500,
            'message': {
                'type': 'danger',
                'message': f'Could not print the picture ({e})'
            }
        })
        return False
    printer.disconnect()

def run(server: str):
    """Run the agent"""
    # Connect to the Flask-SocketIO server
    sio.connect(server, transports=['websocket'])

    # Keep the client running to listen for events
    sio.wait()
