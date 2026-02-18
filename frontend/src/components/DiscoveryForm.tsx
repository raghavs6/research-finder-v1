import type { AreaItem } from "../types/api";

type DiscoveryFormProps = {
  area: string;
  onAreaChange: (value: string) => void;
  areas: AreaItem[];
  onSearch: () => void;
  isLoading: boolean;
  hasInstitutionSelected: boolean;
};

export function DiscoveryForm({
  area,
  onAreaChange,
  areas,
  onSearch,
  isLoading,
  hasInstitutionSelected
}: DiscoveryFormProps) {
  const disabled = isLoading || area === "" || !hasInstitutionSelected;
  const selectedArea = areas.find((a) => a.name === area);

  return (
    <section className="panel">
      <div className="step-label">
        <span className="step-num">002</span> // AREA
      </div>
      <h2>Find Professors</h2>
      <div className="form-row">
        <select
          value={area}
          onChange={(e) => onAreaChange(e.target.value)}
          disabled={!hasInstitutionSelected}
          aria-label="Research area"
        >
          <option value="">-- select research area --</option>
          {areas.map((a) => (
            <option key={a.name} value={a.name}>{a.name}</option>
          ))}
        </select>
        <button type="button" onClick={onSearch} disabled={disabled}>
          {isLoading ? "Loading..." : "Discover"}
        </button>
      </div>
      {!hasInstitutionSelected ? (
        <p className="helper-text">Select an institution first.</p>
      ) : selectedArea ? (
        <p className="helper-text">covering: {selectedArea.conferences.join(", ")}</p>
      ) : null}
    </section>
  );
}
