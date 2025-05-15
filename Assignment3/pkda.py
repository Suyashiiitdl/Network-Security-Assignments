import socket
import ast
import rsa
import json
from pprint import pprint
from server_creds import *

CREDS_FILE = "creds/pkda.json"

with open (CREDS_FILE, "r") as f:
    creds = json.load(f)
    d, e, n = int(creds["d"]), int(creds["e"]), int(creds["n"])

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"Server listening on {HOST}:{PORT}")

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")

    encrypted_request = int(client_socket.recv(40960).decode())

    request_dict = ast.literal_eval(str(rsa.decrypt(encrypted_request, d, n)))

    print("Decrypted request from client:")
    pprint(request_dict)

    """
    Request structure
    request_dict = {
        "request_type": "request_public_key",
        "initiator": 0,
        "requested": 1,
        "timestamp": "ignore",
        "nonce": "buttons - by the pussycat girls"
    }
    """

    initiator, requested, nonce = request_dict["initiator"], request_dict["requested"], request_dict["nonce"]

    with open(f"creds/client{initiator}.json", "r") as file:
        creds = json.load(file)
        i_e, i_n = int(creds["e"]), int(creds["n"])

    with open(f"creds/client{requested}.json", "r") as file:
        creds = json.load(file)
        r_e, r_n = int(creds["e"]), int(creds["n"])

    response_dict = {
        "e": str(r_e),
        "n": str(r_n),
        "nonce": nonce
    } 

    response_str = str(response_dict)

    print("Unencrypted response from PKDA:")
    pprint(response_dict)

    # encrypted_response = str(rsa.encrypt(response_str, i_e, i_n))
    encrypted_response = response_str
    client_socket.send(encrypted_response.encode())
    client_socket.close()