import socketio
import peripage

from PIL import Image
import io

from bluetooth.btcommon import BluetoothError

from pymemorybox.tools.string_processing import remove_accents

def remove_accents(input_str):
    # Normalize the string to decomposed form (NFD)
    nfkd_form = unicodedata.normalize('NFD', input_str)
    
    # Filter out combining characters (accents, etc.)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

# Create a Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print('Connection established')

@sio.event
def disconnect():
    print('Disconnected from server')
    exit(1)

@sio.on('request_print')
def on_print_requested(data):
    print('Print request received')
    sio.emit('agent_response', {
        'request_id': data['request_id'],
        'memory_id': data['memory_id'],
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
            'memory_id': data['memory_id'],
            'status': 100,
            'message': {
                'type': 'info',
                'message': 'Connected to the printer.'
            }
        })
    except BluetoothError as e:
        sio.emit('agent_response', {
            'request_id': data['request_id'],
            'memory_id': data['memory_id'],
            'status': 500,
            'message': {
                'type': 'danger',
                'message': 'Could not connect to the printer ({e})'
            }
        })
        return False
    except Exception as e:
        sio.emit('agent_response', {
            'request_id': data['request_id'],
            'memory_id': data['memory_id'],
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
            'memory_id': data['memory_id'],
            'status': 100,
            'message': {
                'type': 'info',
                'message': 'Picture processed.'
            }
        })
    except Exception as e:
        sio.emit('agent_response', {
            'request_id': data['request_id'],
            'memory_id': data['memory_id'],
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
        if 'captation' in data:
            printer.printBreak(30)
            printer.printlnASCII(remove_accents(data['captation']))
        printer.printBreak(150)
        sio.emit('agent_response', {
            'request_id': data['request_id'],
            'memory_id': data['memory_id'],
            'status': 200,
            'message': {
                'type': 'success',
                'message': 'Memory printed !'
            }
        })
    except Exception as e:
        sio.emit('agent_response', {
            'request_id': data['request_id'],
            'memory_id': data['memory_id'],
            'status': 500,
            'message': {
                'type': 'danger',
                'message': f'Could not print the picture ({e})'
            }
        })
        return False
    printer.disconnect()

def run(server: str, token: str):
    """Run the agent"""
    # Connect to the Flask-SocketIO server
    sio.connect(server, headers={'token': token}, transports=['websocket'])

    # Keep the client running to listen for events
    sio.wait()
