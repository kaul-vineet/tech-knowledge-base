"""Build task (lesson 9): cap long-term memory at max_notes; the oldest note is evicted."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "solution"))
from capped_memory import CappedMemoryStore  # noqa: E402


class BuildTask(unittest.TestCase):
    def test_oldest_note_evicted(self):
        store = CappedMemoryStore(max_notes=3)
        for i in range(1, 5):
            store.save(f"fact number {i} about staging")
        self.assertEqual(store.recall("staging", limit=10),
                         "4: fact number 4 about staging; 3: fact number 3 about staging; 2: fact number 2 about staging")
        store.close()


if __name__ == "__main__":
    unittest.main()
