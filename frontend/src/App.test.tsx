import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";

import App from "./App";

vi.mock("./api/client", () => ({
  fetchInstitutions: vi.fn(),
  fetchAreas: vi.fn(),
  fetchDiscovery: vi.fn()
}));

import { fetchAreas, fetchDiscovery, fetchInstitutions } from "./api/client";

const mockedFetchInstitutions = vi.mocked(fetchInstitutions);
const mockedFetchAreas = vi.mocked(fetchAreas);
const mockedFetchDiscovery = vi.mocked(fetchDiscovery);

describe("App", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedFetchAreas.mockResolvedValue({
      areas: [
        { name: "Machine Learning", conferences: ["NeurIPS", "ICML", "ICLR", "COLT"] },
        { name: "Computer Vision", conferences: ["CVPR", "ICCV", "ECCV"] }
      ]
    });
  });

  it("runs institution search and discovery flow", async () => {
    mockedFetchInstitutions.mockResolvedValue({
      query: "mit",
      limit: 10,
      total: 1,
      results: [
        {
          institution_id: "https://openalex.org/I1",
          name: "MIT",
          country_code: "US",
          works_count: 100,
          cited_by_count: 1000
        }
      ]
    });

    mockedFetchDiscovery.mockResolvedValue({
      area: "Machine Learning",
      institution_id: "https://openalex.org/I1",
      offset: 0,
      limit: 5,
      total: 1,
      results: [
        {
          author_id: "https://openalex.org/A1",
          author_name: "Alice Zhang",
          institution_name: "MIT",
          score: 2.1,
          matching_works_count: 2,
          recent_works_count: 2,
          top_venue_works_count: 2,
          top_works: [
            {
              work_id: "https://openalex.org/W1",
              title: "Machine Learning for Healthcare",
              publication_year: 2025,
              venue: "NeurIPS 2025",
              openalex_url: "https://openalex.org/W1"
            }
          ]
        }
      ]
    });

    render(<App />);

    // Areas are fetched on mount
    await waitFor(() => expect(mockedFetchAreas).toHaveBeenCalled());

    fireEvent.change(screen.getByLabelText("Institution query"), { target: { value: "mit" } });
    fireEvent.click(screen.getByRole("button", { name: "Search" }));

    await waitFor(() => expect(mockedFetchInstitutions).toHaveBeenCalled());

    fireEvent.click(screen.getByRole("button", { name: /MIT/i }));
    fireEvent.change(screen.getByLabelText("Research area"), { target: { value: "Machine Learning" } });
    fireEvent.click(screen.getByRole("button", { name: "Discover" }));

    await waitFor(() => expect(mockedFetchDiscovery).toHaveBeenCalled());
    expect(mockedFetchDiscovery).toHaveBeenCalledWith({
      area: "Machine Learning",
      institutionId: "https://openalex.org/I1",
      offset: 0,
      limit: 5
    });
    expect(screen.getByRole("dialog", { name: "Professor results" })).toBeInTheDocument();
    expect(screen.getByText("Alice Zhang")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    await waitFor(() => {
      expect(screen.queryByRole("dialog", { name: "Professor results" })).not.toBeInTheDocument();
    });
  });

  it("opens modal with empty-state message when discovery has no results", async () => {
    mockedFetchInstitutions.mockResolvedValue({
      query: "mit",
      limit: 10,
      total: 1,
      results: [
        {
          institution_id: "https://openalex.org/I1",
          name: "MIT",
          country_code: "US",
          works_count: 100,
          cited_by_count: 1000
        }
      ]
    });

    mockedFetchDiscovery.mockResolvedValue({
      area: "Machine Learning",
      institution_id: "https://openalex.org/I1",
      offset: 0,
      limit: 5,
      total: 0,
      results: []
    });

    render(<App />);

    await waitFor(() => expect(mockedFetchAreas).toHaveBeenCalled());
    fireEvent.change(screen.getByLabelText("Institution query"), { target: { value: "mit" } });
    fireEvent.click(screen.getByRole("button", { name: "Search" }));
    await waitFor(() => expect(mockedFetchInstitutions).toHaveBeenCalled());

    fireEvent.click(screen.getByRole("button", { name: /MIT/i }));
    fireEvent.change(screen.getByLabelText("Research area"), { target: { value: "Machine Learning" } });
    fireEvent.click(screen.getByRole("button", { name: "Discover" }));

    await waitFor(() => expect(mockedFetchDiscovery).toHaveBeenCalled());
    expect(screen.getByRole("dialog", { name: "Professor results" })).toBeInTheDocument();
    expect(screen.getByText("No professors matched this query yet.")).toBeInTheDocument();
  });
});
