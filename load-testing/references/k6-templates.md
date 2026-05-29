# k6 Load Testing Templates

## Basic Load Test

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const latency = new Trend('api_latency');

export const options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp up
    { duration: '1m', target: 20 },    // Stay at 20 VUs
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],   // 95% of requests < 500ms
    errors: ['rate<0.1'],               // Error rate < 10%
  },
};

export default function () {
  const res = http.get('https://api.example.com/users');

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
    'has correct content-type': (r) =>
      r.headers['Content-Type']?.includes('application/json'),
  });

  errorRate.add(res.status !== 200);
  latency.add(res.timings.duration);

  sleep(1);
}
```

## Scenario-Based Test

```javascript
import http from 'k6/http';
import { check, sleep, group } from 'k6';

export const options = {
  scenarios: {
    // Constant rate scenario
    browse_products: {
      executor: 'constant-arrival-rate',
      rate: 100,              // 100 iterations per timeUnit
      timeUnit: '1s',
      duration: '2m',
      preAllocatedVUs: 50,
      exec: 'browseProducts',
    },
    // Ramping VUs scenario
    checkout_flow: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 10 },
        { duration: '1m', target: 10 },
        { duration: '30s', target: 0 },
      ],
      exec: 'checkoutFlow',
    },
  },
};

export function browseProducts() {
  group('Browse Products', () => {
    const productsRes = http.get('https://api.example.com/products');
    check(productsRes, { 'products loaded': (r) => r.status === 200 });

    sleep(2);

    const productId = Math.floor(Math.random() * 100) + 1;
    const productRes = http.get(`https://api.example.com/products/${productId}`);
    check(productRes, { 'product loaded': (r) => r.status === 200 });

    sleep(1);
  });
}

export function checkoutFlow() {
  group('Checkout Flow', () => {
    // Add to cart
    const cartRes = http.post('https://api.example.com/cart', JSON.stringify({
      productId: Math.floor(Math.random() * 100) + 1,
      quantity: 1,
    }), { headers: { 'Content-Type': 'application/json' } });

    check(cartRes, { 'added to cart': (r) => r.status === 201 });
    sleep(1);

    // Checkout
    const checkoutRes = http.post('https://api.example.com/checkout', JSON.stringify({
      cartId: cartRes.json('cartId'),
      paymentMethod: 'credit_card',
    }), { headers: { 'Content-Type': 'application/json' } });

    check(checkoutRes, { 'checkout success': (r) => r.status === 200 });
  });
}
```

## Authentication Test

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

let authToken;

export function setup() {
  // Login once to get token
  const loginRes = http.post('https://api.example.com/auth/login', JSON.stringify({
    email: __ENV.TEST_USER_EMAIL,
    password: __ENV.TEST_USER_PASSWORD,
  }), { headers: { 'Content-Type': 'application/json' } });

  check(loginRes, { 'login successful': (r) => r.status === 200 });
  return { token: loginRes.json('token') };
}

export default function (data) {
  const headers = {
    Authorization: `Bearer ${data.token}`,
    'Content-Type': 'application/json',
  };

  const res = http.get('https://api.example.com/me', { headers });
  check(res, { 'profile loaded': (r) => r.status === 200 });
  sleep(1);
}
```

## Data-Driven Test (CSV)

```javascript
import http from 'k6/http';
import { check } from 'k6';
import { SharedArray } from 'k6/data';
import papaparse from 'https://jslib.k6.io/papaparse/5.1.1/index.js';

const users = new SharedArray('users', function () {
  return papaparse.parse(open('./users.csv'), { header: true }).data;
});

export default function () {
  const user = users[Math.floor(Math.random() * users.length)];

  const res = http.post('https://api.example.com/login', JSON.stringify({
    email: user.email,
    password: user.password,
  }), { headers: { 'Content-Type': 'application/json' } });

  check(res, { 'login success': (r) => r.status === 200 });
}
```

## WebSocket Test

```javascript
import ws from 'k6/ws';
import { check, sleep } from 'k6';

export default function () {
  const url = 'wss://api.example.com/ws';
  const params = { tags: { my_tag: 'ws-test' } };

  const res = ws.connect(url, params, function (socket) {
    socket.on('open', () => {
      console.log('Connected');
      socket.send(JSON.stringify({ type: 'subscribe', channel: 'updates' }));
    });

    socket.on('message', (data) => {
      const msg = JSON.parse(data);
      check(msg, { 'received update': (m) => m.type === 'update' });
    });

    socket.on('close', () => console.log('Disconnected'));

    socket.setTimeout(() => {
      socket.close();
    }, 5000);
  });

  check(res, { 'status is 101': (r) => r && r.status === 101 });
}
```

## Custom Metrics

```javascript
import { Counter, Gauge, Rate, Trend } from 'k6/metrics';

const myCounter = new Counter('items_processed');
const myGauge = new Gauge('active_users');
const myRate = new Rate('successful_logins');
const myTrend = new Trend('login_duration');

export default function () {
  const start = Date.now();
  const res = http.post('https://api.example.com/login', payload);
  const duration = Date.now() - start;

  myCounter.add(1);
  myGauge.add(res.json('activeUsers'));
  myRate.add(res.status === 200);
  myTrend.add(duration);
}
```

## Environment Variables

```bash
# Run with environment variables
k6 run -e BASE_URL=https://staging.example.com \
       -e TEST_USER=test@example.com \
       -e TEST_PASS=secret \
       script.js
```

```javascript
const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';
```

## Running Tests

```bash
# Basic run
k6 run script.js

# With VU count and duration override
k6 run --vus 50 --duration 30s script.js

# Output results to JSON
k6 run --out json=results.json script.js

# Run with cloud output
K6_CLOUD_TOKEN=xxx k6 cloud script.js
```
