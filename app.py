from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import imagehash
import os

# 🔥 blockchain
from mint import create_certificate  

# 🔥 QR
import qrcode
import base64
from io import BytesIO

app = Flask(__name__)

# ✅ FIXED CORS (important for Vercel → Render)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

hashes = set()

print("🔥 App started")

# ✅ HEALTH CHECK
@app.route("/")
def home():
    return jsonify({
        "success": True,
        "message": "your server is up and running"
    })


# ✅ DEBUG ROUTE (VERY IMPORTANT)
@app.route("/upload", methods=["GET"])
def upload_check():
    return jsonify({"message": "Upload route is live ✅"})


# 🚀 MAIN ROUTE
@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files.get("file")
        name = request.form.get("name")
        event = request.form.get("event")

        # ✅ validation
        if not file:
            return jsonify({"message": "❌ No file received"}), 400

        if not name or not event:
            return jsonify({"message": "❌ Name and Event required"}), 400

        # 📂 SAVE FILE
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # 🧠 HASH
        img = Image.open(file_path)
        hash_val = str(imagehash.average_hash(img))

        # ❌ DUPLICATE CHECK
        if hash_val in hashes:
            return jsonify({
                "message": "❌ Duplicate Certificate Detected"
            }), 400

        hashes.add(hash_val)

        # 🔥 NFT NAME
        asset_name = f"{name} - {event}"

        # 🔥 BLOCKCHAIN MINT
        tx_id = create_certificate(asset_name)

        # 🔗 EXPLORER (TESTNET)
        explorer_url = f"https://testnet.algoexplorer.io/tx/{tx_id}"

        # 🔗 VERIFY PAGE
        verify_url = f"https://nirman-verify-ai.vercel.app/verify.html?tx={tx_id}"

        # 🔥 QR GENERATION
        qr = qrcode.make(verify_url)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        # ✅ RESPONSE
        return jsonify({
            "message": "✅ Certificate Verified & Minted",
            "tx_id": tx_id,
            "explorer": explorer_url,
            "qr": qr_base64,
            "name": name,
            "event": event
        })

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({
            "message": "❌ Server Error",
            "error": str(e)
        }), 500


# 🚀 RUN
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)