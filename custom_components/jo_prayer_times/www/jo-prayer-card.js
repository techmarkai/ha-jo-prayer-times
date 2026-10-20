// Jordan prayer times card. Served by the jo_prayer_times integration, no install needed.
// type: custom:jo-prayer-card   (entity: sensor.xxx_next_prayer is optional, auto-detected)
// Plain script, not a module: the legacy (es5) frontend loads it with a classic <script>.
const BASE = "/jo_prayer_times/";
const NAMES = { fajr: "الفجر", sunrise: "الشروق", dhuhr: "الظهر", asr: "العصر", maghrib: "المغرب", isha: "العشاء" };
const TZ = "Asia/Amman";

// Islamic rosette: rings of petals, interlaced squares (8-point stars) and dots, all vector so it stays sharp at 4K.
function rosette() {
  const p = [];
  const ring = (n, fn) => { for (let i = 0; i < n; i++) p.push(fn((360 / n) * i)); };
  ring(16, (a) => `<path transform="rotate(${a})" d="M0 -96 C 20 -78 20 -52 0 -36 C -20 -52 -20 -78 0 -96Z"/>`);
  ring(16, (a) => `<path transform="rotate(${a + 11.25})" d="M0 -78 C 10 -66 10 -54 0 -46 C -10 -54 -10 -66 0 -78Z"/>`);
  ring(8, (a) => `<rect transform="rotate(${a})" x="-24" y="-24" width="48" height="48"/>`);
  ring(32, (a) => `<circle transform="rotate(${a})" cy="-104" r="2.2"/>`);
  ring(12, (a) => `<path transform="rotate(${a})" d="M0 -124 L 7 -112 L 0 -100 L -7 -112Z"/>`);
  return `<svg viewBox="-130 -130 260 260"><g fill="none" stroke="currentColor" stroke-width="1.2">
    <circle r="126"/><circle r="104" stroke-dasharray="2 4"/><circle r="36"/><circle r="12"/>${p.join("")}</g></svg>`;
}

function star(x, y, s, d) {
  return `<span class="star" style="left:${x}%;top:${y}%;--s:${s}cqw;animation-delay:${d}s"></span>`;
}

class JoPrayerCard extends HTMLElement {
  setConfig(config) {
    this._config = config || {};
  }

  set hass(hass) {
    this._hass = hass;
    if (!this.shadowRoot) {
      this._build();
      if (window.ResizeObserver) new ResizeObserver(() => this._size()).observe(this);
    }
    this._tick();
  }

  // --u = 1% of card width; stands in for cqw, which older browsers lack.
  _size() {
    const w = this.shadowRoot.querySelector(".wrap");
    w.style.setProperty("--u", w.offsetWidth / 100 + "px");
  }

  static getConfigElement() {
    return document.createElement("jo-prayer-card-editor");
  }

  static getStubConfig(hass) {
    const e = Object.keys(hass.states).find((id) => id.startsWith("sensor.") && hass.states[id].attributes.prayer);
    return e ? { entity: e } : {};
  }

  getCardSize() {
    return 4;
  }

  connectedCallback() {
    this._timer = setInterval(() => this._tick(), 1000);
  }

  disconnectedCallback() {
    clearInterval(this._timer);
  }

  _build() {
    const r = rosette();
    const stars = [star(58, 30, 0.5, 0), star(70, 18, 0.35, 1.3), star(86, 26, 0.45, 2.1),
      star(64, 70, 0.3, 0.7), star(95, 55, 0.4, 2.8), star(52, 50, 0.3, 1.8)].join("");
    this.attachShadow({ mode: "open" }).innerHTML = `
<style>
  :host { display: block; }
  ha-card { background: none; border: none; box-shadow: none; overflow: visible; cursor: pointer; }
  .wrap { position: relative; direction: rtl;
          font-family: "Noto Kufi Arabic", "Segoe UI", Tahoma, sans-serif; color: #fff; }
  .wrap::before { content: ""; display: block; padding-top: 44.206%; } /* 1536:679, aspect-ratio for old browsers */
  .panel { position: absolute; top: 16.5%; right: 0; bottom: 0; left: 0; border-radius: 4cqw; overflow: hidden;
           background: linear-gradient(180deg, #0b1c38 0%, #1d3d6e 45%, #3b6aa6 100%);
           box-shadow: 0 1.2cqw 3cqw rgba(5, 15, 35, .35); }
  .glow { position: absolute; top: -40%; right: -40%; bottom: -40%; left: -40%; background: radial-gradient(circle at 30% 60%, rgba(120,190,255,.22), transparent 45%);
          animation: drift 18s ease-in-out infinite alternate; }
  .sweep { position: absolute; top: 0; right: 0; bottom: 0; left: 0; background: linear-gradient(105deg, transparent 35%, rgba(255,255,255,.07) 50%, transparent 65%);
           background-size: 250% 100%; animation: sweep 9s linear infinite; }
  .rosette { position: absolute; color: rgba(255,255,255,.09); }
  .rosette svg { width: 100%; height: 100%; display: block; }
  .r1 { width: 46cqw; right: -9cqw; bottom: -24cqw; animation: spin 120s linear infinite; }
  .r2 { width: 24cqw; left: -8cqw; top: -10cqw; color: rgba(255,255,255,.05); animation: spin 80s linear infinite reverse; }
  .r1 svg { animation: pulse 8s ease-in-out infinite; }
  .star { position: absolute; width: var(--s); height: var(--s); background: #fff; border-radius: 50%;
          box-shadow: 0 0 .8cqw .2cqw rgba(190,225,255,.8); animation: twinkle 4s ease-in-out infinite; opacity: 0; }
  /* fills the same box as the reference design (slightly taller than the photo's own ratio) */
  .mosque { position: absolute; left: 2.7cqw; top: 5%; width: 54.6cqw; height: 85.7%; filter: drop-shadow(0 .6cqw .8cqw rgba(0,0,0,.35)); }
  .text { position: absolute; left: 50%; right: 8.5cqw; top: 22%; text-align: right; line-height: 1.25; }
  .label { font-size: 2.7cqw; opacity: .95; }
  .count { font-size: 7.6cqw; font-weight: 500; direction: ltr; text-align: right; letter-spacing: .1cqw;
           font-variant-numeric: tabular-nums; margin: .4cqw 0 2.6cqw; }
  .name { font-size: 2.7cqw; }
  .time { font-size: 2.9cqw; font-weight: 700; margin-bottom: 1.4cqw; }
  .meta { font-size: 2.6cqw; opacity: .95; }
  @keyframes spin { to { transform: rotate(360deg); } }
  @keyframes pulse { 50% { opacity: .55; transform: scale(.97); } }
  @keyframes drift { to { transform: translate(18%, -10%); } }
  @keyframes sweep { from { background-position: 150% 0; } to { background-position: -100% 0; } }
  @keyframes twinkle { 50% { opacity: .9; } }
  @media (prefers-reduced-motion: reduce) { * { animation: none !important; } .star { opacity: .5; } }
</style>
<ha-card>
  <div class="wrap">
    <div class="panel">
      <div class="glow"></div>
      <div class="rosette r1">${r}</div>
      <div class="rosette r2">${r}</div>
      ${stars}
      <div class="sweep"></div>
    </div>
    <img class="mosque" src="${BASE}mosque.png" alt="">
    <div class="text">
      <div class="label"></div>
      <div class="count"></div>
      <div class="name"></div>
      <div class="time"></div>
      <div class="meta"></div>
    </div>
  </div>
</ha-card>`.replace(/(-?[\d.]+)cqw/g, "calc($1 * var(--u))");
    this.shadowRoot.querySelector("ha-card").addEventListener("click", () => {
      const ev = new Event("hass-more-info", { bubbles: true, composed: true });
      ev.detail = { entityId: this._entity() };
      this.dispatchEvent(ev);
    });
  }

  _entity() {
    return this._config.entity || JoPrayerCard.getStubConfig(this._hass).entity;
  }

  _tick() {
    const root = this.shadowRoot;
    if (root) this._size();
    const st = this._hass && this._hass.states[this._entity()];
    if (!root || !st) return;
    const $ = (c) => root.querySelector(c);
    const name = NAMES[st.attributes.prayer] || "";
    const at = new Date(st.state);
    const left = Math.max(0, Math.floor((at - Date.now()) / 1000));
    const pad = (n) => String(n).padStart(2, "0");
    const [h, m] = at.toLocaleTimeString("en-GB", { timeZone: TZ, hour: "2-digit", minute: "2-digit", hour12: false })
      .split(":").map(Number);
    const date = new Date().toLocaleDateString("ar-EG-u-nu-latn", { timeZone: TZ, day: "numeric", month: "long", year: "numeric" });
    $(".label").textContent = `تبقى لل${name.slice(2)}`;
    $(".count").textContent = `${pad(Math.floor(left / 3600))}:${pad(Math.floor(left / 60) % 60)}:${pad(left % 60)}`;
    $(".name").textContent = name;
    $(".time").textContent = `${pad(h % 12 || 12)}:${pad(m)} ${h < 12 ? "ص" : "م"}`;
    $(".meta").textContent = `${this._config.city || st.attributes.city || ""} | ${date}`;
  }
}

// Visual editor shown after picking the card: choose the city's sensor and an optional label.
class JoPrayerCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = config;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  _render() {
    if (!this._hass || !this._config) return;
    if (!this._form) {
      this._form = document.createElement("ha-form");
      this._form.schema = [
        { name: "entity", selector: { entity: { filter: { integration: "jo_prayer_times", domain: "sensor" } } } },
        { name: "city", selector: { text: {} } },
      ];
      this._form.computeLabel = (s) => (s.name === "entity" ? "Next prayer sensor (اختر المدينة)" : "City label (optional)");
      this._form.addEventListener("value-changed", (e) =>
        this.dispatchEvent(new CustomEvent("config-changed", { detail: { config: e.detail.value }, bubbles: true, composed: true })));
      this.appendChild(this._form);
    }
    this._form.hass = this._hass;
    this._form.data = this._config;
  }
}

customElements.define("jo-prayer-card", JoPrayerCard);
customElements.define("jo-prayer-card-editor", JoPrayerCardEditor);
window.customCards = window.customCards || [];
window.customCards.push({
  type: "jo-prayer-card",
  name: "Jordan Prayer Card",
  description: "Countdown to the next prayer (official Awqaf times)",
  preview: true,
  documentationURL: "https://github.com/techmarkai/ha-jo-prayer-times",
});
