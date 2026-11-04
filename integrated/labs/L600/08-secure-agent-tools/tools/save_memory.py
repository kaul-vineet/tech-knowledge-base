"""Tool: save_memory (side effect, low risk). Appends a note to the user's memory."""


def run(world, note):
    world.effects.append(("save_memory", {"note": note}))
    return "saved"
