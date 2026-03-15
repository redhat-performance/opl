# Changelog

All notable changes to the AI Software Architect framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-12-12

### Added

#### Externalizing Senior Engineering Thinking (ADR-010)
- **Implementation Strategist**: New architecture team member focused on HOW and WHEN (blast radius analysis, reversibility design, team readiness assessment, change sequencing)
- **Change Impact Awareness Principle**: New Principle #8 systematically captures blast radius, reversibility, timing, social cost, and false confidence detection
- **Senior Thinking Checklist**: Enhanced review template with framing questions that externalize the "silent checklist" senior engineers use
- **Implementation Strategy Section**: Enhanced ADR template with systematic impact analysis (blast radius, reversibility, sequencing & timing, social cost, confidence assessment)
- **Strategic Framework Positioning**: Framework now explicitly creates the "missing corpus" of senior architectural thinking identified by industry thought leaders

#### Framework Capabilities
- **Knowledge Capture**: Systematically documents invisible architectural reasoning that typically stays undocumented
- **Progressive Disclosure Compliance**: All enhancements maintain instruction capacity constraints (ADR-005, ADR-006, ADR-008)
- **Auto-Discovery**: Implementation Strategist automatically available in Skills, MCP server, and all integration points via dynamic member loading

### Changed
- **Architecture Team**: Expanded from 7 to 8 core members with Implementation Strategist
- **Architectural Principles**: Enhanced from 7 to 8 principles with Change Impact Awareness
- **Review Process**: Review template now includes Senior Thinking Checklist for comprehensive impact framing
- **ADR Process**: ADR template now requires Implementation Strategy analysis before implementation
- **Directory Structure**: Added `agent_docs/` to standard structure (progressive disclosure pattern)

### Documentation
- **ADR-010**: Externalizing Senior Engineering Thinking - Documents strategic value and positions framework as solving industry gap
- **Referenced Work**: Obie Fernandez - "What happens when the coding becomes the least interesting part of the work" (2025)
- **README**: Updated to reflect Implementation Strategist, senior thinking capture, and agent_docs/ directory

### Technical Details

**New Team Member:**
```yaml
implementation_strategist:
  specialties:
    - change sequencing
    - blast radius analysis
    - reversibility design
    - team readiness assessment
  perspective: "Evaluates HOW and WHEN changes should be implemented"
```

**Enhanced Templates:**
- Review template: +100 lines (Senior Thinking Checklist)
- ADR template: +119 lines (Implementation Strategy section)
- Principles: +38 lines (Principle #8)

**Statistics:**
- 5 files modified, 486 lines added
- 1 new ADR created (ADR-010)
- Framework positioned as strategic knowledge capture system

## [1.2.0] - 2025-01-20

### Added

#### Agents.md Standard Adoption (ADR-003)
- **Cross-Platform AI Assistant Support**: Added `AGENTS.md` as universal entry point for all AI assistants (Claude, Cursor, Copilot, Jules, etc.)
- **Template System**: Created `.architecture/templates/AGENTS.md` for project-specific generation during setup
- **Multi-Assistant Architecture**: Framework now works seamlessly across 20,000+ projects using the Agents.md standard
- **Complementary Documentation**: `AGENTS.md` provides cross-platform instructions while `CLAUDE.md` adds Claude Code-specific enhancements

#### Implementation Command with Configuration (ADR-004)
- **Configuration-Driven Implementation**: Specify methodology, influences, and practices once in `.architecture/config.yml`
- **Simple Command Pattern**: Use "Implement X as the architects" instead of 40+ word prompts (90% reduction)
- **Methodology Support**: TDD, BDD, DDD, Test-Last, Exploratory development approaches
- **Coding Influences**: Configure thought leaders (Kent Beck, Sandi Metz, Martin Fowler, Gary Bernhardt, Jeremy Evans, Vladimir Dementyev)
- **Language-Specific Practices**: Per-language style guides, idioms, and framework conventions
- **Security-First**: Security practices always applied, exempt from YAGNI challenges
- **Quality Standards**: Configurable definition of done, refactoring guidelines, testing approach

#### Cross-Integration Implementation Support
- **MCP Server**: Added `get_implementation_guidance` tool for programmatic access to implementation configuration
- **Claude Code**: Full implementation command recognition with methodology application
- **Codex**: Setup instructions with implementation guidance and examples
- **Cursor**: README documentation with configuration and usage patterns
- **Claude Skills**: Updated `setup-architect` skill to include implementation commands

#### Pragmatic Guard Mode Enhancements
- **MCP Tool**: Added `pragmatic_enforcer` tool to MCP server for programmatic YAGNI analysis
- **Automated Complexity Assessment**: Scores necessity (0-10) and complexity (0-10) with ratio analysis
- **Simpler Alternatives**: Always proposes concrete simpler approaches
- **Deferral Recommendations**: Tracks what can be implemented later with trigger conditions

### Changed

- **Framework Version**: Bumped from 1.1.0 to 1.2.0
- **MCP Server Version**: Bumped from 1.1.0 to 1.2.0
- **Documentation Structure**: Clarified relationship between AGENTS.md (cross-platform) and CLAUDE.md (Claude-specific)
- **Config Template**: Expanded `.architecture/templates/config.yml` with implementation section (+175 lines)
- **Setup Process**: Framework setup now generates project-specific AGENTS.md from template

### Documentation

- **ADR-003**: Agents.md Standard Adoption - Full decision record with alternatives analysis
- **ADR-004**: Implementation Command with Configuration - Comprehensive decision record with pragmatic assessment
- **Architecture Reviews**:
  - `feature-agents-md-adoption.md` - Multi-perspective review of Agents.md adoption
  - `feature-implementation-command-configuration.md` - 7-member collaborative review
- **AGENTS.md**: 518 lines documenting framework for all AI assistants
- **Implementation Examples**: Ruby TDD, JavaScript BDD, Python Test-Last configurations

### Fixed

- **Update Command Clarity**: Added full GitHub URL to update instructions to avoid ambiguity
- **Cross-Platform Consistency**: Ensured all integration methods have equivalent implementation feature documentation

### Technical Details

**Implementation Configuration Structure:**
```yaml
implementation:
  enabled: true
  methodology: "TDD"  # or BDD, DDD, Test-Last, Exploratory
  influences:
    - "Kent Beck - TDD by Example"
    - "Sandi Metz - POODR, 99 Bottles"
    - "Martin Fowler - Refactoring"
  languages:
    ruby:
      style_guide: "Rubocop"
      idioms: "Blocks over loops, meaningful names"
  quality:
    definition_of_done:
      - "Tests passing"
      - "Code refactored"
```

**MCP Server New Tools:**
- `get_implementation_guidance(projectPath, featureDescription?)` - Returns formatted implementation guidance
- `pragmatic_enforcer(recommendation, context, mode?)` - Analyzes recommendations for YAGNI compliance

**Statistics:**
- 8 files modified, 2,886 lines added
- 2 new ADRs created
- 2 comprehensive architecture reviews conducted
- 5 integration methods fully documented

## [1.1.0] - 2025-11-17

### Added

- Claude Skills conversion for all architecture operations
- Pragmatic Guard Mode configuration and behavior
- Initial MCP server implementation with core tools
- Cross-assistant configuration directories

### Changed

- Converted to Skills-based architecture for Claude Code
- Enhanced members.yml with Pragmatic Enforcer role
- Improved setup process with project-specific customization

## [1.0.0] - 2025-11-15

### Added

- Initial framework release
- Architecture Decision Records (ADRs) system
- Architecture reviews with multi-perspective analysis
- Architecture recalibration process
- Members system with specialized roles
- Principles-based architectural guidance
- Template system for ADRs and reviews
- Claude Code integration

### Documentation

- CLAUDE.md for Claude Code usage
- USAGE-WITH-CLAUDE.md comprehensive guide
- Installation and setup instructions
- Example ADRs and reviews

---

## Release Links

- [1.2.0](https://github.com/codenamev/ai-software-architect/releases/tag/v1.2.0) - 2025-01-20
- [1.1.0](https://github.com/codenamev/ai-software-architect/releases/tag/v1.1.0) - 2025-11-17
- [1.0.0](https://github.com/codenamev/ai-software-architect/releases/tag/v1.0.0) - 2025-11-15

## Contributing

See [AGENTS.md](AGENTS.md#contributing-to-the-framework) for guidelines on contributing to the framework.
