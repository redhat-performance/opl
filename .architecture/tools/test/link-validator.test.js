import { describe, it } from 'node:test';
import assert from 'node:assert';
import { validateLinks, checkLinks } from '../lib/link-validator.js';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

describe('Link Validator', () => {
  describe('validateLinks', () => {
    it('returns empty array when no markdown links found', () => {
      const content = 'This is plain text without links.';
      const result = validateLinks(content, '/test.md');

      assert.strictEqual(result.length, 0);
    });

    it('extracts markdown links from content', () => {
      const content = 'Check [this](./file.md) and [that](../other.md)';
      const result = validateLinks(content, '/test.md');

      assert.strictEqual(result.length, 2);
      assert.strictEqual(result[0].target, './file.md');
      assert.strictEqual(result[1].target, '../other.md');
    });

    it('ignores external HTTP links', () => {
      const content = 'See [docs](https://example.com) for details';
      const result = validateLinks(content, '/test.md');

      assert.strictEqual(result.length, 0);
    });

    it('ignores anchor-only links', () => {
      const content = 'Jump to [section](#heading)';
      const result = validateLinks(content, '/test.md');

      assert.strictEqual(result.length, 0);
    });

    it('includes line numbers for each link', () => {
      const content = 'Line 1\nCheck [link](./file.md) here\nLine 3';
      const result = validateLinks(content, '/test.md');

      assert.strictEqual(result[0].line, 2);
    });
  });

  describe('checkLinks', () => {
    it('resolves relative paths from source file', () => {
      const links = [
        { target: './link-validator.test.js', line: 1, file: 'test/source.md' }
      ];
      const baseDir = path.join(__dirname, '..');

      const result = checkLinks(links, baseDir);

      assert.strictEqual(result.valid.length, 1);
      assert.strictEqual(result.broken.length, 0);
    });

    it('identifies broken links', () => {
      const links = [
        { target: './nonexistent.md', line: 1, file: 'test/source.md' }
      ];
      const baseDir = path.join(__dirname, '..');

      const result = checkLinks(links, baseDir);

      assert.strictEqual(result.valid.length, 0);
      assert.strictEqual(result.broken.length, 1);
      assert.strictEqual(result.broken[0].target, './nonexistent.md');
    });

    it('handles parent directory references', () => {
      const links = [
        { target: '../package.json', line: 1, file: 'test/source.md' }
      ];
      const baseDir = path.join(__dirname, '..');

      const result = checkLinks(links, baseDir);

      assert.strictEqual(result.valid.length, 1);
    });

    it('reports all broken links with details', () => {
      const links = [
        { target: './missing1.md', line: 5, file: 'doc.md', text: 'Link 1' },
        { target: './missing2.md', line: 10, file: 'doc.md', text: 'Link 2' }
      ];
      const baseDir = path.join(__dirname, '..');

      const result = checkLinks(links, baseDir);

      assert.strictEqual(result.broken.length, 2);
      assert.ok(result.broken[0].text);
      assert.ok(result.broken[0].line);
    });
  });
});
