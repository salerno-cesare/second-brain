const shell = document.querySelector(".togaf-shell");
const pageList = document.getElementById("page-list");
const searchInput = document.getElementById("vault-search");
const activeTab = document.getElementById("active-tab");
const noteMeta = document.getElementById("note-meta");
const noteContent = document.getElementById("note-content");
const backlinkList = document.getElementById("backlink-list");
const outlinkList = document.getElementById("outlink-list");
const graphSvg = document.getElementById("wiki-graph");
const metadataList = document.getElementById("togaf-metadata");

let currentSlug = "";
let graphData = null;
let searchTimer = null;
let basePages = [];

function collectBasePages() {
  if (!pageList) {
    return [];
  }
  return Array.from(pageList.querySelectorAll(".note-item")).map((button) => ({
    slug: button.dataset.slug,
    title: button.dataset.title || button.textContent.trim(),
    links: button.querySelector("small")?.textContent || "",
  }));
}

function renderPageButtons(pages) {
  if (!pageList) {
    return;
  }

  pageList.textContent = "";
  pages.forEach((page) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "note-item";
    if (page.snippet) {
      button.classList.add("search-hit");
    }
    button.dataset.slug = page.slug;
    button.dataset.title = page.title;

    const title = document.createElement("span");
    title.textContent = page.title;
    button.appendChild(title);

    const detail = document.createElement("small");
    detail.textContent = page.snippet || page.links || "";
    button.appendChild(detail);

    if (page.slug === currentSlug) {
      button.classList.add("active");
    }

    button.addEventListener("click", () => navigateToPage(page.slug));
    pageList.appendChild(button);
  });
}

function setActiveButton(slug) {
  document.querySelectorAll(".note-item").forEach((button) => {
    button.classList.toggle("active", button.dataset.slug === slug);
  });
}

function navigateToPage(slug) {
  if (!slug) {
    return;
  }
  if (window.location.hash.slice(1) !== slug) {
    window.location.hash = slug;
    return;
  }
  loadPage(slug);
}

function renderMetadata(metadata) {
  if (!metadataList) {
    return;
  }
  metadataList.textContent = "";
  const rows = [
    ["Fase ADM", metadata?.adm_phase || "Non classificata"],
    ["Dominio", metadata?.domain || "Non classificato"],
    ["Tipo", metadata?.artifact_type || "Artefatto"],
    ["Stato", metadata?.status || "Da verificare"],
  ];
  rows.forEach(([label, value]) => {
    const term = document.createElement("dt");
    term.textContent = label;
    const detail = document.createElement("dd");
    detail.textContent = value;
    metadataList.appendChild(term);
    metadataList.appendChild(detail);
  });
}

async function loadPage(slug) {
  if (!slug || !noteContent) {
    return;
  }

  currentSlug = slug;
  setActiveButton(slug);
  noteContent.innerHTML = '<div class="empty-note">Caricamento...</div>';

  try {
    const resp = await fetch(`/api/togaf/page/${encodeURIComponent(slug)}`);
    const data = await resp.json();
    if (!resp.ok) {
      throw new Error(data.detail || "artefatto non disponibile");
    }

    activeTab.textContent = data.page.title;
    noteMeta.textContent = `${data.page.rel_path} | ${data.page.updated_at} | ${data.togaf.artifact_type}`;
    noteContent.innerHTML = data.html;
    renderMetadata(data.togaf);
    renderLinkList(backlinkList, data.backlinks, "Nessun backlink");
    renderLinkList(outlinkList, data.outgoing, "Nessun outlink");
    bindWikiLinks();
    await drawGraph(slug);
  } catch (err) {
    activeTab.textContent = "Errore";
    noteMeta.textContent = "";
    renderMetadata(null);
    noteContent.innerHTML = "";
    const message = document.createElement("div");
    message.className = "empty-note";
    message.textContent = `Impossibile aprire l'artefatto: ${err.message}`;
    noteContent.appendChild(message);
  }
}

function bindWikiLinks() {
  if (!noteContent) {
    return;
  }

  noteContent.querySelectorAll('a[href^="/togaf/"]').forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      const slug = link.getAttribute("href").split("/").pop();
      navigateToPage(decodeURIComponent(slug));
    });
  });
}

function renderLinkList(targetList, links, emptyText) {
  if (!targetList) {
    return;
  }

  targetList.textContent = "";
  if (!links || links.length === 0) {
    const empty = document.createElement("li");
    empty.className = "empty-list";
    empty.textContent = emptyText;
    targetList.appendChild(empty);
    return;
  }

  links.forEach((link) => {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.className = link.exists === false ? "inspector-link missing" : "inspector-link";
    button.textContent = link.title;
    button.addEventListener("click", () => navigateToPage(link.slug));
    item.appendChild(button);
    if (link.count) {
      const badge = document.createElement("small");
      badge.textContent = String(link.count);
      item.appendChild(badge);
    }
    targetList.appendChild(item);
  });
}

async function ensureGraphData() {
  if (!graphData) {
    const resp = await fetch("/api/togaf/graph");
    graphData = await resp.json();
  }
  return graphData;
}

async function drawGraph(slug) {
  if (!graphSvg) {
    return;
  }

  const graph = await ensureGraphData();
  const nodeMap = new Map(graph.nodes.map((node) => [node.slug, node]));
  const related = new Set([slug]);
  graph.edges.forEach((edge) => {
    if (edge.source === slug) {
      related.add(edge.target);
    }
    if (edge.target === slug) {
      related.add(edge.source);
    }
  });

  let visibleNodes = Array.from(related)
    .map((item) => nodeMap.get(item))
    .filter(Boolean);
  if (visibleNodes.length <= 1) {
    visibleNodes = graph.nodes.slice(0, 24);
  }

  const visibleSlugs = new Set(visibleNodes.map((node) => node.slug));
  const edges = graph.edges.filter((edge) => visibleSlugs.has(edge.source) && visibleSlugs.has(edge.target));
  const positions = new Map();
  const centerX = 160;
  const centerY = 120;
  const radius = Math.min(92, 28 + visibleNodes.length * 4);
  const current = visibleNodes.find((node) => node.slug === slug);
  const neighbors = visibleNodes.filter((node) => node.slug !== slug);

  if (current) {
    positions.set(current.slug, { x: centerX, y: centerY });
    neighbors.forEach((node, index) => {
      const angle = (Math.PI * 2 * index) / Math.max(neighbors.length, 1) - Math.PI / 2;
      positions.set(node.slug, {
        x: centerX + Math.cos(angle) * radius,
        y: centerY + Math.sin(angle) * radius,
      });
    });
  } else {
    visibleNodes.forEach((node, index) => {
      const angle = (Math.PI * 2 * index) / Math.max(visibleNodes.length, 1) - Math.PI / 2;
      positions.set(node.slug, {
        x: centerX + Math.cos(angle) * radius,
        y: centerY + Math.sin(angle) * radius,
      });
    });
  }

  graphSvg.textContent = "";
  edges.forEach((edge) => {
    const start = positions.get(edge.source);
    const end = positions.get(edge.target);
    if (!start || !end) {
      return;
    }
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", start.x);
    line.setAttribute("y1", start.y);
    line.setAttribute("x2", end.x);
    line.setAttribute("y2", end.y);
    line.setAttribute("class", edge.missing ? "graph-edge missing" : "graph-edge");
    graphSvg.appendChild(line);
  });

  visibleNodes.forEach((node) => {
    const point = positions.get(node.slug);
    if (!point) {
      return;
    }

    const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
    group.setAttribute("class", node.slug === slug ? "graph-node active" : "graph-node");

    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", point.x);
    circle.setAttribute("cy", point.y);
    circle.setAttribute("r", node.slug === slug ? 8 : 5);
    group.appendChild(circle);

    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("x", point.x);
    text.setAttribute("y", point.y + 18);
    text.textContent = node.title.length > 18 ? `${node.title.slice(0, 17)}...` : node.title;
    group.appendChild(text);

    if (!node.missing) {
      group.addEventListener("click", () => navigateToPage(node.slug));
    } else {
      group.classList.add("missing");
    }
    graphSvg.appendChild(group);
  });
}

async function runSearch(query) {
  if (!query) {
    renderPageButtons(basePages);
    return;
  }

  const resp = await fetch(`/api/togaf/search?q=${encodeURIComponent(query)}`);
  const data = await resp.json();
  renderPageButtons(data.results || []);
}

document.querySelectorAll(".js-artifact-link").forEach((button) => {
  button.addEventListener("click", () => navigateToPage(button.dataset.slug));
});

if (searchInput) {
  searchInput.addEventListener("input", () => {
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(() => runSearch(searchInput.value.trim()), 180);
  });
}

window.addEventListener("hashchange", () => {
  const slug = window.location.hash.slice(1);
  if (slug) {
    loadPage(slug);
  }
});

basePages = collectBasePages();
renderPageButtons(basePages);
renderMetadata(null);

const startSlug = window.location.hash.slice(1) || shell?.dataset.initialSlug || basePages[0]?.slug;
if (startSlug) {
  navigateToPage(startSlug);
}
