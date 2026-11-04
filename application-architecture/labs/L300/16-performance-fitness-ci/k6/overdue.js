// Lesson 16 load test for Grafana k6 (AGPL-3.0) - the same test as load_test.py, with thresholds as the CI gate.
// Start the API first:  python http_api.py 8016
// Run:                  k6 run k6/overdue.js         (exit code != 0 when a threshold fails)
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 4,             // 4 virtual users, like load_test.py's 4 threads
  iterations: 40,     // 40 requests in total
  thresholds: {
    http_req_failed: ['rate<0.01'],      // fewer than 1% errors
    http_req_duration: ['p(95)<200'],    // response-time budget: p95 under 200 ms
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8016';

export default function () {
  const res = http.get(`${BASE_URL}/reports/overdue`);
  check(res, { 'status is 200': (r) => r.status === 200 });
}
