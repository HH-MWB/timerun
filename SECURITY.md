# Security Policy

## Supported Versions

We provide security updates exclusively for the latest release on PyPI. Please ensure you are running the latest version of `timerun` before reporting an issue.

## Reporting a Vulnerability

If you discover a security vulnerability, please **do not** open a public issue. Submit a private report via [GitHub Security Advisory](https://github.com/HH-MWB/timerun/security/advisories/new).

Please include:

- A description of the vulnerability and its potential impact.
- Reproducible steps or a minimal proof of concept (PoC).
- Any proposed fix or mitigation (if available).

## Response & Coordinated Disclosure

- **Acknowledgement**: We will acknowledge receipt within **48 hours**.
- **Assessment**: We will evaluate severity and provide an update within **7 days**.
- **Resolution**: Once a fix is verified, we will release a patch and publish a GitHub Security Advisory crediting you (unless you prefer to remain anonymous).

## Supply Chain Security & Provenance

- **Trusted Publishing (OIDC)**: PyPI and TestPyPI distributions are published strictly via GitHub Actions using OpenID Connect (OIDC). No static API tokens or passwords are stored in the repository.
- **Digital Attestations (PEP 740)**: PyPI releases include cryptographically signed build provenance, verifying that artifacts originate from this repository and workflow run.
- **Zero Runtime Dependencies**: `timerun` relies solely on the Python standard library, eliminating third-party runtime supply chain risks.
