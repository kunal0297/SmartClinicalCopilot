"""End-to-end and unit tests for the Smart Clinical Copilot core.

These tests exercise the *actual* shipped behaviour: rule loading, the trie
autocomplete engine, condition matching, and the public API — all running with
SQLite and no external services (see conftest.py).
"""

import os

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.rule_loader import RuleLoader
from backend.trie_engine import TrieEngine

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RULES_DIR = os.path.join(REPO_ROOT, "rules")


@pytest.fixture(scope="module")
def client():
    # The context manager triggers startup events (which populate the trie
    # engine used by /suggest-rules).
    with TestClient(app) as c:
        yield c


# --------------------------------------------------------------------------
# Rule loading
# --------------------------------------------------------------------------
def test_rules_load_from_project_rules_dir():
    rules = RuleLoader(RULES_DIR).load_rules()
    ids = {r.id for r in rules}
    assert "CKD_NSAID" in ids
    assert "QT_Prolongation" in ids


def test_loaded_rule_has_conditions_and_actions():
    rules = RuleLoader(RULES_DIR).load_rules()
    ckd = next(r for r in rules if r.id == "CKD_NSAID")
    assert ckd.text
    assert len(ckd.conditions) >= 1
    assert len(ckd.actions) >= 1


# --------------------------------------------------------------------------
# Trie autocomplete engine
# --------------------------------------------------------------------------
def test_trie_add_and_search_dict_rule():
    trie = TrieEngine()
    trie.add_rule({"id": "CKD_NSAID", "text": "Avoid NSAIDs in advanced CKD",
                   "conditions": [{"type": "eGFR"}]})
    # rule id is indexed and searchable
    assert "ckd_nsaid" in trie.search("ckd")
    # rule text is indexed and searchable
    assert "avoid nsaids in advanced ckd" in trie.search("avoid")


def test_trie_accepts_pydantic_rule_model():
    rules = RuleLoader(RULES_DIR).load_rules()
    trie = TrieEngine()
    for rule in rules:
        trie.add_rule(rule)  # should accept Pydantic models, not just dicts
    assert trie.get_rule("CKD_NSAID") is not None
    assert "monitor for qt prolongation" in trie.search("monitor")


# --------------------------------------------------------------------------
# API: health & metadata
# --------------------------------------------------------------------------
def test_root_endpoint(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Smart Clinical Copilot" in r.json()["message"]


def test_health_endpoint(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_detailed_health_reports_rule_count(client):
    r = client.get("/health/detailed")
    assert r.status_code == 200
    assert r.json()["components"]["rules"]["count"] >= 2


# --------------------------------------------------------------------------
# API: demo patients
# --------------------------------------------------------------------------
def test_demo_patients_endpoint(client):
    r = client.get("/demo-patients")
    assert r.status_code == 200
    patients = r.json()
    assert {p["id"] for p in patients} == {"demo-1", "demo-2", "demo-3"}


@pytest.fixture
def demo_patients(client):
    return client.get("/demo-patients").json()


# --------------------------------------------------------------------------
# API: clinical rule matching (the core feature)
# --------------------------------------------------------------------------
def test_match_rules_triggers_ckd_nsaid(client, demo_patients):
    p1 = next(p for p in demo_patients if p["id"] == "demo-1")
    r = client.post("/match-rules", json=p1)
    assert r.status_code == 200
    alerts = r.json()
    assert any(a["rule_id"] == "CKD_NSAID" for a in alerts)
    ckd = next(a for a in alerts if a["rule_id"] == "CKD_NSAID")
    assert ckd["severity"] == "error"
    # evidence lists both the low eGFR and the NSAID
    evidence = " ".join(ckd["triggered_by"]).lower()
    assert "filtration" in evidence or "egfr" in evidence
    assert "ibuprofen" in evidence


def test_match_rules_triggers_qt_prolongation(client, demo_patients):
    p2 = next(p for p in demo_patients if p["id"] == "demo-2")
    alerts = client.post("/match-rules", json=p2).json()
    assert any(a["rule_id"] == "QT_Prolongation" for a in alerts)


def test_match_rules_healthy_patient_has_no_alerts(client, demo_patients):
    p3 = next(p for p in demo_patients if p["id"] == "demo-3")
    alerts = client.post("/match-rules", json=p3).json()
    assert alerts == []


# --------------------------------------------------------------------------
# API: autocomplete & analytics
# --------------------------------------------------------------------------
def test_suggest_rules_endpoint(client):
    r = client.get("/suggest-rules", params={"prefix": "ckd"})
    assert r.status_code == 200
    assert "ckd_nsaid" in r.json()["suggestions"]


def test_cohort_analytics_endpoint(client):
    r = client.get("/cohort-analytics")
    assert r.status_code == 200
    data = r.json()
    assert data["total_patients"] == 3
    assert data["ckd_count"] >= 1


def test_get_patient_by_id(client):
    r = client.get("/patients/demo-1")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "demo-1"
    assert body["conditions"]["observations"]
