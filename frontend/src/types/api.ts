export type InstitutionItem = {
  institution_id: string;
  name: string;
  country_code: string | null;
  works_count: number;
  cited_by_count: number;
};

export type InstitutionSearchResponse = {
  query: string;
  limit: number;
  total: number;
  results: InstitutionItem[];
};

export type WorkItem = {
  work_id: string;
  title: string;
  publication_year: number | null;
  venue: string | null;
  openalex_url: string | null;
};

export type DiscoveryAuthorResult = {
  author_id: string;
  author_name: string;
  institution_name: string | null;
  score: number;
  matching_works_count: number;
  recent_works_count: number;
  top_venue_works_count: number;
  top_works: WorkItem[];
};

export type DiscoveryResponse = {
  query: string;
  institution_id: string;
  offset: number;
  limit: number;
  total: number;
  results: DiscoveryAuthorResult[];
};
