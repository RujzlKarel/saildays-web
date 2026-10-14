// Cookie lista podle vzoru rujzl.cz (RujzlWeb/js/cookie-consent.js).
// Volbu uklada do cookie saildays_consent (granted / denied), posila Consent Mode update
// a po prijeti push consent_granted (trigger CE - consent_granted v GTM-5BL8T5LD).
// Vracejiciho se navstevnika obnovuje uz inline blok v <head> pred nactenim GTM.
(function () {
var COOKIE_KEY = 'saildays_consent';
var COOKIE_DAYS = 365;
var cs = (document.documentElement.lang || '').toLowerCase().indexOf('cs') === 0;
var T = cs ? {
  label: 'Souhlas s cookies',
  text: 'Cookies používáme jen pro anonymní analytiku, a to až po vašem souhlasu.',
  more: 'Více v zásadách ochrany soukromí',
  privacy: '/cs/privacy/',
  accept: 'Přijmout vše',
  decline: 'Jen nezbytné'
} : {
  label: 'Cookie consent',
  text: 'We use cookies for anonymous analytics only after you agree.',
  more: 'More in the privacy policy',
  privacy: '/privacy/',
  accept: 'Accept all',
  decline: 'Only necessary'
};
var CSS =
'#cookie-banner{position:fixed;inset:0;z-index:9999;display:grid;place-items:center;padding:16px;background:rgba(11,58,92,.32);-webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px);opacity:0;transition:opacity .25s ease}' +
'#cookie-banner.cookie-banner--visible{opacity:1}' +
'#cookie-banner .cookie-banner__card{width:100%;max-width:440px;background:#fff;color:#13202e;border-radius:16px;padding:22px 24px;box-shadow:0 24px 60px -20px rgba(11,58,92,.45),0 0 0 1px rgba(11,58,92,.08);display:grid;gap:16px;font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;transform:translateY(10px) scale(.98);transition:transform .25s cubic-bezier(.4,0,.2,1)}' +
'#cookie-banner.cookie-banner--visible .cookie-banner__card{transform:none}' +
'#cookie-banner p{margin:0}' +
'#cookie-banner a{color:#1971c2}' +
'#cookie-banner .cookie-banner__actions{display:flex;gap:12px;flex-wrap:wrap}' +
'#cookie-banner button{flex:1 1 140px;padding:10px 16px;border-radius:8px;border:1.5px solid #0b3a5c;font:600 15px/1.2 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;cursor:pointer}' +
'#cookie-banner #cookie-decline{background:transparent;color:#0b3a5c}' +
'#cookie-banner #cookie-accept{background:#0b3a5c;color:#fff}' +
'#cookie-banner.cookie-banner--bar{place-items:end center;background:transparent;-webkit-backdrop-filter:none;backdrop-filter:none;pointer-events:none}' +
'#cookie-banner.cookie-banner--bar .cookie-banner__card{pointer-events:auto}' +
'@media (prefers-color-scheme:dark){#cookie-banner .cookie-banner__card{background:#1b2430;color:#e6edf3;box-shadow:0 24px 60px -20px rgba(0,0,0,.6),0 0 0 1px #2a3644}#cookie-banner a{color:#4dabf7}#cookie-banner button{border-color:#4dabf7}#cookie-banner #cookie-decline{color:#4dabf7}#cookie-banner #cookie-accept{background:#4dabf7;color:#0f1720}}' +
'@media (prefers-reduced-motion:reduce){#cookie-banner,#cookie-banner .cookie-banner__card{transition:none}}';
function getConsent() {
var match = document.cookie.match(new RegExp('(?:^|; )' + COOKIE_KEY + '=([^;]*)'));
return match ? match[1] : null;
}
function setConsent(value) {
var expires = new Date();
expires.setDate(expires.getDate() + COOKIE_DAYS);
document.cookie = COOKIE_KEY + '=' + value + '; expires=' + expires.toUTCString() + '; path=/; SameSite=Lax; Secure';
}
function updateGTMConsent(granted) {
window.dataLayer = window.dataLayer || [];
function gtag() { dataLayer.push(arguments); }
var g = granted ? 'granted' : 'denied';
gtag('consent', 'update', {
analytics_storage: g,
ad_storage: g,
ad_user_data: g,
ad_personalization: g
});
}
function hideBanner() {
var banner = document.getElementById('cookie-banner');
if (!banner) return;
banner.classList.remove('cookie-banner--visible');
setTimeout(function () {
if (banner.parentNode) banner.parentNode.removeChild(banner);
}, 300);
}
function showBanner() {
var style = document.createElement('style');
style.textContent = CSS;
document.head.appendChild(style);
// Na strance zasad lista text nezakryva: jen karta dole, bez zatmaveni a bez odkazu sama na sebe.
var onPrivacy = location.pathname === T.privacy;
var banner = document.createElement('div');
banner.id = 'cookie-banner';
if (onPrivacy) banner.className = 'cookie-banner--bar';
banner.setAttribute('role', 'dialog');
banner.setAttribute('aria-modal', onPrivacy ? 'false' : 'true');
banner.setAttribute('aria-label', T.label);
banner.innerHTML =
'<div class="cookie-banner__card">' +
'  <p>' + T.text + (onPrivacy ? '' : ' <a href="' + T.privacy + '">' + T.more + '</a>.') + '</p>' +
'  <div class="cookie-banner__actions">' +
'    <button type="button" id="cookie-decline">' + T.decline + '</button>' +
'    <button type="button" id="cookie-accept">' + T.accept + '</button>' +
'  </div>' +
'</div>';
document.body.appendChild(banner);
requestAnimationFrame(function () {
requestAnimationFrame(function () {
banner.classList.add('cookie-banner--visible');
});
});
function accept() {
setConsent('granted');
updateGTMConsent(true);
window.dataLayer.push({ event: 'consent_granted' });
hideBanner();
}
function decline() {
setConsent('denied');
updateGTMConsent(false);
hideBanner();
}
document.getElementById('cookie-accept').addEventListener('click', accept);
document.getElementById('cookie-decline').addEventListener('click', decline);
if (!onPrivacy) document.getElementById('cookie-accept').focus();
banner.addEventListener('click', function (e) {
if (e.target === banner) decline();
});
document.addEventListener('keydown', function esc(e) {
if (e.key === 'Escape' && document.body.contains(banner)) {
decline();
document.removeEventListener('keydown', esc);
}
});
}
var consent = getConsent();
if (consent === 'granted') {
updateGTMConsent(true);
} else if (consent === 'denied') {
updateGTMConsent(false);
} else {
if (document.readyState === 'loading') {
document.addEventListener('DOMContentLoaded', showBanner);
} else {
showBanner();
}
}
})();
