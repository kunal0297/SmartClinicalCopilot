from typing import List, Dict, Any, Set
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrieNode:
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end_of_word: bool = False
        self.rule_ids: Set[str] = set()

class TrieEngine:
    def __init__(self):
        self.root = TrieNode()
        self.rules: Dict[str, Dict[str, Any]] = {}

    def insert(self, text: str, rule_id: str = None) -> None:
        """
        Insert a text string into the trie.
        
        Args:
            text: The text to insert
            rule_id: Optional rule ID associated with this text
        """
        node = self.root
        for char in text.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        if rule_id:
            node.rule_ids.add(rule_id)

    def search(self, prefix: str) -> List[str]:
        """
        Search for all texts that start with the given prefix.
        
        Args:
            prefix: The prefix to search for
            
        Returns:
            List of matching texts
        """
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        
        return self._get_all_words(node, prefix)

    def _get_all_words(self, node: TrieNode, prefix: str) -> List[str]:
        """
        Get all words starting from a given node.
        
        Args:
            node: The current trie node
            prefix: The prefix accumulated so far
            
        Returns:
            List of complete words
        """
        words = []
        if node.is_end_of_word:
            words.append(prefix)
        
        for char, child in node.children.items():
            words.extend(self._get_all_words(child, prefix + char))
        
        return words

    def get_rule_ids(self, text: str) -> Set[str]:
        """
        Get all rule IDs associated with a text.
        
        Args:
            text: The text to look up
            
        Returns:
            Set of rule IDs
        """
        node = self.root
        for char in text.lower():
            if char not in node.children:
                return set()
            node = node.children[char]
        
        return node.rule_ids if node.is_end_of_word else set()

    def add_rule(self, rule: Dict[str, Any]) -> None:
        """
        Add a rule to the trie engine.
        
        Args:
            rule: The rule dictionary to add
        """
        if 'id' not in rule or 'text' not in rule:
            logger.error("Invalid rule format: missing id or text")
            return

        rule_id = rule['id']
        self.rules[rule_id] = rule
        
        # Insert the rule text
        self.insert(rule['text'], rule_id)
        
        # Insert keywords from conditions
        for condition in rule.get('conditions', []):
            if 'type' in condition:
                self.insert(condition['type'], rule_id)

    def remove_rule(self, rule_id: str) -> None:
        """
        Remove a rule from the trie engine.
        
        Args:
            rule_id: The ID of the rule to remove
        """
        if rule_id in self.rules:
            rule = self.rules[rule_id]
            # Remove the rule text
            self._remove_text(rule['text'], rule_id)
            
            # Remove keywords from conditions
            for condition in rule.get('conditions', []):
                if 'type' in condition:
                    self._remove_text(condition['type'], rule_id)
            
            # Remove from rules dictionary
            del self.rules[rule_id]

    def _remove_text(self, text: str, rule_id: str) -> None:
        """
        Remove a text and its associated rule ID from the trie.
        
        Args:
            text: The text to remove
            rule_id: The rule ID to remove
        """
        node = self.root
        for char in text.lower():
            if char not in node.children:
                return
            node = node.children[char]
        
        if node.is_end_of_word:
            node.rule_ids.discard(rule_id)
            if not node.rule_ids:
                node.is_end_of_word = False

    def get_rule(self, rule_id: str) -> Dict[str, Any]:
        """
        Get a rule by its ID.
        
        Args:
            rule_id: The ID of the rule to get
            
        Returns:
            The rule dictionary or None if not found
        """
        return self.rules.get(rule_id)

    def get_all_rules(self) -> List[Dict[str, Any]]:
        """
        Get all rules in the engine.
        
        Returns:
            List of all rule dictionaries
        """
        return list(self.rules.values())

# Example usage:
# trie = TrieEngine()
# trie.add_rule({
#     "id": "rule1",
#     "text": "Monitor QT interval",
#     "conditions": [{"type": "QT_interval"}]
# })
# matches = trie.search("mon")
# print(matches)  # ['monitor qt interval'] 