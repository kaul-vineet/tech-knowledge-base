# Lab 11 - a game as a state machine: "catch the dot".
# idle --A or shake--> play --6 s--> over --A--> idle; in play, press A when
# the moving dot is in the middle column to score.
from microbit import *

ROUND_MS = 6000            # one round, timed with running_time()
STEP_MS = 300              # the dot moves one column every 300 ms
TARGET_X = 2               # middle column

# transition table: (state, event) -> (next state, action). Anything else is ignored.
TRANSITIONS = {
    ("idle", "a"): ("play", "start"),
    ("idle", "shake"): ("play", "start"),
    ("play", "a"): ("play", "hit"),
    ("play", "shake"): ("idle", "abort"),
    ("play", "timeout"): ("over", "score"),
    ("over", "a"): ("idle", None),
}


def next_state(state, event):
    return TRANSITIONS.get((state, event), (state, None))


def new_game():
    return {"state": "idle", "score": 0, "started": 0}


def dot_x(game, now):
    return ((now - game["started"]) // STEP_MS) % 5


def events(game, now):
    # events come from buttons, gestures and time; the table decides what they mean
    found = []
    if button_a.was_pressed():
        found.append("a")
    if accelerometer.was_gesture("shake"):
        found.append("shake")
    if game["state"] == "play" and now - game["started"] >= ROUND_MS:
        found.append("timeout")    # time is an event too: elapsed ms since "start"
    return found


def handle(game, event, now):
    state, action = next_state(game["state"], event)
    if action == "start":
        game["score"], game["started"] = 0, now
    elif action == "hit":
        hit = dot_x(game, now) == TARGET_X
        game["score"] += 1 if hit else 0
        print("hit" if hit else "miss", game["score"])
    if state != game["state"]:
        print("{} -> {} ({})".format(game["state"], state, event))
        game["state"] = state
    if action == "score":
        print("score", game["score"])


def draw(game, now):
    if game["state"] == "play":
        display.clear()
        display.set_pixel(dot_x(game, now), 2, 9)
    elif game["state"] == "over":
        display.show(min(game["score"], 9), wait=False)
    else:
        display.show(Image.TARGET, wait=False)


def step(game):
    now = running_time()           # ms since start: never sleep() to measure time
    for event in events(game, now):
        handle(game, event, now)
    draw(game, now)


def main():
    print("game ready: A or shake to start")
    game = new_game()
    while True:
        step(game)
        sleep(20)


if __name__ == "__main__":
    main()
