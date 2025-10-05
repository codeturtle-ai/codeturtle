import pytest
from src.ai.knowledge_base import FastAPISecurityKB

def test_kb_retrieve():
    kb = FastAPISecurityKB()
    results = kb.retrieve("SELECT * FROM users WHERE id = '1'")
    assert len(results) > 0
    assert "sql_injection" in [r["vulnerability"] for r in results]

def test_kb_no_match():
    kb = FastAPISecurityKB()
    results = kb.retrieve("print('hello world')")
    assert len(results) == 0
