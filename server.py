from flask import Flask, session, render_template
import yaml
import firebase_admin
from firebase_admin import credentials, db, messaging, storage

with open("config.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    
cred = credentials.Certificate("certificate.json")
firebase_admin.initialize_app(cred, {'storageBucket' : 'fedmobile-7362c.appspot.com'})

current_round = 1
n_completed_clients = 0
def upload_model():
    file_path = config['global_model']
    bucket = storage.bucket()
    uploaded_file_name = f"{config['project_name']}/Round_{str(current_round)}/global_model_.bin"
    blob = bucket.blob(uploaded_file_name)
    blob.upload_from_filename(file_path)

app = Flask(__name__, template_folder='template')
@app.route('/')
def home():
    # Retrieve the connected devices from the session
    connected_clients = session.get('connected_devices', [])
    return render_template('connected_client.html', connected_clients=connected_clients)

@app.route('/connect/<client_id>', methods=['POST'])
def connect(client_id):
    # Retrieve the connected devices from the session
    connected_clients = session.get('connected_devices', [])
    if client_id not in connected_devices:
        # Add the new device to the connected devices list
        connected_devices.append(client_id)
        session['connected_devices'] = connected_devices
        return f"Sucessful connectected to project {cofig[project_name]}"
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

if __name__ == '__main__':
    model_file_path = config['global_model']
    upload_model()
    app.run(host="0.0.0.0", port=8080, debug=True)
