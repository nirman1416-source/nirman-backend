from algosdk.v2client import algod
from algosdk import mnemonic, account, transaction
from algosdk.transaction import wait_for_confirmation

# 🌐 Algorand TestNet (AlgoNode - FREE, no API key needed)
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""  # no token required

# 🔴 Your wallet mnemonic (keep secret in real apps)
MNEMONIC = "thunder truth sunset stairs venue action believe coyote purchase fever success salute guitar tunnel live cube omit mesh post sibling work beef service absorb knee"

# 🔌 Initialize client
client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)


def create_certificate(asset_name):
    try:
        # 🔐 Get account
        private_key = mnemonic.to_private_key(MNEMONIC)
        sender = account.address_from_private_key(private_key)

        print(f"👤 Sender: {sender}")

        # 📡 Get suggested params
        params = client.suggested_params()

        # 🪙 Create NFT (Algorand Standard Asset)
        txn = transaction.AssetConfigTxn(
            sender=sender,
            sp=params,
            total=1,  # NFT
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