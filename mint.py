from algosdk.v2client import algod
from algosdk import mnemonic, account, transaction
from algosdk.transaction import wait_for_confirmation

# 🔗 Local Algorand node (AlgoKit LocalNet)
ALGOD_ADDRESS = "http://localhost:4001"
ALGOD_TOKEN = "a" * 64

# 🔴 IMPORTANT: Replace with your 25-word mnemonic
MNEMONIC = "thunder truth sunset stairs venue action believe coyote purchase fever success salute guitar tunnel live cube omit mesh post sibling work beef service absorb knee"

# Initialize client
client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)


def create_certificate(asset_name):
    try:
        # 🔐 Get account
        private_key = mnemonic.to_private_key(MNEMONIC)
        sender = account.address_from_private_key(private_key)

        print(f"👤 Sender: {sender}")

        # 📡 Get suggested params
        params = client.suggested_params()

        # 🪙 Create NFT (ASA)
        txn = transaction.AssetConfigTxn(
            sender=sender,
            sp=params,
            total=1,  # NFT = 1 unit
            default_frozen=False,
            unit_name="CERT",
            asset_name=asset_name,
            manager=sender,
            reserve=sender,
            freeze=sender,
            clawback=sender,
            url="https://nirman-cert.com",
            decimals=0,
        )

        # ✍️ Sign transaction
        signed_txn = txn.sign(private_key)

        # 🚀 Send transaction
        tx_id = client.send_transaction(signed_txn)
        print(f"📤 Transaction sent: {tx_id}")

        # ⏳ Wait for confirmation
        confirmed_txn = wait_for_confirmation(client, tx_id, 4)

        print("✅ Transaction confirmed!")
        print(f"🔗 Asset ID: {confirmed_txn['asset-index']}")

        return tx_id

    except Exception as e:
        print("❌ Blockchain Error:", str(e))
        raise e