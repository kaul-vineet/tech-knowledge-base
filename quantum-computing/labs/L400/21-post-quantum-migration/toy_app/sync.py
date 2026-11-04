"""Device sync: ephemeral ECDH on P-384, then the shared secret keys the replication channel."""
from cryptography.hazmat.primitives.asymmetric.ec import ECDH, SECP384R1, generate_private_key


def shared_secret(peer_public):
    mine = generate_private_key(SECP384R1())
    return mine.public_key(), mine.exchange(ECDH(), peer_public)
