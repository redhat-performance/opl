# agent_docs/ - Detailed Framework Guidance

Welcome to the AI Software Architect framework's detailed documentation for AI assistants.

## What's Here

This directory contains in-depth, step-by-step procedures and advanced topics for the AI Software Architect framework, following a **progressive disclosure pattern** to respect LLM instruction capacity constraints.

**Documents:**
- **[workflows.md](workflows.md)** - Step-by-step procedures for common tasks
- **[reference.md](reference.md)** - Advanced topics, pragmatic mode, troubleshooting

## Why This Structure?

Based on research (see [ADR-005](../decisions/adrs/ADR-005-llm-instruction-capacity-constraints.md)), LLMs have limited instruction-following capacity (~150-200 instructions). This structure:

1. **AGENTS.md**: Core concepts, always-relevant (~150 instructions)
2. **CLAUDE.md**: Claude Code-specific features (~14 instructions)
3. **agent_docs/**: Detailed task-specific procedures (loaded as needed)

This approach keeps the main documentation concise while providing deep details when required.

## Quick Navigation

### I Want To...

| Task | Document | Section |
|------|----------|---------|
| **Set up the framework** | [workflows.md](workflows.md) | [Setup Procedures](workflows.md#setup-procedures) |
| **Update the framework** | [workflows.md](workflows.md) | [Update Procedures](workflows.md#update-procedures) |
| **Request an architecture review** | [workflows.md](workflows.md) | [Architecture Review Workflows](workflows.md#architecture-review-workflows) |
| **Create an ADR** | [workflows.md](workflows.md) | [ADR Creation Workflow](workflows.md#adr-creation-workflow) |
| **Implement with methodology** | [workflows.md](workflows.md) | [Implementation with Methodology](workflows.md#implementation-with-methodology) |
| **Enable pragmatic mode** | [reference.md](reference.md) | [Pragmatic Guard Mode](reference.md#pragmatic-guard-mode) |
| **Understand recalibration** | [reference.md](reference.md) | [Architecture Recalibration](reference.md#architecture-recalibration) |
| **Configure the framework** | [reference.md](reference.md) | [Advanced Configuration](reference.md#advanced-configuration) |
| **Troubleshoot issues** | [reference.md](reference.md) | [Troubleshooting Guide](reference.md#troubleshooting-guide) |
| **Use with other assistants** | [reference.md](reference.md) | [Cross-Assistant Compatibility](reference.md#cross-assistant-compatibility) |

## New to the Framework?

**Start here:**

1. **Read**: [../../AGENTS.md](../../AGENTS.md) - Framework overview and core concepts
2. **Install**: [workflows.md § Setup Procedures](workflows.md#setup-procedures)
3. **Configure**: Set up [.architecture/config.yml](../config.yml)
4. **Explore**: Review [example ADRs](../decisions/adrs/) and [reviews](../reviews/)
5. **Practice**: Request your first architecture review

**Recommended Reading Order:**
1. Project overview → AGENTS.md
2. Installation → workflows.md § Setup
3. Core workflows → workflows.md § Review Workflows
4. Your first ADR → workflows.md § ADR Creation
5. Advanced features → reference.md

## Returning User?

**Quick lookup:**

- Need detailed steps? → [workflows.md](workflows.md)
- Need advanced config? → [reference.md](reference.md)
- Need framework overview? → [../../AGENTS.md](../../AGENTS.md)
- Need Claude-specific? → [../../CLAUDE.md](../../CLAUDE.md)

## Common Workflows

### Setup and Installation

**First time setup:**
```
Setup ai-software-architect
```

AI assistant will:
1. Analyze your project
2. Customize templates
3. Create directory structure
4. Conduct initial architectural analysis

**See**: [workflows.md § Setup Procedures](workflows.md#setup-procedures)

### Requesting Reviews

**Full architecture review:**
```
Start architecture review for version X.Y.Z
Start architecture review for [feature name]
```

**Specialist review:**
```
Ask [Specialist] to review [component]
```

**See**: [workflows.md § Architecture Review Workflows](workflows.md#architecture-review-workflows)

### Creating ADRs

**Document a decision:**
```
Create ADR for [topic]
```

**See**: [workflows.md § ADR Creation Workflow](workflows.md#adr-creation-workflow)

### Implementation with Methodology

**Apply configured methodology:**
```
Implement [feature] as the architects
```

**See**: [workflows.md § Implementation with Methodology](workflows.md#implementation-with-methodology)

### Enable Pragmatic Mode

**Turn on YAGNI enforcement:**
```
Enable pragmatic mode
```

**See**: [reference.md § Pragmatic Guard Mode](reference.md#pragmatic-guard-mode)

## Documentation Structure

```
├── AGENTS.md                    # Framework overview (cross-platform)
├── CLAUDE.md                    # Claude Code-specific features
├── agent_docs/                  # You are here
│   ├── README.md               # This navigation guide
│   ├── workflows.md            # Step-by-step procedures
│   └── reference.md            # Advanced topics and troubleshooting
└── .architecture/              # Framework files
    ├── decisions/adrs/         # Architectural Decision Records
    ├── reviews/                # Architecture reviews
    ├── recalibration/         # Recalibration plans
    ├── templates/             # Document templates
    ├── members.yml            # Architecture team members
    ├── principles.md          # Architectural principles
    └── config.yml             # Framework configuration
```

## Best Practices

**For AI Assistants:**
1. **Load progressively**: Start with AGENTS.md, reference agent_docs/ as needed
2. **Follow structure**: WHAT (AGENTS.md) → WHY (principles) → HOW (workflows)
3. **Check configuration**: Always read `.architecture/config.yml` for user preferences
4. **Reference appropriately**: Use file:line format for code references

**For Humans:**
1. **Start simple**: Don't try to read everything at once
2. **Task-oriented**: Look up what you need when you need it
3. **Keep updated**: Run framework updates periodically
4. **Customize**: Tailor `.architecture/config.yml` to your needs

## Getting Help

### Can't Find What You're Looking For?

**Check these resources:**
1. [workflows.md](workflows.md) - Step-by-step task procedures
2. [reference.md](reference.md) - Advanced topics and troubleshooting
3. [../../AGENTS.md](../../AGENTS.md) - Framework overview
4. [../principles.md](../principles.md) - Architectural guidance
5. [../config.yml](../config.yml) - Configuration options

### Still Need Help?

- **Repository**: https://github.com/codenamev/ai-software-architect
- **Issues**: https://github.com/codenamev/ai-software-architect/issues
- **Examples**: Check [../decisions/adrs/](../decisions/adrs/) for example ADRs
- **Examples**: Check [../reviews/](../reviews/) for example reviews

## Version Information

**Framework Version**: 1.2.0
**Documentation Version**: 2.0.0 (Progressive Disclosure)
**Last Updated**: 2025-12-04

**Changes in 2.0.0:**
- Adopted progressive disclosure pattern (ADR-006)
- Moved detailed procedures to agent_docs/
- Reduced CLAUDE.md from 572 to 126 lines
- Respects LLM instruction capacity constraints (ADR-005)
