from flask import Flask, request, jsonify, send_from_directory, redirect, url_for
from flask_cors import CORS
from datetime import datetime
import json
import os

# 把当前资料夹当成静态目录来服务（index.html / sc.html 放同一层）
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # 若你用跨网域访问也OK；同源时不会有影响

@app.get("/")
def root():
    # 如果有 index.html 就导到它；没有就给个提示
    if os.path.exists(os.path.join(app.static_folder, "index.html")):
        return redirect(url_for('serve_static', filename="index.html"))
    return "放一個 index.html 到此資料夾，然後重新整理即可。"

@app.get("/<path:filename>")
def serve_static(filename):
    # 提供当前资料夹下的任何静态文件（index.html, sc.html, css, js, 图像等）
    return send_from_directory(app.static_folder, filename)

@app.post("/api/submit")
def submit():
    """
    接收前端送来的问卷資料，保存到 answers.jsonl。
    每行一筆，格式：{"time":"...","ip":"...","payload":{...}}
    """
    try:
        payload = request.get_json(force=True, silent=False)
    except Exception:
        return jsonify({"ok": False, "error": "invalid_json"}), 400

    record = {
        "time": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "ip": request.headers.get("X-Forwarded-For", request.remote_addr),
        "payload": payload
    }

    out_path = os.path.join(os.getcwd(), "answers.jsonl")
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return jsonify({"ok": True})

@app.get("/health")
def health():
    return jsonify({"ok": True})

if __name__ == "__main__":
    # 0.0.0.0 方便局域网测试；只在本机可用的话可以换成 127.0.0.1
    app.run(host="0.0.0.0", port=5000, debug=True)
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
