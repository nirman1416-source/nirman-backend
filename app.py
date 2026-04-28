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

print("🔥 App is starting...")

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

hashes = set()


# ✅ HEALTH CHECK
@app.route("/")
def home():
    return "Backend running ✅"


# 🚀 MAIN ROUTE
@app.route("/upload", methods=["POST"])
def upload():

    # 📂 FILE VALIDATION
    if "file" not in request.files:
        return jsonify({"message": "❌ No file received"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"message": "❌ No file selected"}), 400

    # 📊 FORM DATA
    name = request.form.get("name")
    event = request.form.get("event")
    wallet = request.form.get("wallet")

    if not name or not event:
        return jsonify({"message": "❌ Name and Event required"}), 400

    if not wallet:
        return jsonify({"message": "❌ Wallet not connected"}), 400

    try:
        print("\n========== NEW REQUEST ==========")
        print("📂 File:", file.filename)
        print("👤 Name:", name)
        print("🎉 Event:", event)
        print("🔐 Wallet:", wallet)

        # ✅ SAVE FILE
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # 🧠 ML HASH
        img = Image.open(file_path)
        hash_val = str(imagehash.average_hash(img))
        print("🧠 Hash:", hash_val)

        # ❌ DUPLICATE CHECK
        if hash_val in hashes:
            print("❌ Duplicate detected")
            return jsonify({
                "message": "❌ Duplicate Certificate Detected"
            })

        hashes.add(hash_val)

        # 🔥 NFT NAME
        asset_name = f"{name} - {event}"

        # 🔥 BLOCKCHAIN MINT
        try:
            print("⛓️ Minting NFT:", asset_name)
            tx_id = create_certificate(asset_name)
            print("✅ TX ID:", tx_id)

        except Exception as e:
            print("❌ Blockchain error:", str(e))
            return jsonify({
                "message": "⚠️ Blockchain mint failed",
                "error": str(e)
            }), 500

        # 🔗 EXPLORER LINK (LocalNet)
        explorer_url = f"http://localhost:8980/v2/transactions/{tx_id}"

        # 📱 VERIFY PAGE (QR LINK)
        verify_url = f"http://localhost:5500/verify.html?tx={tx_id}"

        # 🔥 GENERATE QR
        qr = qrcode.make(verify_url)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")

        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        print("✅ SUCCESS RESPONSE SENT\n")

        # ✅ FINAL RESPONSE
        return jsonify({
            "message": "✅ Certificate Verified & Minted",
            "tx_id": tx_id,
            "explorer": explorer_url,
            "qr": qr_base64,
            "name": name,
            "event": event,
            "wallet": wallet
        })

    except Exception as e:
        print("❌ General error:", str(e))
        return jsonify({
            "message": "❌ Error processing file",
            "error": str(e)
        }), 500


# 🚀 RUN SERVER
if __name__ == "__main__":
    print("🚀 Flask running on http://127.0.0.1:5000")
    app.run(debug=True)