from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import re
import openai
import os

app = Flask(__name__)
CORS(app)

# Load OpenAI API Key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Connect to MongoDB
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

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are IndexValley — a fast, smart, no-nonsense AI loan assistant. "
                        "Your job is to help users get their loan eligibility quickly. "
                        "Always skip generic greetings. Never ask vague questions. "
                        "If the user mentions anything about loans, immediately ask for:\n"
                        "1. Aadhaar number (and confirm it's encrypted and secure)\n"
                        "2. Monthly or yearly income\n"
                        "3. Desired loan amount\n\n"
                        "Then:\n"
                        "- Check eligibility logically (loan <= 10x income = approved, <=15x = maybe, else = rejected)\n"
                        "- Tell them exactly how much they can borrow\n"
                        "- Be brief, clear, and helpful — like a fintech chatbot\n\n"
                        "Never say things like 'how can I help you today?' or 'tell me more about your query'."
                    )
                },
                {"role": "user", "content": user_msg}
            ]
        )

        bot_reply = response.choices[0].message.content
        return jsonify({"reply": bot_reply})

    except Exception as e:
        print("💥 Error in /chat route:", e)
        return jsonify({"reply": "Sorry, something went wrong."}), 500

if __name__ == "__main__":
    app.run(debug=True)






