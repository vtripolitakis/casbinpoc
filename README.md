# Casbin Resolver API

## Run the app (development)

Activate the included virtualenv, install dependencies (optional) and run the FastAPI app with uvicorn:

```bash
# create a virtualenv if you don't have one
python3 -m venv casbinenv

# activate the virtualenv
source casbinenv/bin/activate
# install the dependencies
pip install -r requirements.txt

# Run the app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000.

## API endpoints

All requests use `application/json` where a body is present. Replace `localhost:8000` with your host/port if different.

### POST /enforce
Evaluate whether a subject is allowed to perform an action on an object in a resolved context.

Request JSON shape:
- context: { tenant?: string }
- sub: any
- obj: any
- act: any

Example:

```bash
curl -sS -X POST "http://localhost:8000/enforce" \
  -H "Content-Type: application/json" \
  -d '{
    "context": { "tenant": "tenant1" },
    "sub": "alice",
    "obj": "document:123",
    "act": "read"
  }'
```

Example response (200):

```json
{ "allowed": true }
```

Error responses:
- 404: resolver lookup failed (context/model not found)
- 500: internal server / enforce error

---

### POST /policies
Add a policy (subject, object, action) for the resolved context and persist it.

Request JSON shape:
- context: { tenant?: string }
- sub: string
- obj: string
- act: string

Example:

```bash
curl -sS -X POST "http://localhost:8000/policies" \
  -H "Content-Type: application/json" \
  -d '{
    "context": { "tenant": "tenant1" },
    "sub": "bob",
    "obj": "document:123",
    "act": "write"
  }'
```

Example response (200):

```json
{ "added": true }
```

---

### DELETE /policies
Remove a policy (subject, object, action) for the resolved context and persist it.

Request JSON shape: same as POST /policies

Example:

```bash
curl -sS -X DELETE "http://localhost:8000/policies" \
  -H "Content-Type: application/json" \
  -d '{
    "context": { "tenant": "tenant1" },
    "sub": "bob",
    "obj": "document:123",
    "act": "write"
  }'
```

Example response (200):

```json
{ "removed": true }
```

---

### GET /policies
Retrieve policies for a given tenant context.

Query parameters:
- tenant (optional)

Example (all policies for tenant1):

```bash
curl -sS "http://localhost:8000/policies?tenant=tenant1"
```

Example response (200):

```json
{ "policies": [ ["alice", "document:123", "read"], ["bob", "document:123", "write"] ] }
```

If no tenant is provided, the resolver will be called with an empty context (behavior depends on resolver configuration).

## Notes
- The API returns 404 when the `CasbinResolver` cannot resolve the requested context (missing model/policy mapping).
- The API returns 500 for unexpected errors and includes a short error message.
- Consider replacing raw dict responses with Pydantic response models to improve OpenAPI docs and strictness.
