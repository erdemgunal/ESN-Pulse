# ESN PULSE - High-Level Design (HLD)

**Versiyon:** v1.0  
**Tarih:** 01.08.2025  
**Proje:** ESN PULSE - ESN Network Data Scraper & Analytics Platform

---

## 1. Sistem Genel Bakış

ESN PULSE, 46 ülke ve 517 ESN şubesinin verilerini otomatik olarak toplayan, işleyen ve analiz için hazır hale getiren bir veri scraping ve analitik platformudur. Sistem, asenkron veri toplama, güvenilir görev kuyruğu yönetimi ve ölçeklenebilir veri depolama prensipleri üzerine kurulmuştur.

### 1.1. Temel Hedefler
- **Otomasyon:** 517 şubeden haftalık otomatik veri toplama
- **Ölçeklenebilirlik:** Asenkron işleme ile yüksek performans
- **Güvenilirlik:** Hata yönetimi ve kurtarma mekanizmaları
- **Analitik Destek:** BI araçları için optimize edilmiş veri yapısı

---

## 2. Sistem Mimarisi

### 2.1. Genel Mimari Diyagramı

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ESN PULSE SYSTEM ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────┐  │
│  │   DATA SOURCES  │    │  ORCHESTRATION  │    │     DATA PROCESSING     │  │
│  │                 │    │                 │    │                         │  │
│  │ accounts.esn.org│───▶│  run_scraper.py │───▶│   AccountsScraper       │  │
│  │activities.esn.org│   │                 │    │ ActivitiesStatsScaper   │  │
│  │                 │    │   - CLI args    │    │                         │  │
│  │  46 Countries   │    │   - Scheduling  │    │  ┌─────────────────────┐ │  │
│  │  517 Sections   │    │   - Dependencies│    │  │    Async HTTP       │ │  │
│  └─────────────────┘    └─────────────────┘    │  │   (aiohttp)         │ │  │
│                                                │  │                     │ │  │
│                                                │  │  ┌─────────────────┐│ │  │
│                                                │  │  │ HTML Parser     ││ │  │
│                                                │  │  │(BeautifulSoup4) ││ │  │
│                                                │  │  └─────────────────┘│ │  │
│                                                │  │                     │ │  │
│                                                │  │  ┌─────────────────┐│ │  │
│                                                │  │  │Data Validation  ││ │  │
│                                                │  │  │  (Pydantic)     ││ │  │
│                                                │  │  └─────────────────┘│ │  │
│                                                │  └─────────────────────┘ │  │
│                                                └─────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                        TASK QUEUE & PROCESSING                         │  │
│  │                                                                         │  │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐ │  │
│  │  │   CELERY BEAT   │    │  CELERY WORKERS │    │    REDIS BROKER     │ │  │
│  │  │                 │    │                 │    │                     │ │  │
│  │  │ - Weekly Tasks  │───▶│ Country Tasks   │◄──▶│  - Task Queue       │ │  │
│  │  │ - Monthly Tasks │    │ Section Tasks   │    │  - Result Backend   │ │  │
│  │  │ - Manual Trigger│    │ Activity Tasks  │    │  - Task Locks       │ │  │
│  │  │                 │    │ Statistics Tasks│    │                     │ │  │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────────┘ │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                         DATA LAYER                                     │  │
│  │                                                                         │  │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────┐ │  │
│  │  │   POSTGRESQL    │    │   MONITORING    │    │    BI INTEGRATION   │ │  │
│  │  │                 │    │                 │    │                     │ │  │
│  │  │ Core Tables:    │    │ scraper_status  │    │ - Power BI          │ │  │
│  │  │ - countries     │    │ validation_errors│   │ - Tableau           │ │  │
│  │  │ - sections      │    │ failed_scrapes  │    │ - Custom SQL        │ │  │
│  │  │ - activities    │    │                 │    │                     │ │  │
│  │  │                 │    │ Logs:           │    │ Analytics Tables:   │ │  │
│  │  │ Relationship:   │    │ - Success rates │    │ - Statistics        │ │  │
│  │  │ - Many-to-Many  │    │ - Error tracking│    │ - Aggregations      │ │  │
│  │  │ - Foreign Keys  │    │ - Performance   │    │                     │ │  │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────────┘ │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2. Bileşen Düzeyinde Mimari

```
DETAILED SCRAPER ARCHITECTURE
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                      SCRAPER MODULES                                │ │
│  │                                                                     │ │
│  │  ┌─────────────────┐              ┌────────────────────────────────┐ │ │
│  │  │ AccountsScraper │              │ ActivitiesAndStatisticsScraper │ │ │
│  │  │                 │              │                                │ │ │
│  │  │ Data Sources:   │              │ Data Sources:                  │ │ │
│  │  │ accounts.esn.org│              │ activities.esn.org             │ │ │
│  │  │                 │              │                                │ │ │
│  │  │ Endpoints:      │              │ Endpoints:                     │ │ │
│  │  │ • /             │              │ • /organisation/<slug>/        │ │ │
│  │  │ • /country/     │              │   activities                   │ │ │
│  │  │   <country_code>│              │ • /activity/<event_slug>       │ │ │
│  │  │ • /section/     │              │ • /organisation/<slug>/        │ │ │
│  │  │   <accounts_    │              │   statistics                   │ │ │
│  │  │   platform_slug>│              │                                │ │ │
│  │  │ Extraction:     │              │                                │ │ │
│  │  │ • Country list  │              │ Extraction:                    │ │ │
│  │  │ • Section list  │              │ • Activity details             │ │ │
│  │  │ • Basic info    │              │ • Event metadata               │ │ │
│  │  │ • Slug          │              │ • Statistical data             │ │ │
│  │  │   validation    │              │ • Relationships                │ │ │
│  │  │                 │              │                                │ │ │
│  │  │ Schedule:       │              │ Schedule:                      │ │ │
│  │  │ Monthly/Manual  │              │ Weekly                         │ │ │
│  │  └─────────────────┘              └────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                    SHARED INFRASTRUCTURE                            │ │
│  │                                                                     │ │
│  │  ┌─────────────────┐   ┌─────────────────┐   ┌────────────────────┐ │ │
│  │  │  HTTP Client    │   │  HTML Parser    │   │  Data Validation   │ │ │
│  │  │                 │   │                 │   │                    │ │ │
│  │  │ • aiohttp       │   │ • BeautifulSoup4│   │ • Pydantic Models  │ │ │
│  │  │ • Async/await   │   │ • CSS Selectors │   │ • Type checking    │ │ │
│  │  │ • Rate limiting │   │ • JSON parsing  │   │ • Field validation │ │ │
│  │  │ • User-Agent    │   │ • Error handling│   │ • Data cleaning    │ │ │
│  │  │   rotation      │   │                 │   │                    │ │ │
│  │  │ • Retry logic   │   │                 │   │                    │ │ │
│  │  └─────────────────┘   └─────────────────┘   └────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                      DATA PROCESSING                                │ │
│  │                                                                     │ │
│  │  Raw HTML/JSON → BeautifulSoup Parsing → Pydantic Validation       │ │
│  │               → Database Operations → Error Handling               │ │
│  │                                                                     │ │
│  │  Key Processing Steps:                                              │ │
│  │  1. HTTP Request with error handling                                │ │
│  │  2. Content parsing (HTML/JSON)                                     │ │
│  │  3. Data extraction using CSS selectors                             │ │
│  │  4. Pydantic model validation                                       │ │
│  │  5. Database UPSERT operations                                      │ │
│  │  6. Relationship management (Many-to-Many)                          │ │
│  │  7. Error logging and recovery                                      │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
```

**AccountsScraper Module Specifications:**

```python
# Core Data Models
class CountryModel(BaseModel):
    country_code: str = Field(max_length=10, pattern=r'^[A-Z]{2}$')
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=100)
    url: HttpUrl
    section_count: int = Field(ge=0)

class SectionModel(BaseModel):
    country_code: str = Field(max_length=10)
    name: str = Field(min_length=1, max_length=255)
    accounts_platform_slug: str = Field(min_length=1, max_length=255)
    activities_platform_slug: Optional[str] = Field(max_length=255)
    city: Optional[str] = Field(max_length=100)
    email: Optional[EmailStr]
    website: Optional[HttpUrl]
    university_name: Optional[str] = Field(max_length=255)
    longitude: Optional[condecimal(max_digits=9, decimal_places=6)]
    latitude: Optional[condecimal(max_digits=9, decimal_places=6)]
    social_media: Optional[Dict[str, str]]
    logo_url: Optional[str]
    can_scrape_activities: Optional[bool] = None

# Key Processing Functions
async def extract_countries() -> List[CountryModel]:
    """Extract all countries from accounts.esn.org"""
    pass

async def extract_sections_for_country(country_code: str) -> List[SectionModel]:
    """Extract sections from /countries/<country_code> page"""
    pass

async def validate_activities_slug(slug: str) -> bool:
    """Validate slug with HEAD request to activities platform"""
    url = f"https://activities.esn.org/organisation/{slug}/activities"
    # HTTP HEAD request, return True if 200 OK
    pass
```

**ActivitiesAndStatisticsScraper Module Specifications:**

```python
# Core Data Models
class ActivityModel(BaseModel):
    event_slug: str = Field(min_length=1, max_length=255)
    url: HttpUrl
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    start_date: date
    end_date: Optional[date] = None
    city: Optional[str] = Field(max_length=100)
    country_code: Optional[str] = Field(max_length=10)
    participants: int = Field(ge=0)
    activity_type: Optional[str] = Field(max_length=100)
    is_future_event: bool
    organisers: List[str] = []
    causes: List[str] = []
    sdgs: List[str] = []
    objectives: List[str] = []
    is_valid: bool = True

class SectionStatisticsModel(BaseModel):
    section_id: int
    physical_activities: int = Field(ge=0)
    online_activities: int = Field(ge=0)
    total_local_students: int = Field(ge=0)
    total_international_students: int = Field(ge=0)
    total_coordinators: int = Field(ge=0)
    cause_statistics: Dict[str, Dict[str, int]] = {}
    type_statistics: Dict[str, Dict[str, int]] = {}
    participant_statistics: Dict[str, Dict[str, int]] = {}

# CSS Selectors for Data Extraction
ACTIVITY_SELECTORS = {
    'container': 'article.node.ct-physical-activity.ct-physical-activity--full',
    'title': '.field__item h1, .activity-label',
    'event_slug': '.url',  # Extract from href attribute
    'description': '.ct-physical-activity__field-ct-act-description .field__item',
    'dates': '.highlight-dates-single span',
    'location': '.highlight-data-text span',
    'organisers': '.pseudo__organisers .pseudo__organiser a',
    'participants': '.highlight-data-number .highlight-data-text-big',
    'sdgs': '.field-sdgs-wrapper img',  # alt attribute
    'objectives': '.activity__objectives .field__item span',
    'causes': '.activity-causes .activity-label a',
    'activity_type': '.activity-types .activity-type a'
}

# Key Processing Functions
async def get_pagination_info(section_slug: str) -> int:
    """Get total page count from 'Last' link in navigation"""
    pass

async def process_activity_pages_chunk(section_slug: str, page_range: List[int]) -> List[ActivityModel]:
    """Process a chunk of activity pages (5 pages per chunk)"""
    pass

async def extract_activity_details(activity_html: str) -> ActivityModel:
    """Extract activity details using CSS selectors"""
    pass

async def get_section_statistics(section_slug: str) -> SectionStatisticsModel:
    """Get statistics JSON from /organisation/<slug>/statistics"""
    pass
```

**Shared Infrastructure Components:**

```python
# HTTP Client Configuration
class ESNHTTPClient:
    def __init__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=10)
        )
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
    async def get_with_retry(self, url: str, max_retries: int = 3) -> str:
        """HTTP GET with exponential backoff retry"""
        for attempt in range(max_retries):
            try:
                headers = {'User-Agent': random.choice(self.user_agents)}
                await asyncio.sleep(0.5)  # Rate limiting
                async with self.session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status in [403, 404, 500]:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status
                        )
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

# Error Handling
class ScrapingError(Exception):
    def __init__(self, url: str, status_code: int, message: str):
        self.url = url
        self.status_code = status_code
        self.message = message
        super().__init__(f"Failed to scrape {url}: {status_code} - {message}")

class ValidationError(Exception):
    def __init__(self, field: str, value: Any, message: str):
        self.field = field
        self.value = value
        self.message = message
        super().__init__(f"Validation failed for {field}: {message}")
```

---

## 3. Teknoloji Yığını (Technology Stack)

### 3.1. Core Technologies

| Katman | Teknoloji | Versiyon | Kullanım Amacı |
|--------|-----------|----------|----------------|
| **Language** | Python | 3.11+ | Ana development language |
| **Database** | PostgreSQL | 15+ | Structured data storage |
| **Task Queue** | Celery | 5.3+ | Distributed task processing |
| **Message Broker** | Redis | 7.0+ | Celery broker & caching |
| **HTTP Client** | aiohttp | 3.8+ | Async HTTP requests |
| **HTML Parser** | BeautifulSoup4 | 4.12+ | HTML content extraction |
| **Data Validation** | Pydantic | 2.0+ | Data modeling & validation |
| **DB Driver** | asyncpg | 0.28+ | Async PostgreSQL connector |

### 3.2. Development & Operations

| Kategori | Teknoloji | Kullanım |
|----------|-----------|----------|
| **Containerization** | Docker, Docker Compose | Local development |
| **Process Management** | systemd (production) | Service management |
| **Logging** | Python logging | Application logs |
| **Testing** | pytest, pytest-asyncio | Unit & integration tests |
| **Code Quality** | black, isort, flake8 | Code formatting & linting |

---

## 4. Veri Modeli ve İlişkiler

### 4.1. Veri Katmanı Mimarisi

```
DATABASE ARCHITECTURE
┌────────────────────────────────────────────────────────────────────────────┐
│                           CORE DATA ENTITIES                               │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌─────────────────┐    ┌──────────────────────────────────────────────┐  │
│  │   COUNTRIES     │    │                SECTIONS                      │  │
│  │                 │    │                                              │  │
│  │ country_code PK │───▶│ id PK                                        │  │
│  │ name            │    │ country_code FK                              │  │
│  │ slug            │    │ accounts_platform_slug                       │  │
│  │ url             │    │ activities_platform_slug                     │  │
│  │ section_count   │    │ name, city, coordinates                      │  │
│  └─────────────────┘    │ can_scrape_activities BOOLEAN                │  │
│                         │ last_scraped TIMESTAMP                       │  │
│                         └──────────────────────────────────────────────┘  │
│                                              │                            │
│                                              ▼                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        ACTIVITIES ECOSYSTEM                          │  │
│  │                                                                      │  │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │  │
│  │  │   ACTIVITIES    │    │ LOOKUP TABLES   │    │ RELATIONSHIP    │   │  │
│  │  │                 │    │                 │    │    TABLES       │   │  │
│  │  │ id PK           │    │ activity_causes │    │                 │   │  │
│  │  │ event_slug      │◄──▶│ sdgs            │◄──▶│ activity_to_*   │   │  │
│  │  │ title           │    │ objectives      │    │                 │   │  │
│  │  │ start_date      │    │                 │    │ Many-to-Many    │   │  │
│  │  │ participants    │    │                 │    │ Relationships   │   │  │
│  │  │ activity_type   │    │                 │    │                 │   │  │
│  │  │ is_valid        │    │                 │    │                 │   │  │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      STATISTICS & ANALYTICS                          │  │
│  │                                                                      │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │  │
│  │  │                SECTION STATISTICS TABLES                        │ │  │
│  │  │                                                                 │ │  │
│  │  │ section_overall_statistics     - General activity counts        │ │  │
│  │  │ section_cause_statistics       - By cause breakdown             │ │  │
│  │  │ section_type_statistics        - By activity type               │ │  │
│  │  │ section_participant_statistics - By participant type            │ │  │
│  │  └─────────────────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    OPERATIONAL MONITORING                            │  │
│  │                                                                      │  │
│  │  scraper_status        - Scraper run history & status                │  │
│  │  validation_errors     - Data validation failures                    │  │
│  │  failed_scrapes        - HTTP request failures                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
```

### 4.2. Veri İlişkileri ve Detaylı Şema

**Core Entity Specifications:**

```sql
-- COUNTRIES TABLE
CREATE TABLE countries (
    country_code VARCHAR(10) PRIMARY KEY,  -- "TR", "DE", "FR"
    name VARCHAR(100) NOT NULL,            -- "Turkey", "Germany"
    slug VARCHAR(100) NOT NULL,            -- "turkey", "germany"
    url VARCHAR(255) NOT NULL,             -- "https://accounts.esn.org/countries/tr"
    section_count INTEGER DEFAULT 0        -- Total sections in country
);

-- SECTIONS TABLE (517 ESN sections worldwide)
CREATE TABLE sections (
    id SERIAL PRIMARY KEY,                                 -- Auto-increment ID
    country_code VARCHAR(10) REFERENCES countries(country_code),
    name VARCHAR(255) NOT NULL,                           -- "ESN METU", "ESN Yıldız"
    
    -- Platform-specific slugs
    accounts_platform_slug VARCHAR(255) UNIQUE NOT NULL,  -- "tr-anka-met"
    activities_platform_slug VARCHAR(255),                -- "esn-metu"
    
    -- URLs
    accounts_url VARCHAR(255),                            -- Full accounts URL
    activities_url VARCHAR(255),                          -- Full activities URL
    
    -- Contact & Location Info
    city VARCHAR(100),                                    -- "Ankara", "Istanbul"
    address TEXT,                                         -- Full address
    email VARCHAR(255),                                   -- "esnmetu@metu.edu.tr"
    website VARCHAR(255),                                 -- "https://metu.esnturkey.org"
    university_name VARCHAR(255),                         -- "Middle East Technical University"
    
    -- Geographic Coordinates
    longitude DECIMAL(9,6),                               -- GPS longitude
    latitude DECIMAL(9,6),                                -- GPS latitude
    
    -- Social Media (JSONB for flexible structure)
    social_media JSONB,                                   -- {"facebook": "...", "instagram": "..."}
    
    -- Logo
    logo_url VARCHAR(255),                                -- Logo image path
    
    -- Scraping Control Flags
    can_scrape_activities BOOLEAN DEFAULT NULL,           -- Validation flag
    last_validated_activities_slug TIMESTAMP,             -- Last slug validation
    last_scraped TIMESTAMP,                               -- Last successful scrape
    
    UNIQUE(accounts_platform_slug)
);

-- ACTIVITIES TABLE (Core event data)
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    event_slug VARCHAR(255) UNIQUE NOT NULL,              -- "boat-party-20885"
    url VARCHAR(255) NOT NULL,                            -- Full event URL
    title VARCHAR(255) NOT NULL,                          -- "Boat Party"
    description TEXT NOT NULL,                            -- Event description
    
    -- Temporal Data
    start_date DATE NOT NULL,                             -- ISO format: YYYY-MM-DD
    end_date DATE,                                        -- Can be same as start_date
    is_future_event BOOLEAN NOT NULL,                     -- Computed from dates
    
    -- Location
    city VARCHAR(100),                                    -- "Istanbul"
    country_code VARCHAR(10),                             -- "TR"
    
    -- Participation Data
    participants INTEGER CHECK (participants >= 0),       -- Non-negative
    activity_type VARCHAR(100),                           -- "Game or Social Activity"
    
    -- Data Quality Control
    is_valid BOOLEAN DEFAULT TRUE,                        -- Validation flag
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Foreign Key Constraints
    CONSTRAINT fk_activities_country 
        FOREIGN KEY (country_code) REFERENCES countries(country_code)
        ON UPDATE CASCADE ON DELETE SET NULL
);

-- LOOKUP TABLES for Many-to-Many Relationships
CREATE TABLE activity_causes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL                     -- "Culture", "Education & Youth"
);

CREATE TABLE sdgs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,                    -- "SDG 3", "SDG 4"
    description TEXT                                      -- Full SDG description
);

CREATE TABLE objectives (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL                     -- "Mental Health & Well-Being"
);

-- JUNCTION TABLES (Many-to-Many Relationships)
CREATE TABLE activity_section_organisers (
    activity_id INTEGER REFERENCES activities(id) ON DELETE CASCADE,
    section_id INTEGER REFERENCES sections(id) ON DELETE CASCADE,
    PRIMARY KEY (activity_id, section_id)
);

CREATE TABLE activity_to_cause (
    activity_id INTEGER REFERENCES activities(id) ON DELETE CASCADE,
    cause_id INTEGER REFERENCES activity_causes(id) ON DELETE CASCADE,
    PRIMARY KEY (activity_id, cause_id)
);

CREATE TABLE activity_to_sdg (
    activity_id INTEGER REFERENCES activities(id) ON DELETE CASCADE,
    sdg_id INTEGER REFERENCES sdgs(id) ON DELETE CASCADE,
    PRIMARY KEY (activity_id, sdg_id)
);

CREATE TABLE activity_to_objective (
    activity_id INTEGER REFERENCES activities(id) ON DELETE CASCADE,
    objective_id INTEGER REFERENCES objectives(id) ON DELETE CASCADE,
    PRIMARY KEY (activity_id, objective_id)
);

-- STATISTICS TABLES (From activities.esn.org JSON API)
CREATE TABLE section_overall_statistics (
    id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES sections(id) ON DELETE CASCADE,
    
    -- Activity Counts by Type
    physical_activities INTEGER DEFAULT 0,               -- activities_statistics.total_activities.values[0][1]
    online_activities INTEGER DEFAULT 0,                 -- activities_statistics.total_activities.values[1][1]
    
    -- Participant Counts by Type  
    total_local_students INTEGER DEFAULT 0,              -- activities_statistics.total_participants.values[0][1]
    total_international_students INTEGER DEFAULT 0,      -- activities_statistics.total_participants.values[1][1]
    total_coordinators INTEGER DEFAULT 0,                -- activities_statistics.total_participants.values[2][1]
    
    scraped_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(section_id)                                   -- One record per section
);

CREATE TABLE section_cause_statistics (
    id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES sections(id) ON DELETE CASCADE,
    cause_name VARCHAR(100) NOT NULL,                   -- From JSON: causes names
    
    total_count INTEGER DEFAULT 0,                      -- activities_statistics.total_causes.values
    physical_count INTEGER DEFAULT 0,                   -- activities_statistics.physical_causes.values  
    online_count INTEGER DEFAULT 0,                     -- activities_statistics.online_causes.values
    
    scraped_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(section_id, cause_name)
);

CREATE TABLE section_type_statistics (
    id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES sections(id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL,                -- Activity type name
    
    physical_count INTEGER DEFAULT 0,                   -- activities_statistics.physical_types.values
    online_count INTEGER DEFAULT 0,                     -- activities_statistics.online_types.values
    
    scraped_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(section_id, activity_type)
);

CREATE TABLE section_participant_statistics (
    id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES sections(id) ON DELETE CASCADE,
    participant_type VARCHAR(100) NOT NULL,             -- "Local Students", "International", etc.
    
    physical_count INTEGER DEFAULT 0,                   -- activities_statistics.physical_participants.values
    online_count INTEGER DEFAULT 0,                     -- activities_statistics.online_participants.values
    
    scraped_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(section_id, participant_type)
);
```

**Monitoring & Error Management Tables:**

```sql
-- OPERATIONAL MONITORING
CREATE TABLE scraper_status (
    id SERIAL PRIMARY KEY,
    scraper_module VARCHAR(50) NOT NULL,                -- "AccountsScraper", "ActivitiesAndStatisticsScraper"
    status VARCHAR(20) NOT NULL,                         -- "running", "completed", "failed"
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    sections_processed INTEGER DEFAULT 0,
    sections_failed INTEGER DEFAULT 0,
    error_message TEXT
);

CREATE TABLE validation_errors (
    id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES sections(id),
    activity_event_slug VARCHAR(255),                   -- Reference to failed activity
    field_name VARCHAR(100),                            -- Which field failed validation
    error_message TEXT NOT NULL,
    raw_data JSONB,                                     -- Original scraped data
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE failed_scrapes (
    id SERIAL PRIMARY KEY,
    url VARCHAR(500) NOT NULL,                          -- Failed URL
    section_id INTEGER REFERENCES sections(id),
    scraper_module VARCHAR(50),                         -- Which scraper failed
    http_status_code INTEGER,                           -- 404, 500, etc.
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    last_attempt TIMESTAMP DEFAULT NOW(),
    will_retry BOOLEAN DEFAULT TRUE
);
```

**Performance Indexes:**

```sql
-- Strategic Indexes for Query Performance
CREATE INDEX idx_sections_can_scrape ON sections(can_scrape_activities) WHERE can_scrape_activities = TRUE;
CREATE INDEX idx_sections_last_scraped ON sections(last_scraped ASC NULLS FIRST);
CREATE INDEX idx_activities_start_date ON activities(start_date);
CREATE INDEX idx_activities_country ON activities(country_code);
CREATE INDEX idx_activities_valid ON activities(is_valid) WHERE is_valid = TRUE;
CREATE INDEX idx_failed_scrapes_retry ON failed_scrapes(will_retry) WHERE will_retry = TRUE;

-- Statistics Tables Performance Indexes
CREATE INDEX idx_section_overall_stats_section_id ON section_overall_statistics(section_id);
CREATE INDEX idx_section_cause_stats_section_id ON section_cause_statistics(section_id);
CREATE INDEX idx_section_type_stats_section_id ON section_type_statistics(section_id);
CREATE INDEX idx_section_participant_stats_section_id ON section_participant_statistics(section_id);

-- Additional composite indexes for common query patterns
CREATE INDEX idx_section_cause_stats_lookup ON section_cause_statistics(section_id, cause_name);
CREATE INDEX idx_section_type_stats_lookup ON section_type_statistics(section_id, activity_type);
CREATE INDEX idx_section_participant_stats_lookup ON section_participant_statistics(section_id, participant_type);
```

**Data Integrity and Performance Optimizations:**

- **Foreign Key Constraints:** `activities.country_code` → `countries.country_code` ilişkisi veri tutarlılığını garanti eder
- **Cascade Options:** `ON UPDATE CASCADE` country_code güncellemelerini otomatik yayar, `ON DELETE SET NULL` country silindiğinde activities kaydı korunur
- **Statistics Table Indexes:** `section_id` üzerindeki indexler istatistik sorgularının performansını %300-500 artırır
- **Composite Indexes:** `(section_id, category_name)` kombinasyonları analitik raporlama için optimize edilmiştir
- **Partial Indexes:** `WHERE` clause'lu indexler sadece aktif kayıtları indexleyerek disk kullanımını optimize eder

---

## 5. İşlem Akışları (Process Flows)

### 5.1. Ana Orkestrasyon Akışı

```
ORCHESTRATION FLOW
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌─────────────────┐                                                        │
│  │ run_scraper.py  │                                                        │
│  │     START       │                                                        │
│  └─────────┬───────┘                                                        │
│            │                                                                │
│            ▼                                                                │
│  ┌─────────────────┐    NO    ┌──────────────────┐                          │
│  │Check sections   │─────────▶│  Trigger         │                          │
│  │table populated? │          │  AccountsScraper │                          │
│  └─────────┬───────┘          └──────┬───────────┘                          │
│            │ YES                     │                                      │
│            ▼                         ▼                                      │
│  ┌─────────────────┐          ┌──────────────────┐                          │
│  │Check last       │          │  Wait for        │                          │
│  │AccountsScraper  │          │  completion      │                          │
│  │run < 30 days?   │          └──────┬───────────┘                          │
│  └─────────┬───────┘                 │                                      │
│            │ NO                      │                                      │
│            ▼                         ▼                                      │
│  ┌─────────────────┐          ┌──────────────────┐                          │
│  │  Trigger        │◄─────────│   SUCCESS?       │                          │
│  │ Activities &    │          └──────┬───────────┘                          │
│  │ Statistics      │                 │ FAIL                                 │
│  │   Scraper       │                 ▼                                      │
│  └─────────────────┘          ┌──────────────────┐                          │
│                               │   Log Error &    │                          │
│                               │   Exit           │                          │
│                               └──────────────────┘                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Celery Chain Dependencies:**
```python
# Bağımlılık yönetimi Celery chain ile
accounts_scraper_task.s() | activities_scraper_task.s()
```

### 5.2. AccountsScraper İş Akışı (Detaylı)

```
ACCOUNTS SCRAPER DETAILED WORKFLOW
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  PHASE 1: COUNTRY DISCOVERY                                                 │
│  ┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐        │
│  │GET accounts     │───▶│ Parse Country    │───▶│ UPSERT countries │        │
│  │.esn.org/        │    │ List & URLs      │    │     table        │        │
│  │countries        │    │                  │    │ - country_code   │        │
│  └─────────────────┘    │ Extract:         │    │ - name           │        │
│                         │ - country_code   │    │ - slug           │        │
│                         │ - name           │    │ - url            │        │
│                         │ - country URLs   │    │ - section_count  │        │
│                         └──────────────────┘    └──────────────────┘        │
│                                                                             │
│  PHASE 2: SECTION EXTRACTION PER COUNTRY                                   │
│  ┌─────────────────┐                                                        │
│  │  For Each       │                                                        │
│  │   Country       │                                                        │
│  └─────────┬───────┘                                                        │
│            │                                                                │
│            ▼                                                                │
│  ┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐        │
│  │GET /country/    │───▶│ Parse Section    │───▶│ Generate Activity│        │
│  │<country_code>   │    │ List from HTML   │    │ Platform Slug    │        │
│  │                 │    │                  │    │                  │        │
│  │CSS Selector:    │    │CSS Selector:     │    │ Slug Generation: │        │
│  │- Country page   │    │<span class=      │    │ "ESN METU" →     │        │
│  │- Section links  │    │"field-content">  │    │ "esn-metu"       │        │
│  └─────────────────┘    └──────────────────┘    └─────────┬────────┘        │
│                                                           │                 │
│                                                           ▼                 │
│  PHASE 3: SLUG VALIDATION                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                      SLUG VALIDATION PROCESS                            │ │
│  │                                                                         │ │
│  │  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐ │ │
│  │  │ Generate Slug   │───▶│  HTTP HEAD       │───▶│ Update Database     │ │ │
│  │  │ from Section    │    │  Request to:     │    │                     │ │ │
│  │  │ Name            │    │                  │    │ can_scrape_         │ │ │
│  │  │                 │    │ activities.esn   │    │ activities = TRUE   │ │ │
│  │  │ "ESN Yıldız" →  │    │ .org/organisa    │    │ (if 200 OK)         │ │ │
│  │  │ "esn-yildiz"    │    │ tion/<slug>/     │    │                     │ │ │
│  │  │                 │    │ activities       │    │ can_scrape_         │ │ │
│  │  │ python-slugify  │    │                  │    │ activities = FALSE  │ │ │
│  │  │ library         │    │ Response: 200 OK │    │ (if 404/error)      │ │ │
│  │  └─────────────────┘    │ or 404 Not Found │    └─────────────────────┘ │ │
│  │                         └──────────────────┘                            │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  PHASE 4: DATABASE OPERATIONS                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                        UPSERT STRATEGY                                  │ │
│  │                                                                         │ │
│  │  INSERT INTO sections (                                                 │ │
│  │    country_code, name, accounts_platform_slug,                          │ │
│  │    activities_platform_slug, city, coordinates,                         │ │
│  │    can_scrape_activities, last_validated_activities_slug                │ │
│  │  ) VALUES (...) ON CONFLICT (accounts_platform_slug)                    │ │
│  │  DO UPDATE SET                                                          │ │
│  │    name = EXCLUDED.name,                                                │ │
│  │    activities_platform_slug = EXCLUDED.activities_platform_slug,        │ │
│  │    can_scrape_activities = EXCLUDED.can_scrape_activities,              │ │
│  │    last_validated_activities_slug = NOW()                               │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3. ActivitiesAndStatisticsScraper İş Akışı (Detaylı)

```
ACTIVITIES & STATISTICS SCRAPER DETAILED WORKFLOW
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  PHASE 1: SECTION PRIORITIZATION                                           │
│  ┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐        │
│  │SELECT sections  │───▶│ Prioritize by    │───▶│ Create Celery    │        │
│  │WHERE can_scrape_│    │ last_scraped:    │    │ Tasks (2 per     │        │
│  │activities=TRUE  │    │                  │    │ section)         │        │
│  │                 │    │ ORDER BY         │    │                  │        │
│  │Query Result:    │    │ last_scraped ASC │    │ 1. Activities    │        │
│  │- section_id     │    │ NULLS FIRST      │    │ 2. Statistics    │        │
│  │- activities_    │    │                  │    │                  │        │
│  │  platform_slug  │    │ (Never scraped   │    │                  │        │
│  │- last_scraped   │    │  sections first) │    │                  │        │
│  └─────────────────┘    └──────────────────┘    └──────────────────┘        │
│                                                                             │
│  PHASE 2A: ACTIVITIES EXTRACTION                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                        ACTIVITIES WORKFLOW                              │ │
│  │                                                                         │ │
│  │  STEP 1: PAGINATION DISCOVERY                                           │ │
│  │  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐ │ │
│  │  │GET activities   │───▶│ Parse "Last"     │───▶│ Calculate Total     │ │ │
│  │  │.esn.org/organ   │    │ Link from <nav>  │    │ Pages Count         │ │ │
│  │  │isation/<slug>/  │    │                  │    │                     │ │ │
│  │  │activities?page=0│    │ <a href="?page=  │    │ Example: "?page=27" │ │ │
│  │  │                 │    │ 27">Last</a>     │    │ → 28 total pages    │ │ │
│  │  └─────────────────┘    │                  │    │ (0-27)              │ │ │
│  │                         │ BeautifulSoup:   │    └─────────────────────┘ │ │
│  │                         │ soup.find('nav') │                            │ │
│  │                         │ .find_all('a')   │                            │ │
│  │                         └──────────────────┘                            │ │
│  │                                                                         │ │
│  │  STEP 2: CHUNKED PARALLEL PROCESSING                                    │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                    PAGINATION STRATEGY                              │ │ │
│  │  │                                                                     │ │ │
│  │  │  Total Pages: 28 (0-27)                                             │ │ │
│  │  │  Chunk Size: 5 pages per Celery task                               │ │ │
│  │  │                                                                     │ │ │
│  │  │  Chunk 1: [0,1,2,3,4]    → CeleryTask_1                            │ │ │
│  │  │  Chunk 2: [5,6,7,8,9]    → CeleryTask_2                            │ │ │
│  │  │  Chunk 3: [10,11,12,13,14] → CeleryTask_3                          │ │ │
│  │  │  Chunk 4: [15,16,17,18,19] → CeleryTask_4                          │ │ │
│  │  │  Chunk 5: [20,21,22,23,24] → CeleryTask_5                          │ │ │
│  │  │  Chunk 6: [25,26,27]       → CeleryTask_6                          │ │ │
│  │  │                                                                     │ │ │
│  │  │  Async Processing: aiohttp with 0.5s delay between requests         │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                         │ │
│  │  STEP 3: HTML PARSING & DATA EXTRACTION                                 │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                      CSS SELECTORS                                  │ │ │
│  │  │                                                                     │ │ │
│  │  │  Activity Container: <article class="node ct-physical-activity      │ │ │
│  │  │                              ct-physical-activity--full">           │ │ │
│  │  │                                                                     │ │ │
│  │  │  Data Extraction:                                                   │ │ │
│  │  │  ├─ title: .field__item h1 OR .activity-label                      │ │ │
│  │  │  ├─ event_slug: .url (extract from href)                           │ │ │
│  │  │  ├─ description: .ct-physical-activity__field-ct-act-description    │ │ │
│  │  │  │              .field__item                                       │ │ │
│  │  │  ├─ dates: .highlight-dates-single span (ISO format conversion)    │ │ │
│  │  │  ├─ location: .highlight-data-text span                            │ │ │
│  │  │  ├─ organisers: .pseudo__organisers .pseudo__organiser a           │ │ │
│  │  │  ├─ participants: .highlight-data-number                           │ │ │
│  │  │  │               .highlight-data-text-big (convert to int)         │ │ │
│  │  │  ├─ sdgs: .field-sdgs-wrapper img[alt] attributes                  │ │ │
│  │  │  ├─ objectives: .activity__objectives .field__item span            │ │ │
│  │  │  ├─ causes: .activity-causes .activity-label a                     │ │ │
│  │  │  └─ activity_type: .activity-types .activity-type a                │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  PHASE 2B: STATISTICS EXTRACTION                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                       STATISTICS WORKFLOW                               │ │
│  │                                                                         │ │
│  │  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐ │ │
│  │  │GET activities   │───▶│ Parse JSON       │───▶│ Map to Database     │ │ │
│  │  │.esn.org/organ   │    │ Response         │    │ Statistics Tables   │ │ │
│  │  │isation/<slug>/  │    │                  │    │                     │ │ │
│  │  │statistics       │    │ activities_      │    │ section_overall_    │ │ │
│  │  │                 │    │ statistics:      │    │ statistics          │ │ │
│  │  │Content-Type:    │    │                  │    │                     │ │ │
│  │  │application/json │    │ {                │    │ section_cause_      │ │ │
│  │  │                 │    │   total_         │    │ statistics          │ │ │
│  │  │                 │    │   activities,    │    │                     │ │ │
│  │  │                 │    │   total_         │    │ section_type_       │ │ │
│  │  │                 │    │   participants,  │    │ statistics          │ │ │
│  │  │                 │    │   total_causes,  │    │                     │ │ │
│  │  │                 │    │   physical_      │    │ section_participant_│ │ │
│  │  │                 │    │   activities,    │    │ statistics          │ │ │
│  │  │                 │    │   online_        │    │                     │ │ │
│  │  │                 │    │   activities     │    │                     │ │ │
│  │  │                 │    │ }                │    │                     │ │ │
│  │  └─────────────────┘    └──────────────────┘    └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  PHASE 3: DATA VALIDATION & STORAGE                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                        PYDANTIC VALIDATION                              │ │
│  │                                                                         │ │
│  │  ActivityModel Validation:                                              │ │
│  │  ├─ title: Required, non-empty string                                   │ │
│  │  ├─ event_slug: Required, unique identifier                             │ │
│  │  ├─ description: Required, non-empty text                               │ │
│  │  ├─ start_date/end_date: ISO format (YYYY-MM-DD)                        │ │
│  │  ├─ participants: Non-negative integer                                  │ │
│  │  ├─ activity_type: Valid enum value                                     │ │
│  │  └─ is_future_event: Boolean (computed from dates)                      │ │
│  │                                                                         │ │
│  │  Validation Failures → validation_errors table                          │ │
│  │  Invalid records → is_valid = FALSE                                     │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  PHASE 4: RELATIONSHIP MANAGEMENT                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                    MANY-TO-MANY RELATIONSHIPS                           │ │
│  │                                                                         │ │
│  │  Junction Tables Management:                                            │ │
│  │  ├─ activity_section_organisers (activity_id, section_id)               │ │
│  │  ├─ activity_to_cause (activity_id, cause_id)                           │ │
│  │  ├─ activity_to_sdg (activity_id, sdg_id)                               │ │
│  │  └─ activity_to_objective (activity_id, objective_id)                   │ │
│  │                                                                         │ │
│  │  UPSERT Strategy:                                                       │ │
│  │  1. Insert/Update main activity record                                  │ │
│  │  2. Clear existing relationships for activity                           │ │
│  │  3. Insert new relationship records                                     │ │
│  │  4. Update section.last_scraped timestamp                               │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.4. Error Handling ve Recovery

```
ERROR HANDLING & RECOVERY WORKFLOW
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  HTTP Errors (Network, Server Issues)                                      │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────────┐ │
│  │ Retry Logic     │───▶│ Exponential      │───▶│ failed_scrapes table    │ │
│  │ (Max 3 times)   │    │ Backoff          │    │ - url                   │ │
│  │                 │    │ (2^n seconds)    │    │ - error_message         │ │
│  │ 404, 500, 403   │    │                  │    │ - retry_count           │ │
│  │ Timeout errors  │    │ 2s, 4s, 8s       │    │ - timestamp             │ │
│  └─────────────────┘    └──────────────────┘    └─────────────────────────┘ │
│                                                                             │
│  Data Validation Errors                                                     │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────────┐ │
│  │ Pydantic        │───▶│ Log & Continue   │───▶│ validation_errors table │ │
│  │ ValidationError │    │ Processing       │    │ - section_id            │ │
│  │                 │    │                  │    │ - field_name            │ │
│  │ Invalid dates   │    │ Set is_valid =   │    │ - error_message         │ │
│  │ Negative values │    │ FALSE            │    │ - raw_data              │ │
│  │ Missing fields  │    │                  │    │ - timestamp             │ │
│  └─────────────────┘    └──────────────────┘    └─────────────────────────┘ │
│                                                                             │
│  Manual Recovery Options                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                         │ │
│  │  CLI Commands:                                                          │ │
│  │  ├─ python run_scraper.py --retry-failed                                │ │
│  │  ├─ python run_scraper.py --module activities --section esn-metu       │ │
│  │  ├─ python run_scraper.py --fix-validation-errors                       │ │
│  │  └─ python run_scraper.py --health-check                                │ │
│  │                                                                         │ │
│  │  Database Queries for Monitoring:                                       │ │
│  │  ├─ SELECT * FROM failed_scrapes WHERE retry_count >= 3                 │ │
│  │  ├─ SELECT * FROM validation_errors ORDER BY timestamp DESC LIMIT 100   │ │
│  │  └─ SELECT * FROM activities WHERE is_valid = FALSE                     │ │
│  │                                                                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Güvenlik ve Performans

### 6.1. Güvenlik Mimarisı

**Veri Güvenliği:**
- HTTPS zorunlu tüm external requests için
- Database connection string'leri environment variables'da
- Kişisel veriler toplama yok (GDPR compliance)
- Input validation ile SQL injection koruması

**Operational Security:**
- Rate limiting (0.5s delay) web scraping için
- Retry limits (max 3) infinite loop koruması
- User-Agent rotation bot detection önleme
- Error logging sensitive data içermeyen

### 6.2. Performans Stratejisi

**Asenkron İşleme:**
- `aiohttp` ile concurrent HTTP requests (max 10 parallel)
- `asyncpg` ile non-blocking database operations
- Celery workers horizontal scaling için

**Database Optimizasyonu:**
- Strategic indexing high-frequency queries için
- UPSERT operations conflict resolution ile
- Connection pooling (PgBouncer future)
- Read replicas for analytics (future)

**Memory Management:**
- Streaming JSON parsing büyük responses için
- Chunked pagination processing
- Garbage collection optimization

---

## 7. İzleme ve Operasyonel Yönetim

### 7.1. Monitoring Strategy

```
MONITORING ARCHITECTURE
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐      │
│  │  APPLICATION    │    │    DATABASE      │    │     SYSTEM       │      │
│  │   MONITORING    │    │   MONITORING     │    │   MONITORING     │      │
│  │                 │    │                  │    │                  │      │
│  │ - Scraper runs  │    │ - Query performance│  │ - CPU/Memory     │      │
│  │ - Success rates │    │ - Connection pools │  │ - Disk usage     │      │
│  │ - Error counts  │    │ - Table sizes     │   │ - Network I/O    │      │
│  │ - Task durations│    │ - Index usage     │   │                  │      │
│  └─────────────────┘    └──────────────────┘    └──────────────────┘      │
│           │                       │                       │                │
│           ▼                       ▼                       ▼                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        LOGGING SYSTEM                              │   │
│  │                                                                     │   │
│  │  File Logs: logs/scrape_YYYY-MM-DD.log                            │   │
│  │  - Structured JSON logging                                         │   │
│  │  - Rotation daily                                                  │   │
│  │  - Error level separation                                          │   │
│  │                                                                     │   │
│  │  Database Tables:                                                   │   │
│  │  - scraper_status (run history)                                   │   │
│  │  - validation_errors (data issues)                                │   │
│  │  - failed_scrapes (HTTP failures)                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2. Alerting & Recovery

**Critical Alerts:**
- Scraper success rate < 80%
- Database connection failures
- Disk space > 90% full
- Task queue backing up (> 100 pending tasks)

**Recovery Mechanisms:**
- Automatic retry with exponential backoff
- Manual trigger capabilities via CLI
- Database backup & restore procedures
- Failed task reprocessing from logs

---

## 8. Deployment ve Scaling

### 8.1. Deployment Architecture

**Phase 1 (Current): Local Development**
```
┌─────────────────────────────────────────────────────────────────┐
│                    LOCAL DEPLOYMENT                            │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Docker     │  │    Docker    │  │      Docker          │  │
│  │ PostgreSQL   │  │    Redis     │  │   Python App         │  │
│  │              │  │              │  │                      │  │
│  │ - Port 5432  │  │ - Port 6379  │  │ - Celery Workers     │  │
│  │ - Volume     │  │ - Persistence│  │ - Beat Scheduler     │  │
│  │   mounted    │  │   optional   │  │ - CLI Interface      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

**Command:**
```bash
docker-compose up -d
python run_scraper.py --module all
```

**Phase 2 (Future): Web Deployment**
```
┌─────────────────────────────────────────────────────────────────┐
│                   CLOUD DEPLOYMENT                             │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Managed    │  │   Managed    │  │    Containerized     │  │
│  │ PostgreSQL   │  │    Redis     │  │     Services         │  │
│  │ (AWS RDS)    │  │ (AWS ElastiC)│  │                      │  │
│  │              │  │              │  │ - FastAPI Web App    │  │
│  │ - Backup     │  │ - Clustering │  │ - Celery Workers     │  │
│  │ - Scaling    │  │ - Persistence│  │ - Nginx Load Balancer│  │
│  │ - Monitoring │  │              │  │ - HTTPS/SSL          │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2. Scaling Strategy

**Horizontal Scaling:**
- Celery workers can be distributed across multiple machines
- Database read replicas for analytics workload
- Load balancing for web interface (Phase 2)

**Vertical Scaling:**
- PostgreSQL memory/CPU scaling for large datasets
- Redis memory scaling for task queue
- Worker process tuning based on system resources

**Performance Targets:**
- 517 sections scraped within 2 hours
- < 5% failure rate on HTTP requests
- Database queries < 100ms average response time
- 99% uptime for scheduled scraping tasks

---

## 9. Veri Akışı Detayları

### 9.1. Veri Dönüşüm Pipeline'ı

```
COMPREHENSIVE DATA TRANSFORMATION PIPELINE
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  PHASE 1: DATA ACQUISITION                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                    MULTI-SOURCE DATA EXTRACTION                         │ │
│  │                                                                         │ │
│  │  accounts.esn.org              activities.esn.org                       │ │
│  │  ┌─────────────────┐           ┌──────────────────────────────────────┐  │ │
│  │  │ Country Data    │           │        Activity Data                 │  │ │
│  │  │                 │           │                                      │  │ │
│  │  │ • /             │           │ • /organisation/<slug>/activities    │  │ │
│  │  │ • HTML page     │           │ • HTML pages with pagination         │  │ │
│  │  │ • Country list  │           │ • CSS selector-based extraction      │  │ │
│  │  │                 │           │                                      │  │ │
│  │  │ Section Data    │           │        Activity Details             │  │ │
│  │  │                 │           │                                      │  │ │
│  │  │ • /country/     │           │ • /activity/<event_slug>             │  │ │
│  │  │   <country_code>│           │ • HTML page parsing                  │  │ │
│  │  │ • /section/     │           │ • Individual event data              │  │ │
│  │  │   <accounts_    │           │                                      │  │ │
│  │  │   platform_slug>│           │        Statistics Data              │  │ │
│  │  │ • HTML parsing  │           │                                      │  │ │
│  │  │ • <span class=  │           │ • /organisation/<slug>/statistics    │  │ │
│  │  │   "field-       │           │ • JSON API response                  │  │ │
│  │  │   content">     │           │ • Direct statistical values          │  │ │
│  │  └─────────────────┘           └──────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                        │
│                                    ▼                                        │
│  PHASE 2: PARSING & STRUCTURING                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                      BEAUTIFULSOUP4 PARSING ENGINE                      │ │
│  │                                                                         │ │
│  │  HTML Content Processing:                                               │ │
│  │  ├─ Parse DOM structure                                                 │ │
│  │  ├─ Apply CSS selectors                                                 │ │
│  │  ├─ Extract text content                                                │ │
│  │  ├─ Handle nested elements                                              │ │
│  │  └─ Manage encoding issues                                              │ │
│  │                                                                         │ │
│  │  Specific Extraction Rules:                                             │ │
│  │  ┌───────────────────────────────────────────────────────────────────┐  │ │
│  │  │ ACTIVITY PARSING RULES                                            │  │ │
│  │  │                                                                   │  │ │
│  │  │ Container: article.node.ct-physical-activity                      │  │ │
│  │  │           .ct-physical-activity--full                             │  │ │
│  │  │                                                                   │  │ │
│  │  │ Field Extractions:                                                │  │ │
│  │  │ ├─ Title: .field__item h1 OR .activity-label                     │  │ │
│  │  │ ├─ Event Slug: Extract from .url href attribute                  │  │ │
│  │  │ ├─ Description: .ct-physical-activity__field-ct-act-description   │  │ │
│  │  │ │              .field__item                                      │  │ │
│  │  │ ├─ Dates: .highlight-dates-single span → ISO conversion          │  │ │
│  │  │ ├─ Location: .highlight-data-text span → city/country split      │  │ │
│  │  │ ├─ Organisers: .pseudo__organisers .pseudo__organiser a          │  │ │
│  │  │ ├─ Participants: .highlight-data-number                          │  │ │
│  │  │ │               .highlight-data-text-big → int conversion        │  │ │
│  │  │ ├─ SDGs: .field-sdgs-wrapper img[alt] → list extraction          │  │ │
│  │  │ ├─ Objectives: .activity__objectives .field__item span           │  │ │
│  │  │ ├─ Causes: .activity-causes .activity-label a                    │  │ │
│  │  │ └─ Type: .activity-types .activity-type a                        │  │ │
│  │  └───────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                         │ │
│  │  JSON Processing (Statistics):                                          │ │
│  │  ├─ Parse activities_statistics object                                  │ │
│  │  ├─ Map to section_*_statistics tables                                 │ │
│  │  ├─ Handle nested value structures                                      │ │
│  │  └─ Extract multi-dimensional data                                      │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                        │
│                                    ▼                                        │
│  PHASE 3: DATA VALIDATION & CLEANING                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                       PYDANTIC VALIDATION LAYER                         │ │
│  │                                                                         │ │
│  │  Validation Categories:                                                 │ │
│  │                                                                         │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │ │
│  │  │  Type Safety    │  │ Business Rules  │  │    Data Quality         │  │ │
│  │  │                 │  │                 │  │                         │  │ │
│  │  │ • String limits │  │ • Participants  │  │ • Required fields       │  │ │
│  │  │ • Date formats  │  │   >= 0          │  │ • Non-empty strings     │  │ │
│  │  │ • Email format  │  │ • Valid dates   │  │ • URL validation        │  │ │
│  │  │ • URL structure │  │ • Future event  │  │ • Coordinate ranges     │  │ │
│  │  │ • Coordinates   │  │   calculation   │  │ • Slug uniqueness       │  │ │
│  │  │   precision     │  │                 │  │                         │  │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────────┘  │ │
│  │                                                                         │ │
│  │  Validation Outcomes:                                                   │ │
│  │  ├─ Valid Data → Continue to database operations                        │ │
│  │  ├─ Validation Errors → Log to validation_errors table                 │ │
│  │  ├─ Partial Errors → Set is_valid=FALSE, continue processing           │ │
│  │  └─ Critical Errors → Skip record, log for manual review               │ │
│  │                                                                         │ │
│  │  Example Validation Rules:                                              │ │
│  │  ```python                                                             │ │
│  │  class ActivityModel(BaseModel):                                        │ │
│  │      title: str = Field(min_length=1, max_length=255)                   │ │
│  │      description: str = Field(min_length=1)                             │ │
│  │      participants: int = Field(ge=0)                                    │ │
│  │      start_date: date                                                   │ │
│  │      event_slug: str = Field(regex=r'^[a-z0-9-]+$')                     │ │
│  │      coordinates: Optional[Tuple[float, float]] = Field(                │ │
│  │          validator=lambda v: validate_coordinates(v)                    │ │
│  │      )                                                                  │ │
│  │  ```                                                                    │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                        │
│                                    ▼                                        │
│  PHASE 4: DATABASE OPERATIONS                                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                        POSTGRESQL UPSERT STRATEGY                       │ │
│  │                                                                         │ │
│  │  Transaction Management:                                                │ │
│  │  ┌───────────────────────────────────────────────────────────────────┐  │ │
│  │  │                                                                   │  │ │
│  │  │ BEGIN TRANSACTION                                                 │  │ │
│  │  │                                                                   │  │ │
│  │  │ 1. UPSERT Core Entity (activities, sections)                     │  │ │
│  │  │    ON CONFLICT (unique_constraint) DO UPDATE                      │  │ │
│  │  │                                                                   │  │ │
│  │  │ 2. MANAGE Many-to-Many Relationships                              │  │ │
│  │  │    - Clear existing relationships for entity                      │  │ │
│  │  │    - Insert new relationship records                              │  │ │
│  │  │    - Handle junction table constraints                            │  │ │
│  │  │                                                                   │  │ │
│  │  │ 3. UPDATE Timestamps and Status Fields                            │  │ │
│  │  │    - last_scraped = NOW()                                         │  │ │
│  │  │    - updated_at = NOW()                                           │  │ │
│  │  │                                                                   │  │ │
│  │  │ 4. HANDLE Validation Errors                                       │  │ │
│  │  │    - INSERT INTO validation_errors                                │  │ │
│  │  │    - Log details for manual review                                │  │ │
│  │  │                                                                   │  │ │
│  │  │ COMMIT / ROLLBACK based on success                                │  │ │
│  │  └───────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                         │ │
│  │  Relationship Handling Example:                                         │ │
│  │  ```sql                                                                 │ │
│  │  -- Clear existing relationships                                        │ │
│  │  DELETE FROM activity_to_cause WHERE activity_id = %s;                  │ │
│  │  DELETE FROM activity_to_sdg WHERE activity_id = %s;                    │ │
│  │                                                                         │ │
│  │  -- Insert new relationships                                            │ │
│  │  INSERT INTO activity_to_cause (activity_id, cause_id)                  │ │
│  │  SELECT %s, id FROM activity_causes WHERE name = ANY(%s);               │ │
│  │  ```                                                                    │ │
│  │                                                                         │ │
│  │  Performance Optimizations:                                             │ │
│  │  ├─ Batch INSERT operations for bulk data                               │ │
│  │  ├─ Prepared statements for repeated queries                            │ │
│  │  ├─ Index usage for conflict resolution                                 │ │
│  │  └─ Connection pooling for concurrent operations                        │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                                    ▼                                         │
│  PHASE 5: ERROR HANDLING & MONITORING                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                         COMPREHENSIVE ERROR MANAGEMENT                  │ │
│  │                                                                         │ │
│  │  Error Classification:                                                  │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │ │
│  │  │  HTTP Errors    │  │ Parsing Errors  │  │   Database Errors       │  │ │
│  │  │                 │  │                 │  │                         │  │ │
│  │  │ • 404 Not Found │  │ • Invalid HTML  │  │ • Connection failures   │  │ │
│  │  │ • 403 Forbidden │  │ • Missing CSS   │  │ • Constraint violations │  │ │
│  │  │ • 500 Server    │  │   selectors     │  │ • Transaction rollbacks │  │ │
│  │  │ • Timeout       │  │ • Malformed     │  │ • Deadlocks             │  │ │
│  │  │ • Rate limiting │  │   JSON          │  │                         │  │ │
│  │  │                 │  │                 │  │                         │  │ │
│  │  │ → failed_       │  │ → Skip record,  │  │ → Retry with backoff,   │  │ │
│  │  │   scrapes       │  │   log error     │  │   alert on failure      │  │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────────┘  │ │
│  │                                                                         │ │
│  │  Recovery Mechanisms:                                                   │ │
│  │  ├─ Exponential backoff for HTTP retries (2^n seconds)                 │ │
│  │  ├─ Circuit breaker for persistent failures                            │ │
│  │  ├─ Manual reprocessing via CLI commands                               │ │
│  │  ├─ Data consistency checks and repairs                                │ │
│  │  └─ Health monitoring and alerting                                     │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Data Quality Assurance Framework:**

```python
# Quality Metrics Collection
class DataQualityMetrics:
    def __init__(self):
        self.total_records_processed = 0
        self.validation_failures = 0
        self.http_failures = 0
        self.successful_inserts = 0
        self.duplicate_records = 0
        
    def calculate_quality_score(self) -> float:
        """Calculate overall data quality percentage"""
        if self.total_records_processed == 0:
            return 0.0
        return (self.successful_inserts / self.total_records_processed) * 100

# Real-time Quality Monitoring
async def monitor_data_quality():
    """Monitor data quality in real-time during scraping"""
    quality_checks = [
        "SELECT COUNT(*) FROM activities WHERE is_valid = FALSE",
        "SELECT COUNT(*) FROM validation_errors WHERE created_at > NOW() - INTERVAL '1 hour'",
        "SELECT COUNT(*) FROM failed_scrapes WHERE will_retry = TRUE",
        "SELECT AVG(participants) FROM activities WHERE participants > 0"
    ]
    # Execute checks and alert if thresholds exceeded

# Data Completeness Validation
async def validate_data_completeness():
    """Ensure all expected data is present"""
    checks = {
        'sections_without_activities': """
            SELECT s.name FROM sections s 
            LEFT JOIN activity_section_organisers aso ON s.id = aso.section_id
            WHERE s.can_scrape_activities = TRUE AND aso.section_id IS NULL
        """,
        'activities_without_organisers': """
            SELECT a.title FROM activities a
            LEFT JOIN activity_section_organisers aso ON a.id = aso.activity_id
            WHERE aso.activity_id IS NULL
        """,
        'missing_statistics': """
            SELECT s.name FROM sections s
            LEFT JOIN section_overall_statistics sos ON s.id = sos.section_id
            WHERE s.can_scrape_activities = TRUE AND sos.section_id IS NULL
        """
    }
    return checks
```

### 9.2. Error Handling Flow

```
ERROR HANDLING ARCHITECTURE
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         ERROR TYPES                                  │  │
│  │                                                                      │  │
│  │  HTTP Errors          Data Errors           System Errors           │  │
│  │  ├─ 404 Not Found     ├─ Invalid Dates      ├─ DB Connection         │  │
│  │  ├─ 403 Forbidden     ├─ Missing Fields     ├─ Memory Exhaustion     │  │
│  │  ├─ 500 Server Error  ├─ Bad Coordinates    ├─ Disk Full             │  │
│  │  └─ Timeout           └─ Negative Values    └─ Network Issues        │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│                                    ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    ERROR ROUTING                                     │  │
│  │                                                                      │  │
│  │  HTTP Errors ────────┬────▶ failed_scrapes table                    │  │
│  │                      │      ├─ Retry logic (3x)                     │  │
│  │                      │      ├─ Exponential backoff                  │  │
│  │                      │      └─ Manual reprocessing                  │  │
│  │                      │                                               │  │
│  │  Data Errors ────────┼────▶ validation_errors table                 │  │
│  │                      │      ├─ Skip invalid records                 │  │
│  │                      │      ├─ Continue processing                  │  │
│  │                      │      └─ Manual data review                   │  │
│  │                      │                                               │  │
│  │  System Errors ──────┼────▶ Application logs                        │  │
│  │                      │      ├─ Immediate alerts                     │  │
│  │                      │      ├─ Celery task restart                  │  │
│  │                      │      └─ System monitoring                    │  │
│  └──────────────────────┼──────────────────────────────────────────────┘  │
│                         │                                                  │
│                         ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                   RECOVERY ACTIONS                                   │  │
│  │                                                                      │  │
│  │  Automatic Recovery:                                                 │  │
│  │  - Retry failed HTTP requests with backoff                          │  │
│  │  - Skip validation errors and continue                              │  │
│  │  - Restart workers on system errors                                 │  │
│  │                                                                      │  │
│  │  Manual Recovery:                                                    │  │
│  │  - Reprocess failed_scrapes via CLI                                 │  │
│  │  - Fix validation_errors with data patches                          │  │
│  │  - Manual scraper trigger for specific sections                     │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. API ve Entegrasyon Noktaları

### 10.1. External API Dependencies

**ESN Platform APIs:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            ESN API INTERFACES                              │
│                                                                             │
│  accounts.esn.org                        activities.esn.org                │
│  ┌─────────────────────────────┐         ┌──────────────────────────────┐  │
│  │                             │         │                              │  │
│  │ Endpoints:                  │         │ Endpoints:                   │  │
│  │ - /                         │         │ - /organisation/             │  │
│  │ - /country/<country_code>   │         │   <activities_platform_slug>/│  │
│  │ - /section/                 │         │ - /organisation/             │  │
│  │   <accounts_platform_slug>  │         │   <activities_platform_slug>/│  │
│  │                             │         │   activities                 │  │
│  │ Data Format: HTML           │         │ - /activity/<event_slug>     │  │
│  │ Authentication: None        │         │ - /organisation/             │  │
│  │ Rate Limit: 0.5s delay      │         │   <activities_platform_slug>/│  │
│  │ Caching: Browser cache      │         │   statistics                 │  │
│  │                             │         │                              │  │
│  │ Examples:                   │         │ Data Format: HTML + JSON     │  │
│  │ • /country/tr               │         │ Authentication: None          │  │
│  │ • /section/tr-anka-met      │         │ Rate Limit: 0.5s delay      │  │
│  │                             │         │ Caching: Dynamic content     │  │
│  │                             │         │                              │  │
│  │                             │         │ Examples:                    │  │
│  │                             │         │ • /organisation/esn-metu/    │  │
│  │                             │         │ • /activity/boat-party-20885 │  │
│  └─────────────────────────────┘         └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 10.2. Future API Endpoints (Phase 2)

**Internal API Design:**
```python
# FastAPI endpoints for Phase 2
@app.get("/api/v1/countries")
async def get_countries() -> List[Country]

@app.get("/api/v1/countries/{code}/sections")
async def get_country_sections(code: str) -> List[Section]

@app.get("/api/v1/sections/{section_id}/activities")
async def get_section_activities(
    section_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    limit: int = 20
) -> PaginatedActivities

@app.get("/api/v1/sections/{section_id}/statistics")
async def get_section_statistics(section_id: int) -> SectionStats

@app.post("/api/v1/trigger/scraper")
async def trigger_scraper(
    request: ScraperTriggerRequest,
    api_key: str = Depends(get_api_key)
) -> ScraperResponse
```

---

## 11. Testing Strategy

### 11.1. Test Architecture

```
TESTING PYRAMID
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                            ┌─────────────────┐                             │
│                            │  E2E TESTS      │                             │
│                            │                 │                             │
│                            │ - Full workflow │                             │
│                            │ - 5 sections    │                             │
│                            │ - Real database │                             │
│                            └─────────────────┘                             │
│                        ┌─────────────────────────┐                         │
│                        │  INTEGRATION TESTS      │                         │
│                        │                         │                         │
│                        │ - Database operations   │                         │
│                        │ - Celery task execution │                         │
│                        │ - HTTP client mocking   │                         │
│                        │ - Error scenarios       │                         │
│                        └─────────────────────────┘                         │
│              ┌─────────────────────────────────────────────┐               │
│              │                UNIT TESTS                   │               │
│              │                                             │               │
│              │ - Data parsing functions                    │               │
│              │ - Validation logic                          │               │
│              │ - Utility functions                         │               │
│              │ - Model serialization                       │               │
│              │ - Error handling                            │               │
│              │                                             │               │
│              │ Target: 80% code coverage                   │               │
│              └─────────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 11.2. Test Data Management

**Mock Data Strategy:**
- Sample HTML responses from ESN platforms
- Test database with realistic but anonymized data
- Fixtures for common scenarios (success, errors, edge cases)
- Snapshot testing for parser output consistency

**CI/CD Integration:**
```yaml
# GitHub Actions workflow
- Unit tests on every commit
- Integration tests on pull requests
- E2E tests on release candidates
- Performance benchmarks on main branch
```

---

## 12. Maintenance ve Operations

### 12.1. Operational Runbooks

**Daily Operations:**
- Monitor scraper_status table for failures
- Check error logs for unusual patterns
- Verify disk space and database size
- Review success rates dashboard

**Weekly Operations:**
- Analyze validation_errors for data quality issues
- Review failed_scrapes for platform changes
- Update test data with recent samples
- Performance monitoring review

**Monthly Operations:**
- Database maintenance (VACUUM, REINDEX)
- Backup verification and testing
- Security updates for dependencies
- Platform compatibility checks

### 12.2. Disaster Recovery

**Backup Strategy:**
```bash
# Daily automated backups
pg_dump -U postgres -h localhost esn_pulse > backup_$(date +%Y%m%d).sql

# Weekly full system backup
tar -czf esn_pulse_full_$(date +%Y%m%d).tar.gz \
    /opt/esn_pulse/ \
    /var/lib/postgresql/data/ \
    /var/log/esn_pulse/
```

**Recovery Procedures:**
1. Database corruption: Restore from latest backup
2. Code deployment failure: Rollback to previous version
3. External API changes: Update parsers and retry failed tasks
4. System failure: Migrate to backup infrastructure

---

## 13. Performance Benchmarks ve SLA

### 13.1. Performance Targets

| Metric | Target | Measurement |
|--------|---------|-------------|
| **Full scrape duration** | < 2 hours | All 517 sections |
| **HTTP success rate** | > 95% | Per scraping session |
| **Data validation success** | > 98% | Per activity record |
| **Database query time** | < 100ms | 95th percentile |
| **Memory usage** | < 2GB | Peak during scraping |
| **Storage growth** | < 1GB/month | Database size |

### 13.2. Service Level Agreements

**Availability:**
- Scheduled scraping: 99% success rate
- Data freshness: < 7 days for activities
- Recovery time: < 4 hours for major failures

**Data Quality:**
- Completeness: > 95% of available records
- Accuracy: < 2% validation error rate
- Consistency: Foreign key integrity maintained

---

## 14. Future Architecture Considerations

### 14.1. Scalability Roadmap

**Phase 2 Enhancements:**
- Web dashboard with role-based access
- Real-time scraping triggers via web interface
- Advanced analytics and reporting
- Multi-tenant support for different ESN levels

**Phase 3 Vision:**
- Machine learning integration for activity recommendations
- Predictive analytics for event planning
- Social media integration for engagement metrics
- Mobile API for ESN mobile applications

### 14.2. Technology Evolution

**Potential Migrations:**
- Database: PostgreSQL → TimeSeriesDB for metrics
- Queue: Redis → Apache Kafka for streaming
- Monitoring: Logs → Prometheus + Grafana
- Deployment: Docker → Kubernetes for orchestration

---

## 15. Başarı Metrikleri

### 15.1. Technical KPIs

- **Scraping Efficiency:** Sections/hour processed
- **Error Rate:** Failed requests / Total requests
- **Data Quality Score:** Valid records / Total records
- **System Uptime:** Availability percentage
- **Resource Utilization:** CPU, Memory, Disk usage

### 15.2. Business KPIs

- **Data Coverage:** ESN sections with complete data
- **User Adoption:** BI tool users accessing data
- **Decision Impact:** Reports generated using the data
- **Cost Efficiency:** Infrastructure cost per GB processed