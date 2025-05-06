# backend/trie_engine_wrapper.py

import trie_wrapper

class TrieEngine:
    def __init__(self):
        trie_wrapper.init_trie()

    def insert(self, rule: str):
        rule_lower = rule.lower()
        trie_wrapper.insert_rule(rule_lower)

    def search(self, rule: str) -> bool:
        rule_lower = rule.lower()
        found = trie_wrapper.search_rule(rule_lower)
        return bool(found)

    def free(self):
        trie_wrapper.free_trie()

# Example usage:
# trie = TrieEngine()
# trie.insert("example")
# print(trie.search("example"))  # True
# trie.free()
