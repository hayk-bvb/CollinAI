from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    return jsonify({'you_sent': data})
