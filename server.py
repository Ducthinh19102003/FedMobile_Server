import flask
import requests

app = flask.Flask(__name__)

#Display connection status
@app.route('/check',  methods=['GET'])
def check_connection():
    return "Successfully Connected"

if __name__=='__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)