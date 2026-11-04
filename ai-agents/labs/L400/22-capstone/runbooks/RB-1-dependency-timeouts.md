# RB-1 Dependency timeouts

Symptoms: TimeoutError in the logs of the calling service, p99 latency above 2000 ms, errors rise with traffic. The downstream dependency is slow or saturated.

Steps: check the downstream service dashboard, lower the client timeout budget, enable the circuit breaker, shed non-critical traffic. Page the owner of the slow dependency if its error budget burns fast.
