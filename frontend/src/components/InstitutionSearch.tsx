import type { InstitutionItem } from "../types/api";

type InstitutionSearchProps = {
  query: string;
  onQueryChange: (value: string) => void;
  onSearch: () => void;
  institutions: InstitutionItem[];
  selectedInstitutionId: string;
  onSelectInstitution: (id: string) => void;
  isLoading: boolean;
};

export function InstitutionSearch({
  query,
  onQueryChange,
  onSearch,
  institutions,
  selectedInstitutionId,
  onSelectInstitution,
  isLoading
}: InstitutionSearchProps) {
  return (
    <section className="panel">
      <h2>1. Choose University</h2>
      <div className="form-row">
        <input
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          placeholder="Search institution, e.g. MIT"
          aria-label="Institution query"
        />
        <button type="button" onClick={onSearch} disabled={isLoading || query.trim().length < 2}>
          {isLoading ? "Searching..." : "Search"}
        </button>
      </div>

      <ul className="institution-list">
        {institutions.map((item) => {
          const isSelected = selectedInstitutionId === item.institution_id;
          return (
            <li key={item.institution_id}>
              <button
                type="button"
                className={isSelected ? "institution-button selected" : "institution-button"}
                onClick={() => onSelectInstitution(item.institution_id)}
              >
                <span>{item.name}</span>
                <small>
                  {item.country_code ?? "N/A"} | works: {item.works_count}
                </small>
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
