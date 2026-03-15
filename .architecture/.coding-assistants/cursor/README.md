# Cursor Configuration

This directory contains rule files for the Cursor AI coding assistant to understand and work with the AI Software Architect framework.

## Rules Structure

Cursor uses `.mdc` files in the `.cursor/rules` directory (or in project subdirectories like this one) for providing context. Each rule file follows this format:

```
---
description: Rule Description
globs:
  - "file/path/pattern/**/*.js"
alwaysApply: false
---

The actual rule content that guides Cursor...
```

## Available Rules

- `ai_software_architect_overview.mdc` - High-level overview of the framework
- `ai_software_architect_structure.mdc` - Directory structure and organization  
- `ai_software_architect_usage.mdc` - How to use the framework
- `ai_software_architect_reviews.mdc` - How to conduct architecture reviews
- `ai_software_architect_setup.mdc` - Setup and configuration instructions

## Usage with Cursor

When using Cursor with a project that implements the AI Software Architect framework, you can:

1. Ask for architectural reviews: "Review this architecture using the AI Software Architect framework"
2. Get specialized perspectives: "Analyze this from a security perspective using AI Software Architect"
3. Create architecture documentation: "Create an ADR for this decision using the AI Software Architect format"
4. Implement features with methodology: "Implement [feature] as the architects"

## Implementation Guidance

The framework supports configuration-driven implementation that applies your preferred methodology, influences, and practices automatically.

### Configuration

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
    ruby:
      style_guide: "Rubocop"
      idioms: "Blocks over loops, meaningful names"

  quality:
    definition_of_done:
      - "Tests passing"
      - "Code refactored"
      - "Code reviewed"
```

### Commands

When configuration is enabled, use these commands with Cursor:

- "Implement [feature] as the architects" - Apply configured methodology and practices
- "Implement as the architects" - When feature context is clear from previous conversation
- "Implement this" - With prior architectural discussion

### How It Works

When you use implementation commands:

1. Cursor reads `.architecture/config.yml` implementation section
2. Applies your configured methodology (TDD, BDD, etc.)
3. References your influences (Kent Beck, Sandi Metz, etc.)
4. Uses language-specific practices and idioms
5. Follows your testing approach and quality standards

### Benefits

- **Consistency**: Same approach across all implementations
- **Efficiency**: 90% reduction in prompt length
- **Quality**: Best practices applied systematically
- **Team alignment**: Shared configuration in version control

For complete configuration options, see `.architecture/templates/config.yml`.

## Documentation

For more information on Cursor rules, see the [Cursor documentation](https://docs.cursor.com/context/rules).