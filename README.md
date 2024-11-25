# NLU Integration

## Usage

### RASA Server
Navigate to the rasa_server folder
```bash
cd .../rasa_server
```

Start the [actions server](https://rasa.com/docs/rasa/action-server/running-action-server/).
```bash
rasa run actions
```

Start the rasa server to enable [API](https://rasa.com/docs/rasa/http-api/) endpoints.
```bash
rasa run --enable-api
```

## Train the Data
Navigate to the `app` folder
```bash
cd .../app
```

Run `training.py`
```bash
python training.py
```

## Flask App
Navigate to `app` folder
```bash
cd .../app
```

Start the Flask app by running `app.py`
```bash
python app.py
```

## Example
Send a request to the Flask app.
Example Request:
```bash
curl -i -X POST -H "Content-Type application/json" -d "{\"message\" : \"what is the tempertature in New York\"}" http://127.0.0.1:5000/rasa
```
Example Response:
```bash
HTTP/1.1 200 OK
Server: Werkzeug/3.0.1 Python/3.9.6
Date: Thu, 08, Feb 2024 18:31:53 GMT
Content-Type: application/json
Content-Length: 80
Connection: close

[
    {
        "recipient_id": "Rasa",
        "text": "temperature, location=New York"
    }
]
```

## CSV Training Data
The csv file will contain 4 columns: id, sub_id, key, and value.

One story or rule will share the same **id** and the steps are numbers with ther **sub_id**.
For an intent, the **value** will be `intent|[name of the intent]`.
For an action, the **value** will be `action|[action or response]|[name of the action or response]`.

id|sub_id|key|value
---|---|---|---
1|0|story|story_name
1|1|step|intent&#124;intent_name
1|2|step|action&#124;action&#124;action_name

When the **id** is 0, this means that the key value are not bound to any story or rule.

Example: A *response* may not be directly bound to a story or rule and is instead called in an action function. In this case, the **id** can be set to 0.

The **id** and **sub_id** link the row data.

Example: An *entity*, `entity_name`. is detected using a regex, and the regex pattern is `&\d*$`.

id|sub_id|key|value
---|---|---|---
0|1|response|utter_response
0|2|entity|entity_name
0|2|nlu&#124;regex|entity_name
0|2|example|&\d*$

The intent or response can be specified with an **id** 0 (not bounded to any story or rule) and the list values can reference that **id** and **sub_id**. Alternatively, it can reference **id** and **sub_id** of the step it is included in.

Example: `my_response` is the *response_content* for the *resposne*, `utter_response`.
`my intent example` is an *example* for the *intent*, `intent_name`.

id|sub_id|key|value
---|---|---|---
1|0|story|story_name_1
1|1|step|intent&#124;intent_name
2|0|story|story_name_2
2|1|step|intent&#124;intent_name
1|1|example|example 1
2|1|example|example 2
