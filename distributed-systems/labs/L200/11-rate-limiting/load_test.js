// k6 load for lesson 11 (pending a manual run): start `python serve_realtime.py`, then `k6 run load_test.js`.
// Open model: 10 requests/s for 10 s from one client id, above the limiter's 2/s refill (burst 5).
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  discardResponseBodies: true,
  scenarios: {
    over_limit: {
      executor: 'constant-arrival-rate',
      rate: 10,
      timeUnit: '1s',
      duration: '10s',
      preAllocatedVUs: 2,
      maxVUs: 20,
    },
  },
};

export default function () {
  const res = http.get('http://127.0.0.1:8011/data', { headers: { 'X-Client-Id': 'k6' } });
  check(res, {
    'status is 200 or 429': (r) => r.status === 200 || r.status === 429,
    '429 carries Retry-After': (r) => r.status !== 429 || r.headers['Retry-After'] !== undefined,
  });
}
