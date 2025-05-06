import trie_wrapper
from typing import Optional

class TrieEngine:
    def __init__(self):
        """
        Initialize the trie engine.
        """
        trie_wrapper.init_trie()

    def insert(self, rule: str) -> None:
        """
        Insert a rule into the trie.

        Args:
            rule (str): The rule to insert.
        """
        rule_lower = rule.lower()
        trie_wrapper.insert_rule(rule_lower)

    def search(self, rule: str) -> bool:
        """
        Search for a rule in the trie.

        Args:
            rule (str): The rule to search for.

        Returns:
            bool: True if the rule is found, False otherwise.
        """
        rule_lower = rule.lower()
        found = trie_wrapper.search_rule(rule_lower)
        return bool(found)

    def free(self) -> None:
        """
        Free the trie memory.
        """
        trie_wrapper.free_trie()

    def __enter__(self):
        """
        Context manager enter method.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit method. Frees the trie memory.
        """
        self.free()

# Example usage:
# with TrieEngine() as trie:
#     trie.insert("example")
#     print(trie.search("example"))  # Output: True
