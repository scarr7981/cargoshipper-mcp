# Release Management

This document explains how to create new releases of CargoShipper MCP.

## Release Strategy

The project uses a **tag-based release strategy**:
- **Pull Requests**: Run tests to ensure code quality
- **Main branch pushes**: Run tests only (no publishing)
- **Tagged releases**: Publish to PyPI automatically

### How it works:

1. **PRs and main pushes** trigger testing on Python 3.11 and 3.12
2. **Tagged releases** trigger testing + PyPI publishing
3. **Version validation** - ensures tag matches `pyproject.toml` version
4. **Automatic publish** - publishes to PyPI on successful release

## Creating a New Release

### 1. Update Version Number

Edit `pyproject.toml`:
```toml
[project]
name = "cargoshipper-mcp"
version = "1.0.1"  # <- Update this
```

### 2. Create Pull Request

```bash
git checkout -b release/v1.0.1
git add pyproject.toml
git commit -m "🔖 Prepare release v1.0.1

- Add new feature X
- Fix bug Y  
- Improve Z"
git push origin release/v1.0.1
```

Create PR and ensure tests pass.

### 3. Merge to Main

Once PR is approved and tests pass, merge to main.

### 4. Create Tagged Release

```bash
git checkout main
git pull origin main
git tag -a v1.0.1 -m "Release v1.0.1

- Add new feature X
- Fix bug Y
- Improve Z"
git push origin v1.0.1
```

**Or use GitHub UI:**
1. Go to https://github.com/scarr7981/cargoshipper-mcp/releases
2. Click "Create a new release"
3. Tag: `v1.0.1`
4. Title: `Release v1.0.1`
5. Description: Release notes
6. Click "Publish release"

### 5. Automatic Publishing

GitHub Actions will:
- ✅ Run tests on Python 3.11 and 3.12
- ✅ Build package
- ✅ Verify tag version matches `pyproject.toml`
- 🚀 Publish to PyPI
- 🎉 Available globally via `uvx cargoshipper-mcp`

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