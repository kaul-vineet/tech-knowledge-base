"""Demo: loans -> outbox -> relay -> bus -> consumers, checked against asyncapi.json. Run: python app.py"""
from asyncapi_check import load, validate_event
from bus import InProcessBus
from consumers import ActiveLoansProjection, NotificationConsumer
from outbox import BookAlreadyOnLoan, LoansWithOutbox, Relay


def wire(loans):
    bus, notify, projection, contract = InProcessBus(), NotificationConsumer(), ActiveLoansProjection(), load()
    problems = []
    for channel in ("loanCreated", "loanReturned"):
        bus.subscribe(channel, lambda e, c=channel: problems.extend(validate_event(contract, c, e)))  # contract check
        bus.subscribe(channel, notify)
        bus.subscribe(channel, projection)
    return Relay(loans.db, bus), bus, notify, projection, problems


if __name__ == "__main__":
    loans = LoansWithOutbox()
    relay, bus, notify, projection, problems = wire(loans)
    loans.borrow("b1", "m1")
    print(f"borrow b1 by m1 -> outbox pending: {loans.pending()}")
    try:
        loans.borrow("b1", "m2")
    except BookAlreadyOnLoan as exc:
        print(f"borrow b1 by m2 -> {type(exc).__name__}; outbox pending: {loans.pending()} (rolled back, no event)")
    loans.give_back(1)
    print(f"return loan 1   -> outbox pending: {loans.pending()}")
    print(f"relay run 1     -> published {relay.publish_pending()}: {bus.delivered}")
    print(f"relay run 2     -> published {relay.publish_pending()} (nothing pending)")
    print(f"notifications   -> {notify.sent}")
    print(f"projection      -> active loans per member {dict(projection.active)}")
    print(f"asyncapi.json   -> {len(bus.delivered)} events checked, problems: {problems}")
