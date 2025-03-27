import os
import requests
import yaml
import json
import pandas as pd

DATA_FILE = "./training_data/training_data_v3.csv"

RASA_VERSION = "3.1"
RASA_TRAIN_URL = "http://localhost:5005/model/train"
RASA_LOAD_MODEL_URL = "http://localhost:5005/model"

MODELS_DIR_FROM_APP = "../rasa_server/models"
MODELS_DIR_FROM_RASA_SERVER = "./models"


# Check if model already exists
def does_model_exist():
    if os.path.isdir(MODELS_DIR_FROM_APP):
        files = os.listdir(MODELS_DIR_FROM_APP)
        if len(files) > 0:
            return True
    return False


def train_from_csv():
    SEPARATOR = "|"

    ID = "id"
    SUB_ID = "sub_id"
    KEY = "key"
    VALUE = "value"

    STORY = "story"
    RULE = "rule"
    STEP = "step"
    STEPS = "steps"
    INTENT = "intent"
    ACTION = "action"
    RESPONSE = "response"
    RESPONSE_CONTENT = "response_content"
    EXAMPLE = "example"
    EXAMPLES = "examples"
    ENTITY = "entity"
    TYPE = "type"

    # Rasa model
    intents = []
    entities = []
    slots = {}
    actions = []
    responses = {}
    nlu = []
    stories = []
    rules = []

    # Prepare the data
    df = pd.read_csv(DATA_FILE)
    df = df.dropna()
    df.fillna("", inplace=True)

    groupings = df.groupby(ID)
    for group_id, group in groupings:
        behaviour = {} # A story or rule
        steps = []

        sub_groupings = group.groupby(SUB_ID)
        for sub_id, sub_group in sub_groupings:
            nlu_content = {EXAMPLES: [], TYPE: None}
            response_content = {RESPONSE: None, RESPONSE_CONTENT: []}
            for index, row in sub_group.iterrows():
                key = row[KEY].strip()
                value = row[VALUE].strip()

                if key == STORY or key == RULE:
                    behaviour = {key: value}

                elif key == STEP:
                    value_arr = value.split(SEPARATOR)
                    count = len(value_arr)
                    step = {}
                    if count == 2 and value_arr[0] == INTENT:
                        if value_arr[1] not in intents:
                            intents.append(value_arr[1])
                        step[value_arr[0]] = value_arr[1]
                        nlu_content[value_arr[0]] = value_arr[1]
                        nlu_content[TYPE] = value_arr[0]
                    elif count == 3 and value_arr[0] == ACTION:
                        if value_arr[1] == ACTION and value_arr[2] not in actions:
                            actions.append(value_arr[2])
                        elif value_arr[1] == RESPONSE:
                            response_content[RESPONSE] = value_arr[2]
                        step[value_arr[0]] = value_arr[2]
                    if len(step) > 0:
                        steps.append(step)
                
                elif key == EXAMPLE:
                    nlu_content[EXAMPLES].append("- " + value)
                
                elif key == ENTITY and value not in entities:
                    entities.append(value)
                    slots[value] = {"type": "text", "influence_conversation": False, 
                                    "mappings": [{"type": "from_entity", "entity": value}]}
                
                elif key == RESPONSE:
                    response_content[RESPONSE] = value

                elif key == RESPONSE_CONTENT:
                    response_content[RESPONSE_CONTENT].append({"text": value})

                elif key == INTENT:
                    nlu_content[INTENT] = value

                else:
                    key_arr = key.split(SEPARATOR)
                    if len(key_arr) == 2 and key_arr[0] == "nlu":
                        nlu_content[key_arr[1]] = value
                        nlu_content[TYPE] = key_arr[1]
        
            if nlu_content[TYPE]:
                nlu_key = nlu_content.pop(TYPE, None)
                index = next((i for i, item in enumerate(nlu)
                            if (nlu_key in item) and (item[nlu_key] == nlu_content[nlu_key])), -1)
                if index < 0:
                    examples = "\n".join(nlu_content[EXAMPLES])
                    nlu_content[EXAMPLES] = examples
                    nlu.append(nlu_content)
                else:
                    item = nlu[index]
                    orig_examples = item[EXAMPLES].split("\n")
                    new_examples = [x for x in nlu_content[EXAMPLES] if x not in orig_examples]
                    examples = "\n".join(orig_examples + new_examples)
                    nlu[index][EXAMPLES] = examples
                
            elif response_content[RESPONSE]:
                response_name = response_content[RESPONSE]
                response_lst = response_content[RESPONSE_CONTENT]
                if response_name in responses:
                    response_lst = [x for x in response_lst if x not in responses[response_name]]
                    responses[response_name] += response_lst
                else:
                    responses[response_name] = response_lst
            
        behaviour[STEPS] = steps
        if STORY in behaviour:
            stories.append(behaviour)
        elif RULE in behaviour:
            rules.append(behaviour)

    data = {
        "version": RASA_VERSION,
        "intents": intents,
        "entities": entities,
        "slots": slots,
        "actions": actions,
        "responses": responses,
        "session_config": {
            "session_expiration_time": 60,
            "carry_over_slots_to_new_session": True
        },
        "nlu": nlu,
        "rules": rules,
        "stories": stories
    }

    yaml.add_representer(str, __str_presenter__)
    yaml_data = yaml.dump(data)

    # Send POST request to train the model
    print("Sending POST request to train model...")
    response = requests.post(
        RASA_TRAIN_URL,
        data=yaml_data,
        headers={"Content-Type": "application/yaml"}
    )

    if response.status_code == 200:
        model_name = response.headers["filename"]
        print("Model training completed successfully: " + model_name)

        data = {"model_file": MODELS_DIR_FROM_RASA_SERVER + "/" + model_name}
        json_data = json.dumps(data)

        # Send PUT request to replace the loaded model
        print("Sending PUT request to load model...")
        response = requests.put(
            "http://localhost:5005/model",
            data=json_data,
            headers={"Content-Type": "application/json"}
        ) 

        if response.status_code == 204:
            print("Model loading completed successfully: " + model_name)
            return True
        else:
            print("Model loading failed with status code:", response.status_code)
            return False

    else:
        # Training Failed
        print("Model training failed with status code:", response.status_code)
        print(response.json())
        return False


# Convert the Python object to YAML
def __str_presenter__(dumper, data_str):
    if len(data_str.splitlines()) > 1: # Check for multi-line string
        return dumper.represent_scalar('tag:yaml.org,2002:str', data_str, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data_str)

