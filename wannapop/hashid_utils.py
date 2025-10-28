from hashids import Hashids
from config import SALT  


salt = (SALT or "")
if not salt:
    raise RuntimeError("SALT no esta configurado en .env")

_hashids = Hashids(salt=SALT, min_length=4)

def encode_id(id: int) -> str:
    return _hashids.encode(id)

def decode_id(hashid: str):
    decoded = _hashids.decode(hashid)
    return decoded[0] if decoded else None