/**
 * Custom React-style Subscription Hook Simulation
 */

function useDataSubscription(emitter, channel, pollIntervalMs = 1000) {
  let active = true;
  const receivedData = [];

  const handler = (data) => {
    if (active) {
      receivedData.push(data);
    }
  };

  emitter.on(channel, handler);

  const timerId = setInterval(() => {
    if (active) {
      emitter.emit(channel, { timestamp: Date.now(), polled: true });
    }
  }, pollIntervalMs);

  // Return unsubscribe cleanup function
  return {
    getData: () => receivedData,
    unsubscribe: () => {
      active = false;
      if (typeof emitter.removeListener === 'function') {
        emitter.removeListener(channel, handler);
      } else if (typeof emitter.off === 'function') {
        emitter.off(channel, handler);
      }
      clearInterval(timerId);
    }
  };
}

module.exports = {
  useDataSubscription
};

