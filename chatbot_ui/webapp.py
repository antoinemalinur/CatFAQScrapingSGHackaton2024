from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route("/")
def index():
    """Render the main web page."""
    return render_template("index.html")

@app.route("/api/answer", methods=["POST"])
def answer():
    """
    Local API to process a question and return an answer.
    """
    data = request.get_json()
    question = data.get("question", "")

    # Example logic to generate an answer
    if question.lower() == "what is ai?":
        answer = "AI stands for Artificial Intelligence."
    elif question.lower() == "who is the smartest cat?":
        answer = "The smartest cat is the one asking the right questions!"   
    elif question.lower() == "what is the cat report?":
        answer = "The Consolidated Audit Trail (CAT) is a system that tracks trading activity for options and equities listed on US exchanges. The CAT is a key regulatory tool used by regulators to monitor broker-dealers and detect potential violations."
    else:
        answer = f"Great question: '{question}'. Unfortunately, I don't have an answer."

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
