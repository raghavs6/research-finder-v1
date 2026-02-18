import type { DiscoveryAuthorResult } from "../types/api";

type ProfessorResultsProps = {
  results: DiscoveryAuthorResult[];
  total: number;
  offset: number;
  limit: number;
  onPrev: () => void;
  onNext: () => void;
};

const RANK_COLORS = ["#00c8d4", "#7b5ea7", "#e67e22", "#f1c40f", "#2ecc71"];

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
      <div className="step-label">
        <span className="step-num">003</span> // RESULTS
      </div>
      <div className="results-header">
        <h2>Ranked Results</h2>
        <p className="results-count">
          Showing {results.length} of {total}
        </p>
      </div>

      {results.length === 0 ? <p>No professors matched this query yet.</p> : null}

      <div className="cards">
        {results.map((author, index) => {
          const rank = offset + index + 1;
          const rankStr = String(rank).padStart(3, "0");
          const rankAccent = RANK_COLORS[(rank - 1) % RANK_COLORS.length];
          return (
            <article
              key={author.author_id}
              className="result-card"
              style={{ "--rank-accent": rankAccent } as React.CSSProperties}
            >
              <div className="step-label">
                <span className="step-num">{rankStr}</span> // {author.author_name.toUpperCase()}
              </div>
              <h3>{author.author_name}</h3>
              <p>{author.institution_name ?? "Unknown institution"}</p>
              <p className="score-line">
                SCR: {author.score.toFixed(2)} | WRK: {author.matching_works_count} | RCT: {author.recent_works_count}
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
          );
        })}
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
