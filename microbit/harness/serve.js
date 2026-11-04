// Tiny static server for host.html (no dependencies). Used by playwright.config.js.
const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = Number(process.env.PORT || 4173);
const HOST_FILE = path.join(__dirname, "host.html");

http
  .createServer((req, res) => {
    const pathname = new URL(req.url, "http://localhost").pathname;
    if (pathname === "/" || pathname === "/host.html") {
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      fs.createReadStream(HOST_FILE).pipe(res);
    } else {
      res.writeHead(404).end("not found");
    }
  })
  // loopback only: not reachable from the network on any OS
  .listen(PORT, "127.0.0.1", () => console.log(`host ready on http://127.0.0.1:${PORT}`));
