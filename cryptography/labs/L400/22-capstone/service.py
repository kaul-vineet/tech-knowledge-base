"""Wire the capstone together on 127.0.0.1: PKI (lessons 9-10), token PIN from a file (lesson 16), soft token keys
(lesson 19), signed audit log, KMS behind mutual TLS, document service with redacted JSON logs."""
import io
import secrets
from pathlib import Path
from types import SimpleNamespace

import paths  # noqa: F401
import doc_service
import kms
import secrets_app
import solution_mtls
import solution_redact
from audit import AuditLog, FakeClock


def start(work: Path) -> SimpleNamespace:
    clock = FakeClock()
    pki = solution_mtls.make_pki_with_client(work / "pki", client_cn="doc-service")  # CA, KMS server cert, client cert
    pin_file = work / "token-pin"
    pin_file.write_text(secrets.token_urlsafe(16), encoding="utf-8")  # stands in for a mounted secret file
    pin = secrets_app.load_secret("CAP_TOKEN_PIN", {"CAP_TOKEN_PIN_FILE": str(pin_file)})
    tk = doc_service.open_token(pin)
    audit = AuditLog(tk["keys"]["audit-log"][0], clock)
    server, kms_core = kms.start_kms(pki, audit)
    client = kms.KMSClient(server.server_address[1], pki)
    stream = io.StringIO()
    log = solution_redact.json_logger(stream, "docsvc", known_secrets=[pin.reveal()])
    svc = doc_service.DocService(client, tk["keys"], audit, clock, log)
    return SimpleNamespace(clock=clock, pki=pki, pin=pin, token=tk["token"], audit=audit, audit_pub=tk["keys"]["audit-log"][1],
                           server=server, kms=kms_core, port=server.server_address[1], svc=svc, log=log, log_stream=stream)


def stop(ns: SimpleNamespace):
    ns.server.shutdown()
    ns.server.server_close()
    ns.pin.wipe()
