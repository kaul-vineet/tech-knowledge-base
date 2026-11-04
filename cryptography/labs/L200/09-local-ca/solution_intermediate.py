"""Build-task solution: root -> INTERMEDIATE -> leaf. The root key can then stay offline."""
import datetime as dt

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

import local_ca


def make_hierarchy(names=("localhost",)):
    root_key, root = local_ca.make_root("KB Root CA (offline)")
    # make_root uses path_length=0; a root that signs an intermediate needs path_length >= 1
    root = (x509.CertificateBuilder().subject_name(root.subject).issuer_name(root.subject)
            .public_key(root_key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(local_ca.NOW).not_valid_after(local_ca.NOW + dt.timedelta(days=3650))
            .add_extension(x509.BasicConstraints(ca=True, path_length=1), critical=True)
            .add_extension(x509.KeyUsage(digital_signature=False, key_cert_sign=True, crl_sign=True, **local_ca.KU),
                           critical=True)
            .add_extension(x509.SubjectKeyIdentifier.from_public_key(root_key.public_key()), critical=False)
            .sign(root_key, hashes.SHA256()))
    int_key = ec.generate_private_key(ec.SECP256R1())
    inter = (x509.CertificateBuilder().subject_name(local_ca._name("KB Issuing CA")).issuer_name(root.subject)
             .public_key(int_key.public_key()).serial_number(x509.random_serial_number())
             .not_valid_before(local_ca.NOW).not_valid_after(local_ca.NOW + dt.timedelta(days=365))
             .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
             .add_extension(x509.KeyUsage(digital_signature=False, key_cert_sign=True, crl_sign=True, **local_ca.KU),
                            critical=True)
             .add_extension(x509.SubjectKeyIdentifier.from_public_key(int_key.public_key()), critical=False)
             .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(root_key.public_key()), critical=False)
             .sign(root_key, hashes.SHA256()))
    leaf_key, leaf = local_ca.issue_server(int_key, inter, names=names)
    return root, inter, leaf, leaf_key
