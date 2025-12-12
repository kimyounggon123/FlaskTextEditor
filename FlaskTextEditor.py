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
grammar = GrammarManager('en-US')


@app.route("/", methods=["GET", "POST"])
def editor():
    content = ""

    if request.method == "POST":
        # 버튼 값 확인
        action = request.form.get("action")
        content = request.form.get("editor")

        if action == "save":
            print("Save pressed!")
            return render_template("textEditor.html", content=content)
        
        else:
            return jsonify({"error": "잘못된 값을 전송"}), 500

    return render_template("textEditor.html", content=content)


@app.route("/check", methods=["POST"])
def check():
    try:
        data = request.json
        text = data.get("text", "")
        level = data.get("level", "basic")
        lang = data.get("lang", "kr")
        
        if "text" not in data:
            return jsonify({"error": "no text field"})
    
        corrected = grammar.check(data["text"])
        print(corrected)
        return jsonify({"corrected": corrected})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host = "localhost", port= 1000, debug=True)