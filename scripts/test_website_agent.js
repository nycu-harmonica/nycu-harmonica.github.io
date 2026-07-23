'use strict';

const fs = require('fs');

function read(path) {
  return fs.readFileSync(path, 'utf8');
}

const config = read('hugo.toml');
const base = read('layouts/baseof.html');
const partial = read('layouts/partials/website-agent.html');
const client = read('assets/js/website-agent.js');

if (!config.includes('[params.websiteAgent]')) throw new Error('website agent config missing');
if (!base.includes('partial "website-agent.html"')) throw new Error('website agent partial missing');
if (!base.includes('website-agent-config')) throw new Error('website agent runtime config missing');
if (!base.includes('vendor/deep-chat/deepChat.bundle.js')) throw new Error('Deep Chat bundle missing');
if (!partial.includes('<dialog') || !partial.includes('<deep-chat')) {
  throw new Error('website agent dialog accessibility structure missing');
}
if (!client.includes("credentials: 'omit'")) throw new Error('browser request must omit credentials');
if (!client.includes("url.protocol === 'https:'")) throw new Error('production endpoint must require HTTPS');
if (!client.includes('connect = { handler: ask }')) throw new Error('Deep Chat custom handler missing');
if (!client.includes('maxMessages: 4')) throw new Error('conversation history must be bounded');
if (!client.includes('chat.images = false') || !client.includes('chat.microphone = false')) {
  throw new Error('public chat media controls must be disabled');
}
if (!client.includes('link.textContent = source.label')) throw new Error('source labels must render as text');
if (client.includes('localStorage') || client.includes('sessionStorage')) {
  throw new Error('public conversation must not be persisted in browser storage');
}

console.log('website agent frontend checks passed');
