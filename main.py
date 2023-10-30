from Analizadores.analizador_sintactico import parse
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from utils import *
import boto3
import os
from dotenv import load_dotenv

load_dotenv()
aws_access_key_id = os.getenv("KEY_ID")
aws_secret_access_key = os.getenv("SECRET_KEY")
bucket_name = os.getenv("BUCKET_NAME")

app = Flask(__name__)
CORS(app)

@app.route('/execute', methods=['POST'])
@cross_origin()
def execute():
    entrada = request.json['entrada']

    # ejecutar linea por linea el contenido que se recibe
    for line in entrada.splitlines():
        #print ("ESTA ES LA LINEA")
        parse(line)

    print("SALIDA GENERADA", salida)

    return jsonify(salida)

@app.route('/ping', methods=['GET'])
@cross_origin()
def ping():
    return jsonify({'response': 'pong!'})


if __name__ == '__main__':
    app.run(debug=True)