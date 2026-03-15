# AI Software Architect Setup for GitHub Copilot/Codex

This document provides setup instructions for configuring the AI Software Architect framework with GitHub Copilot and OpenAI Codex.

## Setup Recognition

GitHub Copilot/Codex should recognize these setup requests and follow the setup process:

- "Setup architecture using: https://github.com/codenamev/ai-software-architect"
- "Setup ai-software-architect"
- "Setup architecture" 
- "Setup software architect"
- "Setup architect"
- "Customize software architect"

## 6-Step Setup Process

When a user requests setup using any of the recognized phrases, follow this 6-step setup process:

### 1. Detect Setup Context
- Check if `.architecture/` directory exists with framework files
- Verify running from user's project root (not within .architecture)
- Confirm the framework is properly cloned

### 2. Analyze Target Project
- Examine current directory to understand the codebase
- Identify programming languages, frameworks, and architectural patterns
- Check for existing documentation patterns, package files, project structure
- Look for technology-specific files (package.json, requirements.txt, etc.)

### 3. Framework Installation
- Move framework from `.architecture/.architecture/` to `.architecture/`
- Create `.coding-assistants/` directory structure in project root
- Set up initial directory structure for decisions, reviews, recalibration

### 4. Customization for Project
- Update `.architecture/members.yml` with roles relevant to their technology stack
- Modify `.architecture/principles.md` to align with project's architectural needs
- Customize templates in `.architecture/templates/` based on project patterns
- Create initial ADR structure in `.architecture/decisions/adrs/`

### 5. Cleanup & Finalize
- Create a timestamped backup directory: `mkdir -p ~/.ai-architect-backups/setup-$(date +%Y%m%d-%H%M%S)`
- Move (don't delete) template repository files to backup:
  - `mv README.md USAGE*.md INSTALL.md ~/.ai-architect-backups/setup-$(date +%Y%m%d-%H%M%S)/` (if they exist)
- **Move .architecture/.git/ to backup** (NEVER touch project root .git):
  - Verify target exists: `[ -d .architecture/.git ]`
  - Move to backup: `mv .architecture/.git ~/.ai-architect-backups/setup-$(date +%Y%m%d-%H%M%S)/architecture-git`
  - Verify project .git remains intact: `[ -d .git ]`
- Move the now-empty cloned repository structure to backup (if it exists)
- Verify all framework files are properly located
- Inform user: "Backup created at ~/.ai-architect-backups/setup-TIMESTAMP/. You can safely remove this backup directory once you've verified everything works correctly."

### 6. Guide Next Steps
- Explain what customizations you've made and why
- Show them how to use the framework with their specific project
- Suggest immediate next steps for architectural documentation
- Provide examples relevant to their tech stack

## Configuration Files

When setting up, ensure these files are properly configured:

- `.coding-assistants/codex/` - Codex configuration files
- `.architecture/members.yml` - Customize for project's needs
- `.architecture/principles.md` - Align with project architecture

## Natural Language Commands

After setup, GitHub Copilot/Codex should recognize these natural language patterns:

### Architecture Reviews
- "Review this architecture"
- "Start architecture review for version X.Y.Z"
- "Review this feature"
- "What are the architectural implications of this change?"

### Specialized Reviews
- "Review this for security issues"
- "Analyze this database schema for performance"
- "Check this code for maintainability problems"
- "What are the scalability concerns here?"

### ADR Creation
- "Create an ADR for our database choice"
- "Document this architectural decision"
- "Help me write an ADR for microservices"

### Code Generation & Analysis
- "Generate code following our architecture patterns"
- "Refactor this to match our ADRs"
- "Does this code follow our architectural principles?"

### Implementation Commands
- "Implement [feature] as the architects"
- "Implement as the architects" (when feature context is clear)
- "Implement this" (with prior architectural discussion)

## Implementation Guidance Configuration

The framework supports configuration-driven implementation that applies your preferred methodology, influences, and practices automatically when you use implementation commands.

### Configuration Location

Configure implementation guidance in `.architecture/config.yml`:

```yaml
implementation:
  enabled: true
  methodology: "TDD"  # TDD, BDD, DDD, Test-Last, Exploratory

  influences:
    - "Kent Beck - TDD by Example"
    - "Sandi Metz - POODR, 99 Bottles"
    - "Martin Fowler - Refactoring"

  languages:
    javascript:
      style_guide: "ESLint with Airbnb config"
      idioms: "Prefer const, use arrow functions, destructure"
      frameworks:
        react: "Functional components, hooks"
        vue: "Composition API"

  testing:
    framework: "Jest"
    style: "Outside-in TDD"
    approach: "Mock judiciously, prefer real objects"

  quality:
    definition_of_done:
      - "Tests passing"
      - "Code refactored"
      - "Code reviewed"
```

### How It Works

When you use implementation commands like "Implement user authentication as the architects":

1. GitHub Copilot reads `.architecture/config.yml`
2. Extracts your configured methodology (TDD, BDD, etc.)
3. References your influences (Kent Beck, Sandi Metz, etc.)
4. Applies language-specific practices and idioms
5. Follows your testing approach and quality standards
6. Implements with full context automatically

### Common Configuration Examples

**JavaScript BDD with Functional Style:**
```yaml
implementation:
  methodology: "BDD"
  influences:
    - "Dan North - BDD originator"
    - "Kent C. Dodds - Testing Library"
    - "Eric Elliott - Composing Software"
  languages:
    javascript:
      style_guide: "ESLint (Airbnb)"
      idioms: "Functional, immutable, declarative"
```

**Python with Pragmatic Testing:**
```yaml
implementation:
  methodology: "Test-Last"
  influences:
    - "Brett Slatkin - Effective Python"
    - "Luciano Ramalho - Fluent Python"
  languages:
    python:
      style_guide: "Black + PEP 8"
      idioms: "Pythonic patterns, comprehensions"
```

### Benefits

- **90% reduction in prompt length**: Say "Implement X as the architects" instead of repeating methodology and influences
- **Consistency**: Same approach applied across all implementations
- **Team standards**: Configuration is version-controlled and shared
- **Quality**: Best practices applied systematically

### Security Practices

Security practices configured in the `implementation.security` section are always applied, even with pragmatic mode enabled:

```yaml
implementation:
  security:
    mandatory_practices:
      - "Input validation (whitelist approach)"
      - "Output encoding (context-aware)"
      - "Parameterized queries (no string concatenation)"
```

For complete configuration options, see `.architecture/templates/config.yml`.

## Context Integration

The framework ensures GitHub Copilot/Codex understands project context by:

- Referencing existing ADRs in suggestions
- Following established coding patterns
- Maintaining consistency with architectural decisions
- Providing architecture-aware code completions