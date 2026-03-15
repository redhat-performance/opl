# Quarterly Review Process

**Version**: 1.0.0
**Created**: 2025-12-04
**Schedule**: March 1, June 1, September 1, December 1
**Related**: [ADR-005](decisions/adrs/ADR-005-llm-instruction-capacity-constraints.md), [ADR-006](decisions/adrs/ADR-006-progressive-disclosure-pattern.md)

## Purpose

Quarterly review of framework documentation to ensure we maintain instruction capacity constraints, documentation quality, and alignment with user needs.

## Review Schedule

**Frequency**: Quarterly (every 3 months)

**Dates**: March 1, June 1, September 1, December 1

**Duration**: 2-4 hours

**Trigger**: Calendar date OR major framework changes (>20% documentation updates)

## Roles and Responsibilities

**Primary Reviewer**: Framework maintainer or designated contributor

**Stakeholders**:
- Framework users (feedback collection)
- Documentation contributors
- Architecture team (for validation)

## Review Checklist

### Phase 1: Instruction Capacity Audit (30-45 min)

**Objective**: Verify we're within instruction capacity targets.

**Tasks**:

- [ ] **Count AGENTS.md instructions**
  - Method: Run `cd tools && npm run count`
  - Alternative: Manual count using [instruction-counting-methodology.md](instruction-counting-methodology.md)
  - Target: < 150 instructions
  - Record: Current count, change from last review
  - Action if over: Identify candidates for agent_docs/ migration

- [ ] **Count CLAUDE.md instructions**
  - Method: Run `cd tools && npm run count`
  - Alternative: Manual count using [instruction-counting-methodology.md](instruction-counting-methodology.md)
  - Target: < 30 instructions
  - Record: Current count, change from last review
  - Action if over: Remove or consolidate instructions

- [ ] **Check line counts**
  - AGENTS.md target: < 500 lines (current: 418) ✅
  - CLAUDE.md target: < 100 lines (current: 126) ⚠️
  - agent_docs/ total: No limit (progressive disclosure)
  - Tool: `wc -l AGENTS.md CLAUDE.md .architecture/agent_docs/*.md`

- [ ] **Validate total budget**
  - Total instructions across AGENTS.md + CLAUDE.md
  - Target: < 180 (accounting for Claude Code's ~50)
  - Current budget used: ~134/180 ✅

**Document findings**: Update `.architecture/reviews/instruction-capacity-audit-YYYY-QN.md`

### Phase 2: Quality Assessment (30-45 min)

**Objective**: Ensure documentation is clear, accurate, and useful.

**Tasks**:

- [ ] **Check for instruction bloat**
  - Redundant instructions (same directive stated multiple ways)
  - Obsolete instructions (features removed, processes changed)
  - Over-specific instructions (too granular, could be generalized)
  - Action: Consolidate or remove

- [ ] **Validate all internal links**
  - Method: Run `cd tools && npm run validate`
  - Alternative: Manual check of links
  - Checks: Links to .architecture/, agent_docs/, between ADRs and reviews
  - Action: Fix broken links immediately

- [ ] **Review examples for staleness**
  - Code examples still current?
  - Command examples still work?
  - Configuration examples match current config.yml?
  - Version numbers current?
  - Action: Update stale examples

- [ ] **Check consistency**
  - Terminology consistent across files?
  - Formatting consistent?
  - Style guide followed?
  - Action: Standardize inconsistencies

**Document findings**: Update `.architecture/reviews/documentation-quality-YYYY-QN.md`

### Phase 3: Usage Pattern Analysis (30-45 min)

**Objective**: Understand how documentation is being used and optimize accordingly.

**Tasks**:

- [ ] **Analyze usage patterns**
  - Which agent_docs/ sections most accessed?
  - Which workflows most commonly requested?
  - Which documentation paths most followed?
  - Source: User feedback, GitHub issues, community discussions
  - Tool: Review issue tracker for documentation questions

- [ ] **Identify gaps**
  - Common questions not answered by current docs?
  - Missing workflows or procedures?
  - Unclear sections (frequent follow-up questions)?
  - Source: User feedback, support requests
  - Action: Add to documentation backlog

- [ ] **Evaluate progressive disclosure effectiveness**
  - Do users find what they need?
  - Are pointers clear and helpful?
  - Is navigation intuitive?
  - Source: User feedback
  - Action: Improve navigation or pointers

- [ ] **Check agent_docs/ file sizes**
  - Any files exceeding 300-400 lines?
  - Would splitting improve findability?
  - Apply pragmatic principle: split only if justified
  - Action: Split if evidence supports it

**Document findings**: Update `.architecture/reviews/usage-patterns-YYYY-QN.md`

### Phase 4: User Feedback Collection (15-30 min)

**Objective**: Gather direct feedback from framework users.

**Tasks**:

- [ ] **Review user feedback channels**
  - GitHub issues tagged 'documentation'
  - GitHub discussions
  - Pull request comments
  - Direct user reports
  - Community channels

- [ ] **Key questions to answer**:
  - What's working well?
  - What's confusing or hard to find?
  - What's missing?
  - Is AI assistant following instructions correctly?
  - Are instruction capacity improvements noticeable?

- [ ] **Quantitative metrics** (if available):
  - Time to complete common tasks
  - User satisfaction scores
  - Task completion rates
  - AI assistant effectiveness ratings

- [ ] **Qualitative feedback**:
  - User testimonials
  - Specific pain points
  - Improvement suggestions

**Document findings**: Update `.architecture/reviews/user-feedback-YYYY-QN.md`

### Phase 5: Refactoring and Improvements (45-90 min)

**Objective**: Implement improvements based on review findings.

**Tasks**:

- [ ] **Address capacity issues**
  - If AGENTS.md over budget: Move content to agent_docs/
  - If CLAUDE.md over budget: Consolidate or remove
  - If total budget tight: Prioritize highest-value instructions

- [ ] **Fix identified problems**
  - Broken links → Fix immediately
  - Stale examples → Update
  - Inconsistencies → Standardize
  - Gaps → Add to backlog or implement if quick

- [ ] **Implement quick wins**
  - Minor clarifications
  - Navigation improvements
  - Formatting fixes
  - Small additions

- [ ] **Plan larger improvements**
  - Major restructuring
  - New sections or guides
  - Significant rewrites
  - Create issues or ADRs as appropriate

- [ ] **Update documentation version numbers**
  - AGENTS.md if changed
  - CLAUDE.md if changed
  - agent_docs/ files if changed
  - Include change summary

**Track changes**: Commit with clear message referencing quarterly review

### Phase 6: Reporting and Planning (15-30 min)

**Objective**: Document review outcomes and plan next steps.

**Tasks**:

- [ ] **Create review summary**
  - Instruction counts (current vs. targets)
  - Key findings from each phase
  - Actions taken during review
  - Actions deferred to backlog
  - Next review date

- [ ] **Update tracking metrics**
  - Historical instruction counts
  - Documentation growth trends
  - User satisfaction trends
  - Common issues trends

- [ ] **Plan for next quarter**
  - Known upcoming changes
  - Deferred improvements from this review
  - Expected documentation needs

- [ ] **Communicate results**
  - Update repository documentation
  - Notify contributors
  - Share with community if appropriate

**Document**: Create `.architecture/reviews/quarterly-review-YYYY-QN-summary.md`

## Review Templates

### Instruction Capacity Audit Template

```markdown
# Instruction Capacity Audit - YYYY Q#

**Review Date**: YYYY-MM-DD
**Reviewer**: [Name]

## Instruction Counts

| Document | Target | Current | Last Quarter | Change | Status |
|----------|--------|---------|--------------|--------|--------|
| AGENTS.md | < 150 | X | Y | +/- Z | ✅/⚠️/❌ |
| CLAUDE.md | < 30 | X | Y | +/- Z | ✅/⚠️/❌ |
| **Total** | < 180 | X | Y | +/- Z | ✅/⚠️/❌ |

## Line Counts

| Document | Target | Current | Status |
|----------|--------|---------|--------|
| AGENTS.md | < 500 | X | ✅/⚠️/❌ |
| CLAUDE.md | < 100 | X | ✅/⚠️/❌ |

## Findings

### Over Budget Items
[List any documents exceeding targets]

### Instruction Bloat
[Redundant, obsolete, or unnecessary instructions identified]

### Recommendations
[Specific actions to take]

## Actions Taken

- [ ] Action 1
- [ ] Action 2

## Deferred to Backlog

- [ ] Item 1
- [ ] Item 2
```

### User Feedback Template

```markdown
# User Feedback Summary - YYYY Q#

**Review Date**: YYYY-MM-DD
**Reviewer**: [Name]

## Feedback Sources

- GitHub Issues: [count] documentation-related
- GitHub Discussions: [count] threads reviewed
- Direct Reports: [count] received
- Other: [describe]

## Key Themes

### What's Working Well
- Theme 1: [description]
- Theme 2: [description]

### Pain Points
- Issue 1: [description + frequency]
- Issue 2: [description + frequency]

### Missing Documentation
- Gap 1: [what users need]
- Gap 2: [what users need]

## Quantitative Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| User satisfaction | X/10 | > 8/10 | ✅/⚠️/❌ |
| Time-to-find info | X seconds | < 60s | ✅/⚠️/❌ |
| Task completion rate | X% | > 90% | ✅/⚠️/❌ |

## Recommendations

1. [Priority 1 improvement]
2. [Priority 2 improvement]
3. [Priority 3 improvement]

## Actions

- [ ] Immediate: [quick fixes]
- [ ] Short-term: [this quarter]
- [ ] Long-term: [future quarters]
```

## Success Metrics

Track these metrics over time:

| Metric | Target | Measurement |
|--------|--------|-------------|
| **AGENTS.md instruction count** | < 150 | Manual count per methodology |
| **CLAUDE.md instruction count** | < 30 | Manual count per methodology |
| **Total instruction budget used** | < 180 | Sum of above |
| **User satisfaction** | > 8/10 | User surveys, feedback |
| **Time-to-find documentation** | < 60 seconds | User testing |
| **Documentation-related issues** | Decreasing | GitHub issue count |
| **AI assistant effectiveness** | > 8/10 | User reports |

## Historical Tracking

Maintain a simple tracking document:

```markdown
# Documentation Metrics History

| Quarter | AGENTS.md | CLAUDE.md | Total | User Sat | Notes |
|---------|-----------|-----------|-------|----------|-------|
| 2025-Q1 | 120 | 14 | 134 | 8.5/10 | Initial optimization |
| 2025-Q2 | ? | ? | ? | ? | [Add notes] |
```

Location: `.architecture/documentation-metrics.md`

## Continuous Improvement

### Between Quarterly Reviews

**Ad-hoc checks**:
- After major documentation changes (> 20% of file)
- When adding new features requiring documentation
- If user feedback indicates documentation problems
- Before major version releases

**Ongoing activities**:
- Monitor documentation-related issues
- Collect user feedback continuously
- Fix broken links immediately when found
- Update stale examples as noticed

### Adapting the Process

This process should evolve based on experience:

**Triggers for process updates**:
- Review takes significantly more/less time than estimated
- Steps consistently yield no findings
- New tools or methods available
- User needs change
- Framework grows or changes significantly

**Update process**:
1. Identify what's not working
2. Propose changes to process
3. Test changes for one cycle
4. Evaluate and adopt or revert

## Tools and Resources

**Required**:
- [instruction-counting-methodology.md](instruction-counting-methodology.md)
- Text editor or IDE
- Terminal (for `wc -l` line counting)
- GitHub issue tracker access

**Automated Tools** (in `tools/` directory):
- `npm run validate` - Validates markdown links
- `npm run count` - Counts instructions with target checking
- See [tools/README.md](../tools/README.md) for full documentation

**Helpful**:
- Diff tool for comparing changes
- User feedback collection system
- Analytics (if available)

## Questions or Issues

**Process unclear?**
- Review [documentation-guidelines.md](documentation-guidelines.md)
- Check [ADR-005](decisions/adrs/ADR-005-llm-instruction-capacity-constraints.md) and [ADR-006](decisions/adrs/ADR-006-progressive-disclosure-pattern.md)
- Open GitHub issue for process improvements

**Can't complete review?**
- Review as much as possible
- Document what's missing
- Seek help from framework maintainers
- Defer complex items to next review

## Next Review

**Date**: [Next scheduled date]

**Reminder**: Set calendar reminder 1 week before review date

**Preparation**:
- Collect user feedback throughout quarter
- Note documentation issues as they arise
- Track framework changes affecting documentation

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-04 | Initial process based on ADR-005 and ADR-006 implementation |

## References

- [ADR-005: LLM Instruction Capacity Constraints](decisions/adrs/ADR-005-llm-instruction-capacity-constraints.md)
- [ADR-006: Progressive Disclosure Pattern](decisions/adrs/ADR-006-progressive-disclosure-pattern.md)
- [Documentation Guidelines](documentation-guidelines.md)
- [Instruction Counting Methodology](instruction-counting-methodology.md)
