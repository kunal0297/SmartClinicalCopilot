import pytest
from trie_engine import TrieEngine, TrieNode

@pytest.fixture
def trie_engine():
    return TrieEngine()

@pytest.fixture
def sample_rules():
    return [
        {
            "id": "CKD_NSAID",
            "text": "Avoid NSAIDs in advanced CKD",
            "category": "medication",
            "severity": "error",
            "confidence": 0.95,
            "conditions": [
                {
                    "type": "lab",
                    "code": "eGFR",
                    "operator": "<",
                    "value": 30,
                    "unit": "mL/min/1.73m²"
                },
                {
                    "type": "medication",
                    "code": "ibuprofen",
                    "operator": "=",
                    "value": "active"
                }
            ]
        },
        {
            "id": "QT_Prolongation",
            "text": "Monitor for QT prolongation",
            "category": "lab",
            "severity": "warning",
            "confidence": 0.85,
            "conditions": [
                {
                    "type": "lab",
                    "code": "QT_interval",
                    "operator": ">",
                    "value": 450,
                    "unit": "ms"
                },
                {
                    "type": "medication",
                    "code": "amiodarone",
                    "operator": "=",
                    "value": "active"
                }
            ]
        }
    ]

def test_trie_node_creation():
    node = TrieNode()
    assert node.children == {}
    assert node.is_end_of_word is False
    assert node.rule_ids == set()

def test_insert_word(trie_engine):
    trie_engine.insert("test")
    assert "t" in trie_engine.root.children
    assert "e" in trie_engine.root.children["t"].children
    assert "s" in trie_engine.root.children["t"].children["e"].children
    assert "t" in trie_engine.root.children["t"].children["e"].children["s"].children
    assert trie_engine.root.children["t"].children["e"].children["s"].children["t"].is_end_of_word is True

def test_insert_word_with_rule_id(trie_engine):
    trie_engine.insert("test", "rule1")
    assert "t" in trie_engine.root.children
    assert "rule1" in trie_engine.root.children["t"].children["e"].children["s"].children["t"].rule_ids

def test_search_prefix(trie_engine):
    trie_engine.insert("test")
    trie_engine.insert("testing")
    trie_engine.insert("tested")
    
    results = trie_engine.search("test")
    assert len(results) == 3
    assert "test" in results
    assert "testing" in results
    assert "tested" in results

def test_search_nonexistent_prefix(trie_engine):
    trie_engine.insert("test")
    results = trie_engine.search("nonexistent")
    assert len(results) == 0

def test_get_rule_ids(trie_engine):
    trie_engine.insert("test", "rule1")
    trie_engine.insert("test", "rule2")
    
    rule_ids = trie_engine.get_rule_ids("test")
    assert len(rule_ids) == 2
    assert "rule1" in rule_ids
    assert "rule2" in rule_ids

def test_add_rule(trie_engine, sample_rules):
    trie_engine.add_rule(sample_rules[0])
    
    # Check if rule text is inserted
    results = trie_engine.search("Avoid NSAIDs")
    assert len(results) == 1
    assert "Avoid NSAIDs in advanced CKD" in results
    
    # Check if rule ID is associated
    rule_ids = trie_engine.get_rule_ids("Avoid NSAIDs in advanced CKD")
    assert len(rule_ids) == 1
    assert "CKD_NSAID" in rule_ids

def test_remove_rule(trie_engine, sample_rules):
    trie_engine.add_rule(sample_rules[0])
    trie_engine.remove_rule("CKD_NSAID")
    
    # Check if rule text is removed
    results = trie_engine.search("Avoid NSAIDs")
    assert len(results) == 0
    
    # Check if rule ID is removed
    rule_ids = trie_engine.get_rule_ids("Avoid NSAIDs in advanced CKD")
    assert len(rule_ids) == 0

def test_get_all_rules(trie_engine, sample_rules):
    for rule in sample_rules:
        trie_engine.add_rule(rule)
    
    all_rules = trie_engine.get_all_rules()
    assert len(all_rules) == 2
    assert "CKD_NSAID" in all_rules
    assert "QT_Prolongation" in all_rules

def test_case_insensitive_search(trie_engine):
    trie_engine.insert("Test")
    results = trie_engine.search("test")
    assert len(results) == 1
    assert "Test" in results

def test_empty_prefix_search(trie_engine):
    trie_engine.insert("test")
    trie_engine.insert("testing")
    results = trie_engine.search("")
    assert len(results) == 2
    assert "test" in results
    assert "testing" in results

def test_duplicate_rule_ids(trie_engine):
    trie_engine.insert("test", "rule1")
    trie_engine.insert("test", "rule1")  # Duplicate rule ID
    
    rule_ids = trie_engine.get_rule_ids("test")
    assert len(rule_ids) == 1
    assert "rule1" in rule_ids

def test_remove_nonexistent_rule(trie_engine):
    trie_engine.insert("test", "rule1")
    trie_engine.remove_rule("nonexistent")
    
    rule_ids = trie_engine.get_rule_ids("test")
    assert len(rule_ids) == 1
    assert "rule1" in rule_ids 