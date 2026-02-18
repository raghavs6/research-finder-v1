from dataclasses import dataclass


AREA_CONFERENCES: dict[str, tuple[str, ...]] = {
    "Machine Learning":            ("NeurIPS", "ICML", "ICLR", "COLT"),
    "Computer Vision":             ("CVPR", "ICCV", "ECCV"),
    "Natural Language Processing": ("ACL", "EMNLP", "NAACL", "COLING"),
    "Data Mining":                 ("KDD", "WSDM", "SIGIR", "WWW"),
    "Databases":                   ("SIGMOD", "VLDB", "ICDE"),
    "Systems":                     ("OSDI", "SOSP", "EuroSys", "USENIX ATC"),
    "Computer Networks":           ("SIGCOMM", "NSDI", "IMC"),
    "Security & Privacy":          ("IEEE S&P", "CCS", "USENIX Security", "NDSS"),
    "Human-Computer Interaction":  ("CHI", "UIST", "CSCW"),
    "Computer Architecture":       ("ISCA", "MICRO", "HPCA", "ASPLOS"),
    "Programming Languages":       ("PLDI", "POPL", "OOPSLA"),
    "Robotics":                    ("ICRA", "IROS", "RSS"),
}

AREA_VENUE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Machine Learning":            ("neurips", "neural information processing", "icml", "international conference on machine learning", "iclr", "learning representations", "colt", "computational learning"),
    "Computer Vision":             ("cvpr", "computer vision and pattern recognition", "iccv", "international conference on computer vision", "eccv", "european conference on computer vision"),
    "Natural Language Processing": ("association for computational linguistics", "empirical methods in natural language", "naacl", "north american chapter", "coling", "computational linguistics"),
    "Data Mining":                 ("knowledge discovery and data mining", "wsdm", "web search and data mining", "information retrieval", "world wide web conference", "thewebconf"),
    "Databases":                   ("sigmod", "management of data", "vldb", "very large data", "icde", "data engineering"),
    "Systems":                     ("osdi", "operating systems design", "sosp", "symposium on operating systems", "eurosys", "usenix annual technical"),
    "Computer Networks":           ("sigcomm", "data communication", "nsdi", "networked systems design", "internet measurement"),
    "Security & Privacy":          ("ieee symposium on security and privacy", "computer and communications security", "usenix security", "network and distributed system security"),
    "Human-Computer Interaction":  ("human factors in computing", "user interface software and technology", "computer-supported cooperative"),
    "Computer Architecture":       ("isca", "computer architecture", "hpca", "high-performance computer architecture", "asplos", "architectural support"),
    "Programming Languages":       ("pldi", "programming language design and implementation", "popl", "principles of programming languages", "oopsla"),
    "Robotics":                    ("icra", "robotics and automation", "iros", "intelligent robots and systems", "robotics: science and systems"),
}


@dataclass(frozen=True)
class Settings:
    api_v1_prefix: str = "/api/v1"
    cors_allowed_origins: tuple[str, ...] = (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    )
    openalex_base_url: str = "https://api.openalex.org"
    openalex_timeout_seconds: float = 5.0
    openalex_max_retries: int = 2
    openalex_retry_backoff_seconds: float = 0.2
    openalex_default_per_page: int = 100
    openalex_max_per_page: int = 200
    max_page_size: int = 25
    top_works_per_author: int = 3
    recency_window_years: int = 5
    area_names: tuple[str, ...] = tuple(AREA_CONFERENCES.keys())


settings = Settings()
