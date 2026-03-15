# Deferred Architectural Decisions

This document tracks architectural features, patterns, and complexity that have been consciously deferred for future implementation. Each deferral includes the rationale for waiting and clear trigger conditions for when it should be reconsidered.

## Status Key

- **Deferred**: Decision to defer is active, watching for trigger
- **Triggered**: Trigger condition met, needs implementation
- **Implemented**: Feature has been implemented (moved to ADR)
- **Cancelled**: No longer needed or relevant

---

## Deferred Decisions

### Multiple Example Reviews (Phase 2B)

**Status**: Deferred
**Deferred Date**: 2025-11-05
**Category**: Documentation
**Priority**: Low

**What Was Deferred**:
Creating 3-5 comprehensive example architectural reviews demonstrating pragmatic mode in various scenarios

**Original Proposal**:
Phase 2 roadmap included creating 3-5 complete example reviews to demonstrate pragmatic mode in different contexts (performance optimization, security features, test infrastructure, etc.)

**Rationale for Deferring**:
- Current need score: 5/10 (helpful but not essential)
- Complexity score: 6/10 (time-consuming to create realistic examples)
- Cost of waiting: Low
- Already have one complete example (`example-pragmatic-api-feature.md`)
- Already have 13+ scenarios in `pragmatic-mode-usage-examples.md`
- Real usage will inform better examples than synthetic ones
- Risk of creating examples that don't match actual usage patterns

**Simpler Current Approach**:
Single comprehensive example demonstrating core pragmatic mode patterns. Reference existing usage examples documentation for additional scenarios.

**Trigger Conditions** (Implement when):
- [ ] Users request more example reviews
- [ ] First 3 real reviews reveal patterns not covered in current example
- [ ] Feedback indicates template alone is insufficient
- [ ] Specific scenario gaps identified through actual usage

**Implementation Notes**:
When creating additional examples:
- Base on real reviews that have been conducted
- Focus on scenarios that proved confusing or needed clarification
- Prioritize examples that show different intensity levels
- Include examples with different exemption scenarios

**Related Documents**:
- `.architecture/reviews/example-pragmatic-api-feature.md` (current example)
- `.architecture/decisions/pragmatic-mode-usage-examples.md` (13+ scenarios)
- `.architecture/decisions/phase-2-pragmatic-analysis.md` (deferral decision)

**Last Reviewed**: 2025-11-05

---

### Extensive Phase 2 Documentation

**Status**: Deferred
**Deferred Date**: 2025-11-05
**Category**: Documentation
**Priority**: Low

**What Was Deferred**:
Additional documentation for review process integration beyond template and single example

**Original Proposal**:
Create comprehensive documentation covering:
- Detailed review process with pragmatic mode
- Integration patterns
- Troubleshooting guide
- Best practices

**Rationale for Deferring**:
- Current need score: 4/10 (would be nice but not required)
- Complexity score: 5/10 (time-consuming)
- Cost of waiting: Very low
- Existing integration guide covers technical details
- Existing usage examples cover scenarios
- Template provides structure
- Don't know yet what users will find confusing

**Simpler Current Approach**:
Rely on existing documentation:
- Review template with clear structure
- One complete example
- Integration guide
- Usage examples document
- CLAUDE.md instructions

**Trigger Conditions** (Implement when):
- [ ] Users ask questions not covered in existing docs
- [ ] Specific pain points emerge from actual usage
- [ ] Common patterns emerge that need documentation
- [ ] 5+ support requests on same topic

**Implementation Notes**:
Document actual problems users encounter, not imagined ones. This ensures documentation addresses real needs.

**Related Documents**:
- `.architecture/decisions/pragmatic-mode-integration-guide.md`
- `.architecture/decisions/pragmatic-mode-usage-examples.md`
- `CLAUDE.md`

**Last Reviewed**: 2025-11-05

---

### Comprehensive Integration Testing

**Status**: Deferred
**Deferred Date**: 2025-11-05
**Category**: Testing
**Priority**: Medium

**What Was Deferred**:
Extensive integration testing suite for Phase 2 review process integration

**Original Proposal**:
Create comprehensive tests:
- Template rendering with all architect combinations
- Pragmatic mode enabled/disabled scenarios
- Different intensity levels
- All trigger conditions
- Exemption scenarios
- Error cases

**Rationale for Deferring**:
- Current need score: 6/10 (testing is valuable)
- Complexity score: 7/10 (time-consuming, requires test framework)
- Cost of waiting: Low
- Manual testing verifies core functionality
- First real usage will reveal actual edge cases
- Can test with real scenarios vs synthetic ones
- Template is straightforward enough for manual verification

**Simpler Current Approach**:
- Manual verification that template is well-formed
- Test with simple review scenario (done)
- Monitor first real reviews for issues
- Add tests for patterns that prove problematic

**Trigger Conditions** (Implement when):
- [ ] Bugs found in review process
- [ ] Template changes frequently and needs regression protection
- [ ] Complex logic added that's hard to verify manually
- [ ] Multiple contributors need test suite

**Implementation Notes**:
When implementing:
- Focus on testing actual failure modes discovered
- Test template rendering and structure
- Test pragmatic mode activation/deactivation
- Test different intensity levels

**Related Documents**:
- `.architecture/templates/review-template.md`
- `.architecture/PHASE-1-TEST.md`

**Last Reviewed**: 2025-11-05

---

### Multiple Example ADRs (Phase 3B)

**Status**: Deferred
**Deferred Date**: 2025-11-05
**Category**: Documentation
**Priority**: Low

**What Was Deferred**:
Creating 3-5 comprehensive example ADRs demonstrating pragmatic mode analysis for various decision types

**Original Proposal**:
Phase 3 roadmap included creating 3-5 complete example ADRs to demonstrate pragmatic analysis in different contexts:
- Infrastructure decisions
- Technology stack choices
- Design pattern adoptions
- Performance optimization decisions
- Security architecture decisions

**Rationale for Deferring**:
- Current need score: 4/10 (helpful but not essential)
- Complexity score: 7/10 (more complex than review examples, need realistic decisions)
- Cost of waiting: Very low
- Already have one complete example (`example-pragmatic-caching-layer.md`)
- ADR format is well-understood, adding pragmatic section is straightforward
- Real ADRs will provide better examples than synthetic ones
- Risk of creating examples that don't reflect actual architectural decisions
- Technology choices in examples may become dated

**Simpler Current Approach**:
Single comprehensive ADR example demonstrating complete pragmatic analysis pattern. Users understand ADR format; one example shows how to add pragmatic section.

**Trigger Conditions** (Implement when):
- [ ] Users request more ADR examples
- [ ] First 3 real ADRs with pragmatic mode reveal patterns not covered
- [ ] Feedback indicates one example is insufficient
- [ ] Specific decision types emerge that need dedicated examples
- [ ] Common architectural decisions need documented patterns

**Implementation Notes**:
When creating additional examples:
- Base on real ADRs that have been created with pragmatic mode
- Focus on decision types that proved challenging
- Show different pragmatic outcomes (approved, simplified, deferred, rejected)
- Include examples at different intensity levels
- Cover different trigger scenarios and exemptions

**Related Documents**:
- `.architecture/decisions/adrs/example-pragmatic-caching-layer.md` (current example)
- `.architecture/templates/adr-template.md` (updated template)
- `.architecture/decisions/phase-3-pragmatic-analysis.md` (deferral decision)

**Last Reviewed**: 2025-11-05

---

### Extensive ADR Process Documentation (Phase 3B)

**Status**: Deferred
**Deferred Date**: 2025-11-05
**Category**: Documentation
**Priority**: Low

**What Was Deferred**:
Additional documentation for ADR creation process with pragmatic mode beyond template and single example

**Original Proposal**:
Create comprehensive documentation covering:
- Detailed ADR creation workflow with pragmatic mode
- How to conduct pragmatic analysis
- Guidelines for scoring necessity and complexity
- When to defer decisions
- How to set trigger conditions
- Best practices for phased implementations
- Integration with architecture reviews

**Rationale for Deferring**:
- Current need score: 3/10 (would be nice but not required)
- Complexity score: 5/10 (time-consuming)
- Cost of waiting: Very low
- ADR template is self-documenting
- Example ADR shows complete pattern
- CLAUDE.md already covers ADR creation process
- Don't know yet what users will find confusing about ADR pragmatic analysis
- Can document actual pain points instead of speculating

**Simpler Current Approach**:
Rely on existing documentation:
- ADR template with Pragmatic Enforcer Analysis section
- One complete example showing full pattern
- CLAUDE.md instructions for pragmatic mode
- Configuration file with thresholds and settings
- Review example showing pragmatic analysis patterns

**Trigger Conditions** (Implement when):
- [ ] Users ask questions not covered in existing docs
- [ ] Specific pain points emerge from actual ADR creation
- [ ] Common scoring confusion emerges
- [ ] 5+ support requests on same ADR-related topic
- [ ] Teams struggle with pragmatic analysis despite example

**Implementation Notes**:
Document actual problems users encounter when creating ADRs with pragmatic mode. Focus on real confusion, not imagined difficulties.

**Related Documents**:
- `.architecture/templates/adr-template.md`
- `.architecture/decisions/adrs/example-pragmatic-caching-layer.md`
- `CLAUDE.md`
- `.architecture/config.yml`

**Last Reviewed**: 2025-11-05

---

### Comprehensive ADR Integration Testing (Phase 3B)

**Status**: Deferred
**Deferred Date**: 2025-11-05
**Category**: Testing
**Priority**: Medium

**What Was Deferred**:
Extensive integration testing suite for Phase 3 ADR template with pragmatic analysis

**Original Proposal**:
Create comprehensive tests:
- ADR template rendering with pragmatic section
- Different decision types and outcomes
- Necessity/complexity scoring calculations
- Trigger condition formats
- Integration with review process
- Different intensity levels affecting recommendations
- Exemption scenario handling
- Migration paths and phased approaches

**Rationale for Deferring**:
- Current need score: 5/10 (testing is valuable but not urgent)
- Complexity score: 7/10 (time-consuming, requires test framework)
- Cost of waiting: Low
- Manual testing verifies template is well-formed
- First real ADRs will reveal actual edge cases
- Can test with real scenarios vs synthetic ones
- ADR template is straightforward enough for manual verification
- Template structure is simpler than review template

**Simpler Current Approach**:
- Manual verification that template is well-formed
- Verify example ADR uses template correctly
- Monitor first real ADRs for issues
- Add tests for patterns that prove problematic

**Trigger Conditions** (Implement when):
- [ ] Bugs found in ADR pragmatic analysis
- [ ] ADR template changes frequently and needs regression protection
- [ ] Complex logic added for scoring or recommendations
- [ ] Multiple contributors need test suite
- [ ] Automated validation of necessity/complexity ratios needed

**Implementation Notes**:
When implementing:
- Focus on testing actual failure modes discovered
- Test template structure and completeness
- Test pragmatic scoring calculations if automated
- Test integration with review process
- Test different intensity levels if behavior varies

**Related Documents**:
- `.architecture/templates/adr-template.md`
- `.architecture/decisions/adrs/example-pragmatic-caching-layer.md`
- `.architecture/PHASE-1-TEST.md`

**Last Reviewed**: 2025-11-05

---

### Cross-Reference Example Library (Phase 3B)

**Status**: Deferred
**Deferred Date**: 2025-11-05
**Category**: Documentation
**Priority**: Low

**What Was Deferred**:
Building a comprehensive cross-referenced library of pragmatic mode examples across reviews, ADRs, and decision scenarios

**Original Proposal**:
Create an organized library:
- Index of all examples by scenario type
- Cross-references between review and ADR examples
- Searchable catalog of pragmatic challenges
- Decision tree for when to defer vs simplify vs implement
- Pattern library of common architectural over-engineering traps

**Rationale for Deferring**:
- Current need score: 3/10 (nice to have, not essential)
- Complexity score: 6/10 (requires corpus of examples to cross-reference)
- Cost of waiting: Very low
- Only have 2 examples currently (1 review, 1 ADR)
- Need more real examples before patterns emerge
- Premature to create index with limited content
- Pattern library should emerge from actual usage, not speculation

**Simpler Current Approach**:
Let example corpus grow organically from real usage. Cross-reference when patterns emerge naturally.

**Trigger Conditions** (Implement when):
- [ ] 10+ documented examples exist (reviews + ADRs)
- [ ] Clear patterns emerge across multiple examples
- [ ] Users request ability to search examples by scenario
- [ ] Common architectural traps documented from real usage
- [ ] Teaching/training need for organized example library

**Implementation Notes**:
When implementing:
- Wait for corpus of real examples to accumulate
- Identify patterns from actual usage, not speculation
- Create taxonomy based on real decision types encountered
- Build index only when content justifies the structure

**Related Documents**:
- `.architecture/reviews/example-pragmatic-api-feature.md`
- `.architecture/decisions/adrs/example-pragmatic-caching-layer.md`
- Future examples to be added as they're created

**Last Reviewed**: 2025-11-05

---

### Comprehensive Usage Guide (Phase 4B)

**Status**: Deferred
**Deferred Date**: 2025-11-05
**Category**: Documentation
**Priority**: Low

**What Was Deferred**:
Creating a comprehensive usage guide for pragmatic mode beyond existing CLAUDE.md instructions

**Original Proposal**:
Phase 4 roadmap included creating detailed usage guide covering:
- When to enable pragmatic mode
- How to configure intensity levels
- Handling exemptions
- Best practices for usage
- Integration workflows
- Troubleshooting guide

**Rationale for Deferring**:
- Current need score: 3/10 (helpful but not essential)
- Complexity score: 6/10 (significant documentation effort)
- Cost of waiting: Very low
- CLAUDE.md already has comprehensive 9-step activation guide
- config.yml has extensive inline documentation
- Examples demonstrate usage patterns
- Don't know yet what users will struggle with
- Cannot create effective guide without seeing real usage questions

**Simpler Current Approach**:
Rely on existing documentation:
- CLAUDE.md: Complete "Pragmatic Guard Mode Requests" section with 9-step process
- config.yml: Extensive inline documentation for all settings
- Review template: Self-documenting with clear structure
- ADR template: Self-documenting with clear structure
- Examples: 1 review + 1 ADR demonstrate all patterns

**Trigger Conditions** (Implement when):
- [ ] 5+ support questions about how to use pragmatic mode
- [ ] Users report confusion despite existing documentation
- [ ] Common usage patterns emerge that aren't documented
- [ ] Specific workflows prove difficult to understand
- [ ] Feedback indicates current docs insufficient

**Implementation Notes**:
When creating usage guide:
- Base on actual user questions and confusion points
- Focus on scenarios that proved unclear in practice
- Include real-world usage examples from actual projects
- Address specific pain points identified through support
- Avoid documenting what users already understand

**Related Documents**:
- `CLAUDE.md` (current usage instructions)
- `.architecture/config.yml` (configuration documentation)
- `.architecture/reviews/example-pragmatic-api-feature.md`
- `.architecture/decisions/adrs/example-pragmatic-caching-layer.md`
- `.architecture/decisions/phase-4-pragmatic-analysis.md` (deferral decision)

**Last Reviewed**: 2025-11-05

---

### YAGNI Principles Reference Document (Phase 4B)

**Status**: Deferred
**Deferred Date**: 2025-11-05
**Category**: Documentation
**Priority**: Low

**What Was Deferred**:
Creating a comprehensive reference document on YAGNI principles, resources, and best practices

**Original Proposal**:
Phase 4 roadmap included creating reference documentation covering:
- Link to YAGNI resources (Martin Fowler, Kent Beck, XP principles)
- Common pitfalls in architectural decision-making
- Decision frameworks for complexity vs simplicity
- When YAGNI applies and when it doesn't
- Examples of appropriate vs premature optimization
- Cost-benefit frameworks for architectural decisions

**Rationale for Deferring**:
- Current need score: 2/10 (nice to have, not required)
- Complexity score: 5/10 (research and compilation effort)
- Cost of waiting: Zero
- Can link to external resources (Martin Fowler, Kent Beck) as needed
- Don't know yet what principles users need reinforcement on
- Cannot document "common pitfalls" that haven't been encountered
- Better to create based on actual user needs vs speculation

**Simpler Current Approach**:
Link to external resources when needed:
- Martin Fowler's YAGNI article: https://martinfowler.com/bliki/Yagni.html
- Kent Beck's XP principles (reference in principles.md)
- Pragmatic mode config and examples demonstrate principles in action
- Users can request specific references if needed

**Trigger Conditions** (Implement when):
- [ ] Users request deeper learning resources on YAGNI
- [ ] Questions show misunderstanding of when YAGNI applies
- [ ] Common misconceptions emerge from real usage
- [ ] Teams struggle with philosophical understanding despite examples
- [ ] 5+ requests for learning resources or deeper principles

**Implementation Notes**:
When creating principles reference:
- Focus on areas where users show actual confusion
- Include real examples from user projects (anonymized)
- Address specific misconceptions that emerged
- Link to authoritative external resources
- Keep practical and actionable, not purely theoretical

**Related Documents**:
- `.architecture/principles.md` (existing principles)
- External: Martin Fowler YAGNI article
- External: Kent Beck XP principles
- `.architecture/decisions/exploration-pragmatic-guard-mode.md` (rationale)

**Last Reviewed**: 2025-11-05

---

### Common Pitfalls Documentation (Phase 4B)

**Status**: Deferred
**Deferred Date**: 2025-11-05
**Category**: Documentation
**Priority**: Low

**What Was Deferred**:
Documenting common pitfalls and anti-patterns when using pragmatic mode

**Original Proposal**:
Phase 4 roadmap included documenting common pitfalls:
- Mistakes users make when applying pragmatic mode
- Anti-patterns in using YAGNI principles
- When pragmatic mode is applied inappropriately
- Balancing simplicity with necessary complexity
- Avoiding under-engineering critical systems

**Rationale for Deferring**:
- Current need score: 1/10 (cannot do without real usage)
- Complexity score: 4/10 (straightforward documentation once known)
- Cost of waiting: Zero - literally cannot do this before it happens!
- **CANNOT document pitfalls that haven't been encountered**
- Don't know yet what mistakes users will make
- Speculating about pitfalls risks documenting wrong things
- Real usage will reveal actual problems vs imagined ones

**Simpler Current Approach**:
Wait for real usage to reveal pitfalls:
- Monitor first users' experiences
- Collect actual problems encountered
- Document real anti-patterns as they emerge
- Learn from mistakes rather than speculate

**Trigger Conditions** (Implement when):
- [ ] 5+ users have used pragmatic mode on real projects
- [ ] Common mistakes emerge from real usage
- [ ] Patterns of misuse are observed
- [ ] Specific scenarios repeatedly cause problems
- [ ] Anti-patterns identified from actual projects

**Implementation Notes**:
When creating pitfalls documentation:
- Base entirely on real problems encountered
- Include real examples (anonymized if needed)
- Explain why the pitfall is problematic
- Provide corrective guidance
- Show before/after examples
- This document MUST wait for real usage data

**Related Documents**:
- Future: Real user feedback and usage reports
- `.architecture/decisions/phase-4-pragmatic-analysis.md` (why deferred)

**Last Reviewed**: 2025-11-05

---

### Behavioral Pattern Refinement (Phase 4B)

**Status**: Deferred
**Deferred Date**: 2025-11-05
**Category**: Enhancement
**Priority**: Medium

**What Was Deferred**:
Refining pragmatic mode behavioral patterns based on real-world usage feedback

**Original Proposal**:
Phase 4 roadmap included behavioral refinement:
- Test with real projects
- Refine question frameworks
- Adjust response patterns
- Improve challenge structure
- Enhance collaborative discussion integration

**Rationale for Deferring**:
- Current need score: 0/10 (literally impossible without usage data)
- Complexity score: 6/10 (requires analysis and iteration)
- Cost of waiting: Zero until we have usage data
- **CANNOT refine patterns without seeing them in real usage**
- Current patterns are well-designed based on YAGNI principles
- Need real usage to know what works and what doesn't
- Premature refinement risks optimizing wrong things

**Simpler Current Approach**:
Ship current behavioral patterns as-is:
- Question framework is well-designed
- Response patterns are clear and structured
- Assessment framework (0-10 scoring) is straightforward
- Wait for real usage to show what needs refinement

**Trigger Conditions** (Implement when):
- [ ] 10+ pragmatic mode reviews/ADRs conducted
- [ ] Patterns emerge showing specific questions are unclear
- [ ] Users report challenge structure is confusing
- [ ] Response format proves inadequate for real scenarios
- [ ] Feedback indicates specific improvements needed
- [ ] Behavioral patterns produce unhelpful or confusing results

**Implementation Notes**:
When refining behavioral patterns:
- Analyze actual reviews and ADRs created with pragmatic mode
- Identify what worked well vs what caused confusion
- Refine based on real usage patterns, not speculation
- A/B test changes if possible
- Update templates, examples, and documentation consistently

**Related Documents**:
- `.architecture/templates/review-template.md` (current patterns)
- `.architecture/templates/adr-template.md` (current patterns)
- Future: Analysis of real pragmatic mode usage

**Last Reviewed**: 2025-11-05

---

### Intensity Calibration Adjustment (Phase 4B)

**Status**: Deferred
**Deferred Date**: 2025-11-05
**Category**: Enhancement
**Priority**: Medium

**What Was Deferred**:
Adjusting intensity level calibration (strict, balanced, lenient) based on real project data

**Original Proposal**:
Phase 4 roadmap included intensity calibration:
- Validate current thresholds with real projects
- Adjust complexity/necessity ratio targets
- Refine strict/balanced/lenient behaviors
- Tune trigger sensitivity
- Optimize for different project types/sizes

**Rationale for Deferring**:
- Current need score: 0/10 (impossible without real project data)
- Complexity score: 7/10 (requires data collection and analysis)
- Cost of waiting: Zero until we have real usage data
- **CANNOT calibrate without seeing actual intensity levels in use**
- Current calibration is well-designed based on principles
- Thresholds (e.g., <1.5 ratio for balanced mode) are reasonable
- Need real projects to validate or adjust thresholds

**Simpler Current Approach**:
Ship current calibration as-is:
- Strict: Aggressive challenges, high bar for complexity
- Balanced: Thoughtful challenges, middle ground (RECOMMENDED)
- Lenient: Raise concerns, suggest alternatives
- Thresholds: complexity/necessity ratio <1.5 for balanced
- Wait for real usage to show if calibration is appropriate

**Trigger Conditions** (Implement when):
- [ ] 20+ projects using pragmatic mode
- [ ] Data shows intensity levels produce unexpected results
- [ ] Users report strict/balanced/lenient not behaving as expected
- [ ] Thresholds prove too aggressive or too permissive
- [ ] Different project types/sizes need different calibration
- [ ] Quantitative analysis shows calibration issues

**Implementation Notes**:
When adjusting intensity calibration:
- Collect data from real projects using each intensity level
- Analyze necessity scores, complexity scores, and ratios
- Identify patterns in recommendations (approve/simplify/defer/reject)
- Measure project outcomes with different intensity levels
- Adjust thresholds based on data, not intuition
- Document reasoning for any calibration changes
- Update config.yml, examples, and documentation

**Related Documents**:
- `.architecture/config.yml` (current calibration)
- `.architecture/reviews/example-pragmatic-api-feature.md` (balanced mode example)
- `.architecture/decisions/adrs/example-pragmatic-caching-layer.md` (balanced mode example)
- Future: Analysis of intensity level usage across projects

**Last Reviewed**: 2025-11-05

---

## README Documentation Improvements (December 2025)

*Source: Architecture Review - README.md Pragmatic Mode and Implementation Guidance Documentation (2025-12-11)*

The following recommendations emerged from the comprehensive architecture review of README.md documentation. Progressive disclosure principles were applied to categorize recommendations as "implement now" vs. "defer with triggers".

### AI Assistant Capabilities Documentation

**Status**: Deferred
**Deferred Date**: 2025-12-11
**Category**: Documentation
**Priority**: Medium

**What Was Deferred**:
Comprehensive "How AI Assistants Use This" documentation section explaining how AI assistants parse, apply, and handle pragmatic mode and implementation guidance features.

**Original Proposal**:
AI Engineer recommended adding detailed documentation covering:
- How AI assistants parse config.yml settings
- What AI assistants can/cannot do with these features
- Whether AI can create members.yml members dynamically
- Whether AI can detect when pragmatic mode should be enabled
- Error handling when config is invalid/malformed
- Context loading behavior (when config is read, cached, reloaded)

**Rationale for Deferring**:
- Necessity score: 6/10 (valuable but not immediately critical)
- Complexity score: 6/10 (requires comprehensive explanation, examples)
- Ratio: 1.0 (at threshold for deferral)
- Cost of waiting: Low - users discovering capabilities through usage
- No user questions yet about AI behavior or capabilities
- Features are working without this documentation
- Real usage will reveal which aspects actually need explanation
- Risk of documenting speculative concerns vs. actual user questions

**Simpler Current Approach**:
- Config.yml has extensive inline documentation
- ADR-002 and ADR-004 explain feature design
- Natural language commands are intuitive
- Users can experiment and ask questions as needed
- Document specific capabilities when users ask

**Trigger Conditions** (Implement when):
- [ ] 5+ user questions about how AI assistants parse or apply configurations
- [ ] 3+ user questions about AI capabilities or limitations
- [ ] Users encounter unexpected AI behavior with features
- [ ] Support requests about config parsing or application
- [ ] Confusion about what AI can/cannot do with features

**Implementation Notes**:
When triggered, add to TROUBLESHOOTING.md:
- Base on actual user questions, not speculation
- Include examples of actual AI behaviors observed
- Clarify capabilities vs. limitations based on real usage
- Address specific confusion points that emerged
- Show examples of correct vs. incorrect config usage

**Related Documents**:
- `.architecture/reviews/readme-pragmatic-implementation-docs.md` (review source)
- `README.md` (lines 428-492: feature documentation)
- `.architecture/config.yml` (configuration reference)
- ADR-002, ADR-004 (feature design decisions)

**Last Reviewed**: 2025-12-11

---

### Advanced Prompt Patterns Documentation

**Status**: Deferred
**Deferred Date**: 2025-12-11
**Category**: Documentation
**Priority**: Medium

**What Was Deferred**:
Documentation of advanced prompt patterns and member-specific implementation commands.

**Original Proposal**:
AI Engineer recommended documenting full prompt pattern space:
- "Implement as the pragmatic enforcer" (specific member)
- "Implement as the security specialist" (member-specific methodology)
- Advanced command variations and combinations
- Member-specific implementation approaches
- How to override configured practices for specific implementations

**Rationale for Deferring**:
- Necessity score: 5/10 (power user feature, not essential for basic use)
- Complexity score: 3/10 (straightforward documentation once patterns known)
- Ratio: 0.6 (acceptable for deferral, lower necessity)
- Cost of waiting: Very low - users discovering patterns naturally
- No evidence users need these advanced patterns yet
- Basic "Implement X as the architects" command works well
- Advanced users discovering variations through experimentation
- Real usage will show which patterns are actually used vs. speculative

**Simpler Current Approach**:
- Basic implementation command documented: "Implement X as the architects"
- Users can experiment with variations
- Members.yml shows available member perspectives
- Document specific patterns when users ask about them

**Trigger Conditions** (Implement when):
- [ ] 5+ user questions asking "Can I implement as [specific member]?"
- [ ] Users requesting member-specific implementation guidance
- [ ] Advanced patterns emerge from actual usage
- [ ] Power users request documentation of advanced capabilities
- [ ] Evidence that users want more control over implementation approach

**Implementation Notes**:
When triggered, add to TROUBLESHOOTING.md "Advanced Usage" section:
- Document patterns users actually want (not all theoretical possibilities)
- Show examples of member-specific implementations from real usage
- Explain when to use specific members vs. general architects
- Include use cases for each pattern variant
- Based on actual user needs, not speculation

**Related Documents**:
- `.architecture/reviews/readme-pragmatic-implementation-docs.md`
- `README.md` § Implementation Guidance
- `.architecture/members.yml` (available members)
- ADR-004 (implementation guidance design)

**Last Reviewed**: 2025-12-11

---

### Error Handling Documentation

**Status**: Deferred
**Deferred Date**: 2025-12-11
**Category**: Documentation
**Priority**: Medium

**What Was Deferred**:
Documentation of common error scenarios and resolution steps for pragmatic mode and implementation guidance features.

**Original Proposal**:
AI Engineer recommended documenting error scenarios:
- Config file missing or malformed
- Pragmatic mode enabled but pragmatic_enforcer not in members.yml
- Invalid YAML syntax in config.yml
- Conflicting settings between pragmatic mode and implementation guidance
- Missing required fields in configuration
- Invalid values for enum fields (intensity, methodology)

**Rationale for Deferring**:
- Necessity score: 6/10 (helpful when errors occur, not needed if no errors)
- Complexity score: 5/10 (need to identify and document each error scenario)
- Ratio: 0.83 (acceptable for deferral)
- Cost of waiting: Low - no user reports of errors yet
- Features are working without error documentation
- YAML validation provides basic error messages
- No evidence of users encountering these errors
- Better to document actual errors users encounter vs. speculate

**Simpler Current Approach**:
- Config.yml template has extensive inline documentation
- YAML syntax errors caught by parser with standard messages
- Members.yml includes pragmatic_enforcer by default
- Template validation catches basic issues
- Address specific errors when users report them

**Trigger Conditions** (Implement when):
- [ ] 5+ user support requests about configuration errors
- [ ] Specific error scenarios encountered multiple times
- [ ] Users report confusion about error messages
- [ ] Common configuration mistakes emerge from usage
- [ ] Error scenarios cause user frustration or blocked usage

**Implementation Notes**:
When triggered, add to TROUBLESHOOTING.md "Common Errors" section:
- Document only errors users actually encounter
- Include error message text users see
- Provide step-by-step resolution for each error
- Show correct vs. incorrect configuration examples
- Link to relevant config.yml sections for reference

**Related Documents**:
- `.architecture/reviews/readme-pragmatic-implementation-docs.md`
- `.architecture/config.yml` (configuration reference)
- `.architecture/templates/config.yml` (template)
- `.architecture/members.yml` (members reference)

**Last Reviewed**: 2025-12-11

---

### Configuration Maintenance Guidance

**Status**: Deferred
**Deferred Date**: 2025-12-11
**Category**: Documentation
**Priority**: Medium

**What Was Deferred**:
Comprehensive guidance on when and how to review and update config.yml as team practices evolve over time.

**Original Proposal**:
Maintainability Expert recommended documenting configuration lifecycle:
- When to review config.yml (quarterly, when practices change, when team grows)
- How to update configurations as methodologies evolve
- Process for team consensus on configuration changes
- Handling configuration evolution across project lifetime
- Detecting when configuration has become stale
- Migration strategies for config updates

**Rationale for Deferring**:
- Necessity score: 6/10 (valuable long-term, not needed immediately)
- Complexity score: 5/10 (requires thoughtful process documentation)
- Ratio: 0.83 (acceptable for deferral)
- Cost of waiting: Low - configs are new, won't be stale for months
- No evidence of stale configurations yet (features just launched)
- Teams haven't had time for practices to evolve enough to require updates
- Don't know yet what triggers config updates in practice
- Better to document based on real config evolution patterns

**Simpler Current Approach**:
- Config.yml is version-controlled (changes tracked via git)
- Teams can update configs as needed
- No formal process until patterns emerge
- Document specific maintenance needs when they arise

**Trigger Conditions** (Implement when):
- [ ] 3+ projects observed with stale configurations (config doesn't match actual practices)
- [ ] Users ask "how often should we review config?"
- [ ] Teams report difficulty updating configurations
- [ ] Config drift becomes problematic for projects
- [ ] 6+ months have passed since feature launch (natural evolution time)

**Implementation Notes**:
When triggered, add to TROUBLESHOOTING.md "Maintenance" section:
- Base guidance on actual config evolution patterns observed
- Document triggers for config review that emerged from real projects
- Include examples of config updates from real projects (anonymized)
- Provide decision framework for when to update vs. keep stable
- Reference quarterly review process (ADR-005) for alignment

**Related Documents**:
- `.architecture/reviews/readme-pragmatic-implementation-docs.md`
- `.architecture/config.yml` (will evolve over time)
- ADR-005 § Quarterly Review Process (documentation governance)
- Future: Real config evolution examples

**Last Reviewed**: 2025-12-11

---

### "When NOT to Use" Anti-Patterns

**Status**: Deferred
**Deferred Date**: 2025-12-11
**Category**: Documentation
**Priority**: Low

**What Was Deferred**:
Guidance on when NOT to enable pragmatic mode or implementation guidance, including contraindications and anti-patterns.

**Original Proposal**:
Domain Expert recommended documenting:
- Scenarios where pragmatic mode is inappropriate
- When implementation guidance might not help
- Anti-patterns for feature usage
- Contraindications for enabling features
- Common misunderstandings about when to use features

**Rationale for Deferring**:
- Necessity score: 5/10 (helpful to prevent misuse, not critical yet)
- Complexity score: 3/10 (straightforward once misuse patterns known)
- Ratio: 0.6 (low enough to defer comfortably)
- Cost of waiting: Very low - no misuse observed yet
- Features are well-designed with appropriate defaults
- No evidence of users enabling features inappropriately
- Cannot document anti-patterns that haven't been observed
- Better to identify real misuse vs. speculate about hypothetical problems

**Simpler Current Approach**:
- README clearly explains what each feature does
- "When to use" guidance helps set appropriate expectations
- Exemptions (security, compliance) are clearly documented
- Monitor for actual misuse patterns

**Trigger Conditions** (Implement when):
- [ ] 3+ incidents of features being used inappropriately
- [ ] Users report unexpected results from feature usage
- [ ] Patterns emerge showing misunderstanding of feature purpose
- [ ] Support requests indicate confusion about when to enable
- [ ] Feedback suggests clearer contraindications needed

**Implementation Notes**:
When triggered, add to README or TROUBLESHOOTING.md:
- Document only observed anti-patterns, not theoretical ones
- Include real examples of misuse (anonymized)
- Explain why the usage was inappropriate
- Provide guidance on correct usage for those scenarios
- Keep focused on actionable guidance

**Related Documents**:
- `.architecture/reviews/readme-pragmatic-implementation-docs.md`
- `README.md` § Pragmatic Mode, § Implementation Guidance
- Future: Actual misuse examples if they emerge

**Last Reviewed**: 2025-12-11

---

### Command Variations Expansion

**Status**: Deferred
**Deferred Date**: 2025-12-11
**Category**: Documentation
**Priority**: Low

**What Was Deferred**:
Expanded documentation of alternative phrasings for enabling pragmatic mode and using features.

**Original Proposal**:
Systems Architect recommended documenting command variations:
- Alternative ways to say "Enable pragmatic mode"
- Variations like "Turn on YAGNI enforcement", "Activate pragmatic guard"
- Similar to how other commands show alternative phrases
- Help users discover natural language variations

**Rationale for Deferring**:
- Necessity score: 4/10 (nice to have, not essential)
- Complexity score: 2/10 (very simple to add)
- Ratio: 0.5 (borderline, but low necessity tips toward deferral)
- Cost of waiting: Very low - users finding commands successfully
- Natural language commands are working well
- No user questions about alternative phrasings
- Simple addition if users request it
- Users discovering variations through experimentation

**Simpler Current Approach**:
- Primary commands documented clearly
- AI assistants understand natural language variations
- Users can experiment with phrasings
- Add variations if users request them

**Trigger Conditions** (Implement when):
- [ ] Users request more command examples
- [ ] Support questions about how to phrase commands
- [ ] Feedback indicates command discovery is difficult
- [ ] Consistency with other sections demands this addition

**Implementation Notes**:
When triggered, add to README pragmatic mode section:
- List 3-5 alternative phrasings
- Similar to command variations shown for other features
- Keep concise (1-2 lines maximum)
- Based on phrasings users actually try

**Related Documents**:
- `.architecture/reviews/readme-pragmatic-implementation-docs.md`
- `README.md` § Pragmatic Mode

**Last Reviewed**: 2025-12-11

---

### Multi-Language Configuration Examples

**Status**: Deferred
**Deferred Date**: 2025-12-11
**Category**: Documentation
**Priority**: Low

**What Was Deferred**:
Example showing how to configure implementation guidance for polyglot projects (multiple programming languages).

**Original Proposal**:
Maintainability Expert recommended adding example:
- Show Ruby + JavaScript configuration in same project
- Clarify how to handle different languages simultaneously
- Demonstrate language-specific practices configuration
- Support polyglot codebases explicitly

**Rationale for Deferring**:
- Necessity score: 6/10 (valuable for polyglot projects, not universal)
- Complexity score: 2/10 (simple example to add)
- Ratio: 0.33 (low ratio, but necessity not universal enough for immediate addition)
- Cost of waiting: Low - single-language examples generalize well
- Most projects are primarily single-language
- Config.yml template shows multiple language examples (commented out)
- Users can extrapolate from single-language examples
- No user questions about multi-language configuration yet

**Simpler Current Approach**:
- Config template shows structure for multiple languages
- Example shows one language clearly
- Users can add additional language sections following same pattern
- Add explicit multi-language example if users request it

**Trigger Conditions** (Implement when):
- [ ] 3+ users ask about multi-language configuration
- [ ] Polyglot project support requests
- [ ] Users report confusion about configuring multiple languages
- [ ] Multi-language projects become more common in user base

**Implementation Notes**:
When triggered, add to README Implementation Guidance section:
- Show realistic 2-language example (e.g., Ruby backend + React frontend)
- Demonstrate how practices differ between languages
- Keep example concise (5-10 lines)
- Reference config.yml template for full options

**Related Documents**:
- `.architecture/reviews/readme-pragmatic-implementation-docs.md`
- `README.md` § Implementation Guidance
- `.architecture/templates/config.yml` (has multi-language structure)

**Last Reviewed**: 2025-12-11

---

### Progressive Disclosure Performance Benefits

**Status**: Deferred
**Deferred Date**: 2025-12-11
**Category**: Documentation
**Priority**: Low

**What Was Deferred**:
Explanation in README of how progressive disclosure pattern (ADR-005) optimizes AI assistant performance.

**Original Proposal**:
Performance Specialist recommended brief callout:
- Explain why documentation is structured progressively
- Connect to instruction capacity constraints (ADR-005)
- Help users understand framework documentation design
- Show how respecting LLM limits improves AI performance

**Rationale for Deferring**:
- Necessity score: 4/10 (interesting context, not essential for feature use)
- Complexity score: 2/10 (brief explanation, simple to add)
- Ratio: 0.5 (low complexity, but also low necessity)
- Cost of waiting: Very low - feature works without this explanation
- Users don't need to understand why documentation is structured this way to use it
- Meta-explanation of documentation strategy may add cognitive load
- ADR-005 exists for those interested in the rationale
- Documentation structure speaks for itself through usage

**Simpler Current Approach**:
- Documentation works well without explaining why it's structured this way
- ADR-005 thoroughly documents progressive disclosure rationale
- Users can read ADRs if interested in design decisions
- Focus README on "what" and "how", not "why structured this way"

**Trigger Conditions** (Implement when):
- [ ] Users ask why documentation is structured this way
- [ ] Confusion emerges about information distribution across files
- [ ] Users interested in framework design principles behind structure
- [ ] Educational value justifies meta-documentation

**Implementation Notes**:
When triggered, consider adding brief note to README or AGENTS.md:
- Keep very concise (1-2 sentences maximum)
- Link to ADR-005 for detailed explanation
- Focus on user benefit, not technical implementation
- Place where it provides context without disrupting flow

**Related Documents**:
- `.architecture/reviews/readme-pragmatic-implementation-docs.md`
- ADR-005 (progressive disclosure pattern and rationale)
- `README.md`, `AGENTS.md` (documentation structure)

**Last Reviewed**: 2025-12-11

---

### Config Parsing Performance Clarification

**Status**: Deferred
**Deferred Date**: 2025-12-11
**Category**: Documentation
**Priority**: Low

**What Was Deferred**:
Brief note clarifying that config.yml parsing has negligible performance overhead.

**Original Proposal**:
Performance Specialist recommended adding clarification:
- Note that YAML parsing is fast
- Config parsed once per session, negligible overhead
- Address potential user concerns about performance cost
- Reassure users that configuration-driven approach has no meaningful latency

**Rationale for Deferring**:
- Necessity score: 3/10 (addresses concern that may not exist)
- Complexity score: 1/10 (single sentence addition)
- Ratio: 0.33 (very low complexity, but also very low necessity)
- Cost of waiting: Zero - no users have raised performance concerns
- Config parsing is clearly fast in practice
- No evidence users are worried about this
- Speculative concern, not actual user question
- Only add if users actually worry about performance

**Simpler Current Approach**:
- Config parsing works well without explanation
- Performance is obviously fine in practice
- Address if users raise concerns

**Trigger Conditions** (Implement when):
- [ ] User asks about config parsing performance
- [ ] Concerns raised about configuration overhead
- [ ] Performance-sensitive users question approach

**Implementation Notes**:
When triggered, add brief parenthetical note:
- Single sentence or parenthetical
- "(Config parsed once per session, negligible overhead)"
- Place in Implementation Guidance section if added

**Related Documents**:
- `.architecture/reviews/readme-pragmatic-implementation-docs.md`
- `README.md` § Implementation Guidance

**Last Reviewed**: 2025-12-11

---

### Version Consistency Verification

**Status**: Deferred
**Deferred Date**: 2025-12-11
**Category**: Maintenance
**Priority**: Low

**What Was Deferred**:
Audit of all framework documentation files to ensure version number consistency (verify all show 1.2.0).

**Original Proposal**:
Systems Architect recommended verification:
- Audit all docs for version 1.2.0
- Ensure consistency across README, config templates, ADRs
- Catch any stale version references
- Professional consistency check

**Rationale for Deferring**:
- Necessity score: 4/10 (good practice, not critical to function)
- Complexity score: 2/10 (simple grep and update task)
- Ratio: 0.5 (low on both dimensions)
- Cost of waiting: Very low - version inconsistency is cosmetic
- No user confusion from version references
- Can be done during next regular documentation audit
- Part of normal documentation maintenance
- Not blocking any functionality

**Simpler Current Approach**:
- Address version consistency during quarterly documentation review
- Update as part of normal maintenance cycle
- Fix if noticed during other updates

**Trigger Conditions** (Implement when):
- [ ] Quarterly documentation review cycle
- [ ] User reports version inconsistency
- [ ] Preparing for new version release (1.3.0)
- [ ] General documentation audit performed

**Implementation Notes**:
When triggered:
- Grep for version references across all docs
- Update to current version (1.2.0 or later)
- Document version number convention for future
- Consider automation if becomes recurring issue

**Related Documents**:
- `.architecture/reviews/readme-pragmatic-implementation-docs.md`
- All framework documentation (README, config.yml, ADRs, etc.)
- ADR-005 § Quarterly Review Process

**Last Reviewed**: 2025-12-11

---

## Review Process

This document should be reviewed:

**Monthly**: Check for triggered conditions
- Review each deferred item
- Check if any trigger conditions have been met
- Update priority if context has changed

**Quarterly**: Re-evaluate deferrals
- Are deferred items still relevant?
- Have requirements changed?
- Should priority be adjusted?
- Can any be cancelled?

**During Architecture Reviews**: Reference deferrals
- Check if new features relate to deferrals
- Consider if triggered conditions met
- Avoid re-proposing already-deferred items
- Update relevant entries

**When Triggers Met**:
1. Update status to "Triggered"
2. Create or update ADR for implementation
3. Plan implementation in next sprint/release
4. Reference this deferral in the ADR
5. After implementation, update status to "Implemented"

## Metrics

Track deferral outcomes to improve decision-making:

| Metric | Value | Notes |
|--------|-------|-------|
| Total deferrals | 22 | All-time count (3 Phase 2B + 4 Phase 3B + 5 Phase 4B + 10 README docs) |
| Active deferrals | 22 | Currently deferred |
| Triggered awaiting implementation | 0 | Need to address |
| Implemented | 0 | Were eventually needed |
| Cancelled | 0 | Were never needed |
| Average time before trigger | - | How long before we needed it |
| Hit rate (implemented/total) | 0% | How often deferred things are needed |

**Target**: < 40% hit rate (most deferred things remain unneeded, validating deferral decisions)

---

## Template for New Deferrals

When adding a deferral, use this format:

```markdown
### [Feature/Pattern Name]

**Status**: Deferred
**Deferred Date**: YYYY-MM-DD
**Category**: [Architecture | Performance | Testing | Infrastructure | Security]
**Priority**: [Low | Medium | High]

**What Was Deferred**:
[Brief description of the feature, pattern, or complexity that was deferred]

**Original Proposal**:
[What was originally suggested - can quote from review or ADR]

**Rationale for Deferring**:
- Current need score: [0-10]
- Complexity score: [0-10]
- Cost of waiting: [Low | Medium | High]
- Why deferring makes sense: [Explanation]

**Simpler Current Approach**:
[What we're doing instead for now]

**Trigger Conditions** (Implement when):
- [ ] [Specific condition 1 - make this measurable]
- [ ] [Specific condition 2]
- [ ] [Specific condition 3]

**Implementation Notes**:
[Notes for when this is implemented - gotchas, considerations, references]

**Related Documents**:
- [Link to ADR or review]
- [Link to discussion]

**Last Reviewed**: YYYY-MM-DD
```

---

*See `.architecture/templates/deferrals.md` for detailed examples of deferral entries.*
