import unittest
from urllib.error import HTTPError

import two_services as ts


class TestTwoServices(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = ts.start_b()
        cls.url = f"http://127.0.0.1:{cls.b.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.b.shutdown()
        cls.b.server_close()

    def test_request_response(self):
        data, ms = ts.call_b(self.url, "plum")
        self.assertEqual(data, {"item": "plum", "price": 5})
        self.assertGreater(ms, 0)
        self.assertLess(ms, 2000)

    def test_unknown_item_is_404(self):
        with self.assertRaises(HTTPError) as ctx:
            ts.call_b(self.url, "kiwi")
        self.assertEqual(ctx.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
