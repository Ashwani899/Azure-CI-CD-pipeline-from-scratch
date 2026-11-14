import os

from flask import Flask, jsonify, render_template

app = Flask(__name__)


@app.get("/")
def index():
    return render_template(
        "index.html",
        build_id=os.getenv("BUILD_ID", "local-dev"),
        build_time=os.getenv("BUILD_TIME", "not-set"),
    )


@app.get("/health")
def health():
    return jsonify(status="ok"), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
