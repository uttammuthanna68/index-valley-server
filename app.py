from flask import Flask, request, jsonify
from flask_cors import CORS
import openai, os

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are IndexValley, a helpful AI bank assistant."},
            {"role": "user", "content": user_msg}
        ]
    )
    return jsonify({"reply": response.choices[0].message["content"]})

if __name__ == "__main__":
    app.run(debug=True)

