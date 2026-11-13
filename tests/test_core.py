import pytest
from voicedata.core import create_demo_database,parse_intent,query_revenue,analyze

def test_demo_trend(tmp_path):
    db=tmp_path/"demo.db"
    create_demo_database(db)
    result=analyze(query_revenue(db,parse_intent("Show revenue for DemoCo")))
    assert result["highest_growth"]["quarter"]=="2025-Q4"
    assert result["highest_growth"]["growth_pct"]==29.63

def test_unsupported_question():
    with pytest.raises(ValueError):
        parse_intent("delete all records")

def test_empty_data(tmp_path):
    db=tmp_path/"demo.db"
    create_demo_database(db)
    with pytest.raises(LookupError):
        query_revenue(db,{"operation":"revenue_trend","company":"Missing"})

def test_zero_denominator():
    result=analyze([{"quarter":"Q1","revenue":0},{"quarter":"Q2","revenue":10}])
    assert result["highest_growth"] is None
