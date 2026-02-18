from app.services.discovery import rank_authors, recency_score, _venue_matches_area


def test_recency_score_monotonic():
    newer = recency_score(2025)
    older = recency_score(2020)
    assert newer > older


def test_venue_matches_area_substring():
    # Full name match
    assert _venue_matches_area("Neural Information Processing Systems", ("neurips", "neural information processing"))
    # Abbreviation match
    assert _venue_matches_area("NeurIPS 2024", ("neurips", "neural information processing"))
    # ICML match
    assert _venue_matches_area("ICML", ("icml", "international conference on machine learning"))


def test_venue_matches_area_returns_false_for_nonmatch():
    assert not _venue_matches_area("SIGGRAPH", ("neurips", "icml", "iclr"))
    assert not _venue_matches_area(None, ("neurips", "icml"))
    assert not _venue_matches_area("CVPR", ())


def test_rank_authors_deterministic_tiebreak():
    payload = {
        "results": [
            {
                "id": "https://openalex.org/W1",
                "display_name": "Machine Learning Foundations",
                "publication_year": 2024,
                "primary_location": {"source": {"display_name": "NeurIPS 2024"}},
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

    ranked = rank_authors("Machine Learning", "https://openalex.org/I1", payload)

    assert len(ranked) == 2
    assert ranked[0].author_name == "Alice"
    assert ranked[1].author_name == "Bob"
    assert ranked[0].score == ranked[1].score


def test_rank_authors_excludes_non_venue_papers():
    payload = {
        "results": [
            {
                "id": "https://openalex.org/W1",
                "display_name": "Computer Graphics Paper",
                "publication_year": 2024,
                "primary_location": {"source": {"display_name": "SIGGRAPH"}},
                "authorships": [
                    {
                        "author": {"id": "https://openalex.org/A1", "display_name": "Alice"},
                        "institutions": [{"id": "https://openalex.org/I1", "display_name": "MIT"}],
                    }
                ],
            }
        ]
    }

    ranked = rank_authors("Machine Learning", "https://openalex.org/I1", payload)

    assert len(ranked) == 0


def test_rank_authors_null_primary_location_excluded():
    payload = {
        "results": [
            {
                "id": "https://openalex.org/W1",
                "display_name": "Machine Learning Foundations",
                "publication_year": 2024,
                "primary_location": None,
                "authorships": [
                    {
                        "author": {"id": "https://openalex.org/A1", "display_name": "Alice"},
                        "institutions": [{"id": "https://openalex.org/I1", "display_name": "MIT"}],
                    }
                ],
            }
        ]
    }

    ranked = rank_authors("Machine Learning", "https://openalex.org/I1", payload)

    # Works with no venue don't match any area, so no authors are ranked
    assert len(ranked) == 0


def test_rank_authors_handles_malformed_authorship_entries():
    payload = {
        "results": [
            {
                "id": "https://openalex.org/W1",
                "display_name": "Machine Learning Foundations",
                "publication_year": 2024,
                "primary_location": {"source": {"display_name": "ICML 2024"}},
                "authorships": [
                    {"author": None, "institutions": None},
                    None,
                    {
                        "author": {"id": "https://openalex.org/A1", "display_name": "Alice"},
                        "institutions": [{"id": "https://openalex.org/I1", "display_name": "MIT"}],
                    },
                ],
            }
        ]
    }

    ranked = rank_authors("Machine Learning", "https://openalex.org/I1", payload)

    assert len(ranked) == 1
    assert ranked[0].author_name == "Alice"
