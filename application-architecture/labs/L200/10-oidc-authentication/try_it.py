"""Try it (lesson 10): replay a code with a guessed verifier, and accept a token for another app. Run: python try_it.py"""
from app import start
from rp_client import LoginFailed, browser_follow


def try_1_intercepted_code():
    idp, rp = start()
    try:
        url, pending = rp.start_login()
        callback = browser_follow(url)  # an attacker copies this URL (code + state) from a log
        pending.code_verifier = "a" * 43  # ...but cannot know the verifier, which never left the RP
        try:
            rp.finish_login(callback, pending)
        except LoginFailed as exc:
            print(f"[1] stolen code, wrong verifier -> {exc}")
        print(f"[1] codes left at the IdP after the failed attempt -> {len(idp.codes)}")
    finally:
        idp.__exit__(None, None, None)


def try_2_token_for_another_app():
    idp, rp = start()
    try:
        idp.overrides = {"aud": "quiz-app"}  # validly signed, but minted for a different client
        url, pending = rp.start_login()
        try:
            rp.finish_login(browser_follow(url), pending)
        except LoginFailed as exc:
            print(f"[2] aud=quiz-app -> {exc}")
    finally:
        idp.__exit__(None, None, None)


if __name__ == "__main__":
    try_1_intercepted_code()
    try_2_token_for_another_app()
