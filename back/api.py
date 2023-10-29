from Analizadores.analizador_sintactico import parse
from flask import Flask, jsonify, request
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

@app.route('/execute', methods=['POST'])
def execute():
    entrada = request.json['entrada']
    start = time.time()
    salida = parse(entrada)
    end = time.time()
    print(f"Tiempo de ejecucion: {end-start}")
    return jsonify(salida)

if __name__ == '__main__':
    app.run(debug=True)