import json
import qrcode
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64
import os

def main():
    # 1. Load driver data
    with open('driver_data.json', 'r') as f:
        data = json.load(f)

    # 2. Generate RSA key pair
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key  = key.publickey().export_key()

    # Ensure output directory exists
    out_dir = 'output'
    os.makedirs(out_dir, exist_ok=True)

    # 3. Save keys
    with open(os.path.join(out_dir, 'private.pem'), 'wb') as f:
        f.write(private_key)
    with open(os.path.join(out_dir, 'public.pem'), 'wb') as f:
        f.write(public_key)

    # 4. Prepare data for signing
    data_bytes = json.dumps(data, sort_keys=True).encode()

    # 5. Sign
    hash_obj  = SHA256.new(data_bytes)
    signature = pkcs1_15.new(key).sign(hash_obj)
    signature_b64 = base64.b64encode(signature).decode()

    # 6. Bundle into payload
    qr_payload = {
        'data': data,
        'signature': signature_b64
    }
    
    payload_str = json.dumps(qr_payload, sort_keys=True)

    # 7. Generate a crisp, high‑contrast QR code
    qr = qrcode.QRCode(
        version=None,
        error_correction = qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(payload_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white').convert('RGB')

    # 8. Save QR image
    qr_path = os.path.join(out_dir, 'driver_license_qr.png')
    img.save(qr_path)

    print(f"✅ Done. Outputs in '{out_dir}/':")
    print("   • driver_license_qr.png")
    print("   • public.pem")
    print("   • private.pem")

if __name__ == '__main__':
    main()
