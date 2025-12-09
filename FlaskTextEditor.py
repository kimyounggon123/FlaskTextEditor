# cd C:\Users\gram\Desktop\flask
# py FlaskTextEditor.py
from flask import Flask, render_template, request, jsonify, send_file
from Grammar.GrammarManager import GrammarManager
from docx import Document
from dotenv import load_dotenv
import tempfile
import os
app = Flask(__name__) 

# GrammarManager 인스턴스 생성 
api_key = os.getenv("OPENAI_API_KEY")
grammar = GrammarManager(api_key=api_key)


@app.route("/", methods=["GET", "POST"])
def editor():
    content = ""

    if request.method == "POST":
        action = request.form.get("action")
        content = request.form.get("editor")

        if action == "save":
            print("💾 Save pressed!")
            return render_template("textEditor.html", content=content)

        elif action == "grammar":
            print("📝 Grammar check pressed!")
            corrected = grammar.check(content, "basic", "kr")
            return render_template("textEditor.html", content=corrected)

    return render_template("textEditor.html", content=content)


@app.route("/check", methods=["POST"])
def check():
    data = request.json
    text = data.get("text", "")
    level = data.get("level", "basic")
    lang = data.get("lang", "kr")

    corrected = grammar.check(text, level, lang)
    return jsonify({"corrected": corrected})

if __name__ == "__main__":
    app.run(host = "localhost", port= 1000, debug=True)