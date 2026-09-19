const { describe, it } = require('node:test');
const assert = require('node:assert');
const { EventEmitter } = require('node:events');
const { useDataSubscription } = require('./subscriptionHook');

describe('React Custom Hook Subscription Cleanup', () => {
  it('receives events when subscribed', () => {
    const emitter = new EventEmitter();
    const sub = useDataSubscription(emitter, 'updates', 10000);

    emitter.emit('updates', { msg: 'hello' });
    assert.deepStrictEqual(sub.getData(), [{ msg: 'hello' }]);

    sub.unsubscribe();
  });

  it('cleans up emitter listener upon unmount/unsubscribe', () => {
    const emitter = new EventEmitter();
    const sub = useDataSubscription(emitter, 'telemetry', 10000);

    assert.strictEqual(emitter.listenerCount('telemetry'), 1);
    sub.unsubscribe();
    assert.strictEqual(emitter.listenerCount('telemetry'), 0);
  });

  it('cleans up setInterval polling timer upon unsubscribe', async () => {
    const emitter = new EventEmitter();
    const sub = useDataSubscription(emitter, 'heartbeat', 50);

    await new Promise((r) => setTimeout(r, 120));
    const countBefore = sub.getData().length;
    assert.ok(countBefore >= 1);

    sub.unsubscribe();
    await new Promise((r) => setTimeout(r, 120));
    const countAfter = sub.getData().length;

    assert.strictEqual(countBefore, countAfter);
  });
});

