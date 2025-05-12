
import json
import base64
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import qrcode

def main():
    # 1. Build a fake/tampered driver record
    data = {
        "Name": "Evil Hacker",
        "DOB": "1970-01-01",
        "Address": "Unknown Street, Nowhere",
        "DL_No": "FAKE0000",
        "DOI": "2025-01-01",
        "Validity": "2026-01-01",
        "categories": ["LMV"],
        "restrictions": []
    }

    # 2. Sign it with a _different_ RSA key (not your authority's)
    fake_key = RSA.generate(2048)
    data_bytes = json.dumps(data, sort_keys=True).encode()
    digest = SHA256.new(data_bytes)
    signature = pkcs1_15.new(fake_key).sign(digest)
    sig_b64 = base64.b64encode(signature).decode()

    # 3. Bundle into the QR payload
    payload = {
        "data": data,
        "signature": sig_b64
    }
    payload_str = json.dumps(payload, sort_keys=True)

    # 4. Generate and save the “tampered” QR code
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )
    qr.add_data(payload_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white').convert('RGB')
    img.save('tampered_qr.png')

    print("✅ Tampered QR saved as 'tampered_qr.png'")

if __name__ == '__main__':
    main()
