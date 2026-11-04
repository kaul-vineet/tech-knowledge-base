"""Build-task solution (lesson 9): cap long-term memory at max_notes rows; saving evicts the oldest."""
from memory_agent import MemoryStore


class CappedMemoryStore(MemoryStore):
    def __init__(self, path=":memory:", max_notes=3):
        super().__init__(path)
        self.max_notes = max_notes

    def save(self, note):
        result = super().save(note)
        with self.db:  # keep only the newest max_notes rows (bounded growth, bounded recall noise)
            self.db.execute("DELETE FROM notes WHERE id NOT IN (SELECT id FROM notes ORDER BY id DESC LIMIT ?)",
                            (self.max_notes,))
        return result
