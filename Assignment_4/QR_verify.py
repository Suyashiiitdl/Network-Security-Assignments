# QR_verification.py

import json
import base64
import sys
import cv2
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

def main():
    # 1. Load public key
    with open('public.pem', 'rb') as f:
        public_key = RSA.import_key(f.read())

    # 2. Read image and prepare detector
    # img = cv2.imread('driver_license_qr.png')


    img = cv2.imread('tampered_qr.png') # For verifing the tempered QR code uncomment this line and comment the above line

    if img is None:
        print(" Cannot load 'driver_license_qr.png'")
        sys.exit(1)

    detector = cv2.QRCodeDetector()

    # 3a. Try decoding directly
    data_str, points, _ = detector.detectAndDecode(img)

    # 3b. If that fails, binarize + retry
    if not data_str:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, bin_img = cv2.threshold(
            gray, 0, 255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        data_str, points, _ = detector.detectAndDecode(bin_img)

    # 4. Give up if still no payload
    if not data_str:
        print(" No QR code found or unreadable.")
        sys.exit(1)

    # 5. Parse JSON safely
    try:
        payload   = json.loads(data_str)
        data      = payload['data']
        sig_b64   = payload['signature']
    except (ValueError, KeyError):
        print("QR payload is not valid or missing fields.")
        sys.exit(1)

    # 6. Verify signature
    data_bytes = json.dumps(data, sort_keys=True).encode()
    digest     = SHA256.new(data_bytes)
    signature  = base64.b64decode(sig_b64)
    verifier   = pkcs1_15.new(public_key)

    try:
        verifier.verify(digest, signature)
        print(" Signature valid. Driver info:")
        print(json.dumps(data, indent=2))
    except (ValueError, TypeError):
        print("Signature invalid — data may be tampered.")

if __name__ == '__main__':
    main()
