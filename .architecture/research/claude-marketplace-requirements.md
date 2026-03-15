# Claude Marketplace Research: Requirements & Implementation Path

**Research Date**: 2026-01-21
**Purpose**: Understand Claude Code plugin marketplace requirements for ADR-011 implementation
**Status**: Initial research complete

## Executive Summary

**Critical Finding**: Claude Code uses a **distributed marketplace model**, not a centralized Anthropic-curated app store. Anyone can create and host their own marketplace. This significantly changes our implementation approach.

### Key Implications for AI Software Architect Framework

1. **No centralized submission process**: We don't submit to Anthropic for approval
2. **We can create our own marketplace**: Host `marketplace.json` on our GitHub repo
3. **Distribution flexibility**: Users can install directly from our repo without a third-party marketplace
4. **Lower barriers**: No app store review process, faster to market
5. **Less discoverability**: Without a centralized marketplace, discovery depends on our own marketing

## Marketplace System Architecture

### How It Works

```
User adds marketplace:
  /plugin marketplace add anthropics/ai-software-architect

Claude Code fetches marketplace.json:
  https://github.com/anthropics/ai-software-architect/.claude-plugin/marketplace.json

User installs plugin:
  /plugin install architect-tools@ai-software-architect

Claude Code copies plugin to cache:
  ~/.claude/plugin-cache/architect-tools/
```

### Marketplace File Structure

**Location**: `.claude-plugin/marketplace.json` in repository root

**Required Fields**:
- `name`: Marketplace identifier (kebab-case)
- `owner`: Object with `name` (required) and `email` (optional)
- `plugins`: Array of plugin entries

**Plugin Entry Fields**:
- `name`: Plugin identifier (kebab-case, public-facing)
- `source`: Where to fetch plugin (relative path, GitHub repo, or git URL)
- `description`: Brief description
- `version`: Semantic version (optional but recommended)
- `author`: Object with name and email (optional)
- Standard metadata: `homepage`, `repository`, `license`, `keywords`

### Example Marketplace.json

```json
{
  "name": "ai-software-architect",
  "owner": {
    "name": "AI Software Architect Project",
    "email": "support@example.com"
  },
  "plugins": [
    {
      "name": "architect-tools",
      "source": "./",
      "description": "AI-powered architecture documentation framework",
      "version": "1.3.0",
      "author": {
        "name": "AI Software Architect Team"
      },
      "homepage": "https://github.com/anthropics/ai-software-architect",
      "repository": "https://github.com/anthropics/ai-software-architect",
      "license": "MIT",
      "keywords": ["architecture", "adr", "documentation", "reviews"],
      "category": "development-tools",
      "mcpServers": "./.mcp.json"
    }
  ]
}
```

## Plugin Manifest Requirements

### File Location

**Manifest**: `.claude-plugin/plugin.json` at plugin root

**Important**: All other directories (commands/, agents/, skills/, hooks/) go at plugin root, NOT inside `.claude-plugin/`

### Required Manifest Fields

```json
{
  "name": "architect-tools",
  "version": "1.3.0",
  "description": "AI-powered architecture documentation framework"
}
```

### Recommended Optional Fields

```json
{
  "author": {
    "name": "Team Name",
    "email": "team@example.com"
  },
  "homepage": "https://docs.example.com",
  "repository": "https://github.com/org/repo",
  "license": "MIT",
  "keywords": ["architecture", "documentation"],
  "mcpServers": "./.mcp.json"
}
```

### Component Configuration

```json
{
  "commands": "./commands/",           // Custom command paths
  "agents": "./agents/",               // Agent definitions
  "skills": "./skills/",               // Agent Skills
  "hooks": "./hooks/hooks.json",       // Event handlers
  "mcpServers": "./.mcp.json",         // MCP server config
  "lspServers": "./.lsp.json"          // LSP server config
}
```

## Integration with Existing MCP Server

### Current State

- **MCP Server**: `mcp/index.js` (1,823 lines)
- **MCP Config**: `mcp/package.json`
- **Version**: 1.3.0
- **Distribution**: npm package `ai-software-architect`

### Plugin Wrapper Approach (Thin Wrapper)

**Strategy**: Create marketplace plugin that references existing MCP npm package

```
Repository Structure:
├── .claude-plugin/
│   ├── marketplace.json      # Marketplace catalog
│   └── plugin.json          # Plugin manifest
├── .mcp.json                # MCP server config (points to npm package)
├── mcp/                     # Existing MCP server (unchanged)
│   ├── index.js
│   └── package.json
└── README.md               # Installation instructions
```

### .mcp.json Configuration

```json
{
  "mcpServers": {
    "ai-software-architect": {
      "command": "npx",
      "args": ["ai-software-architect"],
      "env": {
        "PROJECT_ROOT": "${CLAUDE_PROJECT_ROOT}"
      }
    }
  }
}
```

This approach:
- Delegates to existing npm package (95%+ code sharing)
- Users install plugin, which installs MCP server via npm
- Changes to MCP package automatically available to plugin users
- No code duplication, single maintenance point

## Installation & Distribution

### User Installation Flow

**Step 1: Add Marketplace**
```bash
/plugin marketplace add anthropics/ai-software-architect
```

**Step 2: Install Plugin**
```bash
/plugin install architect-tools@ai-software-architect
```

**Alternative: Direct Installation** (no marketplace needed)
```bash
/plugin marketplace add https://github.com/anthropics/ai-software-architect
/plugin install architect-tools
```

### Installation Scopes

| Scope     | Location                      | Use Case                           |
|-----------|-------------------------------|------------------------------------|
| `user`    | `~/.claude/settings.json`     | Personal, all projects (default)   |
| `project` | `.claude/settings.json`       | Team, version controlled           |
| `local`   | `.claude/settings.local.json` | Project-specific, gitignored       |

### Team Distribution

For teams, add to `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "ai-software-architect": {
      "source": {
        "source": "github",
        "repo": "anthropics/ai-software-architect"
      }
    }
  },
  "enabledPlugins": {
    "architect-tools@ai-software-architect": true
  }
}
```

Users are automatically prompted to install when they trust the project folder.

## Quality & Validation Requirements

### No Formal Submission Process

Unlike iOS App Store or Chrome Web Store:
- No centralized review/approval
- No waiting for Anthropic to review
- Quality standards are self-enforced
- Community-driven curation

### Validation Tools

**CLI Validation**:
```bash
claude plugin validate .
# Or from within Claude Code:
/plugin validate .
```

**Common Validation Errors**:
- Missing required fields in manifest
- Invalid JSON syntax
- Duplicate plugin names
- Path traversal attempts (`..` in paths)

### Testing Checklist

Before distribution:
- [ ] `claude plugin validate .` passes
- [ ] Install locally works: `claude --plugin-dir ./`
- [ ] All MCP tools function correctly
- [ ] Skills invoke properly
- [ ] Hooks trigger on expected events
- [ ] Documentation complete (README, usage examples)

## Discovery & Marketing

### Challenge: No Centralized Discovery

Without a centralized Anthropic marketplace:
- Users must know about our marketplace to add it
- Discovery depends on:
  - GitHub stars/trending
  - Social media mentions
  - Documentation/blog posts
  - Word of mouth
  - Search engine results

### Discovery Strategy Recommendations

1. **GitHub Optimization**:
   - Clear README with installation instructions
   - "Install with Claude Code" badge
   - Topics: `claude-code`, `claude-plugin`, `architecture`, `adr`
   - GitHub Discussions for community

2. **Documentation Hub**:
   - Dedicated page: "Install as Claude Code Plugin"
   - Copy-paste installation commands
   - Video walkthrough

3. **Community Engagement**:
   - Blog post: "AI Software Architect now available as Claude Code plugin"
   - Reddit/HN posts
   - Discord/Slack communities

4. **SEO Optimization**:
   - Target: "claude code architecture plugin"
   - Target: "claude code adr plugin"
   - Target: "architecture documentation claude"

## Technical Constraints & Limitations

### Plugin Caching Behavior

**Critical**: Plugins are copied to cache, not used in-place
- Location: `~/.claude/plugin-cache/`
- Implication: Paths like `../shared-utils` won't work
- Solution: Use symlinks or restructure to keep all files in plugin root

### Path Requirements

- All paths must be relative
- Must start with `./`
- Cannot traverse outside plugin root (`..`)

### MCP Server Requirements

- Must use `${CLAUDE_PLUGIN_ROOT}` for plugin-relative paths
- Must use `${CLAUDE_PROJECT_ROOT}` for project-relative paths
- Must handle both plugin cache and project working directory

### Version Synchronization

**Challenge**: Plugin version vs. npm package version

**Solution**: Thin wrapper approach
- Plugin manifest references npm package
- Plugin version matches npm package version
- Single source of truth: npm package
- Updates: publish npm → update plugin manifest version → users run `/plugin update`

## Comparison: Original Assumption vs. Reality

| Aspect                  | Original Assumption (ADR-011)       | Research Findings                              |
|-------------------------|-------------------------------------|------------------------------------------------|
| **Marketplace Type**    | Centralized Anthropic marketplace   | Distributed, self-hosted marketplaces          |
| **Submission Process**  | Review/approval by Anthropic        | No submission, self-publish to GitHub          |
| **Quality Gates**       | Anthropic review requirements       | Self-validation with CLI tools                 |
| **Discoverability**     | Marketplace search & ratings        | GitHub, SEO, community marketing               |
| **First-Mover Advantage**| Critical for early marketplace     | Less critical, no central marketplace to "win" |
| **Preparation Timeline**| 6 weeks to meet marketplace standards| 2-3 weeks to create plugin wrapper + docs     |
| **Reversibility**       | Low (public marketplace presence)   | High (just a GitHub repo we control)           |
| **Maintenance Burden**  | Fourth distribution channel         | Thin wrapper, delegates to existing MCP        |

## Revised Implementation Recommendation

### Phase 1: Create Self-Hosted Marketplace (Week 1-2)

**Tasks**:
1. Create `.claude-plugin/marketplace.json` in repo root
2. Create `.claude-plugin/plugin.json` manifest
3. Create `.mcp.json` that references npm package
4. Update README with plugin installation instructions
5. Test locally with `claude --plugin-dir ./`
6. Create installation demo video
7. Publish to GitHub

**Deliverable**: Users can install via `/plugin marketplace add anthropics/ai-software-architect`

**Effort**: 2 weeks (vs. 6 weeks for centralized marketplace prep)

### Phase 2: Enhance Discoverability (Ongoing)

**Tasks**:
1. GitHub Discussions for support
2. Blog post announcement
3. Social media outreach
4. Community engagement (Reddit, Discord, etc.)
5. SEO optimization (documentation, keywords)

**Deliverable**: Increased awareness and adoption

**Effort**: Ongoing, low-intensity (1-2 hours/week)

### Phase 3: Monitor & Iterate (Month 2+)

**Tasks**:
1. Track installation metrics (GitHub clone rate, discussions activity)
2. Gather user feedback
3. Iterate on plugin features based on usage
4. Consider creating themed marketplaces (e.g., "enterprise-tools", "architecture-plugins")

## Decision Impact: Path A vs. Path B

### Path A (Immediate Marketplace) - REVISED

**Original Plan**: 6-week preparation for centralized marketplace submission

**Revised Reality**: 2-3 week plugin wrapper creation for self-hosted marketplace

**Changes**:
- No need for extensive preparation (tests, security audit) before "submission"
- No submission approval process to wait for
- Lower quality bar (self-enforced vs. platform-enforced)
- Can iterate rapidly based on user feedback
- Reduced risk of "rejection" (no reviewer to reject us)

### Path B (Phased Approach) - LESS COMPELLING

**Original Rationale**: Validate demand before marketplace investment

**Revised Reality**: Marketplace investment is minimal (2-3 weeks), less need for validation

**Reassessment**:
- Phase 1 (GitHub enhancement) still valuable
- Phase 2 (marketplace) is now much cheaper (2-3 weeks vs. 6 weeks)
- Lower barrier means less need for extensive validation
- Could do Phase 1 + Phase 2 simultaneously with minimal additional effort

## Open Questions & Next Steps

### Questions for Discussion

1. **Naming**: Should plugin be named `architect-tools`, `ai-software-architect`, or something else?
2. **Marketplace Name**: Should marketplace be `ai-software-architect` or something more generic like `architecture-tools`?
3. **Multiple Plugins**: Should we create one plugin or separate plugins for different use cases (e.g., `adr-tools`, `review-tools`)?
4. **Installation Scope**: Recommend `--scope user`, `--scope project`, or let users choose?
5. **Skills vs Commands**: Should we migrate existing commands to Skills format (SKILL.md)?

### Recommended Next Steps (Immediate)

1. **Create plugin structure** in repository:
   ```bash
   mkdir -p .claude-plugin
   touch .claude-plugin/marketplace.json
   touch .claude-plugin/plugin.json
   touch .mcp.json
   ```

2. **Write manifests** based on examples above

3. **Test locally**:
   ```bash
   claude --plugin-dir ./
   ```

4. **Document installation** in README.md

5. **Announce** to existing users

### Long-Term Considerations

1. **Official Marketplace**: Monitor for Anthropic creating centralized marketplace (may never happen)
2. **Plugin Ecosystem**: Consider creating "architecture tools" marketplace with other related plugins
3. **Competition**: Other architecture tools may create similar plugins (but distributed model means less direct competition)
4. **Sustainability**: Thin wrapper approach makes maintenance sustainable even if adoption is modest

## Conclusions

### Major Finding: Distributed vs. Centralized

The most significant finding is that Claude Code uses a **distributed marketplace model**, not a centralized app store. This fundamentally changes our implementation strategy:

- **Lower barrier to entry**: No approval process, no waiting
- **Faster to market**: 2-3 weeks vs. 6+ weeks
- **Higher control**: We own the marketplace, set our own standards
- **Discovery challenge**: Must drive awareness ourselves
- **Lower risk**: Easily reversible, no public rejection possibility

### Recommendation: Proceed with Simplified Path A

Given the research findings, we recommend:

1. **Create plugin wrapper immediately** (Week 1-2)
   - Minimal preparation needed
   - Thin wrapper delegates to existing MCP package
   - Self-hosted marketplace on our GitHub repo

2. **Enhance discoverability simultaneously** (Week 1-2)
   - Update README with plugin installation
   - Create demo video
   - Optimize GitHub presence

3. **Monitor and iterate** (Month 2+)
   - Track adoption metrics
   - Gather feedback
   - Evolve based on real usage

**Effort**: 2-3 weeks (down from 6-10 weeks in original Path A)
**Risk**: Low (fully reversible, no submission process)
**Reward**: Improved discoverability for Claude Code users

### Path B Reassessment

Path B (phased approach with validation first) is **less compelling** given:
- Phase 2 cost dropped from 6 weeks to 2-3 weeks
- No submission risk to validate against
- Low reversibility risk
- Can do Phase 1 + Phase 2 simultaneously

**New Recommendation**: Combine Phase 1 (GitHub enhancements) + Phase 2 (plugin creation) into single 2-3 week sprint.

## References

- [Claude Code Plugin Marketplaces Documentation](https://code.claude.com/docs/en/plugin-marketplaces.md)
- [Claude Code Plugins Documentation](https://code.claude.com/docs/en/plugins.md)
- [Claude Code Plugins Reference](https://code.claude.com/docs/en/plugins-reference.md)
- [ADR-011: Claude Marketplace Plugin Implementation](./../decisions/adrs/ADR-011-claude-marketplace-plugin-implementation.md)
- [Architecture Review: Claude Marketplace Plugin](./../reviews/claude-marketplace-plugin.md)

---

**Next Action**: Review findings with maintainer, decide whether to proceed with simplified Path A or adjust timeline/approach based on distributed marketplace reality.
