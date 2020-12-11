import base64
import hmac
import hashlib
import http.client
import time
import os
import urllib.parse
import requests
import json
import random


########################################################################################################################
def create_auth_header(mac_key_id: str, mac_key: str, method: str, url: str, content_type: str, body: str):
    url_parts = urllib.parse.urlparse(url)
    port = url_parts.port or (http.client.HTTPS_PORT if url_parts.scheme == "https" else http.client.HTTP_PORT)
    ts = str(int(time.time()))
    nonce = base64.b64encode(os.urandom(8)).decode()
    if content_type and body:
        ext = hashlib.sha1((content_type + body).encode()).hexdigest()
    else:
        ext = ""
    normalized_request_string = (
            "\n".join([ts, nonce, method, url_parts.path, url_parts.hostname, str(port), ext]) + "\n"
    )
    mac_key = mac_key.ljust((len(mac_key) - len(mac_key) % 4 + 4), "=")
    mac_key = base64.urlsafe_b64decode(mac_key)
    signature = hmac.new(mac_key, normalized_request_string.encode(), hashlib.sha1)
    mac = base64.b64encode(signature.digest())
    return f'MAC id="{mac_key_id}", ts="{ts}", nonce="{nonce}", ext="{ext}", mac="{mac}"'


########################################################################################################################
def generate_cid(suffix=None):
    ran = random.randrange(10 ** 80)
    value = "%064x" % ran
    cid = value[:32]
    if suffix:
        cid += "-" + suffix[:32]
    return cid


########################################################################################################################
def lcp_request(mac_key_id: str, mac_key: str, method: str, url: str, body=None, cid=None, print_rsp=False):
    if body:
        body_ver = str(body).replace("'", '"')
    else:
        body_ver = None
    auth_header = create_auth_header(mac_key_id, mac_key, method, url, "application/json", body_ver)
    auth_str = auth_header.replace("b'", "").replace("'", "")
    headers = {"Authorization": auth_str, "Content-Type": "application/json"}
    if cid:
        headers["Pts-App-CID"] = cid

    if method.lower() == 'get':
        rsp = requests.get(url, headers=headers)
    elif method.lower() == 'post':
        rsp = requests.post(url, json=body, headers=headers)
    elif method.lower() == 'patch':
        rsp = requests.patch(url, json=body, headers=headers)
    elif method.lower() == 'put':
        rsp = requests.put(url, json=body, headers=headers)
    else:
        return "Invalid Method"
    if print_rsp is True:
        print(rsp.text)
    return json.loads(rsp.text)


