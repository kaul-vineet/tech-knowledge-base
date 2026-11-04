"""Local check of valkey_equivalent.py's RESP2 framing against a tiny fake server (GET/SET NX EX/DEL/TTL/PING).
It proves the bytes on the wire and the reply parsing; it is NOT Valkey - the CI job runs the real server."""
import socketserver, threading, unittest

import valkey_equivalent as ve


class FakeResp(socketserver.StreamRequestHandler):
    store = {}

    def handle(self):
        while line := self.rfile.readline():
            n = int(line[1:-2])
            args = []
            for _ in range(n):
                size = int(self.rfile.readline()[1:-2])
                args.append(self.rfile.read(size + 2)[:-2].decode())
            cmd, key = args[0].upper(), args[1] if len(args) > 1 else None
            if cmd == "PING":
                out = b"+PONG\r\n"
            elif cmd == "GET":
                val = self.store.get(key)
                out = b"$-1\r\n" if val is None else b"$%d\r\n%s\r\n" % (len(val), val.encode())
            elif cmd == "SET":
                if "NX" in args and key in self.store:
                    out = b"$-1\r\n"
                else:
                    self.store[key], out = args[2], b"+OK\r\n"
            elif cmd == "DEL":
                out = b":%d\r\n" % sum(self.store.pop(k, None) is not None for k in args[1:])
            elif cmd == "TTL":
                out = b":30\r\n" if key in self.store else b":-2\r\n"
            else:
                out = b"-ERR unknown command\r\n"
            self.wfile.write(out)


class TestRespClient(unittest.TestCase):
    def test_cache_aside_flow_over_resp(self):
        srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), FakeResp)
        threading.Thread(target=srv.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()
        try:
            v = ve.Valkey(port=srv.server_address[1])
            self.assertEqual(v.cmd("PING"), "PONG")
            self.assertEqual(ve.get_price(v, "apple"), ("5", "miss -> filled"))
            self.assertEqual(ve.get_price(v, "apple"), ("5", "hit"))
            ve.set_price(v, "apple", 9)
            self.assertIsNone(v.cmd("GET", "price:apple"))  # invalidated
            self.assertEqual(ve.get_price(v, "apple"), ("9", "miss -> filled"))
            with self.assertRaises(RuntimeError):
                v.cmd("NOPE")
            v.close()
        finally:
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    unittest.main()
