"""Tool: send_email (side effect, high risk). Recorded, never sent: the outbox is a list."""


def run(world, to, subject, body):
    world.effects.append(("send_email", {"to": to, "subject": subject, "body": body}))
    return f"sent to {to}"
