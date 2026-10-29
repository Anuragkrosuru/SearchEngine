"""Checks for explanation arithmetic and frontend integration."""
import math
import pytest
import requests
import index.api.main as ranking
import search

@pytest.fixture
def tiny_index(monkeypatch):
    monkeypatch.setattr(ranking, 'index_data', {
        'alpha': 'alpha 2 00000001 3 100 00000002 1 25',
        'beta': 'beta 1 00000001 4 100 00000002 2 25',
    })
    monkeypatch.setattr(ranking, 'stopwords', {'the'})
    monkeypatch.setattr(ranking, 'pagerank', {'00000001': 0.1, '00000002': 0.8})

@pytest.mark.parametrize('weight', [0, 0.5, 1])
def test_score_components(tiny_index, weight):
    hits = ranking.perform_search('alpha alpha beta', weight, True)
    for hit in hits:
        e = hit['explanation']
        assert e['text_contribution'] + e['pagerank_contribution'] == pytest.approx(hit['score'])
        assert sum(t['cosine_contribution'] for t in e['matched_terms']) == pytest.approx(e['text_relevance'])
        assert len(e['matched_terms']) == 2
    first = next(hit for hit in hits if hit['docid'] == 1)
    assert first['explanation']['text_relevance'] == pytest.approx(28 / (math.sqrt(17) * 10))

def test_api_compatibility(tiny_index):
    from index import app
    client = app.test_client()
    ordinary = client.get('/api/v1/hits/?q=alpha').get_json()['hits']
    assert set(ordinary[0]) == {'docid', 'score'}
    explained = client.get('/api/v1/hits/?q=alpha&explain=1&w=nan').get_json()['hits']
    assert explained[0]['explanation']['pagerank_weight'] == 0.5
    assert ranking.perform_search('alpha unknown', 0.5, True) == []
    assert ranking.perform_search('the', 0.5, True) == []

def test_frontend(tiny_index, monkeypatch):
    import importlib
    view = importlib.import_module('search.views.main')
    monkeypatch.setattr(view, 'fetch_segment', lambda *args: ranking.perform_search('alpha', 0.5, True))
    monkeypatch.setattr(search.model, 'get_documents', lambda ids: [
        {'docid': i, 'title': '<unsafe>', 'summary': 'Example summary', 'url': 'https://example.com'} for i in ids
    ])
    with search.app.test_client() as client:
        assert client.get('/').status_code == 200
        response = client.get('/?q=alpha&w=nan')
        assert b'Why this result?' in response.data
        assert b'&lt;unsafe&gt;' in response.data
        assert response.data.count(b'<article class="doc">') == 2
        assert b'Final score' in response.data
        def unavailable(*args):
            raise requests.ConnectionError('offline')
        monkeypatch.setattr(view, 'fetch_segment', unavailable)
        response = client.get('/?q=alpha')
        assert response.status_code == 200
        assert b'Results may be incomplete' in response.data
