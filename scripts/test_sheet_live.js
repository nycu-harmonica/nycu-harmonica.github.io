'use strict';

const assert = require('node:assert/strict');
const sheetLive = require('../assets/js/sheet-live.js');

function payload(headers, rows) {
  const cells = (values) => ({ c: values.map((value) => value === '' || value == null ? null : { v: value }) });
  return {
    status: 'ok',
    table: {
      cols: headers.map((_header, index) => ({ id: String.fromCharCode(65 + index), type: 'string' })),
      rows: [cells(headers), ...rows.map(cells)]
    }
  };
}

function payloadWithColumnLabels(headers, rows) {
  const value = payload(headers, rows);
  value.table.cols = headers.map((header, index) => ({ id: String.fromCharCode(65 + index), type: 'string', label: header }));
  value.table.rows = value.table.rows.slice(1);
  return value;
}

function fixtures() {
  return {
    gallery_albums: payload(
      ['slug', 'title', 'date', 'description', 'cover', 'status'],
      [
        ['older-album', '舊相簿', '2025-12-20', '舊活動紀錄。', '', ''],
        ['newer-album', '新相簿', '2026-10-15', '活動紀錄,社員合照。', 'cover.webp', 'published']
      ]
    ),
    links: payload(
      ['key', 'label', 'url', 'icon', 'order', 'show_in'],
      [
        ['facebook', 'Facebook 粉絲專頁', 'https://www.facebook.com/example/', 'facebook', '20', 'footer,about'],
        ['discord', 'Discord 社群', 'https://discord.gg/example', 'link', '10', 'footer,about,join']
      ]
    ),
    chronology_events: payload(
      ['id', 'sort_date', 'date_label', 'category', 'tags', 'statement', 'source_label', 'source_url', 'evidence', 'status'],
      [
        ['later-event', '2026-07-01', '2026/07/01', '活動', '活動|演出', '2026 年舉辦公開活動。', '公開行事曆', 'https://example.com/later', 'A1', ''],
        ['early-event', '1968-04-08', '1968/04/08', '創社', '社史|人物', '竹韻口琴社成立。', '官方說明', 'https://example.com/early', 'A1', '']
      ]
    )
  };
}

function testNormalizeAndSort() {
  const data = fixtures();
  const albums = sheetLive.normalizeTab('gallery_albums', data.gallery_albums);
  const links = sheetLive.normalizeTab('links', data.links);
  const chronology = sheetLive.normalizeTab('chronology_events', data.chronology_events);
  assert.deepEqual(albums.map((row) => row.slug), ['newer-album', 'older-album']);
  assert.equal(albums[0].description, '活動紀錄，社員合照。');
  assert.deepEqual(links.map((row) => row.key), ['discord', 'facebook']);
  assert.deepEqual(chronology.map((row) => row.id), ['later-event', 'early-event']);
  assert.equal(chronology[1].tags, '社史|人物');
  assert.equal(chronology[1].statement, '竹韻口琴社成立。');
}

function testChineseHeaders() {
  const value = payload(
    ['代號', '標題', '日期', '說明', '狀態'],
    [['spring-concert', '春季成發', '2026-04-12', '成果發表', '發布']]
  );
  assert.equal(sheetLive.normalizeTab('gallery_albums', value)[0].title, '春季成發');
}

function testGvizColumnLabels() {
  const value = payloadWithColumnLabels(
    ['id', 'sort_date', 'date_label', 'category', 'statement', 'source_label', 'source_url'],
    [['labeled-event', '1968-04-08', '1968/04/08', '創社', '竹韻口琴社成立。', '來源', 'https://example.com/']]
  );
  const rows = sheetLive.normalizeTab('chronology_events', value);
  assert.equal(rows[0].id, 'labeled-event');
  assert.equal(rows[0].date_label, '1968/04/08');
}

function testInvalidTablesAreRejected() {
  const invalid = [
    ['links', payload(['key', 'label', 'url', 'token'], [['discord', 'Discord', 'https://example.com/', 'secret']])],
    ['links', payload(['key', 'label', 'url'], [['discord', 'Discord', 'javascript:alert(1)']])],
    ['links', payload(['key', 'label', 'url'], [['discord', 'A', 'https://example.com/a'], ['discord', 'B', 'https://example.com/b']])],
    ['gallery_albums', payload(['slug', 'title', 'date'], [['bad-album', '標題', '2026-02-30']])],
    ['gallery_albums', payload(['slug', 'title', 'date'], [['bad-album', '<script>', '2026-04-12']])],
    ['links', payload(['key', 'label', 'url'], [['discord', 'Discord', 'https://example.com/'], ['discord', 'Dup', 'https://example.com/b']])]
    ,['chronology_events', payload(['id', 'sort_date', 'date_label', 'category', 'statement', 'source_label', 'source_url'], [['bad-event', '2026-02-30', 'bad', '活動', '敘述', '來源', 'https://example.com/']])]
    ,['chronology_events', payload(['id', 'sort_date', 'date_label', 'category', 'statement', 'source_label', 'source_url'], [['bad-event', '2026-04-12', '2026/04/12', '活動', '<script>', '來源', 'https://example.com/']])]
  ];
  invalid.forEach(([tab, value]) => assert.throws(() => sheetLive.normalizeTab(tab, value), Error));
}

function testUnnamedExtraColumnIsRejected() {
  const value = payload(['key', 'label', 'url', ''], [['discord', 'Discord', 'https://example.com/', '不應公開']]);
  assert.throws(() => sheetLive.normalizeTab('links', value), /未命名欄位/);
}

function testGvizUrl() {
  const config = {
    sheetId: '19facgxayMMiYSz1gNmoQRtkY_EjLTYiRyyTa6KfYWic',
    tabs: { links: { gid: '1378930118' } }
  };
  const url = new URL(sheetLive.buildGvizUrl(config, 'links', '__callback_123', 42));
  assert.equal(url.origin, 'https://docs.google.com');
  assert.equal(url.searchParams.get('gid'), '1378930118');
  assert.equal(url.searchParams.get('tqx'), 'out:json;responseHandler:__callback_123');
  assert.equal(url.searchParams.get('headers'), '1');
  assert.equal(url.searchParams.get('_'), '42');
}

async function testAtomicRefresh() {
  const values = fixtures();
  let renders = 0;
  let renderedData;
  const success = await sheetLive.refreshSheetData({
    document: {},
    config: { sheetId: 'unused', tabs: {} },
    loadTab: async (tab) => values[tab],
    renderImpl: (_doc, data) => { renders += 1; renderedData = data; },
    fetchedAt: new Date('2026-07-18T00:00:00Z')
  });
  assert.equal(success, true);
  assert.equal(renders, 1);
  assert.equal(renderedData.links[0].key, 'discord');

  const broken = Object.assign({}, values, {
    links: payload(['key', 'label', 'url'], [['discord', 'Discord', 'http://insecure.example.com/']])
  });
  const failed = await sheetLive.refreshSheetData({
    document: {},
    config: { sheetId: 'unused', tabs: {} },
    loadTab: async (tab) => broken[tab],
    renderImpl: () => { renders += 1; }
  });
  assert.equal(failed, false);
  assert.equal(renders, 1, '任一工作表失敗時不可局部 render');
}

async function main() {
  testNormalizeAndSort();
  testChineseHeaders();
  testInvalidTablesAreRejected();
  testUnnamedExtraColumnIsRejected();
  testGvizUrl();
  await testAtomicRefresh();
  console.log('Sheet live tests passed.');
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
