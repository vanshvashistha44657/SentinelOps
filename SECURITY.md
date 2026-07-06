# Security Policy & Guidelines

## Security Objectives

As a Security Operations Center (SOC) platform, SentinelOps must maintain the highest standards of security. Trust and integrity are paramount.

---

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

---

## Security Engineering Standards

### 1. Cryptography & Password Hashing
- **Argon2id**: All passwords must be hashed using `argon2id` (via `argon2-cffi`). Plaintext passwords must never touch the database or log files.
- **JWT (JSON Web Tokens)**: Signed using `HS256` (symmetric) or `RS256` (asymmetric, preferred for enterprise).
- **Access Token Expiry**: 15 minutes.
- **Refresh Token Expiry**: 7 days. Stored securely in database and rotated upon use (Refresh Token Rotation).

### 2. Authorization (RBAC)
- **Role-Based Access Control (RBAC)**: Supported roles include:
  - `Administrator`
  - `SOC_Manager`
  - `SOC_Analyst_L2`
  - `SOC_Analyst_L1`
  - `Threat_Hunter`
  - `Read_Only_Auditor`
- **Granular Permissions**: Roles map to permissions (e.g. `alerts:write`, `incidents:resolve`). Controllers/Routers must explicitly enforce permissions using dependencies.

### 3. Auditing & Logging
- **Audit Logs**: All user actions (logins, changing alert status, assigning cases, rule modifications) must generate an audit log entry in the database.
- **Secure Logging**: Personally Identifiable Information (PII), raw passwords, and JWT tokens must be masked in application stdout logs.

---

## Reporting a Vulnerability

We accept security bug reports via a secure reporting process. Please do **NOT** open a public GitHub issue for security vulnerabilities.

Email your report to: `security@sentinelsops.internal`

Please include:
- A description of the vulnerability.
- Steps to reproduce (or a proof-of-concept script).
- Potential impact.
