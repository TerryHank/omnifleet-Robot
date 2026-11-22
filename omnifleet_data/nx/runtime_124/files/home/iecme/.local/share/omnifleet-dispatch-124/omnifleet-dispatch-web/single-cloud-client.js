(() => {
  if (typeof window.fzstd?.decompress !== 'function') return;
  const opcode = 0x7a;
  const headerSize = 13;
  const wireHeaderSize = 21;
  const NativeSocket = window.WebSocket;
  const NativeWorker = window.Worker;

  function usesCloudProxy(url) {
    try {
      const address = new URL(url, location.href);
      return address.host === location.host && address.pathname === '/single-cloud-socket';
    } catch {
      return false;
    }
  }

  function decodeCloud(data, event, deliveredAt, deliver, acknowledge) {
    if (!(data instanceof ArrayBuffer) || new Uint8Array(data)[0] !== opcode) return;
    event.stopImmediatePropagation();
    if (data.byteLength < wireHeaderSize) return;
    const encoded = new Uint8Array(data);
    const meta = new DataView(data);
    const size = meta.getUint32(headerSize, true);
    const sequence = meta.getUint32(headerSize + 4, true);
    try {
      const subscription = meta.getUint32(1, true);
      if (performance.now() - (deliveredAt.get(subscription) ?? -Infinity) < 1000) return;
      if (!size || size > 2 * 1024 * 1024) throw Error('Web point-cloud payload size');
      const payload = window.fzstd.decompress(encoded.subarray(wireHeaderSize));
      if (payload.length !== size) throw Error('Web point-cloud decompressed size mismatch');
      const standard = new Uint8Array(headerSize + size);
      standard.set(encoded.subarray(0, headerSize));
      standard[0] = 1;
      standard.set(payload, headerSize);
      deliveredAt.set(subscription, performance.now());
      deliver(standard.buffer);
    } catch (error) {
      console.error('Web point cloud could not be decoded', error);
    } finally {
      acknowledge(JSON.stringify({op: 'webCloudAck', seq: sequence}));
    }
  }

  if (NativeWorker) {
    window.Worker = class extends NativeWorker {
      #cloudProxy = false;
      #deliveredAt = new Map();

      constructor(...args) {
        super(...args);
        this.addEventListener('message', event => {
          const message = event.data;
          if (!this.#cloudProxy || message?.type !== 'message') return;
          decodeCloud(message.data, event, this.#deliveredAt, buffer => {
            this.dispatchEvent(new MessageEvent('message', {data: {type: 'message', data: buffer}}));
          }, data => { this.postMessage({type: 'data', data}); });
        });
      }

      postMessage(message, ...args) {
        if (message?.type === 'open') this.#cloudProxy = usesCloudProxy(message.data?.wsUrl);
        super.postMessage(message, ...args);
      }
    };
  }

  window.WebSocket = class extends NativeSocket {
    constructor(url, ...args) {
      super(url, ...args);
      if (!usesCloudProxy(url)) return;
      this.binaryType = 'arraybuffer';
      const deliveredAt = new Map();
      this.addEventListener('message', event => {
        decodeCloud(event.data, event, deliveredAt, data => {
          this.dispatchEvent(new MessageEvent('message', {data, origin: event.origin}));
        }, ack => { if (this.readyState === NativeSocket.OPEN) this.send(ack); });
      });
    }
  };

  window.OmniFleetCloudDecoderReady = true;
})();
