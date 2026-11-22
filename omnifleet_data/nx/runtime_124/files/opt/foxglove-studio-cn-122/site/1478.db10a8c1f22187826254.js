// Keep full point clouds and camera frames off the pose/control TCP queue.
(() => {
  const NativeWebSocket = self.WebSocket;
  self.WebSocket = class MediaWebSocket extends NativeWebSocket {
    constructor(url, protocols) {
      super(url, protocols);
      const channels = new Map();
      let closed = false;
      const key = channel => JSON.stringify([channel.topic, channel.schemaName, channel.encoding]);
      const makeStream = accepts => {
        const wanted = new Map();
        const advertised = new Map();
        const sent = new Map();
        let socket;
        let retry;
        const flush = () => {
          if (socket?.readyState !== NativeWebSocket.OPEN) return;
          const subscriptions = [];
          for (const [id, channel] of wanted) {
            const channelId = advertised.get(key(channel));
            if (channelId !== undefined && !sent.has(id)) {
              subscriptions.push({ id, channelId });
              sent.set(id, channelId);
            }
          }
          if (subscriptions.length) socket.send(JSON.stringify({ op: "subscribe", subscriptions }));
        };
        const connect = () => {
          if (closed || !wanted.size || socket) return;
          clearTimeout(retry);
          const current = new NativeWebSocket(url, protocols);
          socket = current;
          current.binaryType = "arraybuffer";
          current.onmessage = event => {
            if (current !== socket) return;
            if (event.data instanceof ArrayBuffer) {
              const view = new DataView(event.data);
              if (view.byteLength >= 13 && view.getUint8(0) === 1 && wanted.has(view.getUint32(1, true))) {
                this.dispatchEvent(new MessageEvent("message", { data: event.data }));
              }
              return;
            }
            const message = JSON.parse(event.data);
            if (message.op === "advertise") {
              for (const channel of message.channels) advertised.set(key(channel), channel.id);
              flush();
            } else if (message.op === "unadvertise") {
              const removed = new Set(message.channelIds);
              for (const [name, id] of advertised) if (removed.has(id)) advertised.delete(name);
              for (const [id, channelId] of sent) if (removed.has(channelId)) sent.delete(id);
            } else if (message.op === "status") {
              this.dispatchEvent(new MessageEvent("message", { data: event.data }));
            }
          };
          current.onerror = () => {
            if (!closed && current === socket) this.dispatchEvent(new Event("error"));
          };
          current.onclose = () => {
            if (current !== socket) return;
            socket = undefined;
            advertised.clear();
            sent.clear();
            if (!closed && wanted.size) retry = setTimeout(connect, 1000);
          };
        };
        const stop = () => {
          clearTimeout(retry);
          const current = socket;
          socket = undefined;
          advertised.clear();
          sent.clear();
          current?.close();
        };
        return {
          accepts,
          wanted,
          subscribe(id, channel) { wanted.set(id, channel); connect(); flush(); },
          unsubscribe(id) {
            wanted.delete(id);
            if (sent.delete(id) && socket?.readyState === NativeWebSocket.OPEN) {
              socket.send(JSON.stringify({ op: "unsubscribe", subscriptionIds: [id] }));
            }
            if (!wanted.size) stop();
          },
          close() { wanted.clear(); stop(); },
        };
      };
      const streams = [
        makeStream(channel => /^\/(camera|vision)\//.test(channel.topic) && /\/(CompressedImage|Image)$/.test(channel.schemaName)),
        makeStream(channel => /\/PointCloud2$/.test(channel.schemaName)),
      ];
      const stopStreams = () => { for (const stream of streams) stream.close(); };
      this.addEventListener("message", event => {
        if (typeof event.data !== "string") return;
        const message = JSON.parse(event.data);
        if (message.op === "advertise") for (const channel of message.channels) channels.set(channel.id, channel);
        if (message.op === "unadvertise") for (const id of message.channelIds) channels.delete(id);
      });
      this.addEventListener("close", () => { closed = true; stopStreams(); });
      this.send = data => {
        if (typeof data !== "string" || this.readyState !== NativeWebSocket.OPEN) return super.send(data);
        const message = JSON.parse(data);
        if (message.op === "subscribe") {
          const subscriptions = [];
          for (const subscription of message.subscriptions) {
            const channel = channels.get(subscription.channelId);
            const stream = channel && streams.find(item => item.accepts(channel));
            if (stream) stream.subscribe(subscription.id, channel);
            else subscriptions.push(subscription);
          }
          if (subscriptions.length) super.send(JSON.stringify({ ...message, subscriptions }));
        } else if (message.op === "unsubscribe") {
          const subscriptionIds = [];
          for (const id of message.subscriptionIds) {
            const stream = streams.find(item => item.wanted.has(id));
            if (stream) stream.unsubscribe(id);
            else subscriptionIds.push(id);
          }
          if (subscriptionIds.length) super.send(JSON.stringify({ ...message, subscriptionIds }));
        } else super.send(data);
      };
      this.close = (...args) => { closed = true; stopStreams(); super.close(...args); };
    }
  };
})();

(()=>{"use strict";var n={};let a;const r=self.postMessage,o=self.postMessage;self.onmessage=t=>{const{type:c,data:s}=t.data;switch(c){case"open":try{a=new WebSocket(s.wsUrl,s.protocols),a.binaryType="arraybuffer",a.onerror=e=>{r({type:"error",error:e.error})},a.onopen=e=>{r({type:"open",protocol:a.protocol})},a.onclose=e=>{r({type:"close",data:JSON.parse(JSON.stringify(e)??"{}")})},a.onmessage=e=>{e.data instanceof ArrayBuffer?o({type:"message",data:e.data},[e.data]):r({type:"message",data:e.data})}}catch(e){r({type:"error",error:e??{message:"Insecure WebSocket connection"}})}break;case"close":a?.close();break;case"data":a?.send(s);break}}})();

//# sourceMappingURL=1478.db10a8c1f22187826254.js.map