# Release Management

This document explains how to create new releases of CargoShipper MCP.

## Automated PyPI Publishing

The project uses GitHub Actions to automatically publish to PyPI when changes are pushed to the `main` branch.

### How it works:

1. **Every push to `main`** triggers the CI/CD pipeline
2. **Tests run** on Python 3.11 and 3.12
3. **Version check** - compares current version in `pyproject.toml` with PyPI
4. **Automatic publish** - if version is new, publishes to PyPI
5. **Skip if exists** - if version already exists, skips publishing

## Creating a New Release

### 1. Update Version Number

Edit `pyproject.toml`:
```toml
[project]
name = "cargoshipper-mcp"
version = "1.0.1"  # <- Update this
```

### 2. Update Changelog (Optional)

Add release notes to README or create CHANGELOG.md

### 3. Commit and Push

```bash
git add pyproject.toml
git commit -m "🔖 Bump version to 1.0.1

- Add new feature X
- Fix bug Y  
- Improve Z"
git push origin main
```

### 4. Automatic Publishing

GitHub Actions will:
- ✅ Run tests
- ✅ Build package  
- ✅ Check if version 1.0.1 exists on PyPI
- 🚀 Publish to PyPI (if new version)
- 🎉 Available via `uvx cargoshipper-mcp`

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **Major** (1.0.0 → 2.0.0): Breaking changes
- **Minor** (1.0.0 → 1.1.0): New features, backwards compatible
- **Patch** (1.0.0 → 1.0.1): Bug fixes, backwards compatible

## Emergency Releases

For critical fixes:
1. Update version in `pyproject.toml`  
2. Push directly to main
3. GitHub Actions handles the rest

## Monitoring Releases

- **GitHub Actions**: https://github.com/scarr7981/cargoshipper-mcp/actions
- **PyPI Releases**: https://pypi.org/project/cargoshipper-mcp/#history
- **Download Stats**: PyPI provides download statistics

## Rollback

If a release has issues:
1. Create hotfix with incremented patch version
2. Push to main - new version will be published
3. PyPI doesn't allow deleting published versions (by design)

## Security

- PyPI API token is stored as GitHub secret `PYPI_API_TOKEN`
- Token has limited scope to this package only
- Rotate token periodically for security