import json
import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/rasa', methods=['POST'])
def get_rasa_response():
    req_data = request.get_json()
    if 'message' in req_data:
        message = req_data['message']
    else:
        return json.dumps({})

    payload = json.dumps({'sender': 'Rasa', 'message': message})
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.request('POST', url='http://localhost:5005/webhooks/rest/webhook', headers=headers, data=payload)
    # TODO: Check for status code
    response = response.json()
    return response

if __name__ == "__main__":
    app.run(debug=True)
