# cd C:\Users\gram\Desktop\flask
# py FlaskTextEditor.py
from flask import Flask, render_template, request, jsonify, send_file
from Grammar.GrammarManager import GrammarManager
from docx import Document
import tempfile

app = Flask(__name__) 

# GrammarManager 인스턴스 생성 
grammar = GrammarManager('en-US')

# 텍스트 에디터 파트
@app.route("/", methods=["GET", "POST"])
def editor():
    content = ""

    if request.method == "POST":
        # 버튼 값 확인
        action = request.form.get("action")
        content = request.form.get("editor")

    return render_template("textEditor.html", content=content)

# 문법 검사기 파트
@app.route("/check", methods=["POST"])
def check():
    try:
        data = request.json
        
        if "text" not in data:
            return jsonify({"error": "no text field"})
    
        corrected, errors = grammar.check(data["text"])
        print(errors)
        return jsonify({
            "corrected": corrected,
            "errors": errors
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 다운로드 파트
@app.route("/download", methods=["POST"])
def download():
    data = request.json
    text = data.get("text", "")

    if not text.strip():
        return {"error": "no content"}, 400

    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(tmp.name)

    return send_file(
        tmp.name,
        as_attachment=True,
        download_name="grammar_checked.docx"
    )

if __name__ == "__main__":
    app.run(host = "localhost", port= 1000, debug=True)