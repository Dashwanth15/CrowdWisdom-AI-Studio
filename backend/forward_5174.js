const net = require('net');

const server = net.createServer((from) => {
  const to = net.createConnection({ host: '127.0.0.1', port: 5173 });
  from.pipe(to);
  to.pipe(from);
  from.on('error', () => to.destroy());
  to.on('error', () => from.destroy());
});

server.listen(5174, '127.0.0.1', () => {
  console.log('Port forwarder running: 127.0.0.1:5174 -> 127.0.0.1:5173');
});
