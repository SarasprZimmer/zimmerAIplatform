## User Usage Endpoints
- `GET /api/user/usage?range=7d&automation_id=` → returns 7 daily points `{ day, tokens, sessions }`
- `GET /api/user/usage?range=6m` → returns monthly points `{ month, value }`
- `GET /api/user/usage/distribution` → tokens grouped by automation `{ name, value }`

Works with SQLite and PostgreSQL (dialect-aware date grouping).

## User Billing Endpoints
- `GET /api/user/automations/active` → list user's active automations with token balances
- `GET /api/user/payments?limit=&offset=&order=desc|asc` → payment history (paginated)
- `GET /api/user/payments/summary?months=6` → monthly expenses for last N months (successful payments)
- `GET /api/user/payments/{id}` → receipt detail