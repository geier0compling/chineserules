let offset = 0;
let lastTotal = 0;
const PAGE_SIZE = 25;

const charInput = document.getElementById("charInput");
const modeSelect = document.getElementById("modeSelect");

const searchBtn = document.getElementById("searchBtn");
const clearBtn = document.getElementById("clearBtn");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");

const statusText = document.getElementById("statusText");
const metaText = document.getElementById("metaText");
const resultsDiv = document.getElementById("results");

function setStatus(text, meta = "") {
  statusText.textContent = text;
  metaText.textContent = meta;
}

// ✅ CHANGE THIS to your real Render API URL (https)
function apiBase() {
  return "/api";
}

function modeLabel(mode) {
  if (mode === "simp") return "Simplified";
  if (mode === "trad") return "Traditional";
  return "Both";
}

function onlyOneChar(s) {
  const trimmed = (s || "").trim();
  return trimmed.length > 0 ? trimmed[0] : "";
}

function renderResults(items, mode) {
  resultsDiv.innerHTML = "";

  if (!items || items.length === 0) {
    resultsDiv.innerHTML = `<div class="resultItem">No results.</div>`;
    return;
  }

  for (const r of items) {
    let wordLine = "";
    if (mode === "simp") {
      wordLine = `${escapeHtml(r.word)} <span class="badge">${modeLabel(mode)}</span>`;
    } else if (mode === "trad") {
      wordLine = `${escapeHtml(r.word)} <span class="badge">${modeLabel(mode)}</span>`;
    } else {
      wordLine = `${escapeHtml(r.simplified)} (${escapeHtml(r.traditional)}) <span class="badge">Both</span>`;
    }

    const defs = (r.definitions || []).slice(0, 4).map(escapeHtml).join("; ");
    const pinyin = escapeHtml(r.pinyin || "");

    const el = document.createElement("div");
    el.className = "resultItem";
    el.innerHTML = `
      <div class="wordHeader">
        <div class="wordLine">${wordLine}</div>
      </div>

      <div class="kv">
        <div class="k">Chinese</div>
        <div class="v">${
          mode === "both"
            ? `${escapeHtml(r.simplified)} <span class="muted">(${escapeHtml(r.traditional)})</span>`
            : `${escapeHtml(r.word)}`
        }</div>

        <div class="k">Pinyin</div>
        <div class="v mono">[${pinyin}]</div>

        <div class="k">English</div>
        <div class="v">${defs}</div>
      </div>
    `;
    resultsDiv.appendChild(el);
  }
}

function updatePager() {
  prevBtn.disabled = offset <= 0;
  nextBtn.disabled = (offset + PAGE_SIZE) >= lastTotal;
}

async function checkHealth() {
  try {
    const res = await fetch(`${apiBase()}/health`);
    if (!res.ok) throw new Error(`Health failed: ${res.status}`);
    const data = await res.json();
    setStatus(
      "Connected.",
      `Entries: ${data.entries.toLocaleString()} | Characters: ${data.unique_characters.toLocaleString()}`
    );
  } catch (e) {
    setStatus("API not reachable.", "Is the Render API deployed and URL correct?");
  }
}

async function search(resetOffset = true) {
  const ch = onlyOneChar(charInput.value);
  charInput.value = ch;

  if (!ch) {
    setStatus("Type a character first.");
    resultsDiv.innerHTML = "";
    return;
  }

  if (resetOffset) offset = 0;

  const mode = modeSelect.value;
  const limit = PAGE_SIZE;

  const url = new URL(`${apiBase()}/lookup`);
  url.searchParams.set("char", ch);
  url.searchParams.set("mode", mode);
  url.searchParams.set("limit", String(limit));
  url.searchParams.set("offset", String(offset));

  setStatus("Searching...", `${ch} | mode=${mode} | offset=${offset}`);

  try {
    const res = await fetch(url.toString());
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Lookup error ${res.status}: ${text}`);
    }

    const data = await res.json();
    lastTotal = data.total || 0;

    setStatus(
      `Found ${lastTotal.toLocaleString()} results for '${ch}'.`,
      `Showing ${Math.min(offset + limit, lastTotal).toLocaleString()} / ${lastTotal.toLocaleString()}`
    );

    renderResults(data.results || [], mode);
    updatePager();
  } catch (e) {
    setStatus("Error.", String(e.message || e));
    resultsDiv.innerHTML = "";
    lastTotal = 0;
    updatePager();
  }
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

// events
searchBtn.addEventListener("click", () => search(true));

clearBtn.addEventListener("click", () => {
  charInput.value = "";
  resultsDiv.innerHTML = "";
  setStatus("Ready.");
  metaText.textContent = "";
  offset = 0;
  lastTotal = 0;
  updatePager();
});

prevBtn.addEventListener("click", () => {
  offset = Math.max(0, offset - PAGE_SIZE);
  search(false);
});

nextBtn.addEventListener("click", () => {
  offset = offset + PAGE_SIZE;
  search(false);
});

charInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") search(true);
});

// initial
checkHealth();
updatePager();
