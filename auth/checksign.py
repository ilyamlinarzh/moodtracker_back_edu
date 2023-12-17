from base64 import b64encode
from collections import OrderedDict
from hashlib import sha256
from hmac import HMAC
from urllib.parse import urlparse, parse_qsl, urlencode
from auth.base import secret_key as secret

def is_valid_sign(url) -> bool:
    query = dict(parse_qsl(urlparse(url).query, keep_blank_values=True))
    vk_subset = OrderedDict(sorted(x for x in query.items() if x[0][:3] == "vk_"))
    hash_code = b64encode(HMAC(secret.encode(), urlencode(vk_subset, doseq=True).encode(), sha256).digest())
    decoded_hash_code = hash_code.decode('utf-8')[:-1].replace('+', '-').replace('/', '_')
    return (query["sign"] == decoded_hash_code, query['vk_user_id'])