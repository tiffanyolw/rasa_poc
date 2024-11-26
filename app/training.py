from common.training_data_v3 import does_model_exist, train_from_csv

# Train the model and load it if no model exists
TRAIN_MODEL = False
if TRAIN_MODEL or (not does_model_exist()):
    print("No trained model found, training a new model...")
    train_from_csv()
else:
    print("Trained model already exists")