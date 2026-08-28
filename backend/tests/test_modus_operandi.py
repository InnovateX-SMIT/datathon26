import pytest
from datetime import datetime, date
from fastapi.testclient import TestClient

from backend.core.database import SessionLocal, Base, engine
from backend.app.main import app
from backend.models.fir_case import CaseMaster, Inv_OccuranceTime
from backend.models.fir_people import Accused
from backend.models.fir_organization import Unit
from backend.models.fir_geography import District
from backend.models.fir_law import CrimeHead, CrimeSubHead, Act, Section, ActSectionAssociation
from backend.models.fir_lookup import CaseCategory, GravityOffence, CaseStatusMaster
from backend.analytics.crime_analysis.modus_operandi_service import ModusOperandiService

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture(scope="module")
def db_session():
    session = SessionLocal()
    yield session
    session.close()

def test_mo_extraction_empty_and_insufficient_text(db_session):
    service = ModusOperandiService(db_session)
    
    # 1. Empty string
    attrs, tags, summary, suff = service.extract_mo(raw_text="")
    assert suff is False
    assert summary == "MO unavailable / insufficient text"
    assert tags == []
    assert attrs.entry_method is None

    # 2. Very short string
    attrs, tags, summary, suff = service.extract_mo(raw_text="No")
    assert suff is False
    assert summary == "MO unavailable / insufficient text"

    # 3. None text
    attrs, tags, summary, suff = service.extract_mo(raw_text=None)
    assert suff is False
    assert summary == "MO unavailable / insufficient text"

def test_mo_extraction_rich_behavioral_text(db_session):
    service = ModusOperandiService(db_session)
    
    # Narrative describing burglary
    burglary_facts = (
        "On 12-05-2024, accused entered through rear window after lock broken at residential house in night-time. "
        "Used iron rod to breach safety grill and fled on motorcycle."
    )
    
    attrs, tags, summary, suff = service.extract_mo(
        raw_text=burglary_facts,
        crime_head="House Theft"
    )
    
    assert suff is True
    assert attrs.entry_method in ["Rear Window / Window Breach", "Forced Door / Lock Breach"]
    assert attrs.weapon_tool == "Mechanical Breaching Tool / Rod"
    assert attrs.target_type == "Residential Premise"
    assert attrs.time_pattern == "Night-time Operation"
    assert attrs.escape_method == "Motorcycle Quick Getaway"
    assert "House Theft" in tags
    assert "Entry:" in summary
    assert "Tool/Vector:" in summary

def test_mo_extraction_cyber_and_financial_text(db_session):
    service = ModusOperandiService(db_session)
    
    cyber_facts = (
        "Dark web crime operation involving unauthorized access to server infrastructure and crypto mixer for money laundering."
    )
    
    attrs, tags, summary, suff = service.extract_mo(
        raw_text=cyber_facts,
        crime_head="Dark Web Crime"
    )
    
    assert suff is True
    assert attrs.entry_method in ["Dark Web Infiltration / Hidden Network", "System Intrusion / Unauthorized Access"]
    assert attrs.weapon_tool == "Crypto Tumbler / Mixer Utility"
    assert attrs.target_type == "IT / Server Infrastructure"
    assert attrs.approach_method in ["Darknet Transaction & Anonymized Channel", "Financial Layering & Obfuscation"]
    assert "Dark Web Crime" in tags

def test_mo_similarity_math_and_ranking(db_session):
    service = ModusOperandiService(db_session)
    
    # Test case MO profile from active DB
    fir_case = db_session.query(CaseMaster).first()
    if fir_case:
        profile = service.get_case_mo_profile(fir_case.id)
        assert profile is not None
        assert profile.case_id == fir_case.id
        assert isinstance(profile.similar_cases, list)
        
        # Verify similarity scores are mathematical (0.0 <= score <= 1.0) and descending
        scores = [sc.similarity_score for sc in profile.similar_cases]
        for s in scores:
            assert 0.0 <= s <= 1.0
        
        assert scores == sorted(scores, reverse=True)

def test_cross_jurisdiction_patterns(db_session):
    service = ModusOperandiService(db_session)
    patterns = service.get_cross_jurisdiction_patterns(min_similarity=0.30, limit=10)
    assert patterns is not None
    assert isinstance(patterns.jurisdiction_pairs, list)
    assert isinstance(patterns.sample_links, list)
    
    for link in patterns.sample_links:
        assert link.source_district != link.target_district
        assert 0.0 <= link.similarity_score <= 1.0
        assert link.similarity_percentage == int(round(link.similarity_score * 100))

def test_offender_behavioral_profile(db_session):
    service = ModusOperandiService(db_session)
    accused = db_session.query(Accused).first()
    if accused:
        profile = service.get_offender_behavioral_profile(accused.id)
        assert profile is not None
        assert profile.accused_id == accused.id
        assert profile.name == accused.AccusedName
        assert profile.total_associated_cases >= 1
        assert isinstance(profile.recurring_mo_signatures, list)
        assert isinstance(profile.associated_cases, list)

def test_api_case_mo_endpoint(client, db_session):
    fir_case = db_session.query(CaseMaster).first()
    if fir_case:
        response = client.get(f"/api/v1/fir/{fir_case.id}/mo")
        assert response.status_code == 200
        data = response.json()
        assert data["case_id"] == fir_case.id
        assert "mo_summary" in data
        assert "attributes" in data
        assert "behavioral_tags" in data
        assert "similar_cases" in data
        assert "interpretation_disclaimer" in data
        assert "Investigative Intelligence" in data["interpretation_disclaimer"]

def test_api_case_mo_not_found(client):
    response = client.get("/api/v1/fir/99999999/mo")
    assert response.status_code == 404

def test_api_similar_cases_endpoint(client, db_session):
    fir_case = db_session.query(CaseMaster).first()
    if fir_case:
        response = client.get(f"/api/v1/fir/mo/similar-cases?case_id={fir_case.id}&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for item in data:
            assert "case_id" in item
            assert "similarity_score" in item
            assert "similarity_percentage" in item
            assert "matching_attributes" in item

def test_api_cross_jurisdiction_endpoint(client):
    response = client.get("/api/v1/fir/mo/cross-jurisdiction?min_similarity=0.30&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "total_cross_jurisdiction_patterns" in data
    assert "jurisdiction_pairs" in data
    assert "sample_links" in data

def test_api_offender_mo_endpoint(client, db_session):
    accused = db_session.query(Accused).first()
    if accused:
        response = client.get(f"/api/v1/fir/mo/offender/{accused.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["accused_id"] == accused.id
        assert "recurring_mo_signatures" in data
        assert "associated_cases" in data
        assert "interpretation_disclaimer" in data
