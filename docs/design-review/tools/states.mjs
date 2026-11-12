// Screenshot inventory for the design review. docs/design-review/states.md
// documents the same IDs; change both together and only between rounds that
// re-shoot the baseline.
//
// data:    normal | loading | error | empty   (every external source at once:
//          Google Sheet gviz, Observatory API, Google Calendar embed, Discord API)
// theme:   light (default) | dark
// sizes:   subset of SIZES (default: desktop + mobile)
// click:   selectors clicked in order after load     anchor: start the shot here
// viewportOnly: capture only the first screen (story player, menus)
// storySelector: reopen /p/ at the story slide matching this selector
export const SIZES = {
  desktop: { width: 1440, height: 900, deviceScaleFactor: 1, maxHeight: 2400 },
  mobile: { width: 390, height: 844, deviceScaleFactor: 2, maxHeight: 1688, isMobile: true, hasTouch: true },
  screen: { width: 1920, height: 1080, deviceScaleFactor: 1, maxHeight: 1080 },
};

const PAGE = ['desktop', 'mobile'];

function family(prefix, path, extra = {}) {
  return [
    { id: prefix, path, ...extra },
    { id: `${prefix}-dark`, path, theme: 'dark', ...extra },
    { id: `${prefix}-loading`, path, data: 'loading', ...extra },
    { id: `${prefix}-error`, path, data: 'error', ...extra },
    { id: `${prefix}-empty`, path, data: 'empty', ...extra },
  ];
}

export const STATES = [
  // Home
  ...family('home', '/'),
  { id: 'home-calendar', path: '/', anchor: '#calendar' },
  { id: 'home-calendar-dark', path: '/', anchor: '#calendar', theme: 'dark' },
  { id: 'home-menu-open', path: '/', sizes: ['mobile'], click: ['#nav-toggle'], viewportOnly: true },
  // About
  ...family('about', '/about/'),
  { id: 'about-contact', path: '/about/', anchor: '#join' },
  // Chronology
  ...family('chronology', '/chronology/'),
  { id: 'chronology-timeline', path: '/chronology/', anchor: '.chronology-timeline' },
  // Site guide
  ...family('site-guide', '/site-guide/'),
  // Join redirect (the form redirect is held so the interstitial stays visible)
  { id: 'join', path: '/join/', viewportOnly: true },
  { id: 'join-dark', path: '/join/', theme: 'dark', viewportOnly: true },
  // Discord landing
  ...family('discord', '/discord/'),
  // Performance portal story player (phone first)
  { id: 'portal', path: '/p/', viewportOnly: true },
  { id: 'portal-dark', path: '/p/', theme: 'dark', viewportOnly: true },
  { id: 'portal-song', path: '/p/', viewportOnly: true, click: ['[data-story-next]'] },
  { id: 'portal-join', path: '/p/', viewportOnly: true, storySelector: '.portal-story-join' },
  // Projection screen: 16:9 only
  { id: 'screen', path: '/p/screen/', sizes: ['screen'], viewportOnly: true },
  { id: 'screen-song', path: '/p/screen/?song=2', sizes: ['screen'], viewportOnly: true },
].map((state) => ({ sizes: PAGE, data: 'normal', theme: 'light', ...state }));

// Reference sites: photographed once and reused in every round.
export const REFERENCES = [
  { id: 'ref-yale-glee-home', url: 'https://gleeclub.yale.edu/' },
  { id: 'ref-yale-glee-about', url: 'https://gleeclub.yale.edu/about' },
  { id: 'ref-yale-glee-events', url: 'https://gleeclub.yale.edu/events' },
  { id: 'ref-cums-home', url: 'https://cums.org.uk/' },
  { id: 'ref-cums-about', url: 'https://cums.org.uk/about' },
  { id: 'ref-mcu-harmonica-home', url: 'http://club.mcu.edu.tw/hc/zh-hant', locale: 'zh-TW' },
];

// Fixed clock so "now", relative dates and the calendar agenda never drift.
export const NOW = '2026-11-13T20:00:00+08:00';
