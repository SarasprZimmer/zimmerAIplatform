# Automation Health Gate System

## Overview

The Automation Health Gate system ensures that only healthy and reliable automations are available for purchase and use. It provides automatic health monitoring, status classification, and purchase gating based on automation health status.

## Health Check Requirements

### Expected Health Check Response

Automations must provide a health check endpoint that returns a JSON response with the following required fields:

```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime": 12345
}
```

**Required Fields:**
- `status`: Must be one of `"ok"`, `"healthy"`, or `"up"` for healthy status
- `version`: Current version of the automation service
- `uptime`: Service uptime in seconds

**Optional Fields:**
- Any additional health metrics or status information

### Health Check URL Format

Health check URLs should be:
- Accessible via HTTP GET
- Return JSON response
- Respond within 5 seconds
- Return HTTP 200 status code for healthy state

Example: `https://your-automation-service.com/health`

## Health Status Classification

The system classifies automation health into three categories:

### 1. Healthy (`healthy`)
- Health check returns HTTP 200
- Response contains all required fields
- `status` field is `"ok"`, `"healthy"`, or `"up"`
- Automation is available for purchase and listing

### 2. Degraded (`degraded`)
- Health check returns HTTP 200
- Response contains all required fields
- `status` field is not `"ok"`, `"healthy"`, or `"up"`
- Automation is not available for purchase

### 3. Unhealthy (`unhealthy`)
- Health check fails (network error, timeout, HTTP error)
- Response missing required fields
- Automation is not available for purchase

## Setting Up Health Check for an Automation

### Via Admin API

When creating or updating an automation, include the `health_check_url` field:

```bash
POST /api/admin/automations
{
  "name": "My Automation",
  "description": "Description",
  "pricing_type": "token_per_session",
  "price_per_token": 10.0,
  "status": true,
  "health_check_url": "https://my-automation.com/health"
}
```

### Health Check Behavior

1. **During Creation/Update**: If `health_check_url` is provided, the system automatically:
   - Probes the health check URL
   - Classifies the health status
   - Sets `is_listed` based on health status
   - Records health check details

2. **Manual Health Check**: Admins can trigger health checks manually:
   ```bash
   POST /api/admin/automations/{automation_id}/health-check
   ```

## Purchase Gating

### Automatic Gating

The system automatically prevents purchases from unhealthy automations:

- **Healthy automations**: Available for purchase
- **Degraded/Unhealthy automations**: Purchase requests return 400 error with "Automation is currently unavailable for purchase"

### Public Listing Filter

The public automations endpoint (`/api/automations/available`) only shows:
- Active automations (`status = true`)
- Listed automations (`is_listed = true`)
- Healthy automations (`health_status = "healthy"`)

## Admin Health Check Endpoint

### Endpoint
```
POST /api/admin/automations/{automation_id}/health-check
```

### Response
```json
{
  "automation_id": 123,
  "health_status": "healthy",
  "is_listed": true,
  "last_health_at": "2025-08-28T10:30:00Z",
  "details": {
    "ok": true,
    "body": {
      "status": "ok",
      "version": "1.0.0",
      "uptime": 12345
    }
  }
}
```

### Usage
```bash
# Run health check for automation
curl -X POST "https://api.example.com/api/admin/automations/123/health-check" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## Database Schema

### New Fields Added to Automation Model

```sql
-- Health check URL
health_check_url VARCHAR(500) NULL

-- Health status (unknown, healthy, degraded, unhealthy)
health_status VARCHAR(16) NOT NULL DEFAULT 'unknown'

-- Last health check timestamp
last_health_at TIMESTAMP WITH TIME ZONE NULL

-- Health check details (JSON)
health_details JSON NULL

-- Listing status (only true when healthy)
is_listed BOOLEAN NOT NULL DEFAULT FALSE

-- Indexes for performance
CREATE INDEX ix_automations_health_status ON automations(health_status);
CREATE INDEX ix_automations_is_listed ON automations(is_listed);
```

## Health Check Configuration

### Timeout and Retry Settings

- **Timeout**: 5 seconds per request
- **Retries**: 2 retry attempts on failure
- **Expected Fields**: `status`, `version`, `uptime`

### Customization

You can modify the health check behavior by editing `services/automation_health.py`:

```python
# Adjust timeout
DEFAULT_TIMEOUT = 10.0  # Increase timeout

# Adjust retry count
RETRIES = 3  # More retries

# Modify expected fields
EXPECTED_FIELDS = {"status", "version", "uptime", "custom_field"}
```

## Monitoring and Alerts

### Health Status Monitoring

Monitor automation health through:

1. **Admin Dashboard**: View health status in automation list
2. **API Endpoints**: Query health status programmatically
3. **Database Queries**: Direct database access for monitoring

### Recommended Monitoring Queries

```sql
-- Count automations by health status
SELECT health_status, COUNT(*) 
FROM automations 
WHERE status = true 
GROUP BY health_status;

-- Find unhealthy automations
SELECT id, name, health_status, last_health_at 
FROM automations 
WHERE health_status != 'healthy' AND status = true;

-- Find automations that haven't been checked recently
SELECT id, name, last_health_at 
FROM automations 
WHERE last_health_at < NOW() - INTERVAL '1 hour';
```

## Best Practices

### 1. Health Check Implementation

- Keep health checks lightweight and fast
- Include essential service metrics
- Use appropriate HTTP status codes
- Implement proper error handling

### 2. Monitoring

- Set up alerts for unhealthy automations
- Monitor health check response times
- Track automation availability metrics
- Regular health check scheduling

### 3. Automation Management

- Test health checks before deployment
- Monitor health status after updates
- Set up automated health check scheduling
- Document health check requirements

## Troubleshooting

### Common Issues

1. **Health Check Timeout**
   - Check network connectivity
   - Verify health check endpoint is accessible
   - Consider increasing timeout if needed

2. **Schema Mismatch**
   - Ensure health check returns required fields
   - Check JSON response format
   - Verify field names match exactly

3. **Authentication Issues**
   - Ensure health check endpoint doesn't require authentication
   - Check for IP restrictions
   - Verify CORS settings if applicable

### Debug Health Checks

```bash
# Test health check endpoint directly
curl -X GET "https://your-automation.com/health"

# Check automation health status
curl -X GET "https://api.example.com/api/admin/automations" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Run manual health check
curl -X POST "https://api.example.com/api/admin/automations/123/health-check" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## API Reference

### Health Check Service

**Location**: `services/automation_health.py`

**Functions**:
- `probe(url: str) -> dict`: Probe health check URL
- `classify(result: dict) -> str`: Classify health status

### Admin Endpoints

**Health Check**: `POST /api/admin/automations/{id}/health-check`
**List Automations**: `GET /api/admin/automations` (includes health info)

### Public Endpoints

**Available Automations**: `GET /api/automations/available` (filtered by health)

### Payment Endpoints

**Init Payment**: `POST /api/payments/zarinpal/init` (gated by health status)
