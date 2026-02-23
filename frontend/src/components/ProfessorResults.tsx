import type { CSSProperties } from "react";

import type { DiscoveryAuthorResult } from "../types/api";

type ProfessorResultsProps = {
  isOpen: boolean;
  onClose: () => void;
  results: DiscoveryAuthorResult[];
  total: number;
  isLoading: boolean;
};

const RANK_COLORS = ["#00c8d4", "#7b5ea7", "#e67e22", "#f1c40f", "#2ecc71"];

export function ProfessorResults({
  isOpen,
  onClose,
  results,
  total,
  isLoading
}: ProfessorResultsProps) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <section
        className="panel modal-dialog"
        role="dialog"
        aria-modal="true"
        aria-label="Professor results"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="step-label">
          <span className="step-num">003</span> // RESULTS
        </div>
        <div className="results-header">
          <h2>Top Professors</h2>
          <button type="button" className="modal-close" onClick={onClose}>
            Close
          </button>
        </div>
        <p className="results-count">
          Showing {results.length} of {total}
        </p>

        {isLoading ? <p>Loading professors...</p> : null}
        {!isLoading && results.length === 0 ? <p>No professors matched this query yet.</p> : null}

        <div className="cards">
          {results.map((author, index) => {
            const rank = index + 1;
            const rankStr = String(rank).padStart(3, "0");
            const rankAccent = RANK_COLORS[(rank - 1) % RANK_COLORS.length];
            return (
              <article
                key={author.author_id}
                className="result-card"
                style={{ "--rank-accent": rankAccent } as CSSProperties}
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

        <div className="modal-footer">
          <button type="button" onClick={onClose}>
            Done
          </button>
        </div>
      </section>
    </div>
  );
}
