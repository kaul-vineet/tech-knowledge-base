// k6 load for lesson 16 (pending a manual run): start `python serve_realtime.py`, then `k6 run load_test.js`.
// Open model: 120 requests/s for 10 s against a server with capacity 80/s (4 workers x 50 ms), queue bound 8.
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  discardResponseBodies: true,
  scenarios: {
    overload: {
      executor: 'constant-arrival-rate',
      rate: 120,
      timeUnit: '1s',
      duration: '10s',
      preAllocatedVUs: 20,
      maxVUs: 200,
    },
  },
};

export default function () {
  const res = http.get('http://127.0.0.1:8016/work');
  check(res, {
    'status is 200 or 503': (r) => r.status === 200 || r.status === 503,
    '503 carries Retry-After': (r) => r.status !== 503 || r.headers['Retry-After'] !== undefined,
  });
}
