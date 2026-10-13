import os, socket, redis
from flask import Flask, jsonify, Response
app = Flask(__name__)
r = redis.Redis(host=os.getenv("REDIS_HOST","redis"), port=int(os.getenv("REDIS_PORT","6379")),
                password=os.getenv("REDIS_PASSWORD") or None, decode_responses=True)
@app.get("/")
def index():
    v = r.incr("visits")
    return Response(f"<h1>Cloud Native Counter</h1><p>Pod: <b>{socket.gethostname()}</b></p><p>Visits: <b>{v}</b></p>", mimetype="text/html")
@app.get("/api")
def api():
    return jsonify({"pod": socket.gethostname(), "visits": r.incr("visits")})
@app.get("/health")
def health(): return "ok", 200
if __name__ == "__main__": app.run(host="0.0.0.0", port=5000)
