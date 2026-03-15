# Troubleshooting & Advanced Usage

This document provides detailed guidance, error resolution, and advanced usage patterns for the AI Software Architect framework. For basic usage, see [README.md](README.md) and [USAGE.md](USAGE.md).

**Last Updated**: 2025-12-11

---

## Quick Links

- [How AI Assistants Use These Features](#how-ai-assistants-use-these-features)
- [Common Errors](#common-errors)
- [Configuration Maintenance](#configuration-maintenance)
- [Advanced Prompt Patterns](#advanced-prompt-patterns)
- [Getting Help](#getting-help)

---

## How AI Assistants Use These Features

*This section will be populated when triggered by user questions (5+ questions about AI behavior or capabilities).*

**Current Status**: Monitoring for user questions - none reported yet.

**What will be documented here**:
- How AI assistants parse and apply config.yml settings
- AI capabilities and limitations with pragmatic mode and implementation guidance
- Whether AI can create members.yml members dynamically
- Context loading behavior (when config is read, cached, reloaded)
- What happens when configuration is invalid or malformed

**Trigger**: 5+ user questions about AI assistant behavior with these features

**In the meantime**: Config.yml has extensive inline documentation explaining all settings. ADR-002 (Pragmatic Mode) and ADR-004 (Implementation Guidance) document feature design and behavior.

---

## Common Errors

*This section will be populated when triggered by user support requests (5+ requests about specific errors).*

**Current Status**: Monitoring for error reports - none reported yet.

**What will be documented here**:
- Config file missing or malformed - resolution steps
- Pragmatic mode enabled but pragmatic_enforcer not in members.yml - how to fix
- Invalid YAML syntax in config.yml - common mistakes and fixes
- Conflicting settings between features - how to resolve
- Missing required fields in configuration - what's required
- Invalid values for enum fields (intensity, methodology) - valid options

**Trigger**: 5+ user support requests about configuration errors

**In the meantime**:
- Config.yml template (`.architecture/templates/config.yml`) has extensive inline documentation
- YAML syntax errors are caught by parser with standard messages
- Members.yml includes pragmatic_enforcer by default in framework installation

---

## Configuration Maintenance

*This section will be populated when triggered by observed config staleness (3+ projects with stale configs) or user questions.*

**Current Status**: Monitoring - features recently launched, configs are fresh.

**What will be documented here**:
- When to review config.yml (quarterly reviews, when practices evolve, when team grows)
- How to update configurations as methodologies evolve
- Process for team consensus on configuration changes
- Detecting when configuration has become stale
- Migration strategies for config updates
- Real examples of config evolution from actual projects

**Trigger**: 3+ projects with stale configurations OR 6+ months since feature launch OR users ask "how often should we review config?"

**In the meantime**:
- Config.yml is version-controlled - changes are tracked via git
- Teams can update configs as needed without formal process
- Quarterly documentation review (per ADR-005) is good time to review configs

---

## Advanced Prompt Patterns

*This section will be populated when triggered by user questions (5+ questions about advanced usage patterns).*

**Current Status**: Monitoring for user questions - none reported yet.

**What will be documented here**:
- Member-specific implementations: "Implement as the pragmatic enforcer"
- "Implement as the security specialist" (member-specific methodology)
- Advanced command variations and combinations
- When to use specific members vs. general "as the architects"
- How to override configured practices for specific implementations
- Real examples from users who discovered advanced patterns

**Trigger**: 5+ user questions asking "Can I implement as [specific member]?" or requesting advanced pattern documentation

**In the meantime**:
- Basic command works well: "Implement X as the architects"
- Members.yml shows available member perspectives
- Users can experiment with command variations
- See [.architecture/members.yml](.architecture/members.yml) for available members

---

## Getting Help

### Documentation Resources

**Core Documentation**:
- [README.md](README.md) - Overview and getting started
- [USAGE.md](USAGE.md) - Detailed workflow instructions
- [AGENTS.md](AGENTS.md) - Cross-platform AI assistant integration
- [CLAUDE.md](CLAUDE.md) - Claude Code-specific features

**Configuration**:
- [.architecture/config.yml](.architecture/config.yml) - Your project configuration
- [.architecture/templates/config.yml](.architecture/templates/config.yml) - Template with all options
- [.architecture/members.yml](.architecture/members.yml) - Architecture team members

**Design Decisions**:
- [ADR-002: Pragmatic Guard Mode](.architecture/decisions/adrs/ADR-002-pragmatic-guard-mode.md)
- [ADR-004: Implementation Command Configuration](.architecture/decisions/adrs/ADR-004-implementation-command-configuration.md)
- [ADR-005: LLM Instruction Capacity Constraints](.architecture/decisions/adrs/ADR-005-llm-instruction-capacity-constraints.md)

### Reporting Issues

**For Framework Issues**:
- GitHub Issues: https://github.com/codenamev/ai-software-architect/issues
- Include: Framework version (currently 1.2.0), AI assistant used (Claude/Cursor/Copilot), error messages, relevant config

**For Feature Requests**:
- GitHub Discussions: https://github.com/codenamev/ai-software-architect/discussions
- Explain your use case, what you're trying to achieve, why current features don't address it

### Community

- GitHub Discussions: General questions, best practices, sharing experiences
- Examples: [.architecture/reviews/](.architecture/reviews/) and [.architecture/decisions/adrs/](.architecture/decisions/adrs/)

---

## Contributing to This Document

This troubleshooting guide grows based on real user needs. When sections reach their trigger conditions (documented above), they'll be populated with comprehensive guidance.

**How triggers work**:
- Each section has specific, measurable trigger conditions (e.g., "5+ user questions")
- Triggers are tracked in [.architecture/deferrals.md](.architecture/deferrals.md)
- When triggered, section is populated with real examples and solutions
- This ensures documentation addresses actual needs, not speculative problems

**Why this approach**:
- Progressive disclosure pattern (see ADR-005) - add detail when needed
- Real problems > hypothetical problems
- Documentation stays focused and relevant
- Respects instruction capacity constraints for AI assistants

**Current trigger status**: All sections monitoring, 0 triggers hit (as of 2025-12-11)

---

*For questions not covered here, see the documentation resources above or report an issue on GitHub.*
