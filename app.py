
import os
from flask import Flask, render_template, request, jsonify
from google import genai
from flask_cors import CORS

app = Flask(__name__)
CORS(
    app,
    resources={
        r"/ask": {
            "origins": [
                "https://pa12082010-papa.github.io"
            ]
        }
    }
)

# 讀取 Gemini API 金鑰
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("找不到 Gemini API 金鑰")

client = genai.Client(api_key=api_key)

# 顯示承勳原本的網頁
@app.route("/")
def home():
    return render_template("index.html")

# 接收網頁傳來的問題
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "")

    if not isinstance(question, str):
        return jsonify({"error": "問題格式不正確"}), 400

    question = question.strip()

    if not question or len(question) > 500:
        return jsonify({"error": "請輸入1至500字的問題"}), 400

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=(
                "你是大學新鮮人的AI小助手。"
                "請用繁體中文、親切簡單的方式回答。"
                "每次回答控制在100字左右。"
                "不確定的資訊請明確說明。"
                "\n使用者問題：" + question
            )
        )

        answer = response.text or "目前無法產生回答"
        return jsonify({"answer": answer})

    except Exception:
        app.logger.exception("Gemini API 呼叫失敗")
        return jsonify({
            "error": "AI服務暫時無法使用，請稍後再試"
        }), 502

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
