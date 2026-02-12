import type { DiscoveryAuthorResult } from "../types/api";

type ProfessorResultsProps = {
  results: DiscoveryAuthorResult[];
  total: number;
  offset: number;
  limit: number;
  onPrev: () => void;
  onNext: () => void;
};

export function ProfessorResults({
  results,
  total,
  offset,
  limit,
  onPrev,
  onNext
}: ProfessorResultsProps) {
  const canPrev = offset > 0;
  const canNext = offset + limit < total;

  return (
    <section className="panel">
      <div className="results-header">
        <h2>3. Ranked Results</h2>
        <p>
          Showing {results.length} of {total}
        </p>
      </div>

      {results.length === 0 ? <p>No professors matched this query yet.</p> : null}

      <div className="cards">
        {results.map((author) => (
          <article key={author.author_id} className="result-card">
            <h3>{author.author_name}</h3>
            <p>{author.institution_name ?? "Unknown institution"}</p>
            <p>
              score {author.score} | works {author.matching_works_count} | recent {author.recent_works_count}
            </p>
            <ul>
              {author.top_works.map((work) => (
                <li key={work.work_id}>
                  {work.openalex_url ? (
                    <a href={work.openalex_url} target="_blank" rel="noreferrer">
                      {work.title}
                    </a>
                  ) : (
                    <span>{work.title}</span>
                  )}
                  <small>
                    {work.publication_year ?? "N/A"} | {work.venue ?? "Unknown venue"}
                  </small>
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>

      <div className="pagination">
        <button type="button" onClick={onPrev} disabled={!canPrev}>
          Prev
        </button>
        <button type="button" onClick={onNext} disabled={!canNext}>
          Next
        </button>
      </div>
    </section>
  );
}
