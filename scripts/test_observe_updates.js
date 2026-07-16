'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const observe = require('../assets/js/observe-updates.js');

class FakeElement {
  constructor(tag) {
    this.tagName = tag;
    this.className = '';
    this.children = [];
    this.dataset = {};
    this.attributes = {};
    this.textContent = '';
  }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  setAttribute(name, value) { this.attributes[name] = String(value); }
}

class FakeDocument {
  constructor(grid, status) { this.elements = { 'observe-updates-grid': grid, 'observe-updates-status': status }; }
  createElement(tag) { return new FakeElement(tag); }
  getElementById(id) { return this.elements[id] || null; }
}

function item(overrides = {}) {
  return Object.assign({
    id: 'post-1234abcd', title: '社團成果發表~', excerpt: '不可顯示',
    url: 'https://example.com/post/1', sourceName: '陽明交大竹韻口琴社',
    platform: 'Instagram', publishedAt: '2026-07-16T11:30:00Z'
  }, overrides);
}

function payload(items = [item()]) {
  return {
    schemaVersion: 1,
    generatedAt: '2026-07-16T11:45:00Z',
    source: {
      id: 198, slug: 'bamboo-melody-harmonica-club', name: '陽明交大竹韻口琴社',
      pageUrl: 'https://harmonica.observe.tw/source/198-bamboo-melody-harmonica-club/'
    },
    items
  };
}

function fixture() {
  const grid = new FakeElement('div');
  const fallback = new FakeElement('article');
  fallback.textContent = 'fallback';
  grid.append(fallback);
  const status = new FakeElement('p');
  status.textContent = '上次同步資料';
  return { grid, status, fallback, document: new FakeDocument(grid, status) };
}

function response(value, ok = true, contentLength = '1031') {
  const raw = typeof value === 'string' ? value : JSON.stringify(value);
  return {
    ok,
    status: ok ? 200 : 503,
    headers: { get: () => contentLength },
    text: async () => raw
  };
}

async function testSuccessReplacesFallbackAtomically() {
  const view = fixture();
  const changed = await observe.refreshObserveUpdates({
    document: view.document, grid: view.grid, status: view.status,
    fetchImpl: async () => response(payload())
  });
  assert.equal(changed, true);
  assert.equal(view.grid.children.length, 1);
  assert.notEqual(view.grid.children[0], view.fallback);
  const link = view.grid.children[0].children[0].children[1].children[0];
  assert.equal(link.textContent, '社團成果發表～');
  assert.equal(link.attributes.href, 'https://example.com/post/1');
  assert.equal(link.attributes.rel, 'noopener noreferrer');
  assert.equal(view.grid.dataset.observeMode, 'live');
  assert.match(view.status.textContent, /^即時資料：/);
}

async function testInvalidPayloadsKeepFallback() {
  const invalid = [
    Object.assign(payload(), { schemaVersion: 2 }),
    Object.assign(payload(), { source: Object.assign({}, payload().source, { id: 71 }) }),
    payload([item({ url: 'javascript:alert(1)' })]),
    payload([item({ title: '<img src=x onerror=alert(1)>' })]),
    payload([item({ sourceName: '其他口琴社' })]),
    payload([])
  ];
  for (const value of invalid) {
    const view = fixture();
    const changed = await observe.refreshObserveUpdates({
      document: view.document, grid: view.grid, status: view.status,
      fetchImpl: async () => response(value)
    });
    assert.equal(changed, false);
    assert.deepEqual(view.grid.children, [view.fallback]);
    assert.equal(view.status.textContent, '上次同步資料');
  }
}

async function testHttpFailureKeepsFallback() {
  const view = fixture();
  const changed = await observe.refreshObserveUpdates({
    document: view.document, grid: view.grid, status: view.status,
    fetchImpl: async () => response(payload(), false)
  });
  assert.equal(changed, false);
  assert.deepEqual(view.grid.children, [view.fallback]);
}

async function testActualBodyLimitAndMalformedJsonKeepFallback() {
  const oversized = Object.assign(payload(), { padding: '界'.repeat(400000) });
  const responses = [
    response(oversized, true, null),
    response(oversized, true, '100'),
    response('{malformed json', true, null)
  ];
  for (const remoteResponse of responses) {
    const view = fixture();
    const changed = await observe.refreshObserveUpdates({
      document: view.document, grid: view.grid, status: view.status,
      fetchImpl: async () => remoteResponse
    });
    assert.equal(changed, false);
    assert.deepEqual(view.grid.children, [view.fallback]);
    assert.equal(view.status.textContent, '上次同步資料');
  }
}

async function testTimeoutKeepsFallback() {
  const view = fixture();
  const fetchImpl = (_url, options) => new Promise((_resolve, reject) => {
    options.signal.addEventListener('abort', () => reject(new Error('aborted')));
  });
  const changed = await observe.refreshObserveUpdates({
    document: view.document, grid: view.grid, status: view.status, fetchImpl, timeoutMs: 1
  });
  assert.equal(changed, false);
  assert.deepEqual(view.grid.children, [view.fallback]);
}

function testNoRemoteInnerHtmlSink() {
  const source = fs.readFileSync(path.join(__dirname, '../assets/js/observe-updates.js'), 'utf8');
  assert.equal(source.includes('innerHTML'), false);
  assert.equal(observe.normalizeDisplayText('中文~更新!'), '中文～更新！');
}

async function main() {
  const tests = [
    testSuccessReplacesFallbackAtomically,
    testInvalidPayloadsKeepFallback,
    testHttpFailureKeepsFallback,
    testActualBodyLimitAndMalformedJsonKeepFallback,
    testTimeoutKeepsFallback,
    testNoRemoteInnerHtmlSink
  ];
  for (const test of tests) {
    await test();
    console.log('ok  ', test.name);
  }
  console.log(`\n${tests.length}/${tests.length} passed`);
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
