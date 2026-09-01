# Error Behavior

Use this reference when debugging Pyserini REST API client behavior, validating error handling, or explaining observed non-`200` responses.

Verified responses:

- Missing `query`:

```json
{"error":"Parameter 'query' is required"}
```

- `hits=0`:

```json
{"error":"Parameter 'hits' must be positive"}
```

- `hits=abc`:

```json
{"error":"Parameter 'hits' must be an integer"}
```

- `parse=maybe`:

```json
{"error":"Parameter 'parse' must be 'true' or 'false'"}
```

- Invalid index:

```json
{"error":"Unable to open index: no-such-index"}
```

- Missing document:

```json
{"error":"Document not found: no-such-docid"}
```

- Non-`GET` request:

```json
{"error":"Only GET is supported"}
```

Status codes observed:

- `400` for invalid parameters and invalid index
- `404` for missing document
- `405` for unsupported method
- `429` when either the observed client IP or normalized email is inside the token-delivery cooldown
- `503` when token issuance is disabled, inventory is unavailable, persistence fails, or email
  delivery fails

Successful `POST /v1/token` requests return `202` with a generic delivery-status body. The response
never contains the token. A later eligible request for an existing normalized email resends that
email's lifetime token instead of returning `409` or allocating a second token.
