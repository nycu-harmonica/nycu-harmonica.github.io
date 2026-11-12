// Freeze every external data source once per hill climb, so the baseline and
// each candidate are photographed against identical data.
//   node fixtures.mjs REPO_DIR DATA_DIR
//
// Writes into DATA_DIR:
//   gviz/<tab>.json        Google Visualization tables built from the repo's
//                          committed last-good CSVs (static/data/*.csv)
//   observe.json           Observatory /api/source/198.json shape, built from
//                          data/generated/observe_updates.json
//   assets/<path>          Observatory-cached images used by those posts
//   discord.json           one real public Discord invite response
//   calendar.har           one recording of the public Google Calendar embed
//   calendar-empty.{har,html}  the same embed for a range with no events
// Nothing is written to any production source; every request here is a GET.
import { chromium } from 'playwright';
import { mkdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';

const [repo, out] = process.argv.slice(2);
mkdirSync(join(out, 'gviz'), { recursive: true });

function parseCsv(text) {
  const rows = [];
  let row = [], field = '', quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') { field += '"'; i += 1; }
      else if (ch === '"') quoted = false;
      else field += ch;
    } else if (ch === '"') quoted = true;
    else if (ch === ',') { row.push(field); field = ''; }
    else if (ch === '\n' || ch === '\r') {
      if (ch === '\r' && text[i + 1] === '\n') i += 1;
      row.push(field); field = '';
      if (row.some((cell) => cell !== '')) rows.push(row);
      row = [];
    } else field += ch;
  }
  if (field || row.length) { row.push(field); rows.push(row); }
  return rows;
}

for (const tab of ['chronology_events', 'gallery_albums', 'links']) {
  const [header, ...rows] = parseCsv(readFileSync(join(repo, 'static/data', `${tab}.csv`), 'utf8').replace(/^﻿/, ''));
  const table = {
    cols: header.map((label, index) => ({ id: String.fromCharCode(65 + index), label, type: 'string' })),
    rows: rows.map((cells) => ({ c: header.map((_, index) => (cells[index] ? { v: cells[index] } : null)) })),
  };
  writeFileSync(join(out, 'gviz', `${tab}.json`), JSON.stringify(table));
}

const observe = JSON.parse(readFileSync(join(repo, 'data/generated/observe_updates.json'), 'utf8'));
const api = {
  schemaVersion: 1,
  generatedAt: observe.source_generated_at,
  source: { id: 198, slug: observe.source.slug, name: observe.source.name, pageUrl: observe.source.page_url },
  items: observe.items.map((item) => ({
    id: item.id, title: item.title, url: item.link, sourceName: item.source, platform: item.platform,
    image: item.image, publishedAt: item.posted_at_local.replace(/\//g, '-').replace(' ', 'T') + ':00+08:00',
  })),
};
writeFileSync(join(out, 'observe.json'), JSON.stringify(api, null, 2));
for (const item of observe.items) {
  if (!item.image) continue;
  const path = join(out, 'assets', new URL(item.image.url).pathname.replace(/^\/assets\//, ''));
  if (existsSync(path)) continue;
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, Buffer.from(await (await fetch(item.image.url)).arrayBuffer()));
}

if (!existsSync(join(out, 'discord.json'))) {
  const response = await fetch('https://discord.com/api/v10/invites/uEQDCbnY8P?with_counts=true&with_expiration=true', { headers: { Accept: 'application/json' } });
  const invite = await response.json();
  // Keep only what the landing page reads.
  writeFileSync(join(out, 'discord.json'), JSON.stringify({
    guild: { name: invite.guild?.name, description: invite.guild?.description },
    approximate_presence_count: invite.approximate_presence_count,
    approximate_member_count: invite.approximate_member_count,
  }, null, 2));
}

const CAL = 'https://calendar.google.com/calendar/embed?src=bmhc1968%40gmail.com&ctz=Asia%2FTaipei&hl=zh_TW&mode=AGENDA&showTitle=0&showPrint=0&showCalendars=0&showTz=0&showTab=1&wkst=1';
if (!existsSync(join(out, 'calendar.har'))) {
  const browser = await chromium.launch();
  const context = await browser.newContext({ recordHar: { path: join(out, 'calendar.har'), urlFilter: /google|gstatic/, content: 'embed' }, locale: 'zh-TW', timezoneId: 'Asia/Taipei' });
  const page = await context.newPage();
  await page.goto(CAL, { waitUntil: 'networkidle', timeout: 45000 }).catch(() => {});
  await page.waitForTimeout(3000);
  await page.screenshot({ path: join(out, 'calendar-recorded.png') });
  await context.close();
  await browser.close();
}
if (!existsSync(join(out, 'calendar-empty.har'))) {
  // An agenda for a range with no events, served in place of the embed for the
  // empty state. Recorded as its own HAR so its event request replays too.
  const browser = await chromium.launch();
  const empty = await browser.newContext({ recordHar: { path: join(out, 'calendar-empty.har'), urlFilter: /google|gstatic/, content: 'embed' }, locale: 'zh-TW', timezoneId: 'Asia/Taipei' });
  const emptyPage = await empty.newPage();
  const response = await emptyPage.goto(CAL + '&dates=20990101%2F20990131', { waitUntil: 'networkidle', timeout: 45000 }).catch(() => null);
  if (response) writeFileSync(join(out, 'calendar-empty.html'), await response.text());
  await emptyPage.waitForTimeout(3000);
  await emptyPage.screenshot({ path: join(out, 'calendar-empty.png') });
  await empty.close();
  await browser.close();
}
console.log('fixtures ready in', out);
