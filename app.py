from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import re
import openai
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set OpenAI API Key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# MongoDB Atlas connection
client = MongoClient("mongodb+srv://uttam:Uttam68%40@cluster0.etz2rpp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["index_valley"]
customers = db["customers"]

# Route 1: Validate name
@app.route("/validate_name", methods=["POST"])
def validate_name():
    data = request.json
    name = data.get("name", "")
    if not re.match(r"^[a-zA-Z\s]+$", name):
        return jsonify({"valid": False, "message": "Invalid name format"})
    return jsonify({"valid": True})

# Route 2: Save user info to MongoDB
@app.route("/submit_user", methods=["POST"])
def submit_user():
    data = request.json
    customers.insert_one(data)
    return jsonify({"status": "success"})

# Route 3: Loan eligibility check
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

# Route 4: AI Chat with OpenAI
@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are IndexValley, a helpful and friendly AI banking assistant. "
                        "Answer questions about loan eligibility, documents, or process clearly. "
                        "Avoid overexplaining, be concise."
                    )
                },
                {"role": "user", "content": user_msg}
            ]
        )
        bot_reply = response.choices[0].message["content"]
        return jsonify({"reply": bot_reply})

    except Exception as e:
        print("💥 Error in /chat route:", str(e))
        return jsonify({"reply": "Sorry, something went wrong."}), 500

# Start the app
if __name__ == "__main__":
    app.run(debug=True)




