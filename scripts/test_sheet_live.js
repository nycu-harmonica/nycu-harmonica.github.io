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

function fixtures() {
  return {
    officers: payload(
      ['order', 'role', 'name', 'status'],
      [['20', '副社長', '凱鈞', 'published'], ['10', '社長', '軾凱', '公開'], ['30', '行政', '草稿姓名', 'draft']]
    ),
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
    )
  };
}

function testNormalizeAndSort() {
  const data = fixtures();
  const officers = sheetLive.normalizeTab('officers', data.officers);
  const albums = sheetLive.normalizeTab('gallery_albums', data.gallery_albums);
  const links = sheetLive.normalizeTab('links', data.links);
  assert.deepEqual(officers.map((row) => row.name), ['軾凱', '凱鈞']);
  assert.deepEqual(albums.map((row) => row.slug), ['newer-album', 'older-album']);
  assert.equal(albums[0].description, '活動紀錄，社員合照。');
  assert.deepEqual(links.map((row) => row.key), ['discord', 'facebook']);
}

function testChineseHeaders() {
  const value = payload(
    ['排序', '職稱', '姓名', '狀態'],
    [['10', '社長', '軾凱', '發布']]
  );
  assert.equal(sheetLive.normalizeTab('officers', value)[0].role, '社長');
}

function testInvalidTablesAreRejected() {
  const invalid = [
    ['links', payload(['key', 'label', 'url', 'token'], [['discord', 'Discord', 'https://example.com/', 'secret']])],
    ['links', payload(['key', 'label', 'url'], [['discord', 'Discord', 'javascript:alert(1)']])],
    ['links', payload(['key', 'label', 'url'], [['discord', 'A', 'https://example.com/a'], ['discord', 'B', 'https://example.com/b']])],
    ['gallery_albums', payload(['slug', 'title', 'date'], [['bad-album', '標題', '2026-02-30']])],
    ['officers', payload(['order', 'role', 'name'], [['ten', '社長', '軾凱']])],
    ['officers', payload(['order', 'role', 'name'], [['10', '社長', '<script>']])]
  ];
  invalid.forEach(([tab, value]) => assert.throws(() => sheetLive.normalizeTab(tab, value), Error));
}

function testUnnamedExtraColumnIsRejected() {
  const value = payload(['order', 'role', 'name', ''], [['10', '社長', '軾凱', '不應公開']]);
  assert.throws(() => sheetLive.normalizeTab('officers', value), /未命名欄位/);
}

function testGvizUrl() {
  const config = {
    sheetId: '19facgxayMMiYSz1gNmoQRtkY_EjLTYiRyyTa6KfYWic',
    tabs: { officers: { gid: '531284051' } }
  };
  const url = new URL(sheetLive.buildGvizUrl(config, 'officers', '__callback_123', 42));
  assert.equal(url.origin, 'https://docs.google.com');
  assert.equal(url.searchParams.get('gid'), '531284051');
  assert.equal(url.searchParams.get('tqx'), 'out:json;responseHandler:__callback_123');
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
  assert.equal(renderedData.officers[0].name, '軾凱');

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
