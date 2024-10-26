import os
import torch
from torchvision import transforms
import aivm_client as aic
import numpy as np

from flask import Flask, request, jsonify
from flask_cors import CORS
from translation_model import get_translation
from PIL import Image

#app instance
app = Flask(__name__)
CORS(app)   # Lets Next JS app make requests to the server
app.config['UPLOAD_FOLDER'] = 'uploads'

DIAGNOSIS_CLASSIFIER_MODEL = "DIAGNOSIS_CLASSIFIER"
ALZHEIRMERS_CLASSIFIER_MODEL = "ALZHEIRMER_IMG_CLASSIFIER"


def load_models():
    """
    Load the classifier models into the blockchain
    """
    
    print("Loading the models... ")
    #load tiny bert model
    try:
        aic.upload_bert_tiny_model(
            "./saved-models/diagnosis-classifier.onnx", DIAGNOSIS_CLASSIFIER_MODEL)
    except Exception:
        print("Diagnosis text classifier already exists")

    # load LeNet image classifier
    try:
        aic.upload_lenet5_model(
            "./saved-models/alzheimer-image-classifier.pth", ALZHEIRMERS_CLASSIFIER_MODEL)
    except Exception:
        print("Alzheimer's image classifier already exists")
        
        
@app.route('/', methods=['GET'])
def hello():
    return jsonify(message="Hello world!")

@app.route('/api/dx/send_text', methods=['POST'])
def dx_text():
    symptoms = request.json.get('symptoms', '')
    labels = [
        "drug reaction",
        "allergy",
        "chicken pox",
        "diabetes",
        "psoriasis",
        "hypertension",
        "cervical spondylosis",
        "bronchial asthma",
        "varicose veins",
        "malaria",
        "dengue",
        "arthritis",
        "impetigo",
        "fungal infection",
        "common cold",
        "gastroesophageal reflux disease",
        "urinary tract infection",
        "typhoid",
        "pneumonia",
        "peptic ulcer disease",
        "jaundice",
        "migraine"
    ]
    
    #perform secure inference using Nillium's aivm
    try:
        tokens = aic.tokenize(symptoms,)
        encrypted_tokens = aic.BertTinyCryptensor(*tokens)
        result = aic.get_prediction(encrypted_tokens, DIAGNOSIS_CLASSIFIER_MODEL)
        probs = torch.nn.functional.softmax(result[0])
    except Exception:
        print("Error performing inference with AIVM")
        return jsonify({
            "message": "Error performing inference with AIVM"
        }), 400
    
    #pair each label with its probability
    label_probs = list(zip(labels, probs.tolist()))
    
    #sort by probability in descending order and get the top 3
    top_4 = sorted(label_probs, key=lambda x: x[1], reverse=True)[:4]
    
    #format the response as a JSON object
    response = {
        "predictions": [
            {"label": label, "probability": prob} for label, prob in top_4
        ]
    }
    
    return jsonify(response), 200
    
    
    

@app.route('/api/dx/send_picture', methods=['POST'])
def dx_picture():
    image = request.files.get('image')

    if image:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(image_path)
        with Image.open(image_path) as image:
            try:
                labels = [
                        "Mild demented",
                        "Moderate demented",
                        "Non demented",
                        "Very mild demented"
                ]

                # pytorch transformation to make image ready for model
                transform = transforms.Compose([
                    transforms.ToPILImage(),
                    transforms.Resize((28, 28)),  # Resize to 28x28
                    transforms.Grayscale(num_output_channels=1),  # Convert to grayscale
                    transforms.ToTensor(),  # Convert image to Tensor
                    transforms.Normalize((0.5,), (1.0,))
                ])
                img_tensor = transform(np.array(image))

                # encrypt image tensor
                encrypted_input = aic.LeNet5Cryptensor(img_tensor.reshape(1, 1, 28, 28))
                label_cls = torch.argmax(aic.get_prediction(encrypted_input, ALZHEIRMERS_CLASSIFIER_MODEL)[0])
            except Exception as e:
                print(e)
                return jsonify({
                    "message": "Error getting model prediction"
                })

            os.remove(image_path)
            
            # return string 
            return jsonify({
                "prediction": labels[label_cls]
            }), 200
    else:
        return jsonify({
            "message": "Error getting model prediction"
        }), 400


@app.route('/api/translation', methods=['POST'])
def translation():
    data = request.json
    input_text = data.get('input_text', '') # defaults to empty string is input_text unavailable
    
    translated_text = get_translation(input_text) # translate the text with LLM model here
    return jsonify({"translated_text" : translated_text})

if __name__ == '__main__':
    load_models()
    app.run(debug=True, port=8080)
