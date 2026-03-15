# Documentation Governance Tools

Automated tools supporting ADR-005 (LLM Instruction Capacity Constraints) and ADR-006 (Progressive Disclosure Pattern).

## Overview

These tools help maintain documentation quality during quarterly reviews by:
- Validating internal markdown links
- Counting discrete instructions
- Checking compliance with instruction capacity targets

## Installation

```bash
cd tools
npm install
```

## Usage

### Validate Links

Check all markdown links in `.architecture/`:

```bash
npm run validate
```

Check specific directory:

```bash
npm run validate ../path/to/docs
```

**What it checks:**
- Internal markdown links (file paths)
- Relative path resolution
- File existence
- Anchor links (file checked, anchor skipped)

**Ignores:**
- External HTTP/HTTPS URLs
- Anchor-only links (#heading)

### Count Instructions

Count instructions in AGENTS.md and CLAUDE.md:

```bash
npm run count
```

Count specific files:

```bash
npm run count ../AGENTS.md
npm run count ../AGENTS.md ../CLAUDE.md ../custom.md
```

**What it counts:**
- Commands (Create, Follow, Apply, etc.)
- Conditionals (If/When/Unless + colon)
- Procedures (Numbered steps with action verbs)
- Guidelines (Keep, Never, Must, Always, Should)

**Ignores:**
- Informational content
- Markdown headings
- Examples
- Human-only references

**Targets:**
- AGENTS.md: < 150 instructions
- CLAUDE.md: < 30 instructions

## Testing

Run all tests:

```bash
npm test
```

Watch mode:

```bash
npm run test:watch
```

**Test Coverage:**
- Link validator: 9 tests
- Instruction counter: 7 tests
- Total: 16 tests

## Architecture

```
tools/
├── lib/
│   ├── link-validator.js     # Link extraction and validation
│   └── instruction-counter.js # Instruction pattern matching
├── test/
│   ├── link-validator.test.js
│   └── instruction-counter.test.js
├── cli.js                     # Command-line interface
├── package.json
└── README.md
```

### Link Validator

**Functions:**
- `validateLinks(content, filePath)` - Extract internal links from markdown
- `checkLinks(links, baseDir)` - Verify link targets exist

**Algorithm:**
1. Parse markdown for `[text](url)` patterns
2. Filter external URLs and anchor-only links
3. Resolve relative paths from source file
4. Check file existence on filesystem

### Instruction Counter

**Functions:**
- `countInstructions(content)` - Count discrete instructions by category

**Algorithm:**
1. Remove markdown headings
2. Process line-by-line
3. Match against instruction patterns (most specific first)
4. Filter exclusions (informational content)
5. Categorize and count

**Methodology:** Implements [.architecture/instruction-counting-methodology.md](../.architecture/instruction-counting-methodology.md)

## Development

Built with TDD following:
- **Gary Bernhardt**: Concise, focused commits
- **Sandi Metz**: Clear, simple logic with single responsibility
- **Kent Beck**: Test-first, refactor after green

**Principles applied:**
- Red-Green-Refactor cycle
- Small, incremental commits
- No premature abstraction
- Line-by-line clarity over cleverness

## Integration with Quarterly Review

These tools support the quarterly review process defined in [.architecture/quarterly-review-process.md](../.architecture/quarterly-review-process.md):

**Phase 1: Instruction Capacity Audit**
```bash
npm run count
```

**Phase 2: Quality Assessment**
```bash
npm run validate
```

Use these tools to:
- Verify instruction counts haven't exceeded targets
- Check for broken links before releases
- Validate documentation structure
- Track metrics over time

## Future Enhancements

Possible additions (YAGNI - only add if needed):
- Anchor validation (parse target files for headings)
- Automated metrics tracking (append to documentation-metrics.md)
- GitHub Actions integration
- HTML report generation
- Instruction pattern customization

## References

- [ADR-005: LLM Instruction Capacity Constraints](../.architecture/decisions/adrs/ADR-005-llm-instruction-capacity-constraints.md)
- [ADR-006: Progressive Disclosure Pattern](../.architecture/decisions/adrs/ADR-006-progressive-disclosure-pattern.md)
- [Documentation Guidelines](../.architecture/documentation-guidelines.md)
- [Quarterly Review Process](../.architecture/quarterly-review-process.md)
- [Instruction Counting Methodology](../.architecture/instruction-counting-methodology.md)
