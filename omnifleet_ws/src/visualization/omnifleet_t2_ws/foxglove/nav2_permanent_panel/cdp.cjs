const http = require('http');
const fs = require('fs');
const WebSocket = require('/home/iecme/omnifleet_ws/src/visualization/foxglove_studio_source/node_modules/ws');
http.get('http://127.0.0.1:9222/json/list', res => {
  let text = '';
  res.on('data', c => text += c);
  res.on('end', () => {
    const page = JSON.parse(text).find(p => p.type === 'page' && p.url.includes('app-web'));
    const ws = new WebSocket(page.webSocketDebuggerUrl);
    const timer = setTimeout(() => { ws.terminate(); process.exit(1); }, 20000);
    ws.on('open', () => ws.send(JSON.stringify({id: 1, method: 'Runtime.evaluate', params: {
      expression: fs.readFileSync(process.argv[2], 'utf8'), returnByValue: true, awaitPromise: true
    }})));
    ws.on('message', raw => {
      const reply = JSON.parse(raw);
      if (reply.id === 1) {
        console.log(JSON.stringify(reply.result || reply.error));
        clearTimeout(timer); ws.close();
      }
    });
  });
});
