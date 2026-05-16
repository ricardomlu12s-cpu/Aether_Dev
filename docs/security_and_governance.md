# Security And Governance

MVP security is local developer security, not enterprise multi-tenant security.

Current behavior:

- `/developer/*`, `/plugins/*`, and `POST /memory/write` require admin token.
- Sensitive operations are recorded in `audit_logs`.
- Runtime changes are recorded in `runtime_events`.

Future upgrades:

- RBAC
- OAuth2/JWT
- macOS Keychain encryption key storage
- database encryption
- backup/restore
- right-to-delete tools
- OpenTelemetry
- Prometheus/Grafana

