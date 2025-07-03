from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import re
import openai
import os

app = Flask(__name__)
CORS(app)
openai.api_key = os.getenv("OPENAI_API_KEY")

client = MongoClient("mongodb+srv://uttam:Uttam68%40@cluster0.etz2rpp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["index_valley"]
customers = db["customers"]

@app.route("/validate_name", methods=["POST"])
def validate_name():
    data = request.json
    name = data.get("name", "")
    if not re.match(r"^[a-zA-Z\s]+$", name):
        return jsonify({"valid": False, "message": "Invalid name format"})
    return jsonify({"valid": True})

@app.route("/submit_user", methods=["POST"])
def submit_user():
    data = request.json
    customers.insert_one(data)
    return jsonify({"status": "success"})

@app.route("/check_eligibility", methods=["POST"])
def check_eligibility():
    income = float(request.json.get("income", 0))
    requested = float(request.json.get("loan_amount", 0))

    if requested > 15 * income:
        return jsonify({"eligible": False, "message": "Requested loan is too high."})
    elif requested <= 10 * income:
        return jsonify({"eligible": True, "message": "Eligible for requested loan."})
    else:
        return jsonify({"eligible": "partial", "message": "May require collateral."})

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are IndexValley, a smart and friendly banking assistant. Answer user questions about loan eligibility, documents, interest rates, or process clearly. Only ask the user essential details like Aadhaar and income. Avoid overexplaining or asking unnecessary follow-up questions. Be concise and confident like a real bank assistant."
            },
            {"role": "user", "content": user_msg}
        ]
    )

    bot_reply = response.choices[0].message["content"]
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
