# CargoShipper MCP Server

**IMPORTANT**: When restarting or reconnecting, always read `RESTART.md` first for current status and context.

## Project Overview

CargoShipper is an MCP (Model Context Protocol) server designed to extend Claude's capabilities by providing direct interfaces to:

- **Docker**: Complete container and image management operations
- **Digital Ocean API**: Droplet, networking, and infrastructure management  
- **CloudFlare API**: DNS, security, and CDN configuration

This MCP server acts as a unified gateway, eliminating the need for Claude to handle complex API negotiations and providing straightforward, reproducible interactions with these critical infrastructure technologies.

## Available MCP Servers

This development environment has access to the following MCP servers configured in `.mcp.json`:

### 1. Playwright MCP Server (`mcp__playwright__*`)
**Purpose**: Browser automation, web testing, and UI interaction

**Key Capabilities**:
- Navigate web pages and take screenshots
- Fill forms and interact with web elements
- Capture accessibility snapshots for testing
- Handle file uploads and downloads
- Execute JavaScript in browser context
- Manage browser tabs and handle dialogs

**Common Usage Patterns**:
```python
# Navigate and take screenshot
mcp__playwright__browser_navigate(url="https://example.com")
mcp__playwright__browser_take_screenshot(filename="page.png")

# Interact with web elements
mcp__playwright__browser_click(element="Submit button", ref="button-123")
mcp__playwright__browser_type(element="Email field", ref="email-input", text="user@example.com")

# Form automation
mcp__playwright__browser_fill_form(fields=[
    {"name": "username", "type": "textbox", "ref": "user-input", "value": "admin"},
    {"name": "remember", "type": "checkbox", "ref": "remember-me", "value": "true"}
])
```

**Best for**: Testing web interfaces, scraping dynamic content, automating web-based configuration tasks

### 2. Memory MCP Server (`mcp__memory__*`) 
**Purpose**: Persistent knowledge graph for session continuity and project memory

**Key Capabilities**:
- Create and manage entities with observations
- Establish relationships between entities
- Search across stored knowledge
- Maintain context across conversations
- Track project state and decisions

**Common Usage Patterns**:
```python
# Create project entities
mcp__memory__create_entities(entities=[
    {
        "name": "CargoShipper Server",
        "entityType": "MCP Server",
        "observations": ["Provides Docker, DO, and CloudFlare APIs", "Written in Python"]
    }
])

# Establish relationships
mcp__memory__create_relations(relations=[
    {"from": "CargoShipper Server", "to": "Docker API", "relationType": "integrates_with"}
])

# Search and retrieve
mcp__memory__search_nodes(query="Docker container management")
mcp__memory__open_nodes(names=["CargoShipper Server"])
```

**Best for**: Maintaining project context, tracking architectural decisions, documenting relationships between components

### 3. Git MCP Server (`mcp__git__*`)
**Purpose**: Version control operations and repository management

**Key Capabilities**:
- Check repository status and view diffs
- Stage files and create commits  
- Manage branches and view commit history
- Handle merges and repository initialization
- View specific commit details

**Common Usage Patterns**:
```python
# Check current state
mcp__git__git_status(repo_path="/path/to/repo")
mcp__git__git_diff_unstaged(repo_path="/path/to/repo")

# Stage and commit changes
mcp__git__git_add(repo_path="/path/to/repo", files=["src/main.py", "docs/README.md"])
mcp__git__git_commit(repo_path="/path/to/repo", message="Add Docker integration tools")

# Branch management
mcp__git__git_create_branch(repo_path="/path/to/repo", branch_name="feature/cloudflare-api")
mcp__git__git_checkout(repo_path="/path/to/repo", branch_name="main")
```

**Best for**: Managing code changes, tracking development progress, handling version control workflows

### 4. Sequential-thinking MCP Server (`mcp__sequential-thinking__*`)
**Purpose**: Enhanced reasoning capabilities for complex problem-solving

**Key Capabilities**:
- Multi-step analytical thinking process
- Hypothesis generation and verification  
- Revision and refinement of thoughts
- Branching logic for exploring alternatives
- Solution verification and validation

**Common Usage Patterns**:
```python
# Complex problem analysis
mcp__sequential-thinking__sequentialthinking(
    thought="Analyzing the requirements for Docker API integration",
    thoughtNumber=1,
    totalThoughts=5,
    nextThoughtNeeded=True
)

# Hypothesis testing
mcp__sequential-thinking__sequentialthinking(
    thought="Testing hypothesis: FastMCP provides better performance than raw JSON-RPC",
    thoughtNumber=3, 
    totalThoughts=5,
    isRevision=True,
    revisesThought=2,
    nextThoughtNeeded=True
)
```

**Best for**: Architectural planning, debugging complex issues, evaluating multiple implementation approaches

## MCP Server Integration Patterns

### Efficient Usage Guidelines

**1. Use Playwright for**:
- Testing web-based APIs (CloudFlare dashboard, DO control panel)
- Automating configuration workflows
- Validating deployed applications
- Capturing visual documentation

**2. Use Memory for**:
- Tracking API endpoints and their purposes
- Documenting configuration relationships  
- Maintaining deployment state information
- Recording architectural decisions and rationale

**3. Use Git for**:
- All code change management
- Branching for feature development
- Commit message consistency
- Release preparation and tagging

**4. Use Sequential-thinking for**:
- Complex API integration design
- Multi-step deployment planning
- Error diagnosis and resolution strategies
- Performance optimization analysis

### Development Workflow

#### Phase 1: Planning and Design
1. Use **Sequential-thinking** to analyze requirements and design approach
2. Use **Memory** to document entities, relationships, and decisions
3. Use **Git** to create feature branches and track progress

#### Phase 2: Implementation
1. Use **Git** for regular commits and branch management
2. Use **Memory** to track implementation notes and API discoveries
3. Use **Playwright** for testing web-based integrations
4. Use **Sequential-thinking** for debugging complex issues

#### Phase 3: Testing and Deployment
1. Use **Playwright** for end-to-end testing of web interfaces
2. Use **Git** for creating release branches and tags
3. Use **Memory** to document deployment procedures and configurations
4. Use **Sequential-thinking** to analyze deployment results and optimizations

## Project Structure

```
cargoshipper-mcp/
├── .github/workflows/       # GitHub Actions CI/CD
│   └── publish.yml          # Automated PyPI publishing
├── .gitignore               # Git ignore patterns
├── .mcp.dev.json           # Development MCP config
├── .mcp.uvx.json           # uvx MCP config example
├── CLAUDE.md               # This documentation
├── LICENSE                 # MIT License
├── README.md               # Project overview
├── RELEASING.md            # Release management guide
├── pyproject.toml          # Python project configuration
├── requirements.txt        # Python dependencies
├── test_server.py          # Test suite
├── cargoshipper_mcp/       # Main package
│   ├── __init__.py
│   ├── server.py           # MCP server entry point
│   ├── config/             # Configuration management
│   ├── tools/              # API operation tools
│   │   ├── docker.py       # Docker operations
│   │   ├── digitalocean.py # DigitalOcean operations
│   │   └── cloudflare.py   # CloudFlare operations
│   ├── resources/          # Read-only data access
│   └── utils/              # Shared utilities
├── docs/                   # Comprehensive documentation
│   ├── mcp-architecture.md
│   ├── docker-api-reference.md
│   ├── digitalocean-api-reference.md
│   ├── cloudflare-api-reference.md
│   ├── implementation-guide.md
│   └── tool-catalog.md
└── dist/                   # Built packages (gitignored)
```

## Development Commands

```bash
# Local development and testing
python test_server.py        # Run test suite
uvx --from . cargoshipper-mcp # Test local installation
python -m build             # Build package for distribution

# Package management
pip install -r requirements.txt  # Install dependencies
pip install -e .             # Install in development mode

# Release management
# 1. Update version in pyproject.toml
# 2. git add pyproject.toml && git commit -m "🔖 Bump to vX.X.X"
# 3. git push origin main     # Triggers automated PyPI publishing

# Git workflow (via MCP)
mcp__git__git_status         # Check repository status
mcp__git__git_add           # Stage changes
mcp__git__git_commit        # Create commits

# Memory management (via MCP)
mcp__memory__create_entities # Document new components
mcp__memory__search_nodes   # Find relevant information

# Testing (via MCP)
mcp__playwright__browser_navigate # Test web interfaces
mcp__playwright__browser_snapshot # Capture current state

# CI/CD monitoring
gh run list                  # Check GitHub Actions status
gh run view <run-id>         # View specific run details
```

## Security and Best Practices

- Store API credentials in environment variables only
- Use Memory MCP to track security decisions and patterns
- Use Git MCP for secure commit practices
- Use Playwright MCP for testing security configurations
- Use Sequential-thinking MCP for security analysis and threat modeling

## Integration Notes

This CargoShipper MCP server integrates with the existing MCP ecosystem by:
- Leveraging Memory for persistent state management
- Using Git for version control of configurations and code
- Using Playwright for testing deployed infrastructure
- Using Sequential-thinking for complex deployment decision-making

The goal is to create a seamless experience where Claude can manage infrastructure across Docker, Digital Ocean, and CloudFlare with the same ease as working with local files.

## Release Management & PyPI Publishing

### 🚀 **Automated Release Pipeline**

CargoShipper uses GitHub Actions for fully automated PyPI publishing. The pipeline is triggered on every push to the `main` branch.

#### **How it Works**:
1. **Tests Run**: Python 3.11 & 3.12 compatibility testing
2. **Version Check**: Compares `pyproject.toml` version against PyPI
3. **Smart Publishing**: Only publishes if version is new
4. **Global Distribution**: Immediately available via `uvx cargoshipper-mcp`

#### **Release Process**:

**Step 1: Update Version**
```toml
# Edit pyproject.toml
[project]
version = "1.0.1"  # <- Change this number
```

**Step 2: Commit & Push**
```bash
git add pyproject.toml
git commit -m "🔖 Bump to v1.0.1 - Add awesome feature"
git push origin main
```

**Step 3: Automatic Publication** ✨
- GitHub Actions runs tests
- Builds package
- Publishes to PyPI (if new version)
- Available globally: `uvx cargoshipper-mcp`

#### **Version Numbering**:
Follow [Semantic Versioning](https://semver.org/):
- **Major** (1.0.0 → 2.0.0): Breaking changes
- **Minor** (1.0.0 → 1.1.0): New features, backwards compatible  
- **Patch** (1.0.0 → 1.0.1): Bug fixes, backwards compatible

#### **Emergency Releases**:
For critical fixes:
1. Update version in `pyproject.toml`
2. Push directly to main
3. GitHub Actions handles publication automatically

#### **Configuration Files**:
- **CI/CD**: `.github/workflows/publish.yml`
- **Release Guide**: `RELEASING.md`
- **PyPI Token**: GitHub secret `PYPI_API_TOKEN`

#### **Monitoring**:
- **Actions**: https://github.com/scarr7981/cargoshipper-mcp/actions
- **PyPI**: https://pypi.org/project/cargoshipper-mcp/
- **Status**: Check latest run status before releasing

#### **Current Status**: ✅ **LIVE & AUTOMATED**
- Published on PyPI: https://pypi.org/project/cargoshipper-mcp/
- Global access: `uvx cargoshipper-mcp`
- Automated pipeline: Active and tested
- Next release: Just update version number and push!

### 🔄 **Standard Operating Procedure**

When working on CargoShipper:

1. **Development**: Make changes, use local testing via `uvx --from . cargoshipper-mcp`
2. **Testing**: Run `python test_server.py` locally
3. **Version**: Update version in `pyproject.toml` for releases
4. **Commit**: Use semantic commit messages
5. **Push**: GitHub Actions handles testing and publication
6. **Verify**: Check PyPI and test global installation
