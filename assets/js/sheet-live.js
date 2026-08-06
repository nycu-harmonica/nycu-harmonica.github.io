// 訪客開頁時直接讀取公開 Google Sheet；靜態 HTML 是失敗時的 last-good 備援。
(function (global) {
  'use strict';

  var TAB_NAMES = ['gallery_albums', 'links', 'chronology_events'];
  var DRAFT_WORDS = new Set(['draft', '草稿', 'hidden', '隱藏']);
  var PUBLISHED_WORDS = new Set(['', 'published', '發布', '公開']);
  var ICONS = new Set(['instagram', 'facebook', 'youtube', 'email', 'line', 'discord', 'link']);
  var SHOW_IN = new Set(['footer', 'about', 'join']);
  var SLUG_RE = /^[a-z0-9][a-z0-9-]{2,60}$/;
  var DATE_RE = /^\d{4}-\d{2}-\d{2}$/;
  var SHEET_ID_RE = /^[A-Za-z0-9_-]{20,100}$/;
  var GID_RE = /^\d{1,20}$/;
  var MAX_ROWS = 500;
  var MAX_COLUMNS = 50;
  var DEFAULT_REFRESH_MS = 60000;
  var HEADER_ALIASES = {
    '代號': 'slug', '日期': 'date', '標題': 'title', '狀態': 'status',
    '排序': 'order', '職稱': 'role', '姓名': 'name', '說明': 'description',
    '封面': 'cover', '名稱': 'label', '網址': 'url', '圖示': 'icon',
    '顯示位置': 'show_in', 'key': 'key',
    '編號': 'id', '排序日期': 'sort_date', '顯示時間': 'date_label',
    '分類': 'category', '標籤': 'tags', '敘述': 'statement', '一句話': 'statement',
    '來源': 'source_label', '證據': 'evidence'
  };
  var SPECS = {
    gallery_albums: {
      required: ['slug', 'title', 'date'],
      allowed: ['slug', 'title', 'date', 'description', 'cover', 'status'],
      unique: 'slug'
    },
    links: {
      required: ['key', 'label', 'url'],
      allowed: ['key', 'label', 'url', 'icon', 'order', 'show_in'],
      unique: 'key'
    },
    chronology_events: {
      required: ['id', 'sort_date', 'date_label', 'category', 'statement', 'source_label', 'source_url'],
      allowed: ['id', 'sort_date', 'date_label', 'category', 'tags', 'statement', 'source_label', 'source_url', 'evidence', 'status'],
      unique: 'id'
    }
  };

  function normalizeDisplayText(value) {
    var text = String(value == null ? '' : value).replace(/\s+/g, ' ').trim();
    text = text
      .replace(/([\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff])\(([^()\n]*)\)/g, '$1（$2）')
      .replace(/\(([^()\n]*[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff][^()\n]*)\)/g, '（$1）');
    var marks = { ',': '，', ':': '：', ';': '；', '!': '！', '?': '？', '|': '｜', '~': '～' };
    return text
      .replace(/([\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff）】」』》〉])([,;:!?|~])/g,
        function (_match, left, mark) { return left + marks[mark]; })
      .replace(/([,;:!?|~])([\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff（【「『《〈])/g,
        function (_match, mark, right) { return marks[mark] + right; });
  }

  function normalizeHeader(value) {
    var name = String(value == null ? '' : value).trim().replace(/^\uFEFF/, '');
    var key = name.toLowerCase().replace(/ /g, '_').replace(/-/g, '_');
    return HEADER_ALIASES[name] || HEADER_ALIASES[key] || key;
  }

  function cellText(cell) {
    if (!cell || cell.v == null) return '';
    if (typeof cell.f === 'string') return cell.f.trim();
    if (cell.v instanceof Date && !Number.isNaN(cell.v.getTime())) {
      return cell.v.getFullYear() + '-' + String(cell.v.getMonth() + 1).padStart(2, '0') + '-' + String(cell.v.getDate()).padStart(2, '0');
    }
    return String(cell.v).trim();
  }

  function parseGvizTable(payload) {
    if (!payload || payload.status !== 'ok' || !payload.table || !Array.isArray(payload.table.rows)) {
      throw new Error('Google Sheet 回應格式錯誤');
    }
    if (payload.table.rows.length < 1 || payload.table.rows.length > MAX_ROWS + 1) {
      throw new Error('Google Sheet 列數不合理');
    }
    if (!Array.isArray(payload.table.cols) || payload.table.cols.length > MAX_COLUMNS) {
      throw new Error('Google Sheet 欄數不合理');
    }
    var rawRows = payload.table.rows.map(function (row) { return Array.isArray(row.c) ? row.c : []; });
    var columnLabels = payload.table.cols.map(function (column) { return normalizeHeader(column.label || ''); });
    var hasColumnLabels = columnLabels.some(Boolean);
    var headers = hasColumnLabels ? columnLabels : rawRows[0].map(function (cell) { return normalizeHeader(cellText(cell)); });
    var dataRows = hasColumnLabels ? rawRows : rawRows.slice(1);
    var positions = [];
    var seenHeaders = new Set();
    headers.forEach(function (header, index) {
      if (!header) return;
      if (seenHeaders.has(header)) throw new Error('Google Sheet 表頭重複：' + header);
      seenHeaders.add(header);
      positions.push({ name: header, index: index });
    });
    if (!positions.length) throw new Error('Google Sheet 缺少表頭');

    var rows = [];
    dataRows.forEach(function (cells, rowIndex) {
      cells.forEach(function (cell, columnIndex) {
        if (cellText(cell) && !headers[columnIndex]) {
          throw new Error('Google Sheet 第 ' + (rowIndex + 2) + ' 列有未命名欄位');
        }
      });
      var row = {};
      positions.forEach(function (position) { row[position.name] = cellText(cells[position.index]); });
      if (Object.keys(row).some(function (key) { return row[key]; })) rows.push(row);
    });
    return { headers: Array.from(seenHeaders), rows: rows };
  }

  function validDate(value) {
    if (!DATE_RE.test(value)) return false;
    var parts = value.split('-').map(Number);
    var date = new Date(Date.UTC(parts[0], parts[1] - 1, parts[2]));
    return date.getUTCFullYear() === parts[0] && date.getUTCMonth() === parts[1] - 1 && date.getUTCDate() === parts[2];
  }

  function validUrl(value) {
    if (/\s|%0a|%0d/i.test(value)) return '';
    if (value.indexOf('mailto:') === 0) return /^mailto:[^@:?]+@[^@:?]+(?:\?[^\r\n]*)?$/.test(value) ? value : '';
    try {
      var url = new URL(value);
      if (url.protocol !== 'https:' || url.username || url.password) return '';
      return url.href;
    } catch (_error) {
      return '';
    }
  }

  function boundedText(value, field) {
    var limits = { name: 80, role: 80, title: 160, description: 1000, statement: 280, label: 160, date_label: 80, category: 60, source_label: 160, evidence: 100 };
    var text = normalizeDisplayText(value);
    if (!text || text.length > (limits[field] || 200) || /[<>]/.test(text)) {
      throw new Error(field + ' 內容不合法');
    }
    return text;
  }

  function integer(value, required) {
    if (!value && !required) return null;
    if (!/^-?\d+$/.test(value)) throw new Error('排序須為整數');
    var number = Number(value);
    if (!Number.isSafeInteger(number)) throw new Error('排序超出範圍');
    return number;
  }

  function chronologyTags(value) {
    var seen = new Set();
    return String(value == null ? '' : value).split(/[|｜]/).map(function (tag) {
      return normalizeDisplayText(tag);
    }).filter(function (tag) {
      if (!tag || tag.length > 60 || /[<>]/.test(tag) || seen.has(tag)) return false;
      seen.add(tag);
      return true;
    }).join('|');
  }

  function normalizeRow(tab, row) {
    var status = String(row.status || '').trim().toLowerCase();
    if (DRAFT_WORDS.has(status)) return null;
    if ((tab === 'gallery_albums' || tab === 'chronology_events') && !PUBLISHED_WORDS.has(status)) {
      throw new Error('狀態值無法辨識');
    }
    if (tab === 'chronology_events') {
      var id = String(row.id || '').trim().toLowerCase();
      if (!SLUG_RE.test(id)) throw new Error('事件代號格式錯誤');
      var sortDate = String(row.sort_date || '').trim();
      if (!validDate(sortDate)) throw new Error('事件排序日期格式錯誤');
      var sourceUrl = validUrl(String(row.source_url || '').trim());
      if (!sourceUrl) throw new Error('事件來源網址不合法');
      return {
        id: id,
        sort_date: sortDate,
        date_label: boundedText(row.date_label, 'date_label'),
        category: boundedText(row.category, 'category'),
        tags: chronologyTags(row.tags),
        statement: boundedText(row.statement, 'statement'),
        source_label: boundedText(row.source_label, 'source_label'),
        source_url: sourceUrl,
        evidence: row.evidence ? boundedText(row.evidence, 'evidence') : ''
      };
    }
    if (tab === 'gallery_albums') {
      var slug = String(row.slug || '').trim().toLowerCase();
      if (!SLUG_RE.test(slug)) throw new Error('相簿代號格式錯誤');
      var date = String(row.date || '').trim();
      if (!validDate(date)) throw new Error('相簿日期格式錯誤');
      var cover = String(row.cover || '').trim();
      if (cover && (cover.indexOf('/') !== -1 || cover.indexOf('\\') !== -1 || cover.indexOf('.') === 0)) {
        throw new Error('封面檔名不可含路徑');
      }
      return {
        slug: slug,
        title: boundedText(row.title, 'title'),
        date: date,
        description: row.description ? boundedText(row.description, 'description') : '',
        cover: cover
      };
    }
    var key = String(row.key || '').trim().toLowerCase();
    if (!SLUG_RE.test(key)) throw new Error('連結代號格式錯誤');
    var icon = String(row.icon || 'link').trim().toLowerCase();
    if (!ICONS.has(icon)) throw new Error('連結圖示不合法');
    var showIn = String(row.show_in || '').split(',').map(function (value) { return value.trim().toLowerCase(); }).filter(Boolean);
    if (showIn.some(function (value) { return !SHOW_IN.has(value); })) throw new Error('連結顯示位置不合法');
    var url = validUrl(String(row.url || '').trim());
    if (!url) throw new Error('連結網址不合法');
    return {
      key: key,
      label: boundedText(row.label, 'label'),
      url: url,
      icon: icon,
      order: integer(row.order, false),
      show_in: showIn
    };
  }

  function normalizeTab(tab, payload) {
    var parsed = parseGvizTable(payload);
    var spec = SPECS[tab];
    spec.required.forEach(function (field) {
      if (parsed.headers.indexOf(field) === -1) throw new Error(tab + ' 缺少必要欄位：' + field);
    });
    parsed.headers.forEach(function (field) {
      if (spec.allowed.indexOf(field) === -1) throw new Error(tab + ' 不允許公開欄位：' + field);
    });
    var seen = new Set();
    var rows = parsed.rows.map(function (row, index) {
      try {
        var normalized = normalizeRow(tab, row);
        if (normalized && spec.unique) {
          if (seen.has(normalized[spec.unique])) throw new Error(spec.unique + ' 重複');
          seen.add(normalized[spec.unique]);
        }
        return normalized;
      } catch (error) {
        throw new Error(tab + ' 第 ' + (index + 2) + ' 列：' + error.message);
      }
    }).filter(Boolean);
    if (tab === 'gallery_albums') rows.sort(function (a, b) { return b.date.localeCompare(a.date); });
    if (tab === 'links') rows.sort(function (a, b) { return (a.order == null ? 9999 : a.order) - (b.order == null ? 9999 : b.order); });
    if (tab === 'chronology_events') rows.sort(function (a, b) { return b.sort_date.localeCompare(a.sort_date) || a.id.localeCompare(b.id); });
    return rows;
  }

  function buildGvizUrl(config, tab, callbackName, now) {
    var params = new URLSearchParams({
      gid: String(config.tabs[tab].gid),
      tqx: 'out:json;responseHandler:' + callbackName,
      headers: '1',
      _: String(now == null ? Date.now() : now)
    });
    return 'https://docs.google.com/spreadsheets/d/' + config.sheetId + '/gviz/tq?' + params.toString();
  }

  function fetchGviz(config, tab, options) {
    options = options || {};
    var doc = options.document || global.document;
    var callbackHost = options.callbackHost || global;
    var callbackName = '__bambooSheetLive_' + Date.now() + '_' + Math.random().toString(36).slice(2);
    return new Promise(function (resolve, reject) {
      var script = doc.createElement('script');
      var finished = false;
      var timer;
      function cleanup() {
        if (timer) global.clearTimeout(timer);
        script.onerror = null;
        if (script.parentNode) script.parentNode.removeChild(script);
        try { delete callbackHost[callbackName]; } catch (_error) { callbackHost[callbackName] = undefined; }
      }
      function finish(error, payload) {
        if (finished) return;
        finished = true;
        cleanup();
        if (error) reject(error); else resolve(payload);
      }
      callbackHost[callbackName] = function (payload) { finish(null, payload); };
      script.async = true;
      script.referrerPolicy = 'no-referrer';
      script.src = buildGvizUrl(config, tab, callbackName);
      script.onerror = function () { finish(new Error('Google Sheet 載入失敗')); };
      timer = global.setTimeout(function () { finish(new Error('Google Sheet 載入逾時')); }, options.timeoutMs || 10000);
      doc.head.appendChild(script);
    });
  }

  function parseConfig(doc) {
    var node = doc.getElementById('sheet-live-config');
    if (!node) throw new Error('缺少 Google Sheet 設定');
    var config = JSON.parse(node.textContent || '{}');
    if (!SHEET_ID_RE.test(String(config.sheetId || ''))) throw new Error('Google Sheet ID 格式錯誤');
    TAB_NAMES.forEach(function (tab) {
      if (!config.tabs || !config.tabs[tab] || !GID_RE.test(String(config.tabs[tab].gid || ''))) {
        throw new Error('Google Sheet gid 格式錯誤：' + tab);
      }
    });
    config.refreshMs = Math.max(30000, Number(config.refreshMs) || DEFAULT_REFRESH_MS);
    if (config.contribute && GID_RE.test(String(config.contribute.gid || ''))) {
      config.tabs.contribute = { gid: String(config.contribute.gid) };
    } else {
      config.contribute = null;
    }
    return config;
  }

  function cloneIcon(doc, name) {
    var source = doc.querySelector('[data-sheet-icon="' + name + '"] svg') || doc.querySelector('[data-sheet-icon="link"] svg');
    return source ? source.cloneNode(true) : null;
  }

  function createPlaceholder(doc, text) {
    var box = doc.createElement('div');
    box.className = 'placeholder-card';
    var paragraph = doc.createElement('p');
    paragraph.textContent = text;
    box.append(paragraph);
    return box;
  }

  function includeLink(row, location) {
    return row.show_in.length === 0 || row.show_in.indexOf(location) !== -1;
  }

  function createLink(doc, row, location) {
    var anchor = doc.createElement('a');
    anchor.dataset.sheetLinkKey = row.key;
    anchor.href = row.url;
    anchor.target = '_blank';
    anchor.rel = location === 'footer' ? 'me noopener' : 'noopener';
    var icon = cloneIcon(doc, row.icon);
    if (icon) anchor.append(icon);
    var label = doc.createElement('span');
    label.textContent = row.label;
    anchor.append(label);
    if (location !== 'about') return anchor;
    var item = doc.createElement('li');
    item.append(anchor);
    return item;
  }

  function renderLinks(doc, links) {
    doc.querySelectorAll('[data-sheet-links]').forEach(function (container) {
      var location = container.dataset.sheetLinks;
      var rows = links.filter(function (row) { return includeLink(row, location); });
      var items = rows.map(function (row) { return createLink(doc, row, location); });
      if (!items.length) items = [createPlaceholder(doc, '社群連結更新中。')];
      container.replaceChildren.apply(container, items);
    });
    var discord = links.find(function (row) { return row.key === 'discord' && includeLink(row, 'join'); });
    if (discord) {
      doc.querySelectorAll('[data-sheet-join-link]').forEach(function (anchor) {
        anchor.href = discord.url;
        anchor.target = '_blank';
        anchor.rel = 'noopener';
        anchor.textContent = discord.label === 'Discord 社群' ? '加入 Discord' : discord.label;
      });
    }
  }

  function updateAlbumCard(card, row) {
    var title = card.querySelector('[data-sheet-album-title]');
    var time = card.querySelector('[data-sheet-album-date]');
    var image = card.querySelector('[data-sheet-album-cover]');
    if (title) title.textContent = row.title;
    if (time) {
      time.dateTime = row.date;
      time.textContent = row.date.replace(/-/g, '/');
    }
    if (image) {
      image.alt = row.title + '封面照片';
      if (row.cover) {
        var options = Array.from(card.querySelectorAll('[data-sheet-cover-option]'));
        var cover = options.find(function (option) { return option.dataset.sheetCoverOption === row.cover; });
        if (cover) image.src = cover.dataset.sheetCoverUrl;
      }
    }
  }

  function renderGallery(doc, albums) {
    var grid = doc.querySelector('[data-sheet-gallery]');
    if (!grid || typeof grid.querySelectorAll !== 'function') return;
    var cards = {};
    grid.querySelectorAll('[data-sheet-album]').forEach(function (card) { cards[card.dataset.sheetAlbum] = card; });
    var visible = [];
    albums.forEach(function (row) {
      var card = cards[row.slug];
      if (!card) return;
      updateAlbumCard(card, row);
      visible.push(card);
    });
    if (Object.keys(cards).length) {
      if (!visible.length) visible.push(createPlaceholder(doc, '相簿建置中，敬請期待！'));
      grid.replaceChildren.apply(grid, visible);
    }
  }

  function renderAlbumPage(doc, albums) {
    var root = doc.querySelector('[data-sheet-album-page]');
    if (!root) return;
    var row = albums.find(function (album) { return album.slug === root.dataset.sheetAlbumPage; });
    var title = root.querySelector('[data-sheet-album-page-title]');
    var time = root.querySelector('[data-sheet-album-page-date]');
    var description = root.querySelector('[data-sheet-album-page-description]');
    var photos = root.querySelector('[data-sheet-album-photos]');
    if (!row) {
      root.dataset.sheetAlbumState = 'hidden';
      if (title) title.textContent = '相簿目前未公開';
      if (time) time.hidden = true;
      if (description) description.textContent = '這本相簿已從公開資料中移除。';
      if (photos) photos.hidden = true;
      return;
    }
    root.dataset.sheetAlbumState = 'live';
    if (title) title.textContent = row.title;
    if (time) {
      time.hidden = false;
      time.dateTime = row.date;
      time.textContent = row.date.replace(/-/g, '/');
    }
    if (description) description.textContent = row.description;
    if (photos) photos.hidden = false;
    root.querySelectorAll('.js-lightbox').forEach(function (link, index) {
      link.setAttribute('aria-label', row.title + '，照片 ' + (index + 1));
    });
    if (doc.title.indexOf('｜') !== -1) doc.title = row.title + '｜' + doc.title.split('｜').slice(1).join('｜');
  }

  function createChronologyItem(doc, row) {
    var item = doc.createElement('article');
    item.className = 'chronology-item';
    item.dataset.chronologyEvent = '';
    item.dataset.chronologyId = row.id;

    var timeBox = doc.createElement('div');
    timeBox.className = 'chronology-event-time';
    var time = doc.createElement('time');
    time.dateTime = row.sort_date;
    time.textContent = row.date_label;
    timeBox.append(time);

    var body = doc.createElement('div');
    body.className = 'chronology-event-body';
    var statement = doc.createElement('p');
    statement.className = 'chronology-event-statement';
    statement.textContent = row.statement;
    var source = doc.createElement('a');
    source.className = 'chronology-source';
    source.href = row.source_url;
    source.target = '_blank';
    source.rel = 'noopener';
    source.textContent = row.source_label;
    body.append(statement, source);
    item.append(timeBox, body);
    return item;
  }

  function renderChronology(doc, events) {
    var root = doc.querySelector('[data-sheet-chronology]');
    if (!root) return;
    var list = root.querySelector('[data-sheet-chronology-list]');
    if (!list) return;
    list.replaceChildren.apply(list, events.map(function (row) { return createChronologyItem(doc, row); }));
  }

  // 社史限時回報:表單回覆分頁的寬鬆讀取。只做展示消毒(純文字 + https 連結),
  // 與正式 chronology_events 的嚴格驗證互不影響。
  function contributeText(value, max) {
    var text = normalizeDisplayText(value).replace(/[<>]/g, '');
    return text.length > max ? text.slice(0, max - 1) + '…' : text;
  }

  function normalizeContribute(payload) {
    var parsed = parseGvizTable(payload);
    function headerFor(keyword) {
      return parsed.headers.find(function (header) { return header.indexOf(keyword) !== -1; }) || '';
    }
    var whenKey = headerFor('大約時間');
    var whatKey = headerFor('事件描述');
    var refKey = headerFor('參考連結');
    var whoKey = headerFor('姓名');
    if (!whatKey) throw new Error('回報分頁缺少事件描述欄');
    return parsed.rows.map(function (row) {
      var what = contributeText(row[whatKey], 280);
      if (!what) return null;
      return {
        when: contributeText(whenKey ? row[whenKey] : '', 80),
        what: what,
        ref: validUrl(String((refKey ? row[refKey] : '') || '').trim()),
        who: contributeText(whoKey ? row[whoKey] : '', 80)
      };
    }).filter(Boolean).reverse().slice(0, 30);
  }

  function renderContribute(doc, rows) {
    var list = doc.querySelector('[data-sheet-contribute]');
    if (!list) return;
    var items = rows.map(function (row) {
      var item = doc.createElement('li');
      var meta = doc.createElement('span');
      meta.className = 'contribute-meta';
      meta.textContent = row.when || '時間待補';
      var text = doc.createElement('span');
      text.className = 'contribute-text';
      text.textContent = row.what;
      item.append(meta, text);
      if (row.ref) {
        var link = doc.createElement('a');
        link.href = row.ref;
        link.target = '_blank';
        link.rel = 'noopener nofollow';
        link.textContent = '參考連結';
        item.append(link);
      }
      if (row.who) {
        var who = doc.createElement('span');
        who.className = 'contribute-who';
        who.textContent = '（' + row.who + ' 提供）';
        item.append(who);
      }
      return item;
    });
    list.replaceChildren.apply(list, items);
    var wrap = doc.querySelector('[data-sheet-contribute-wrap]');
    if (wrap) wrap.hidden = !items.length;
  }

  async function refreshContribute(config, doc, options) {
    if (!config.contribute || !doc.querySelector('[data-sheet-contribute]')) return;
    var expires = Date.parse(config.contribute.expires || '');
    if (expires && Date.now() >= expires) return;
    try {
      var loadTab = (options && options.loadTab) || function (tab) { return fetchGviz(config, tab, { document: doc }); };
      renderContribute(doc, normalizeContribute(await loadTab('contribute')));
    } catch (_error) {
      // 回報清單失敗不影響主要資料
    }
  }

  function formatTaipei(date) {
    var parts = new Intl.DateTimeFormat('en-CA', {
      timeZone: 'Asia/Taipei', year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit', hourCycle: 'h23'
    }).formatToParts(date);
    var values = {};
    parts.forEach(function (part) { values[part.type] = part.value; });
    return values.year + '-' + values.month + '-' + values.day + ' ' + values.hour + ':' + values.minute + ':' + values.second;
  }

  function renderLiveData(doc, data, fetchedAt) {
    renderLinks(doc, data.links);
    renderGallery(doc, data.gallery_albums);
    renderAlbumPage(doc, data.gallery_albums);
    renderChronology(doc, data.chronology_events);
    var status = doc.getElementById('sheet-live-status');
    if (status) {
      status.dataset.sheetMode = 'live';
      status.textContent = 'Google Sheet 即時讀取：' + formatTaipei(fetchedAt) + '（Asia/Taipei）';
    }
  }

  async function refreshSheetData(options) {
    options = options || {};
    var doc = options.document || global.document;
    if (!doc) return false;
    try {
      var config = options.config || parseConfig(doc);
      var loadTab = options.loadTab || function (tab) { return fetchGviz(config, tab, { document: doc }); };
      var payloads = await Promise.all(TAB_NAMES.map(function (tab) { return loadTab(tab); }));
      var data = {};
      TAB_NAMES.forEach(function (tab, index) { data[tab] = normalizeTab(tab, payloads[index]); });
      (options.renderImpl || renderLiveData)(doc, data, options.fetchedAt || new Date());
      await refreshContribute(config, doc, options);
      return true;
    } catch (_error) {
      return false;
    }
  }

  function start(doc) {
    var config;
    try { config = parseConfig(doc); } catch (_error) { return; }
    var inFlight = false;
    var lastAttempt = 0;
    async function run() {
      if (inFlight || doc.visibilityState === 'hidden') return;
      inFlight = true;
      lastAttempt = Date.now();
      try { await refreshSheetData({ document: doc, config: config }); } finally { inFlight = false; }
    }
    run();
    global.setInterval(run, config.refreshMs);
    doc.addEventListener('visibilitychange', function () {
      if (doc.visibilityState !== 'hidden' && Date.now() - lastAttempt > 10000) run();
    });
  }

  var api = {
    buildGvizUrl: buildGvizUrl,
    normalizeDisplayText: normalizeDisplayText,
    normalizeTab: normalizeTab,
    parseGvizTable: parseGvizTable,
    refreshSheetData: refreshSheetData,
    renderLiveData: renderLiveData
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  global.SheetLive = api;
  if (global.document) {
    if (global.document.readyState === 'loading') global.document.addEventListener('DOMContentLoaded', function () { start(global.document); });
    else start(global.document);
  }
})(typeof window !== 'undefined' ? window : globalThis);
