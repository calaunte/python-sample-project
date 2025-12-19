# IP Geolocation Service

FastAPI microservice for IP address geolocation lookup using ip-api.com.

## Features

- **Specific IP Lookup**: Get geolocation data for any public IPv4 address
- **Client IP Detection**: Automatically detect and geolocate the requesting client's IP
- **Rich Geolocation Data**: Country, region, city, coordinates, timezone, ISP, AS number
- **Comprehensive Error Handling**: Clear error messages with machine-readable error types
- **Health Check**: Service and provider health monitoring
- **OpenAPI Documentation**: Interactive API docs with examples

## Requirements

- Python 3.12 or higher
- Virtual environment (recommended)

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd python-sample-project
```

### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -e ".[dev]"
```

## Running the Service

### Start the server

```bash
uvicorn app.main:app --reload
```

The service will be available at `http://localhost:8000`

### Configuration

The service uses environment variables for configuration. Create a `.env` file in the project root:

```env
# Optional configuration (defaults shown)
APP_NAME=IP Geolocation Service
DEBUG=false
API_V1_PREFIX=/api/v1
PROVIDER_NAME=ip-api.com
PROVIDER_BASE_URL=http://ip-api.com/json
PROVIDER_TIMEOUT=5
```

## API Usage

### Look up a specific IP address

```bash
curl http://localhost:8000/api/v1/geolocate/8.8.8.8
```

Response:
```json
{
  "ip": "8.8.8.8",
  "country": "United States",
  "country_code": "US",
  "region": "California",
  "region_code": "CA",
  "city": "Mountain View",
  "zip_code": "94035",
  "latitude": 37.386,
  "longitude": -122.0838,
  "timezone": "America/Los_Angeles",
  "isp": "Google LLC",
  "organization": "Google Public DNS",
  "as_number": "AS15169",
  "as_name": "GOOGLE"
}
```

### Look up client's IP address

```bash
curl http://localhost:8000/api/v1/geolocate
```

Or with a specific IP in headers (useful for testing):

```bash
curl -H "X-Forwarded-For: 8.8.8.8" http://localhost:8000/api/v1/geolocate
```

### Health check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "provider": "ip-api.com",
  "provider_status": "available"
}
```

## API Documentation

Access interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json or see `openapi.yaml`

## Running Tests

### Run all tests

```bash
pytest
```

### Run with coverage

```bash
pytest --cov=app --cov-report=html --cov-report=term
```

View coverage report: `open htmlcov/index.html`

### Run specific test suites

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/unit/test_validators.py -v
```

## Code Quality

### Linting with ruff

```bash
ruff check .
ruff check . --fix  # Auto-fix issues
```

### Type checking with mypy

```bash
mypy app/
```

### Format code

```bash
ruff format .
```

## Project Structure

```
python-sample-project/
├── app/
│   ├── api/v1/
│   │   ├── endpoints/
│   │   │   └── geolocation.py   # API endpoints
│   │   └── router.py             # Router aggregation
│   ├── core/
│   │   ├── exceptions.py         # Custom exceptions
│   │   ├── http_client.py        # Singleton HTTP client
│   │   └── validators.py         # IP validation
│   ├── dependencies/
│   │   └── client_ip.py          # Client IP extraction
│   ├── models/
│   │   ├── errors.py             # Error models
│   │   └── responses.py          # Response models
│   ├── services/
│   │   ├── geolocation.py        # Service layer
│   │   └── ip_providers/
│   │       ├── base.py           # Provider interface
│   │       └── ip_api.py         # ip-api.com implementation
│   ├── config.py                 # Configuration
│   └── main.py                   # FastAPI app
├── tests/
│   ├── integration/              # Integration tests
│   └── unit/                     # Unit tests
├── openapi.yaml                  # OpenAPI specification
├── pyproject.toml                # Project metadata
└── README.md
```

## API Design Decisions

### Two Separate Endpoints

I chose to implement two separate endpoints (`/geolocate/{ip}` and `/geolocate`) rather than a single endpoint with optional parameters:

**Rationale:**
- **Clear intent**: The URL alone tells you what the endpoint does
- **RESTful**: Each endpoint represents a different resource (specific IP vs client's IP)
- **No magic values**: Avoids special parameters like `?ip=me` or `/geolocate/me`
- **Better documentation**: Each endpoint has specific, focused documentation

### Error Response Format

All errors follow a consistent structure:

```json
{
  "error": {
    "type": "error_code",
    "message": "Human-readable message"
  }
}
```

**Rationale:**
- **Machine-readable**: `type` field allows programmatic error handling
- **Human-readable**: `message` field provides debugging context
- **Consistent**: All errors follow the same shape
- **Industry standard**: Similar to Stripe, GitHub, etc.

### Client IP Detection

The service checks headers in this order:
1. `X-Forwarded-For` (most common for proxied requests)
2. `X-Real-IP` (alternative proxy header)
3. Direct connection IP

**Rationale:**
- **Proxy-aware**: Handles nginx, Cloudflare, load balancers correctly
- **Fallback**: Works in direct connection scenarios
- **Standard practice**: Industry convention for IP detection

### Provider Abstraction

The service uses an abstract provider interface, allowing easy switching between geolocation data sources.

**Rationale:**
- **Future-proof**: Can easily add MaxMind, ipapi.co, or other providers
- **Testability**: Provider can be mocked in tests
- **Separation of concerns**: Service layer doesn't depend on provider specifics

## Data Source: ip-api.com

**Why ip-api.com?**
- No authentication required (faster development)
- Generous free tier (45 requests/minute)
- Rich geolocation data
- Simple integration (single HTTP GET request)
- Good reliability

**Trade-offs:**
- Network dependency (adds latency vs local database)
- Rate limits (45/min for free tier)
- No offline support

**Production Recommendation:**
For production at scale, I would recommend a hybrid approach:
1. **Primary**: MaxMind GeoLite2 local database (low latency, no rate limits)
2. **Fallback**: Paid API service (handles edge cases and new IPs)
3. **Caching**: Redis with 24h TTL (reduces both DB and API load by 80-90%)
4. **Updates**: Automated weekly updates for MaxMind data

## Error Handling

The service validates IPs before calling the provider (fail-fast approach):

| Status Code | Error Type | Description |
|-------------|-----------|-------------|
| 400 | `invalid_ip` | Malformed IPv4 address |
| 404 | `ip_not_found` | IP not found in database |
| 422 | `private_ip` | Private/reserved IP (10.x.x.x, 192.168.x.x, 127.0.0.1, etc.) |
| 429 | `rate_limit_exceeded` | Provider rate limit hit |
| 503 | `provider_unavailable` | Provider API down or timeout |

## Testing Strategy

- **Unit tests** (80%): Test individual components with mocking
  - IP validators
  - Provider implementation
  - Service layer
  - Client IP extraction

- **Integration tests** (20%): Test full request/response cycle
  - API endpoints with mocked provider
  - Error scenarios
  - Client IP detection

**Coverage**: 93% overall, 100% on API endpoints and models
