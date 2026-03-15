import { describe, it } from 'node:test';
import assert from 'node:assert';
import { countInstructions } from '../lib/instruction-counter.js';

describe('Instruction Counter', () => {
  describe('countInstructions', () => {
    it('counts command/directive instructions', () => {
      const content = `
- Create ADR for [topic]
- Follow TDD methodology
- Apply pragmatic analysis
      `;

      const result = countInstructions(content);

      assert.strictEqual(result.commands.length, 3);
    });

    it('counts conditional instructions', () => {
      const content = `
If pragmatic_mode.enabled: Apply YAGNI
When conducting reviews: Adopt member personas
      `;

      const result = countInstructions(content);

      assert.ok(result.conditionals.length >= 2);
    });

    it('counts procedure steps', () => {
      const content = `
1. Analyze project structure
2. Customize templates
3. Create directories
      `;

      const result = countInstructions(content);

      assert.ok(result.procedures.length >= 3);
    });

    it('does not count informational content', () => {
      const content = `
The framework provides architecture documentation.
Version 1.2.0 was released in 2025.
This file contains cross-platform instructions.
      `;

      const result = countInstructions(content);

      assert.strictEqual(result.total, 0);
    });

    it('does not count headings', () => {
      const content = `
## Core Workflows
### Setup Procedures
#### Installation
      `;

      const result = countInstructions(content);

      assert.strictEqual(result.total, 0);
    });

    it('returns total count', () => {
      const content = `
- Create ADR for topic
- If enabled: Apply mode
1. Analyze structure
      `;

      const result = countInstructions(content);

      assert.strictEqual(result.total, 3);
    });

    it('identifies guideline instructions', () => {
      const content = `
- Keep CLAUDE.md < 100 lines
- Never compromise security
      `;

      const result = countInstructions(content);

      assert.ok(result.guidelines.length >= 2);
    });
  });
});
