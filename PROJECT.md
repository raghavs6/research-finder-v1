# Project: Research Cold Emailer

## 1. Vision

Build a web application that helps students discover professors to contact for research opportunities.

The app allows users to:
1. Search by research topic (e.g., "machine learning", "oncology").
2. Filter by university.
3. View ranked professors with relevant publications.
4. Paste their resume.
5. Generate a personalized, grounded cold email template.

The system must be:
- Deterministic
- Testable
- Secure
- Resume-privacy safe
- Simple (MVP first)

---

## 2. Core Problem

Students struggle to:
- Identify professors working in a specific niche.
- Understand which professors are active in recent publications.
- Write personalized emails referencing specific work.
- Tailor their resume experience to the professor’s research.

This app automates discovery and personalization while maintaining accuracy and integrity.

---

## 3. Data Source

Primary source: OpenAlex API

Used for:
- Institution search
- Author lookup
- Works (publications) retrieval
- Author affiliations

No scraping.
No Google Scholar automation.

---

## 4. MVP Scope

### Phase 1 – Discovery
- Search institutions by name
- Search works by topic + institution
- Aggregate authors
- Rank authors deterministically
- Return top works per author

### Phase 2 – Personalization
- Accept pasted resume text
- Extract:
  - Key skills
  - 2–4 high-signal bullets
- Generate email template:
  - Reference one real paper
  - Use real resume snippets
  - Clear research request
  - ≤ 180 words (short mode)

No PDF upload in MVP.
No authentication.
No data persistence.

---

## 5. Architecture

Frontend:
- React + Vite
- Calls backend API
- Displays:
  - Search form
  - Ranked professor list
  - Professor detail page
  - Resume input
  - Email preview

Backend:
- FastAPI
- httpx (OpenAlex client)
- Deterministic ranking logic
- Template-based email generation

Testing:
- pytest (backend)
- All OpenAlex calls mocked in tests

CI:
- GitHub Actions
- Runs pytest
- Runs frontend build

---

## 6. Security Principles

1. Resume text must never be logged.
2. Resume text must not be stored.
3. No API keys committed to repository.
4. External API calls must have timeouts and retry limits.
5. Tests must not call real external APIs.

---

## 7. Ranking Strategy (MVP)

Score authors by:
- Number of topic-matching works
- Number of publications at top confrences
- Recency bonus
- Deterministic alphabetical tie-break



---

## 8. Email Generation Rules

Email must:
- Reference 1 real paper title
- Use 2 real resume snippets
- Stay within length limit
- Make a specific ask


---