/**
 * Express Authentication and Rate Limiting Middleware
 */

function authenticateToken(secretKey) {
  return (req, res, next) => {
    const authHeader = req.headers['authorization'];
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Unauthorized: Missing or malformed token' });
    }

    const token = authHeader.split(' ')[1];
    if (token !== secretKey) {
      return res.status(403).json({ error: 'Forbidden: Invalid token' });
    }

    req.user = { authenticated: true };
    next();
  };
}

function createRateLimiter(maxTokens = 10, refillRatePerSec = 2) {
  const buckets = new Map();

  return (req, res, next) => {
    const ip = req.ip || req.headers['x-forwarded-for'] || '127.0.0.1';
    const now = Date.now();

    let bucket = buckets.get(ip);
    if (!bucket) {
      bucket = { tokens: maxTokens, lastRefill: now };
      buckets.set(ip, bucket);
    } else {
      const elapsedSec = (now - bucket.lastRefill) / 1000;
      bucket.tokens = Math.min(maxTokens, bucket.tokens + elapsedSec * refillRatePerSec);
      bucket.lastRefill = now;
    }

    if (bucket.tokens >= 1) {
      bucket.tokens -= 1;
      next();
    } else {
      res.setHeader('Retry-After', '1');
      res.status(429).json({ error: 'Too Many Requests' });
    }
  };
}

module.exports = {
  authenticateToken,
  createRateLimiter
};

