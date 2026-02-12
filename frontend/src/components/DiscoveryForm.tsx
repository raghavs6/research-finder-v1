type DiscoveryFormProps = {
  topic: string;
  onTopicChange: (value: string) => void;
  onSearch: () => void;
  isLoading: boolean;
  hasInstitutionSelected: boolean;
};

export function DiscoveryForm({
  topic,
  onTopicChange,
  onSearch,
  isLoading,
  hasInstitutionSelected
}: DiscoveryFormProps) {
  const disabled = isLoading || topic.trim().length < 2 || !hasInstitutionSelected;

  return (
    <section className="panel">
      <h2>2. Find Professors</h2>
      <div className="form-row">
        <input
          value={topic}
          onChange={(event) => onTopicChange(event.target.value)}
          placeholder="Research topic, e.g. machine learning"
          aria-label="Research topic"
        />
        <button type="button" onClick={onSearch} disabled={disabled}>
          {isLoading ? "Loading..." : "Discover"}
        </button>
      </div>
      {!hasInstitutionSelected ? <p className="helper-text">Select an institution first.</p> : null}
    </section>
  );
}
