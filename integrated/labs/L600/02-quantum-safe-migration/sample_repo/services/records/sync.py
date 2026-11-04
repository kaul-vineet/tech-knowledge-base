"""Records: replicas agree a channel key with ephemeral ECDH on P-384 before shipping customer records."""
from cryptography.hazmat.primitives.asymmetric import ec


def channel_secret(peer_public):
    mine = ec.generate_private_key(ec.SECP384R1())
    return mine.public_key(), mine.exchange(ec.ECDH(), peer_public)
