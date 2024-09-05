import socketio
import peripage

from PIL import Image
import io
import time

from bluetooth.btcommon import BluetoothError


def split_image_into_chunks(image_data):
    image = Image.open(io.BytesIO(image_data))
    image.show()

    # Get the dimensions of the image
    img_width, img_height = image.size

    if img_height > img_width*1.6 :
        chunk_height =  int(img_height / 3)
    elif img_height > img_width*1.2 :
        chunk_height =  int(img_height / 2)
    
    # Initialize the starting y coordinate
    y_start = 0
    
    # List to hold chunks
    chunks = []
    
    # Loop through the image and create chunks
    while y_start < img_height:
        # Calculate the ending y coordinate
        y_end = min(y_start + chunk_height, img_height)
        
        # Create the crop box (left, upper, right, lower)
        box = (0, y_start, img_width, y_end)
        
        # Crop the image
        chunk = image.crop(box)

        if y_end != y_start:
            # Append the chunk to the list
            chunks.append(chunk)
        
        # Increment the y coordinate
        y_start += chunk_height
    
    return chunks


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
        chunks = split_image_into_chunks(image_data)
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
        sio.emit('agent_response', {
            'request_id': data['request_id'],
            'memory_id': data['memory_id'],
            'status': 100,
            'message': {
                'type': 'info',
                'message': 'Printing.'
            }
        })
        for i, chunk in enumerate(chunks):
            printer.printImage(chunk)
            if i < len(chunks) - 1:
                time.sleep(30)
        if 'captation' in data:
            printer.printBreak(30)
            printer.printlnASCII(data['captation'])
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
