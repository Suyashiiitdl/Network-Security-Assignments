import json
import base64
import sys
import cv2
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import os

def main():
    # Paths (adjust if needed)
    out_dir   = 'output'
    qr_path   = os.path.join(out_dir, 'driver_license_qr.png')
    pub_key_p = os.path.join(out_dir, 'public.pem')

    # 1. Load the public key
    try:
        with open(pub_key_p, 'rb') as f:
            public_key = RSA.import_key(f.read())
    except FileNotFoundError:
        print(f"Cannot find public key at '{pub_key_p}'")
        sys.exit(1)

    # 2. Load the QR image
    img = cv2.imread(qr_path)
    if img is None:
        print(f"Could not load image '{qr_path}'.")
        sys.exit(1)
    print(f"Loaded image, shape = {img.shape}")

    # 3. Binarize for maximum contrast
    gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bin_img = cv2.threshold(gray, 0, 255,
                               cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # (optional) save to inspect
    cv2.imwrite(os.path.join(out_dir, 'qr_debug_binary.png'), bin_img)
    print("Binarized QR saved as 'qr_debug_binary.png'")

    # 4. Detect & decode
    detector = cv2.QRCodeDetector()
    data_str, points, _ = detector.detectAndDecode(bin_img)
    print(f"→ Decoded data length: {len(data_str)}; finder points: {points}")
    # print(f"→ Decoded data : {data_str}; finder points: {points}")


    if not data_str:
        print(" No QR detected—you may need to regenerate or check contrast.")
        sys.exit(1)

    # 5. Parse JSON payload
    try:
        qr_payload = json.loads(data_str)
        print ("Payload data : " , qr_payload)
        data       = qr_payload['data']
        sig_b64    = qr_payload['signature']
    except (ValueError, KeyError) as e:
        print(" Payload is not valid JSON or missing fields:", e)
        sys.exit(1)

    # 6. Verify signature
    data_bytes = json.dumps(data, sort_keys=True).encode()
    signature  = base64.b64decode(sig_b64)
    hash_obj   = SHA256.new(data_bytes)

    try:
        pkcs1_15.new(public_key).verify(hash_obj, signature)
        print("Signature valid — data is authentic.")
        print("Driver info:")
        print(json.dumps(data, indent=2))
    except (ValueError, TypeError):
        print("Signature verification failed — data may be tampered.")

if __name__ == '__main__':
    main()
