import unittest
from trie_engine import TrieEngine

class TestTrieEngine(unittest.TestCase):
    def setUp(self):
        self.trie = TrieEngine()

    def tearDown(self):
        self.trie.free()

    def test_insert_and_search(self):
        # Test basic insertion and search
        self.trie.insert("hello")
        self.assertTrue(self.trie.search("hello"))
        self.assertFalse(self.trie.search("world"))

    def test_case_insensitivity(self):
        # Test case insensitivity
        self.trie.insert("Hello")
        self.assertTrue(self.trie.search("hello"))
        self.assertTrue(self.trie.search("HELLO"))
        self.assertTrue(self.trie.search("HeLLo"))

    def test_empty_string(self):
        # Test empty string handling
        self.trie.insert("")
        self.assertTrue(self.trie.search(""))

    def test_special_characters(self):
        # Test special characters (should be ignored)
        self.trie.insert("hello123!")
        self.assertTrue(self.trie.search("hello"))
        self.assertTrue(self.trie.search("hello123!"))  # Should match since we normalize to "hello"
        self.assertTrue(self.trie.search("HELLO!@#"))   # Should match since we normalize to "hello"

    def test_multiple_words(self):
        # Test multiple words
        words = ["hello", "world", "python", "programming"]
        for word in words:
            self.trie.insert(word)
        
        for word in words:
            self.assertTrue(self.trie.search(word))
        
        self.assertFalse(self.trie.search("nonexistent"))

if __name__ == '__main__':
    unittest.main() 