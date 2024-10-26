from flask import Flask, request, jsonify
from flask_cors import CORS
from translation_model import get_translation

#app instance
app = Flask(__name__)
CORS(app)   # Lets Next JS app make requests to the server

@app.route('/', methods=['GET'])
def hello():
    return jsonify(message="Hello world!")

@app.route('/api/dx/send_text', methods =['POST'])
def dx_test():
    return jsonify(message="Text received.")


@app.route('/api/dx/send_picture', methods = ['POST'])
def dx_picture():
    return jsonify(message="Photo received.")

@app.route('/api/translation', methods = ['POST'])
def translation():
    data = request.json
    input_text = data.get('input_text', '') # defaults to empty string is input_text unavailable
    
    translated_text = get_translation(input_text) # translate the text with LLM model here
    return jsonify({"translated_text" : "Translated text"})

if __name__ == '__main__':
    app.run(debug=True, port=8080)
