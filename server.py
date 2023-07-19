from flask import Flask, session, render_template
import requests
import yaml
import firebase_admin
import uuid
import numpy as np
from firebase_admin import credentials, db, messaging, storage

with open("config.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    
cred = credentials.Certificate("certificate.json")
firebase_admin.initialize_app(cred, {'storageBucket' : 'fedmobile-e05c2.appspot.com'})

current_round = 1
n_completed_clients = 0

def upload_model():
    file_path = config['global_model']
    bucket = storage.bucket()
    uploaded_file_name = f"{config['project_name']}/Round_{str(current_round)}/global_model.bin"
    blob = bucket.blob(uploaded_file_name)
    blob.upload_from_filename(file_path)

app = Flask(__name__, template_folder='template')

key = uuid.uuid4().hex
app.config['SECRET_KEY']=key

@app.route('/')
def home():
    # Retrieve the connected devices from the session
    connected_clients = session.get('connected_clients', [])
    return render_template('connected_client.html', connected_clients=connected_clients)

@app.route('/connect/<client_id>', methods=['POST', 'GET'])
def connect(client_id):
    # Retrieve the connected devices from the session
    connected_clients = session.get('connected_devices', [])
    if client_id not in connected_clients:
        # Add the new device to the connected devices list
        connected_clients.append(client_id)
        session['connected_clients'] = connected_clients
        return f"Successful connectected to project {config['project_name']}"
    else:
        return f"Client {client_id} is already connected. Choose different client_ID!"

@app.route('/disconnect/<client_id>', methods=['POST'])
def disconnect(client_id):
    # Retrieve the connected devices from the session
    connected_devices = session.get('connected_devices', [])
    
    if client_id in connected_devices:
        # Remove the device from the connected devices list
        connected_devices.remove(client_id)
        session['connected_devices'] = connected_devices
    
    return f"Device {client_id} disconnected successfully."

@app.route('/notification', methods=['POST'])
def receive_notification():
    global current_round, n_completed_clients
    
    client_id = requests.form.get('client_id')
    message = requests.form.get('message')
    
    print(f"Training completion notification from client {client_id}: {message}")
    
    model_weights[client_id] = get_model_weights_from_client(client_id)
    
    n_completed_clients += 1

    if n_completed_clients == len(session.get('connected_devices', [])):
        number_clients = n_completed_clients
        model_weights = [0 for i in range(number_clients)]
        for i in range(number_clients):
            model_weights[i] = get_model_weights_from_client(i+1)
        federated_averaging(model_weights)
        current_round += 1
        n_completed_clients =0
        upload_model()
        send_model_update_notification(current_round)

    return "Notification received"

def update_model_weights():
    global current_round, n_completed_clients
    number_clients = 10
    model_weights = [0 for i in range(number_clients)]
    for i in range(number_clients):
        model_weights[i] = get_model_weights_from_client(i+1)
    federated_averaging(model_weights)
    current_round += 1
    n_completed_clients =0
    upload_model()
    print(f'Model weights round {current_round} updated successfully.')
    
def get_model_weights_from_client(client_id):
    bucket = storage.bucket()
    file_path = f"{config['project_name']}/Round_{str(current_round)}/client_{str(client_id)}_weights.bin"
    blob = bucket.blob(file_path)

    # Download the weights file
    blob.download_to_filename('temp_weights.bin')

    # Read the weights from the file and convert to NumPy array
    weights = np.fromfile("temp_weights.bin", dtype=np.float64)

    print(weights)
    print(f"Model weights received from client {client_id}")
    return weights

def federated_averaging(model_weights):
    # Perform federated averaging
    averaged_weights = np.mean(model_weights, axis=0)

    # Save averaged weights to a binary file
    averaged_weights.tofile( config['global_model'])
    print("Averaged weights saved to Global_model.bin")


def send_model_update_notification(round_number):
    connected_clients = session.get('connected_devices', [])
    for client_id in connected_clients:
        message = messaging.Message(
            notification=messaging.Notification(
                title='Model Update',
                body=f"The model weights for round {round_number} have been updated. Load the new weights and continue training."
            ),
            token=get_client_device_token(client_id)
        )
        response = messaging.send(message)
        print(f"Model update notification sent to client {client_id}: {response}")

def get_client_device_token(client_id):
    ref = db.reference(f"clients/{client_id}/device_token")
    device_token = ref.get()
    return device_token

def update_weights_in_model(model_path, weights):
    with open(model_path, 'wb') as f:
        f.write(weights)
        
        
if __name__ == '__main__':
    # model_file_path = config['global_model']
    # upload_model()
    app.run(host="0.0.0.0", port=8080, debug=True)
    
