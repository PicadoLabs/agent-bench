const { describe, it } = require('node:test');
const assert = require('node:assert');
const { authenticateToken, createRateLimiter } = require('./authMiddleware');

describe('Authentication Middleware', () => {
  const secret = 'super-secret-key-123';
  const auth = authenticateToken(secret);

  it('rejects requests without authorization header with 401', () => {
    let statusCode = null;
    let jsonBody = null;
    const req = { headers: {} };
    const res = {
      status(code) { statusCode = code; return this; },
      json(body) { jsonBody = body; return this; }
    };
    let nextCalled = false;
    auth(req, res, () => { nextCalled = true; });

    assert.strictEqual(statusCode, 401);
    assert.strictEqual(nextCalled, false);
  });

  it('rejects invalid token with 403', () => {
    let statusCode = null;
    const req = { headers: { authorization: 'Bearer wrong-key' } };
    const res = {
      status(code) { statusCode = code; return this; },
      json() { return this; }
    };
    let nextCalled = false;
    auth(req, res, () => { nextCalled = true; });

    assert.strictEqual(statusCode, 403);
    assert.strictEqual(nextCalled, false);
  });

  it('accepts valid bearer token and sets req.user', () => {
    const req = { headers: { authorization: `Bearer ${secret}` } };
    const res = {};
    let nextCalled = false;
    auth(req, res, () => { nextCalled = true; });

    assert.strictEqual(nextCalled, true);
    assert.deepStrictEqual(req.user, { authenticated: true });
  });
});

describe('Rate Limiter Middleware', () => {
  it('allows requests within capacity and limits burst', () => {
    const limiter = createRateLimiter(2, 1);
    const req = { ip: '192.168.1.1', headers: {} };
    let rateLimited = false;
    const res = {
      setHeader() {},
      status(code) {
        if (code === 429) rateLimited = true;
        return this;
      },
      json() { return this; }
    };

    let allowedCount = 0;
    for (let i = 0; i < 3; i++) {
      limiter(req, res, () => { allowedCount++; });
    }

    assert.strictEqual(allowedCount, 2);
    assert.strictEqual(rateLimited, true);
  });
});

