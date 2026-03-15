# AGENTS.md - AI Software Architect Framework

<!--
TEMPLATE USAGE NOTES:
- Replace [PROJECT_NAME] with your project name
- Replace [PROJECT_TECH_STACK] with your technologies
- Replace [PROJECT_BUILD_COMMANDS] with your build process
- Replace [PROJECT_TEST_COMMANDS] with your test commands
- Replace [PROJECT_CONVENTIONS] with your code conventions
- Replace [FRAMEWORK_VERSION] with current framework version
- Replace [LAST_UPDATED] with current date

INSTRUCTION CAPACITY GUIDANCE (ADR-005):
- Keep this file < 500 lines, target ~400 lines
- Estimated instruction count: aim for < 150 instructions
- Detailed procedures belong in .architecture/agent_docs/ (created during setup)
- Use pointers to .architecture/agent_docs/ for task-specific guidance
- Only include always-relevant content here
-->

> **For [AI Assistant] Users**: This file contains cross-platform instructions for the AI Software Architect framework. For assistant-specific features and detailed procedures, see [.architecture/agent_docs/README.md](.architecture/agent_docs/README.md).

## Project Overview

[PROJECT_NAME] uses the AI Software Architect framework to implement rigorous software architecture practices with AI assistant collaboration.

**Technology Stack**: [PROJECT_TECH_STACK]

The framework provides:
- **Architecture Documentation**: Centralized repository of architectural decisions and reviews
- **Multi-Perspective Reviews**: Specialized reviewers from different architectural domains
- **Decision Records (ADRs)**: Structured documentation of architectural decisions
- **Recalibration Process**: Translating architectural reviews into implementation plans
- **Pragmatic Mode**: Optional YAGNI enforcement to prevent over-engineering
- **Progressive Disclosure**: Detailed procedures in `.architecture/agent_docs/` directory

## Framework Setup

### Directory Structure

```
.architecture/
├── members.yml              # Architecture review team members
├── principles.md            # Core architectural principles
├── config.yml               # Framework configuration (including pragmatic mode)
├── decisions/               # Architectural Decision Records (ADRs)
│   └── adrs/               # Numbered ADR documents
├── reviews/                 # Architecture review documents
├── recalibration/          # Implementation planning documents
└── templates/              # Templates for ADRs, reviews, etc.

.architecture/agent_docs/                  # Detailed AI assistant procedures
├── README.md               # Navigation guide
├── workflows.md            # Step-by-step procedures
└── reference.md            # Advanced topics and troubleshooting
```

**👉 For detailed setup procedures, see [.architecture/agent_docs/workflows.md § Setup Procedures](.architecture/agent_docs/workflows.md#setup-procedures)**

## Core Workflows

**👉 For detailed workflow procedures, see [.architecture/agent_docs/workflows.md](.architecture/agent_docs/workflows.md)**

### Requesting Architecture Reviews

Architecture reviews provide multi-perspective analysis of architectural decisions.

**Command patterns:**
- "Start architecture review for version X.Y.Z"
- "Start architecture review for [feature name]"
- "Ask [Specialist] to review [component]"

Review documents created in `.architecture/reviews/`.

**See**: [.architecture/agent_docs/workflows.md § Architecture Review Workflows](.architecture/agent_docs/workflows.md#architecture-review-workflows)

### Creating Architectural Decision Records (ADRs)

ADRs document significant architectural decisions.

**Command patterns:**
- "Create ADR for [topic]"
- "Document architectural decision for [topic]"

ADRs stored in `.architecture/decisions/adrs/` with sequential numbering.

**See**: [.architecture/agent_docs/workflows.md § ADR Creation Workflow](.architecture/agent_docs/workflows.md#adr-creation-workflow)

### Enabling Pragmatic Mode

Pragmatic mode adds YAGNI enforcement to prevent over-engineering.

**Command patterns:**

- "Enable pragmatic mode"
- "Turn on YAGNI enforcement"

Configuration in `.architecture/config.yml` with three intensity modes: Strict, Balanced, Lenient.

**See**: [.architecture/agent_docs/reference.md § Pragmatic Guard Mode](.architecture/agent_docs/reference.md#pragmatic-guard-mode)

### Architectural Recalibration

Translate architecture review findings into actionable implementation plans.

**Command patterns:**
- "Start architecture recalibration for version X.Y.Z"
- "Recalibrate architecture for [feature name]"

Recalibration documents stored in `.architecture/recalibration/`.

**See**: [.architecture/agent_docs/reference.md § Architecture Recalibration](.architecture/agent_docs/reference.md#architecture-recalibration)

## Architecture Principles

This project follows architectural principles defined in `.architecture/principles.md`. Key principles include:

- **Livable Code**: Design for developers who inhabit the codebase
- **Clarity over Cleverness**: Prefer simple, clear designs
- **Separation of Concerns**: Clear boundaries and single responsibilities
- **Evolvability**: Facilitate change without complete rewrites
- **Observability**: System provides insights into behavior and state
- **Security by Design**: Security integral to architecture, not afterthought
- **Domain-Centric Design**: Reflect and serve the problem domain
- **Pragmatic Simplicity**: Value working solutions over theoretical perfection

For detailed explanations and application guidelines, see `.architecture/principles.md`.

## Build & Test (Framework Development)

If working on the AI Software Architect framework itself:

### Testing Framework Components

```bash
# Verify directory structure
ls -la .architecture/

# Check configuration
cat .architecture/config.yml

# List architecture members
cat .architecture/members.yml

# View templates
ls .architecture/templates/
```

### Validating ADRs and Reviews

- ADRs should follow template at `.architecture/templates/adr-template.md`
- Reviews should follow template at `.architecture/templates/review-template.md`
- Recalibration should follow template at `.architecture/templates/recalibration_plan.md`

## Project-Specific Information

[PROJECT_TECH_STACK]

[PROJECT_BUILD_COMMANDS]

[PROJECT_TEST_COMMANDS]

[PROJECT_CONVENTIONS]

## Assistant-Specific Features

The AI Software Architect framework provides enhanced capabilities for specific AI coding assistants:

### Claude Code

Claude Code users have access to enhanced features including:

- **Claude Skills**: Reusable skills for setup, reviews, ADR creation, and status checks
- **MCP Server Integration**: Tools for architecture operations via Model Context Protocol
- **Slash Commands**: Custom commands for framework operations
- **Enhanced Setup**: Intelligent project analysis and template customization

**See [CLAUDE.md](../CLAUDE.md) for complete Claude Code documentation.**

### Cursor

Cursor users can configure the framework via:

- **Configuration**: See `.coding-assistants/cursor/README.md`
- **Rules**: Custom rules for architecture operations
- **Integration**: Tab completion and inline suggestions

**See [.coding-assistants/cursor/README.md](../.coding-assistants/cursor/README.md) for details.**

### GitHub Copilot / Codex

Copilot users can access framework features via:

- **Configuration**: See `.coding-assistants/codex/README.md`
- **Comments**: Use comments to trigger architecture operations
- **Integration**: Inline suggestions for ADRs and reviews

**See [.coding-assistants/codex/README.md](../.coding-assistants/codex/README.md) for details.**

### Other AI Assistants

The framework works with any AI assistant that can read markdown files and follow structured instructions. Key entry points:

- **This file (AGENTS.md)**: Cross-platform instructions
- **.architecture/**: All framework artifacts and templates
- **principles.md**: Architectural principles to apply
- **members.yml**: Available architecture reviewers
- **templates/**: Templates for ADRs, reviews, and recalibration

## Additional Resources

### Detailed Documentation
- **Workflow Procedures**: `.architecture/agent_docs/workflows.md`
- **Advanced Topics**: `.architecture/agent_docs/reference.md`
- **Documentation Guide**: `.architecture/agent_docs/README.md`

### Framework Files
- **Framework Principles**: `.architecture/principles.md`
- **Architecture Members**: `.architecture/members.yml`
- **Configuration**: `.architecture/config.yml`

### Templates & Examples
- **ADR Template**: `.architecture/templates/adr-template.md`
- **Review Template**: `.architecture/templates/review-template.md`
- **Recalibration Template**: `.architecture/templates/recalibration_plan.md`
- **Example ADRs**: `.architecture/decisions/adrs/`
- **Example Reviews**: `.architecture/reviews/`

---

**Framework Version**: [FRAMEWORK_VERSION]
**Documentation Version**: 2.0.0 (Progressive Disclosure - ADR-006)
**Last Updated**: [LAST_UPDATED]
**Maintained By**: AI Software Architect Framework

<!--
REMINDER FOR AI ASSISTANTS:
During setup, ensure .architecture/agent_docs/ directory is created with:
- workflows.md (setup, reviews, ADRs, implementation procedures)
- reference.md (pragmatic mode, recalibration, troubleshooting)
- README.md (navigation guide)

See ADR-005 and ADR-006 for progressive disclosure pattern rationale.
-->
