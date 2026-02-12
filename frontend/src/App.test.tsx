import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";

import App from "./App";

vi.mock("./api/client", () => ({
  fetchInstitutions: vi.fn(),
  fetchDiscovery: vi.fn()
}));

import { fetchDiscovery, fetchInstitutions } from "./api/client";

const mockedFetchInstitutions = vi.mocked(fetchInstitutions);
const mockedFetchDiscovery = vi.mocked(fetchDiscovery);

describe("App", () => {
  beforeEach(() => {
    vi.clearAllMocks();
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
      query: "machine learning",
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
          top_venue_works_count: 1,
          top_works: [
            {
              work_id: "https://openalex.org/W1",
              title: "Machine Learning for Healthcare",
              publication_year: 2025,
              venue: "neurips",
              openalex_url: "https://openalex.org/W1"
            }
          ]
        }
      ]
    });

    render(<App />);

    fireEvent.change(screen.getByLabelText("Institution query"), { target: { value: "mit" } });
    fireEvent.click(screen.getByRole("button", { name: "Search" }));

    await waitFor(() => expect(mockedFetchInstitutions).toHaveBeenCalled());

    fireEvent.click(screen.getByRole("button", { name: /MIT/i }));
    fireEvent.change(screen.getByLabelText("Research topic"), { target: { value: "machine learning" } });
    fireEvent.click(screen.getByRole("button", { name: "Discover" }));

    await waitFor(() => expect(mockedFetchDiscovery).toHaveBeenCalled());
    expect(screen.getByText("Alice Zhang")).toBeInTheDocument();
  });
});
