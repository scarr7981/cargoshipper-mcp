# CargoShipper MCP Server

**IMPORTANT**: When restarting or reconnecting, always read `RESTART.md` first for current status and context.

## Project Overview

CargoShipper is an MCP (Model Context Protocol) server designed to extend Claude's capabilities by providing direct interfaces to:

- **Docker**: Complete container and image management operations
- **Digital Ocean API**: Droplet, networking, and infrastructure management  
- **CloudFlare API**: DNS, security, and CDN configuration

This MCP server acts as a unified gateway, eliminating the need for Claude to handle complex API negotiations and providing straightforward, reproducible interactions with these critical infrastructure technologies.

## ⚠️ **IMPORTANT SAFETY WARNING**

**USE AT YOUR OWN RISK**: This tool gives AI models direct access to infrastructure management APIs that can:
- Create, modify, or delete cloud resources (potentially incurring costs)
- Modify DNS settings (potentially breaking domains)  
- Manage Docker containers and images (potentially affecting running services)
- Execute destructive operations on your infrastructure

**AI models may:**
- Misinterpret instructions and perform unintended operations
- Make mistakes in resource configuration or deletion
- Execute multiple operations when only one was intended
- Struggle with complex multi-step procedures requiring human judgment

**Recommended safety measures:**
- Use dedicated development/testing accounts with spending limits
- Implement least-privilege API tokens with restricted permissions
- Monitor all operations through cloud provider dashboards
- Test operations in isolated environments first
- Keep backups of critical configurations and data

## 🤖 **VIBECODE FRIENDLY PROJECT**

This project welcomes contributions from AI/LLM agents! **Pull requests from Claude, GPT, and other AI models are actively encouraged.**

**Guidelines for AI contributors:**
- Follow the existing code patterns and documentation standards
- Include comprehensive commit messages explaining changes
- Test your changes thoroughly before submitting PRs
- Use the MCP tools available in this environment for development and testing
- Refer to existing code style and architectural decisions
- Update documentation when adding new features

**For AI agents working on this project:**
- Use the Memory MCP server to track your development decisions
- Use the Git MCP server for proper version control workflow  
- Use Sequential-thinking MCP for complex architectural planning
- Test integrations using the Playwright MCP server when applicable

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
# 1. Create release branch: git checkout -b release/vX.X.X
# 2. Update version in pyproject.toml  
# 3. Create PR, merge after tests pass
# 4. Create release: git tag -a vX.X.X -m "Release vX.X.X" && git push origin vX.X.X

# Git workflow (via MCP)
mcp__git__git_status         # Check repository status
mcp__git__git_add           # Stage changes
mcp__git__git_commit        # Create commits

# Git branch management workflow
# When working on fixes or features:
git stash push -m "WIP: Description of changes"  # Stash current work
git checkout -b fix/branch-name main             # Create feature/fix branch
git stash pop                                    # Apply stashed changes
# ... work on changes ...
git add . && git commit -m "Fix: description"    # Commit changes
git push -u origin fix/branch-name               # Push branch and create PR

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

### 🔐 **Docker Registry Authentication**

CargoShipper supports multiple Docker registry authentication methods for improved `docker_pull_image` reliability:

#### **Environment Variables (Recommended for Linux/Production)**:
```bash
export DOCKER_REGISTRY_USERNAME="your-username"
export DOCKER_REGISTRY_PASSWORD="your-password"  
export DOCKER_REGISTRY_SERVER="https://index.docker.io/v1/"  # Optional, defaults to Docker Hub
export DOCKER_CONFIG_PATH="/custom/path/.docker/config.json"  # Optional custom config path
```

#### **Docker Config Integration**:
- Automatically reads from `~/.docker/config.json`
- Supports base64 encoded `auth` entries
- Supports separate `username`/`password` entries
- Works with credential helpers (basic support)

#### **Usage Examples**:
```python
# Use authentication (default)
docker_pull_image(image="nginx:latest")

# Specify custom registry
docker_pull_image(image="myregistry.com/nginx:latest", registry="https://myregistry.com")

# Skip authentication if needed
docker_pull_image(image="nginx:latest", use_auth=False)
```

#### **Authentication Priority**:
1. **Environment Variables** (highest priority)
2. **Docker Config File** (`~/.docker/config.json`)  
3. **Credential Helpers** (basic support)
4. **No Authentication** (fallback)

#### **Error Handling**:
- Provides specific guidance for authentication failures
- Indicates whether auth was attempted/used
- Suggests environment variable configuration
- Reports auth availability status

## Integration Notes

This CargoShipper MCP server integrates with the existing MCP ecosystem by:
- Leveraging Memory for persistent state management
- Using Git for version control of configurations and code
- Using Playwright for testing deployed infrastructure
- Using Sequential-thinking for complex deployment decision-making

The goal is to create a seamless experience where Claude can manage infrastructure across Docker, Digital Ocean, and CloudFlare with the same ease as working with local files.

## Release Management & PyPI Publishing

### 🚀 **Tag-Based Release Pipeline**

CargoShipper uses GitHub Actions with a **tag-based release strategy**:
- **Pull Requests**: Run tests to ensure code quality
- **Main branch**: Run tests only (no publishing)  
- **Tagged releases**: Automatically publish to PyPI

#### **How it Works**:
1. **PRs & Main**: Python 3.11 & 3.12 compatibility testing
2. **Tagged Releases**: Testing + version validation + PyPI publishing
3. **Version Validation**: Ensures tag matches `pyproject.toml`
4. **Global Distribution**: Immediately available via `uvx cargoshipper-mcp`

#### **Release Process**:

**Step 1: Update Version & Create PR**
```bash
git checkout -b release/v1.0.1
# Edit pyproject.toml version = "1.0.1"
git add pyproject.toml
git commit -m "🔖 Prepare release v1.0.1"
git push origin release/v1.0.1
# Create PR, ensure tests pass, merge
```

**Step 2: Create Tagged Release**
```bash
git checkout main && git pull
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1
```

**Or use GitHub UI:**
- Go to Releases → Create new release
- Tag: `v1.0.1`, Title: `Release v1.0.1`
- Add release notes → Publish

**Step 3: Automatic Publication** ✨
- GitHub Actions runs tests
- Validates tag matches `pyproject.toml` version
- Publishes to PyPI automatically
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
2. **Pull Requests**: Create PRs for all changes, ensure tests pass
3. **Releases**: 
   - Create release branch (`release/vX.X.X`)
   - Update version in `pyproject.toml`
   - Create PR, merge after tests pass
   - Create tagged release (`git tag vX.X.X`)
4. **Automation**: GitHub Actions handles testing (PRs/main) and publication (tags)
5. **Verify**: Check PyPI and test global installation after release
