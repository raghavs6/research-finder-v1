import { useEffect, useState } from "react";

import { fetchDiscovery, fetchInstitutions } from "./api/client";
import { DiscoveryForm } from "./components/DiscoveryForm";
import { ErrorBanner } from "./components/ErrorBanner";
import { InstitutionSearch } from "./components/InstitutionSearch";
import { ProfessorResults } from "./components/ProfessorResults";
import type { DiscoveryAuthorResult, InstitutionItem } from "./types/api";

const PAGE_SIZE = 5;

function App() {
  const [institutionQuery, setInstitutionQuery] = useState("");
  const [topic, setTopic] = useState("");
  const [selectedInstitutionId, setSelectedInstitutionId] = useState("");

  const [institutions, setInstitutions] = useState<InstitutionItem[]>([]);
  const [results, setResults] = useState<DiscoveryAuthorResult[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);

  const [isLoadingInstitutions, setIsLoadingInstitutions] = useState(false);
  const [isLoadingDiscovery, setIsLoadingDiscovery] = useState(false);
  const [error, setError] = useState("");
  const [isDarkMode, setIsDarkMode] = useState(true);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", isDarkMode ? "dark" : "light");
  }, [isDarkMode]);

  const runInstitutionSearch = async () => {
    setError("");
    setIsLoadingInstitutions(true);
    try {
      const payload = await fetchInstitutions(institutionQuery.trim(), 10);
      setInstitutions(payload.results);
      if (!payload.results.some((item) => item.institution_id === selectedInstitutionId)) {
        setSelectedInstitutionId("");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Institution lookup failed");
    } finally {
      setIsLoadingInstitutions(false);
    }
  };

  const runDiscoverySearch = async (nextOffset = 0) => {
    if (!selectedInstitutionId || topic.trim().length < 2) {
      return;
    }

    setError("");
    setIsLoadingDiscovery(true);
    try {
      const payload = await fetchDiscovery({
        topic: topic.trim(),
        institutionId: selectedInstitutionId,
        offset: nextOffset,
        limit: PAGE_SIZE
      });
      setResults(payload.results);
      setTotal(payload.total);
      setOffset(payload.offset);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Discovery request failed");
    } finally {
      setIsLoadingDiscovery(false);
    }
  };

  const onNext = () => {
    const nextOffset = offset + PAGE_SIZE;
    if (nextOffset >= total) return;
    void runDiscoverySearch(nextOffset);
  };

  const onPrev = () => {
    const nextOffset = Math.max(0, offset - PAGE_SIZE);
    if (nextOffset === offset) return;
    void runDiscoverySearch(nextOffset);
  };

  return (
    <main className="app-shell">
      <header className="hero">
        <div className="hero-top">
          <p className="eyebrow">// research discovery tool</p>
          <button
            type="button"
            className="theme-toggle"
            onClick={() => setIsDarkMode((prev) => !prev)}
          >
            {isDarkMode ? "// light" : "// dark"}
          </button>
        </div>
        <h1>RESEARCH.FIND</h1>
        <p className="subtitle">pick a university. search your field. review ranked researchers.</p>
      </header>

      {error ? <ErrorBanner message={error} /> : null}

      <InstitutionSearch
        query={institutionQuery}
        onQueryChange={setInstitutionQuery}
        onSearch={() => void runInstitutionSearch()}
        institutions={institutions}
        selectedInstitutionId={selectedInstitutionId}
        onSelectInstitution={setSelectedInstitutionId}
        isLoading={isLoadingInstitutions}
      />

      <DiscoveryForm
        topic={topic}
        onTopicChange={setTopic}
        onSearch={() => void runDiscoverySearch(0)}
        isLoading={isLoadingDiscovery}
        hasInstitutionSelected={Boolean(selectedInstitutionId)}
      />

      <ProfessorResults
        results={results}
        total={total}
        offset={offset}
        limit={PAGE_SIZE}
        onPrev={onPrev}
        onNext={onNext}
      />
    </main>
  );
}

export default App;
