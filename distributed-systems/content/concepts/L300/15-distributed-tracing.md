## Why it matters
A checkout is slow, and it touches a gateway, an orders service and a payment provider. Each service's logs say "my part was fine". A trace stitches one request's work across every hop into a single timeline so you can see where the time went. It only works if every hop passes the context on; one forgotten header splits the story in two.

## Mental model
A trace is a tree of spans that share one trace id. Each span knows its parent. The context travels in one HTTP header, `traceparent: 00-<trace-id>-<parent-id>-<flags>`; every service keeps the trace id and puts its own span id in the parent-id field for the next call.

```
gateway /checkout   [=================================]   trace 8575..., span 0942
  orders /create      [=========================]           parent 0942, span e9bb
    payments /authorize   [==================]              parent e9bb
  payments /receipt                             [===]       parent 0942
```

## How it works
1. **Server middleware.** Parse the incoming header. A valid one is continued (same trace id; the caller's span becomes the parent). A missing or invalid one (uppercase hex, all-zero ids) starts a new trace. → see lab step 1
2. **Spans as JSON lines.** Each request records trace id, span id, parent id, service, name, start and end. A backend such as Jaeger collects and indexes these lines. → see lab step 1
3. **Rebuild the trace.** Group by trace id and link children to parents. More than one trace id for one request, or a parent id that is never seen, means a hop broke propagation. → see lab step 2
4. **Critical path.** Walk back from the root's end: the child that finished last is on the path, then whatever finished before it started, and so on. Self time is a span's duration minus its children on the path. → see lab step 3
5. **Client middleware.** Inject the current context on every outgoing request in one shared place, so no call site can forget it. → see lab step 5

Worked example (lab output; times vary by run): with the raw call in orders, the request becomes two traces, and the critical path shows "orders GET /create self 88 ms". About 60 ms of that is the payments call the trace cannot see. With the middleware, there is one trace of four spans and the path reads orders 28 ms, payments /authorize 60 ms.

## Failure modes
- **Broken traces:** a hop drops or rewrites the header (raw HTTP clients, message queues, thread pools, proxies). You notice orphan root spans and "self time" that is really someone else's call.
- **Restarted traces** after an invalid header from a buggy or hostile caller. This is correct behaviour, but count it.
- **Sampling gaps:** the caller sampled but the callee did not. Pass the sampled flag on unchanged.
- **Clock skew between hosts:** child spans can appear to start before their parent. Compare durations, not absolute times, across machines.

## Common mistakes
- Creating a new trace id in every service instead of continuing the incoming one.
- Propagating by hand at each call site instead of in middleware.
- Putting user data in trace headers (the W3C spec forbids personal data in traceparent and tracestate).
