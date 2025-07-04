from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import re
import openai
import os

app = Flask(__name__)
CORS(app)

# OpenAI API key (securely loaded)
openai.api_key = os.getenv("OPENAI_API_KEY")

# MongoDB connection
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
                        "You are IndexValley — a confident, helpful, and fast AI loan assistant. "
                        "You're here to help users check loan eligibility quickly.\n\n"

                        "Here’s how to behave:\n"
                        "- If the user says hi or anything casual, greet them quickly and ask if they want to check eligibility.\n"
                        "- If they mention 'loan', 'money', 'borrow', etc., skip small talk and begin asking:\n"
                        "  1. What kind of loan (personal, home, etc.)\n"
                        "  2. Monthly income (in ₹)\n"
                        "  3. Desired loan amount (in ₹)\n"
                        "  4. Aadhaar number (only after other info; affirm security clearly)\n\n"

                        "- After collecting all, evaluate:\n"
                        "  - loan <= 10x income → approved\n"
                        "  - loan <= 15x income → may require collateral\n"
                        "  - loan > 15x income → reject\n"

                        "- Use this logic to respond and clearly tell them the result.\n"
                        "- Never be robotic or cold. Be brief, helpful, confident.\n"
                        "- Only ask for Aadhaar after loan and income.\n"
                        "- Use friendly tone but don’t waste time.\n\n"

                        "If user gives Aadhaar, say: '✅ Received securely. Evaluating your eligibility now...' and then give result.\n"
                        "Never say: 'How can I help you today?' or anything generic."
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







