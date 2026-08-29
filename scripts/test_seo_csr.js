'use strict';

const assert = require('assert');
const fs = require('fs');
const vm = require('vm');

class Element {
  constructor({ content = '', href = '', textContent = '' } = {}) {
    this.content = content;
    this.href = href;
    this.textContent = textContent;
    this.attributes = {};
    this.stateChild = null;
  }

  setAttribute(name, value) {
    this.attributes[name] = value;
    if (name === 'content') this.content = value;
  }

  querySelector(selector) {
    return selector === '[data-seo-heading-state]' ? this.stateChild : null;
  }
}

const canonical = new Element({ href: 'https://harmonica.nycu.club/p/?story=2&utm_source=ig#slide' });
const description = new Element({ content: '竹韻口琴社現場演出的手機節目單。' });
const ogTitle = new Element({ content: '竹韻演出 Portal｜今日曲目與入社資訊' });
const ogDescription = new Element({ content: description.content });
const ogURL = new Element({ content: 'https://harmonica.nycu.club/p/' });
const twitterTitle = new Element({ content: ogTitle.content });
const twitterDescription = new Element({ content: description.content });
const heading = new Element({ textContent: '歡迎來到竹韻的演出現場' });
heading.stateChild = new Element();

const elements = new Map([
  ['link[rel="canonical"]', canonical],
  ['meta[name="description"]', description],
  ['meta[property="og:title"]', ogTitle],
  ['meta[property="og:description"]', ogDescription],
  ['meta[property="og:url"]', ogURL],
  ['meta[name="twitter:title"]', twitterTitle],
  ['meta[name="twitter:description"]', twitterDescription],
  ['[data-seo-heading]', heading],
]);

const document = {
  title: '竹韻演出 Portal｜今日曲目與入社資訊',
  documentElement: { dataset: {} },
  querySelector(selector) { return elements.get(selector) || null; },
};
const window = {
  location: {
    origin: 'https://harmonica.nycu.club',
    href: 'https://harmonica.nycu.club/p/?story=2&utm_source=ig#slide',
  },
};

const source = fs.readFileSync('assets/js/seo-csr.js', 'utf8');
vm.runInNewContext(source, { document, window, URL, Object, String });

assert.equal(canonical.href, 'https://harmonica.nycu.club/p/');
assert.equal(window.BambooSEO.canonicalURL, 'https://harmonica.nycu.club/p/');
assert.equal(document.title, '竹韻演出 Portal｜今日曲目與入社資訊');

window.BambooSEO.setState({
  title: '第 1 首：Just the Way You Are',
  heading: '第 1 首：Just the Way You Are',
  description: '竹韻演出節目第一首曲目。',
});
assert.equal(document.title, '第 1 首：Just the Way You Are｜竹韻演出 Portal｜今日曲目與入社資訊');
assert.equal(description.content, '竹韻演出節目第一首曲目。');
assert.equal(ogTitle.content, document.title);
assert.equal(ogDescription.content, description.content);
assert.equal(twitterTitle.content, document.title);
assert.equal(twitterDescription.content, description.content);
assert.equal(heading.stateChild.textContent, '｜第 1 首：Just the Way You Are');
assert.equal(canonical.href, 'https://harmonica.nycu.club/p/');
assert.equal(ogURL.content, 'https://harmonica.nycu.club/p/?story=2&utm_source=ig');

window.BambooSEO.setState(null);
assert.equal(document.title, '竹韻演出 Portal｜今日曲目與入社資訊');
assert.equal(description.content, '竹韻口琴社現場演出的手機節目單。');
assert.equal(heading.stateChild.textContent, '');
assert.equal(ogURL.content, 'https://harmonica.nycu.club/p/');

const head = fs.readFileSync('layouts/partials/head.html', 'utf8');
const portal = fs.readFileSync('assets/js/portal.js', 'utf8');
assert(head.includes('resources.Get "js/seo-csr.js"'), 'SEO CSR bundle must load on every HTML page');
assert(portal.includes('window.BambooSEO?.setState'), 'Portal query states must update CSR metadata');
assert(source.includes("canonicalURL.search = ''"), 'CSR canonical must remove query parameters');
assert(!source.includes('utm_'), 'Tracking parameters must not create content variants');

console.log('SEO CSR checks passed');
