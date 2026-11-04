"""L100 discrete-event simulation: one barista (or one API worker), customers arrive at random.

Arrivals: Poisson, rate LAM per minute. Service: exponential, rate MU per minute. One server, FIFO.
This is an M/M/1 queue, so we can compare the simulated mean wait with the formula Wq = lam / (mu (mu - lam)).

python des_queue.py
"""
import heapq
import random
from collections import deque

LAM, MU = 0.8, 1.0  # 0.8 customers/min arrive; barista serves 1.0/min on average (utilisation 80%)


def simulate(n_customers, seed, lam=LAM, mu=MU, trace=0):
    rng = random.Random(seed)  # seeded: reruns give identical event sequences
    events = []  # event list: (time, seq, kind, customer) kept as a min-heap ordered by time
    seq = 0

    def schedule(time, kind, cust):
        nonlocal seq
        heapq.heappush(events, (time, seq, kind, cust))  # seq breaks ties so equal times stay FIFO
        seq += 1

    clock, busy, queue = 0.0, False, deque()
    arrival_time, waits = {}, []
    schedule(rng.expovariate(lam), "arrive", 0)
    while events:
        clock, _, kind, cust = heapq.heappop(events)  # clock JUMPS to the next event; nothing happens in between
        if trace and len(waits) < trace and kind == "arrive":
            print(f"t={clock:7.3f}  arrive  customer {cust}  queue={len(queue)} busy={busy}")
        if kind == "arrive":
            arrival_time[cust] = clock
            if cust + 1 < n_customers:
                schedule(clock + rng.expovariate(lam), "arrive", cust + 1)  # each event schedules future events
            if busy:
                queue.append(cust)
            else:
                busy = True
                waits.append(0.0)
                schedule(clock + rng.expovariate(mu), "depart", cust)
        else:  # depart: free the server, start the next customer in line
            if trace and len(waits) <= trace:
                print(f"t={clock:7.3f}  depart  customer {cust}  queue={len(queue)}")
            if queue:
                nxt = queue.popleft()
                waits.append(clock - arrival_time[nxt])  # time in queue = service start - arrival
                schedule(clock + rng.expovariate(mu), "depart", nxt)
            else:
                busy = False
    return waits, clock


def mm1_wq(lam=LAM, mu=MU):
    return lam / (mu * (mu - lam))  # analytic mean wait in queue for M/M/1


def main(seed=1):
    print("first events (clock jumps from event to event):")
    simulate(5, seed, trace=4)
    waits, end = simulate(200_000, seed)
    sim = sum(waits) / len(waits)
    print(f"customers={len(waits)}  simulated time={end:,.0f} min")
    print(f"simulated mean wait = {sim:.3f} min | M/M/1 formula Wq = {mm1_wq():.3f} min | diff {100 * (sim - mm1_wq()) / mm1_wq():+.1f}%")


if __name__ == "__main__":
    main()
