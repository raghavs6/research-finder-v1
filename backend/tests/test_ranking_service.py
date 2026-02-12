from app.services.discovery import rank_authors, recency_score, relevance_score, reconstruct_abstract


def test_reconstruct_abstract():
    inverted = {"machine": [0], "learning": [1], "applications": [2]}
    assert reconstruct_abstract(inverted) == "machine learning applications"


def test_relevance_score_overlap_ratio():
    score = relevance_score("machine learning", "Machine Learning Methods", "useful methods")
    assert score == 1.0


def test_recency_score_monotonic():
    newer = recency_score(2025)
    older = recency_score(2020)
    assert newer > older


def test_rank_authors_deterministic_tiebreak():
    payload = {
        "results": [
            {
                "id": "https://openalex.org/W1",
                "display_name": "Machine Learning Foundations",
                "publication_year": 2024,
                "primary_location": {"source": {"display_name": "neurips"}},
                "abstract_inverted_index": {"machine": [0], "learning": [1]},
                "authorships": [
                    {
                        "author": {"id": "https://openalex.org/A1", "display_name": "Alice"},
                        "institutions": [{"id": "https://openalex.org/I1", "display_name": "MIT"}],
                    },
                    {
                        "author": {"id": "https://openalex.org/A2", "display_name": "Bob"},
                        "institutions": [{"id": "https://openalex.org/I1", "display_name": "MIT"}],
                    },
                ],
            }
        ]
    }

    ranked = rank_authors("machine learning", "https://openalex.org/I1", payload)

    assert len(ranked) == 2
    assert ranked[0].author_name == "Alice"
    assert ranked[1].author_name == "Bob"
    assert ranked[0].score == ranked[1].score
