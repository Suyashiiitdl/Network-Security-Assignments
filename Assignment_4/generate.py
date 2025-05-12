# generate_qr.py

import json
import base64
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import qrcode

def main():
    # 1. Load your driver data
    with open('driver_data.json', 'r') as f:
        data = json.load(f)

    # 2. Generate a new RSA key pair
    key = RSA.generate(2048)
    with open('private.pem', 'wb') as f:
        f.write(key.export_key())
    with open('public.pem', 'wb') as f:
        f.write(key.publickey().export_key())

    # 3. Create a canonical byte stream of the data
    data_bytes = json.dumps(data, sort_keys=True).encode()

    # 4. Sign the data hash with your private key
    signer    = pkcs1_15.new(key)
    digest    = SHA256.new(data_bytes)
    signature = signer.sign(digest)
    sig_b64   = base64.b64encode(signature).decode()

    # 5. Bundle data + signature into one payload
    payload = {
        'data': data,
        'signature': sig_b64
    }
    payload_str = json.dumps(payload, sort_keys=True)

    # 6. Generate and save a high‑contrast QR code
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )
    qr.add_data(payload_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    img.save('driver_license_qr.png')

if __name__ == '__main__':
    main()
