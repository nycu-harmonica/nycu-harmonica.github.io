// Photograph every state in states.mjs against the frozen fixtures.
//   node capture.mjs site http://127.0.0.1:8411 OUT_DIR [DATA_DIR] [id-filter]
//   node capture.mjs references OUT_DIR
// One browser, one page at a time. Every request that leaves 127.0.0.1 is
// either answered from DATA_DIR (default /tmp/bmhc-review/data) or aborted, so
// no production data source is read or written while shooting.
import { chromium } from 'playwright';
import { mkdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { SIZES, STATES, REFERENCES, NOW } from './states.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const [mode, ...rest] = process.argv.slice(2);
const browser = await chromium.launch();

const CORS = { 'access-control-allow-origin': '*', 'cache-control': 'no-store' };
const hang = () => new Promise(() => {});

function loadData(dir) {
  const sources = JSON.parse(readFileSync(join(HERE, '../../../scripts/sources.json'), 'utf8'));
  const tabByGid = Object.fromEntries(Object.entries(sources.tabs).map(([tab, { gid }]) => [String(gid), tab]));
  const gviz = Object.fromEntries(Object.values(tabByGid).map((tab) => [tab, JSON.parse(readFileSync(join(dir, 'gviz', `${tab}.json`), 'utf8'))]));
  const har = JSON.parse(readFileSync(join(dir, 'calendar.har'), 'utf8'));
  const embed = har.log.entries.find((entry) => entry.request.url.includes('/calendar/embed?') && entry.response.status === 200);
  return {
    dir, tabByGid, gviz, harPath: join(dir, 'calendar.har'),
    calendarHtml: Buffer.from(embed.response.content.text, embed.response.content.encoding === 'base64' ? 'base64' : 'utf8'),
    eventEntries: har.log.entries.filter((entry) => /calendar\/v3\/calendars\/[^/]+\/events/.test(entry.request.url)),
    observe: JSON.parse(readFileSync(join(dir, 'observe.json'), 'utf8')),
    discord: JSON.parse(readFileSync(join(dir, 'discord.json'), 'utf8')),
  };
}

async function installRoutes(context, data, state) {
  const mode = state.data;
  // Lowest precedence: nothing else may leave the machine.
  await context.route((url) => !['127.0.0.1', 'localhost'].includes(url.hostname), (route) => route.abort('blockedbyclient'));
  // Google Calendar embed: replay one frozen recording.
  if (mode === 'normal' || mode === 'empty') {
    await context.routeFromHAR(data.harPath, { url: /google\.com|gstatic\.com|googleusercontent\.com/, notFound: 'abort' });
  }
  if (mode === 'empty') {
    // Same recording, same months on screen, but the calendar has no events.
    await context.route(/clients6\.google\.com\/calendar\/v3\/calendars\/[^/]+\/events/, (route) => {
      const entry = data.eventEntries.find((e) => e.request.url === route.request().url()) || data.eventEntries[0];
      const body = JSON.parse(Buffer.from(entry.response.content.text, entry.response.content.encoding === 'base64' ? 'base64' : 'utf8').toString('utf8'));
      return route.fulfill({ status: 200, contentType: 'application/json; charset=UTF-8', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ ...body, items: [] }) });
    });
  }
  await context.route(/calendar\.google\.com\/calendar\/embed\?/, (route) => {
    if (mode === 'loading') return hang();
    if (mode === 'error') return route.abort('connectionrefused');
    return route.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: data.calendarHtml });
  });
  // Google Sheet gviz JSONP.
  await context.route(/docs\.google\.com\/spreadsheets\/d\/[^/]+\/gviz\/tq/, (route) => {
    if (mode === 'loading') return hang();
    if (mode === 'error') return route.abort('connectionrefused');
    const url = new URL(route.request().url());
    const callback = (url.searchParams.get('tqx') || '').match(/responseHandler:([A-Za-z0-9_$]+)/)?.[1];
    const tab = data.tabByGid[url.searchParams.get('gid')];
    if (!callback || !tab) return route.fulfill({ status: 404, body: '' });
    const table = mode === 'empty' ? { cols: data.gviz[tab].cols, rows: [] } : data.gviz[tab];
    return route.fulfill({ status: 200, contentType: 'text/javascript; charset=utf-8', body: `/*O_o*/\n${callback}(${JSON.stringify({ version: '0.6', reqId: '0', status: 'ok', sig: '0', table })});` });
  });
  // Observatory API and its cached images.
  await context.route('https://harmonica.observe.tw/api/source/198.json', (route) => {
    if (mode === 'loading') return hang();
    if (mode === 'error') return route.fulfill({ status: 500, headers: CORS, contentType: 'application/json', body: '{"error":"Server error."}' });
    const body = mode === 'empty' ? { ...data.observe, items: [] } : data.observe;
    return route.fulfill({ status: 200, headers: CORS, contentType: 'application/json', body: JSON.stringify(body) });
  });
  await context.route('https://harmonica.observe.tw/assets/**', (route) => {
    const path = join(data.dir, 'assets', new URL(route.request().url()).pathname.replace(/^\/assets\//, ''));
    try { return route.fulfill({ status: 200, headers: CORS, contentType: 'image/webp', body: readFileSync(path) }); } catch { return route.abort(); }
  });
  // Discord public invite.
  await context.route('https://discord.com/api/**', (route) => {
    if (mode === 'loading') return hang();
    if (mode === 'error') return route.fulfill({ status: 500, headers: CORS, contentType: 'application/json', body: '{"message":"500: Internal Server Error"}' });
    const body = mode === 'empty'
      ? { guild: { name: data.discord.guild.name, description: null }, approximate_presence_count: 0, approximate_member_count: 0 }
      : data.discord;
    return route.fulfill({ status: 200, headers: CORS, contentType: 'application/json', body: JSON.stringify(body) });
  });
  // /join/ redirects to the Google Form at once. Serve the same HTML with only
  // the redirect removed so the interstitial stays on screen.
  await context.route(/\/join\/$/, async (route) => {
    const response = await route.fetch();
    const body = (await response.text())
      .replace(/<meta[^>]+http-equiv="?refresh"?[^>]*>/i, '')
      .replace(/<script>\s*window\.location\.replace\([^<]*<\/script>/i, '');
    return route.fulfill({ response, body });
  });
}

async function settle(page, maxHeight) {
  const height = Math.min(await page.evaluate(() => document.documentElement.scrollHeight), maxHeight * 2);
  for (let y = 0; y < height; y += 500) {
    await page.evaluate((top) => window.scrollTo(0, top), y);
    await page.waitForTimeout(100);
  }
  for (const frame of await page.locator('iframe:visible').all()) {
    await frame.scrollIntoViewIfNeeded({ timeout: 2000 }).catch(() => {});
    await page.waitForTimeout(2500);
  }
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.evaluate(() => Promise.all([...document.images].filter((img) => !img.complete).map((img) => new Promise((done) => { img.onload = img.onerror = done; setTimeout(done, 3000); }))));
  await page.waitForTimeout(500);
}

async function shoot(page, file, size, { anchor, viewportOnly } = {}) {
  let top = 0;
  if (anchor) {
    top = await page.evaluate((selector) => {
      const node = document.querySelector(selector);
      const header = document.querySelector('.site-header');
      const sticky = header && ['sticky', 'fixed'].includes(getComputedStyle(header).position) ? header.offsetHeight : 0;
      return node ? Math.round(Math.max(0, node.getBoundingClientRect().top + window.scrollY - 16 - sticky)) : 0;
    }, anchor);
  }
  if (viewportOnly) {
    await page.evaluate((y) => window.scrollTo(0, y), top);
    await page.waitForTimeout(300);
    return page.screenshot({ path: file });
  }
  const full = await page.evaluate(() => document.documentElement.scrollHeight);
  const height = Math.max(size.height, Math.min(full - top, size.maxHeight));
  // Full-page captures drop iframe paint below the first screen, so grow the
  // viewport to the shot height instead.
  await page.setViewportSize({ width: size.width, height: Math.round(Math.min(height, Math.max(full - top, size.height))) });
  await page.waitForTimeout(1500);
  await page.evaluate((y) => window.scrollTo(0, y), top);
  await page.waitForTimeout(400);
  return page.screenshot({ path: file });
}

function contextOptions(size, extra = {}) {
  return {
    viewport: { width: size.width, height: size.height }, deviceScaleFactor: size.deviceScaleFactor,
    isMobile: !!size.isMobile, hasTouch: !!size.hasTouch, locale: 'zh-TW', timezoneId: 'Asia/Taipei', ...extra,
  };
}

if (mode === 'site') {
  const [base, out, dataDir = '/tmp/bmhc-review/data', filter] = rest;
  const data = loadData(dataDir);
  mkdirSync(out, { recursive: true });
  for (const state of STATES.filter((s) => !filter || new RegExp(filter).test(s.id))) {
    for (const sizeName of state.sizes) {
      const size = SIZES[sizeName];
      const context = await browser.newContext(contextOptions(size, { colorScheme: state.theme === 'dark' ? 'dark' : 'light', reducedMotion: 'reduce' }));
      await installRoutes(context, data, state);
      const page = await context.newPage();
      await page.clock.setFixedTime(new Date(NOW));
      let path = state.path;
      if (state.storySelector) {
        await page.goto(base + path, { waitUntil: 'domcontentloaded' });
        const index = await page.evaluate((sel) => [...document.querySelectorAll('.portal-story-slide')].findIndex((n) => n.matches(sel)), state.storySelector);
        path += (path.includes('?') ? '&' : '?') + 'story=' + (index + 1);
      }
      const loading = state.data === 'loading';
      await page.goto(base + path, { waitUntil: loading ? 'domcontentloaded' : 'load', timeout: 45000 }).catch((error) => console.warn(state.id, error.message.split('\n')[0]));
      if (loading) await page.waitForTimeout(2500);
      else {
        await page.waitForTimeout(1200);
        for (const selector of state.click || []) {
          await page.locator(selector).first().click({ timeout: 5000 }).catch((error) => console.warn(state.id, 'click failed', selector, error.message.split('\n')[0]));
          await page.waitForTimeout(500);
        }
        if (!state.viewportOnly) await settle(page, size.maxHeight);
        else await page.waitForTimeout(1500);
      }
      const file = `${out}/${state.id}_${sizeName}.png`;
      try {
        await shoot(page, file, size, state);
        console.log(file);
      } catch (error) {
        console.warn('FAILED', file, error.message.split('\n')[0]);
      }
      await context.close();
    }
  }
} else if (mode === 'references') {
  const [out, filter] = rest;
  mkdirSync(out, { recursive: true });
  for (const sizeName of ['desktop', 'mobile']) {
    const size = SIZES[sizeName];
    for (const ref of REFERENCES.filter((r) => !filter || r.id.includes(filter))) {
      const context = await browser.newContext(contextOptions(size, {
        locale: ref.locale || 'en-US',
        userAgent: size.isMobile
          ? 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
          : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
      }));
      const page = await context.newPage();
      await page.goto(ref.url, { waitUntil: 'domcontentloaded', timeout: 45000 }).catch(() => {});
      await page.waitForTimeout(6000);
      for (const name of ['Reject All', 'Reject all', 'Accept All', 'Accept all', 'Accept', 'Got it', 'OK']) {
        const button = page.getByRole('button', { name, exact: true });
        if (await button.count().catch(() => 0)) { await button.first().click({ timeout: 2000 }).catch(() => {}); break; }
      }
      await settle(page, size.maxHeight);
      const file = `${out}/${ref.id}_${sizeName}.png`;
      await shoot(page, file, size, {});
      console.log(file);
      await context.close();
    }
  }
}
await browser.close();
