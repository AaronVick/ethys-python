# Security Policy

## Supported Versions

We actively support the latest stable version of the SDK. Security updates are backported to the current stable release.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please email **security@ethys.dev** with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if available)

We will acknowledge receipt within 48 hours and provide a timeline for addressing the issue.

## Security Best Practices

When using this SDK:

1. **Never commit private keys** to version control
2. **Use environment variables** for sensitive configuration
3. **Rotate keys regularly** if compromised
4. **Use hardware wallets** for production agents when possible
5. **Keep dependencies updated** (`pip install --upgrade ethys402`)
6. **Review code changes** before deploying to production

## Disclosure Policy

- We will disclose vulnerabilities after they have been patched
- Credit will be given to reporters (if desired)
- CVEs will be assigned for significant vulnerabilities

