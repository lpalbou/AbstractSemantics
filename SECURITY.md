# Security Policy

Thanks for helping keep `abstractsemantics` and its users safe.

## Scope

This policy covers vulnerabilities in:

- the Python package code under `src/abstractsemantics/`
- the packaged default registry file `src/abstractsemantics/semantics.yaml`

Downstream systems that *consume* this package (runtimes, UIs, ingestion pipelines) should follow their own security policies as well.

## Reporting a vulnerability

Please report security issues **privately** and responsibly:

1. **Do not** open a public GitHub issue with exploit details.
2. If this repository is hosted on GitHub and supports it, use **Security → Report a vulnerability** (preferred).
3. If private reporting is not available, open a minimal public issue that requests a private contact channel (do not include sensitive details).

## What to include

- A clear description of the issue and potential impact
- Steps to reproduce (prefer a minimal proof-of-concept)
- Affected versions/commits if known
- Any suggested fix or mitigation (optional)

## Response expectations

We’ll acknowledge a report as soon as possible and work with you on a fix and coordinated disclosure when appropriate.

## Supported versions

Security fixes are provided for the latest released version in the `0.x` series.
