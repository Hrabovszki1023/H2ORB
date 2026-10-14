const translations = {
  de: {
    subtitle: "Testergebnisse aus AQUA kompakt auswerten",
    ready: "Bereit",
    securityNoticeTitle: "Geschützte AQUA-Sitzung:",
    securityNoticeText: "Die persönlichen AQUA-Zugangsdaten werden nur zur Anmeldung verwendet. Das Passwort wird nicht gespeichert; AQUA-Token bleiben ausschließlich in der serverseitigen Sitzung.",
    loginTitle: "Mit AQUA anmelden",
    loginHint: "Verwenden Sie Ihre persönlichen AQUA-Zugangsdaten. Das Passwort wird nach der Anmeldung nicht gespeichert.",
    username: "Benutzername",
    password: "Passwort",
    login: "Anmelden",
    loggingIn: "Anmeldung läuft …",
    loginFailed: "Anmeldung fehlgeschlagen. Bitte Zugangsdaten prüfen.",
    sessionExpired: "Die Sitzung ist abgelaufen. Bitte erneut anmelden.",
    logout: "Abmelden",
    selectFolder: "AQUA-Startordner auswählen",
    reload: "Neu laden",
    selectedFolder: "Gewählter Startordner",
    startAnalysis: "Auswertung starten",
    resultTree: "Ergebnisbaum",
    selectStart: "Startordner wählen",
    path: "Pfad",
    name: "Bezeichnung",
    loadingProjects: "Projekte werden geladen …",
    chooseFolder: "Projekt öffnen und einen Startordner auswählen.",
    noProjects: "Keine sichtbaren AQUA-Projekte gefunden.",
    noSubfolders: "Keine Unterordner",
    open: "öffnen",
    noChildren: "ohne Unterordner",
    loadingAnalysis: "Wird geladen …",
    loadingScenarios: "Testszenarien unter „{name}“ werden rekursiv geladen …",
    evaluated: "{count} Testfallergebnisse wurden ausgewertet.",
    noScenarios: "Unter diesem Startpunkt wurden keine Testszenarien gefunden.",
    requestFailed: "Anfrage fehlgeschlagen ({status})",
    chooseAsStart: "{name} als Startordner auswählen",
    openInAqua: "{id} in AQUA öffnen",
    sumTip: "Summe aller ausgewerteten Testfälle",
    pTip: "Erfolgreich ausgeführt (Passed)",
    xTip: "Alle fehlgeschlagenen Testfälle: F + N + N?",
    fTip: "Fehlgeschlagen, mit regulärem AQUA-Defect",
    nTip: "Fehlgeschlagen, mit [NOISE] markiertem AQUA-Defect",
    ncandidateTip: "Fehlgeschlagen, noch ohne AQUA-Defect",
    aTip: "Abgebrochen (Aborted)",
    neTip: "Nicht ausgeführt: Not Run, Queued oder Waiting",
    bTip: "Blockiert (Blocked)",
    ncTip: "Nicht abgeschlossen: Incomplete oder In Progress",
    naTip: "Nicht anwendbar (Not Applicable)",
    unknownTip: "Unbekannter oder nicht zugeordneter AQUA-Status",
    pRateTip: "Passrate: P / SUM",
    xRateTip: "Gesamte Failrate: X / SUM",
    fRateTip: "Defect-Rate: F / SUM",
    nRateTip: "Noise-Rate: N / SUM",
    ncandidateRateTip: "Rate ungeklärter Fehlschläge: N? / SUM",
    passedGroup: "Passed",
    onlyFailed: "Nur X-Testfälle",
    report: "Report",
    reportHint: "Reproduzierbarer Bericht für den gewählten Startordner",
    downloadMarkdown: "Markdown herunterladen",
    includeInSummary: "{name} in die Report-Summary aufnehmen",
  },
  en: {
    subtitle: "Compact analysis of AQUA test results",
    ready: "Ready",
    securityNoticeTitle: "Protected AQUA session:",
    securityNoticeText: "Personal AQUA credentials are used only for sign-in. The password is not stored; AQUA tokens remain exclusively in the server-side session.",
    loginTitle: "Sign in to AQUA",
    loginHint: "Use your personal AQUA credentials. The password is not stored after sign-in.",
    username: "Username",
    password: "Password",
    login: "Sign in",
    loggingIn: "Signing in …",
    loginFailed: "Sign-in failed. Check your credentials.",
    sessionExpired: "Your session has expired. Sign in again.",
    logout: "Sign out",
    selectFolder: "Select AQUA start folder",
    reload: "Reload",
    selectedFolder: "Selected start folder",
    startAnalysis: "Start analysis",
    resultTree: "Result tree",
    selectStart: "Select start folder",
    path: "Path",
    name: "Description",
    loadingProjects: "Loading projects …",
    chooseFolder: "Open a project and select a start folder.",
    noProjects: "No visible AQUA projects found.",
    noSubfolders: "No subfolders",
    open: "open",
    noChildren: "without subfolders",
    loadingAnalysis: "Loading …",
    loadingScenarios: "Loading test scenarios below “{name}” recursively …",
    evaluated: "{count} test case results evaluated.",
    noScenarios: "No test scenarios found below this starting point.",
    requestFailed: "Request failed ({status})",
    chooseAsStart: "Select {name} as start folder",
    openInAqua: "Open {id} in AQUA",
    sumTip: "Total evaluated test cases",
    pTip: "Successfully executed (Passed)",
    xTip: "All failed test cases: F + N + N?",
    fTip: "Failed, linked to a regular AQUA defect",
    nTip: "Failed, linked to an AQUA defect marked [NOISE]",
    ncandidateTip: "Failed, not yet linked to an AQUA defect",
    aTip: "Aborted",
    neTip: "Not executed: Not Run, Queued, or Waiting",
    bTip: "Blocked",
    ncTip: "Not completed: Incomplete or In Progress",
    naTip: "Not Applicable",
    unknownTip: "Unknown or unmapped AQUA status",
    pRateTip: "Pass rate: P / SUM",
    xRateTip: "Total fail rate: X / SUM",
    fRateTip: "Defect rate: F / SUM",
    nRateTip: "Noise rate: N / SUM",
    ncandidateRateTip: "Unclassified failure rate: N? / SUM",
    passedGroup: "Passed",
    onlyFailed: "Failed test cases only",
    report: "Report",
    reportHint: "Reproducible report for the selected start folder",
    downloadMarkdown: "Download Markdown",
    includeInSummary: "Include {name} in the report summary",
  },
};

const tree = document.querySelector("#project-tree");
const statusText = document.querySelector("#tree-status");
const selection = document.querySelector("#selection");
const selectionName = document.querySelector("#selection-name");
const selectionSummary = document.querySelector("#selection-summary");
const analyseButton = document.querySelector("#analyse-selection");
const scenarioResults = document.querySelector("#scenario-results");
const scenarioCount = document.querySelector("#scenario-count");
const scenarioStatus = document.querySelector("#scenario-status");
const scenarioTable = document.querySelector("#scenario-table");
const failedOnlyFilter = document.querySelector("#filter-failed");
const failureFilters = document.querySelector("#failure-filters");
const resultFilters = document.querySelector(".result-filters");
const treeView = document.querySelector("#tree-view");
const reportView = document.querySelector("#report-view");
const reportPreview = document.querySelector("#report-preview");
const downloadMarkdownButton = document.querySelector("#download-markdown");
const applicationContent = document.querySelector("#application-content");
const loginDialog = document.querySelector("#login-dialog");
const loginForm = document.querySelector("#login-form");
const loginUsername = document.querySelector("#login-username");
const loginPassword = document.querySelector("#login-password");
const loginSubmit = document.querySelector("#login-submit");
const loginError = document.querySelector("#login-error");
const logoutButton = document.querySelector("#logout");
const resultRows = new Map();

let selectedLocation = null;
let lastReport = null;
let treeMessageKey = "loadingProjects";
let currentLanguage = getInitialLanguage();
let resultFilterWasActive = false;
let expansionBeforeFilter = new Map();
let activeResultView = "tree";
const summaryFolderKeys = new Set();
let csrfToken = null;

function getInitialLanguage() {
  try {
    const saved = localStorage.getItem("arb-language");
    if (saved === "de" || saved === "en") return saved;
  } catch (_) {
    // Storage can be unavailable in locked-down browsers.
  }
  return navigator.language.toLowerCase().startsWith("de") ? "de" : "en";
}

function t(key, values = {}) {
  let text = translations[currentLanguage][key] || key;
  Object.entries(values).forEach(([name, value]) => {
    text = text.replace(`{${name}}`, String(value));
  });
  return text;
}

function setLanguage(language) {
  currentLanguage = language;
  document.documentElement.lang = language;
  try { localStorage.setItem("arb-language", language); } catch (_) { /* optional */ }
  document.querySelectorAll("[data-language]").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.language === language));
  });
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll("[data-tooltip]").forEach((element) => {
    const tooltip = t(element.dataset.tooltip);
    element.title = tooltip;
    element.setAttribute("aria-label", tooltip);
  });
  statusText.textContent = t(treeMessageKey);
  if (lastReport) {
    renderReport(lastReport);
    void updateMarkdownReport();
  }
}

document.querySelectorAll("[data-language]").forEach((button) => {
  button.addEventListener("click", () => setLanguage(button.dataset.language));
});

function selectLocation({ projectId, folderId, label }) {
  selectedLocation = { projectId, folderId, label };
  selectionName.textContent = label;
  selectionSummary.textContent = label;
  selection.hidden = false;
  analyseButton.disabled = false;
  document.querySelectorAll(".location-select").forEach((button) => {
    const isSelected = Number(button.dataset.projectId) === projectId
      && Number(button.dataset.folderId) === folderId;
    button.setAttribute("aria-pressed", String(isSelected));
    button.disabled = isSelected;
    button.textContent = isSelected ? "✓" : "◎";
  });
}

async function requestJson(url, options = {}) {
  const headers = { Accept: "application/json", ...(options.headers || {}) };
  if (csrfToken && options.method && options.method !== "GET") {
    headers["X-CSRF-Token"] = csrfToken;
  }
  const response = await fetch(url, {
    ...options,
    headers,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    if (response.status === 401 && !url.endsWith("/auth/login")) {
      showLogin("sessionExpired");
    }
    throw new Error(body.detail || t("requestFailed", { status: response.status }));
  }
  return response.json();
}

function showLogin(messageKey = null) {
  csrfToken = null;
  applicationContent.hidden = true;
  logoutButton.hidden = true;
  loginPassword.value = "";
  loginError.hidden = !messageKey;
  loginError.textContent = messageKey ? t(messageKey) : "";
  if (!loginDialog.open) loginDialog.showModal();
  loginUsername.focus();
}

function showApplication(session) {
  csrfToken = session.csrfToken;
  if (loginDialog.open) loginDialog.close();
  applicationContent.hidden = false;
  logoutButton.hidden = false;
}

loginDialog.addEventListener("cancel", (event) => event.preventDefault());

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  loginError.hidden = true;
  loginSubmit.disabled = true;
  loginSubmit.textContent = t("loggingIn");
  try {
    const session = await requestJson("/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: loginUsername.value,
        password: loginPassword.value,
      }),
    });
    loginPassword.value = "";
    showApplication(session);
    await loadProjects();
  } catch (_) {
    loginPassword.value = "";
    loginError.textContent = t("loginFailed");
    loginError.hidden = false;
    loginPassword.focus();
  } finally {
    loginSubmit.disabled = false;
    loginSubmit.textContent = t("login");
  }
});

logoutButton.addEventListener("click", async () => {
  try {
    await requestJson("/api/v1/auth/logout", { method: "POST" });
  } finally {
    tree.replaceChildren();
    scenarioResults.hidden = true;
    showLogin();
  }
});

function createNode({ label, projectId, folderId, hasChildren, level, parentPath = [] }) {
  const fullPath = [...parentPath, label];
  const wrapper = document.createElement("div");
  wrapper.className = "tree-node";
  const row = document.createElement("div");
  row.className = "tree-row";
  row.style.setProperty("--tree-level", level);
  const toggle = document.createElement("button");
  toggle.type = "button";
  toggle.className = "tree-toggle";
  toggle.textContent = hasChildren ? "+" : "·";
  toggle.disabled = !hasChildren;
  toggle.setAttribute("aria-label", `${label} ${hasChildren ? t("open") : t("noChildren")}`);
  const choose = document.createElement("button");
  choose.type = "button";
  choose.className = "tree-label";
  choose.textContent = label;
  choose.addEventListener("click", () => {
    document.querySelectorAll(".tree-label[aria-current='true']").forEach((element) => element.removeAttribute("aria-current"));
    choose.setAttribute("aria-current", "true");
    selectLocation({ projectId, folderId, label: fullPath.join(" / ") });
  });
  const children = document.createElement("div");
  children.className = "tree-children";
  children.hidden = true;
  toggle.addEventListener("click", async () => {
    if (!children.hidden) {
      children.hidden = true;
      toggle.textContent = "+";
      return;
    }
    if (!children.dataset.loaded) {
      toggle.textContent = "…";
      try {
        const data = await requestJson(`/api/v1/aqua/projects/${projectId}/folders?folder_id=${folderId}`);
        data.items.forEach((folder) => children.appendChild(createNode({
          label: folder.name,
          projectId: folder.projectId,
          folderId: folder.id,
          hasChildren: folder.hasSubfolders,
          level: level + 1,
          parentPath: fullPath,
        })));
        if (!data.items.length) {
          const empty = document.createElement("p");
          empty.className = "empty-node";
          empty.textContent = t("noSubfolders");
          children.appendChild(empty);
        }
        children.dataset.loaded = "true";
      } catch (error) {
        const message = document.createElement("p");
        message.className = "error-node";
        message.textContent = error.message;
        children.replaceChildren(message);
      }
    }
    children.hidden = false;
    toggle.textContent = "−";
  });
  row.append(toggle, choose);
  wrapper.append(row, children);
  return wrapper;
}

async function loadProjects() {
  tree.replaceChildren();
  selection.hidden = true;
  selectionSummary.textContent = "";
  analyseButton.disabled = true;
  selectedLocation = null;
  lastReport = null;
  scenarioResults.hidden = true;
  treeMessageKey = "loadingProjects";
  statusText.textContent = t(treeMessageKey);
  try {
    const data = await requestJson("/api/v1/aqua/projects");
    data.items.forEach((project) => tree.appendChild(createNode({
      label: project.name,
      projectId: project.id,
      folderId: 0,
      hasChildren: project.hasSubfolders,
      level: 0,
    })));
    treeMessageKey = data.items.length ? "chooseFolder" : "noProjects";
    statusText.textContent = t(treeMessageKey);
  } catch (error) {
    statusText.textContent = error.message;
    statusText.classList.add("error-text");
  }
}

document.querySelector("#reload-tree").addEventListener("click", loadProjects);

function hideDescendants(node) {
  (node.children || []).forEach((child) => {
    const entry = resultRows.get(child);
    if (entry) {
      entry.row.hidden = true;
      entry.expanded = false;
      if (entry.toggle) entry.toggle.textContent = "▸";
    }
    hideDescendants(child);
  });
}

function selectedFailureStatuses() {
  return new Set(
    [...failureFilters.querySelectorAll("input:checked")].map((input) => input.value),
  );
}

function nodeMatchesResultFilter(node, selectedStatuses) {
  if (!failedOnlyFilter.checked) return true;
  if (node.type === "testCase") {
    return [...selectedStatuses].some((status) => (node.totals?.[status] || 0) > 0);
  }
  if (["execution", "defect"].includes(node.type)) return true;
  return (node.children || []).some((child) => nodeMatchesResultFilter(child, selectedStatuses));
}

function refreshResultVisibility() {
  if (!lastReport?.tree) return;
  const selectedStatuses = selectedFailureStatuses();

  function refresh(node, parentVisible = true, parentExpanded = true) {
    const entry = resultRows.get(node);
    if (!entry) return;
    const included = nodeMatchesResultFilter(node, selectedStatuses);
    const visible = parentVisible && parentExpanded && included;
    entry.row.hidden = !visible;
    (node.children || []).forEach((child) => refresh(child, visible, entry.expanded));
  }

  refresh(lastReport.tree);
}

function expandFilteredPaths(node) {
  const selectedStatuses = selectedFailureStatuses();
  const entry = resultRows.get(node);
  if (!entry) return;
  if (["project", "folder", "scenario"].includes(node.type)
      && nodeMatchesResultFilter(node, selectedStatuses)) {
    entry.expanded = true;
    if (entry.toggle) entry.toggle.textContent = "▾";
  }
  (node.children || []).forEach(expandFilteredPaths);
}

function applyResultFilter() {
  if (failedOnlyFilter.checked && !resultFilterWasActive) {
    expansionBeforeFilter = new Map(
      [...resultRows.entries()].map(([node, entry]) => [node.key, entry.expanded]),
    );
  } else if (!failedOnlyFilter.checked && resultFilterWasActive) {
    resultRows.forEach((entry, node) => {
      entry.expanded = expansionBeforeFilter.get(node.key) || false;
      if (entry.toggle) entry.toggle.textContent = entry.expanded ? "▾" : "▸";
    });
    expansionBeforeFilter.clear();
  }
  resultFilterWasActive = failedOnlyFilter.checked;
  failureFilters.disabled = !failedOnlyFilter.checked;
  if (failedOnlyFilter.checked && lastReport?.tree) expandFilteredPaths(lastReport.tree);
  refreshResultVisibility();
}

failedOnlyFilter.addEventListener("change", applyResultFilter);
failureFilters.addEventListener("change", applyResultFilter);

function toggleResultNode(node) {
  const entry = resultRows.get(node);
  if (!entry) return;
  if (entry.expanded) {
    hideDescendants(node);
    entry.expanded = false;
    entry.toggle.textContent = "▸";
    refreshResultVisibility();
    return;
  }
  entry.expanded = true;
  entry.toggle.textContent = "▾";
  refreshResultVisibility();
}

function formatRate(value, total) {
  if (!total) return "–";
  return new Intl.NumberFormat(currentLanguage, {
    style: "percent",
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value / total);
}

const metricClasses = {
  total: "sum", P: "p", X: "x", F: "f", N: "n", "N?": "nq",
  A: "a", NE: "ne", B: "b", NC: "nc", NA: "na", "?": "unknown",
};

function appendMetric(row, key, text) {
  const cell = document.createElement("td");
  cell.className = `metric-cell metric-${metricClasses[key]}`;
  cell.textContent = text;
  row.appendChild(cell);
}

function appendResultNode(node, depth = 0, visible = true, parentPath = []) {
  const row = document.createElement("tr");
  row.className = `result-node result-${node.type}`;
  row.hidden = !visible;
  const nodePath = node.type === "project" || node.type === "folder" ? [...parentPath, node.name] : parentPath;

  const actionCell = document.createElement("td");
  actionCell.className = "result-action-cell";
  if (node.type === "project" || node.type === "folder") {
    const locationButton = document.createElement("button");
    locationButton.type = "button";
    locationButton.className = "location-select";
    locationButton.dataset.projectId = String(selectedLocation.projectId);
    locationButton.dataset.folderId = String(node.type === "project" ? 0 : node.id);
    const isSelected = Number(locationButton.dataset.folderId) === selectedLocation.folderId;
    locationButton.textContent = isSelected ? "✓" : "◎";
    locationButton.setAttribute("aria-pressed", String(isSelected));
    locationButton.disabled = isSelected;
    const label = nodePath.join(" / ");
    locationButton.title = t("chooseAsStart", { name: label });
    locationButton.setAttribute("aria-label", locationButton.title);
    locationButton.addEventListener("click", () => selectLocation({
      projectId: selectedLocation.projectId,
      folderId: node.type === "project" ? 0 : node.id,
      label,
    }));
    if (node.type === "folder") {
      const summaryCheckbox = document.createElement("input");
      summaryCheckbox.type = "checkbox";
      summaryCheckbox.className = "summary-select";
      summaryCheckbox.checked = summaryFolderKeys.has(node.key);
      summaryCheckbox.title = t("includeInSummary", { name: nodePath.join(" / ") });
      summaryCheckbox.setAttribute("aria-label", summaryCheckbox.title);
      summaryCheckbox.addEventListener("change", () => {
        if (summaryCheckbox.checked) summaryFolderKeys.add(node.key);
        else summaryFolderKeys.delete(node.key);
        if (activeResultView === "report") void updateMarkdownReport();
      });
      actionCell.appendChild(summaryCheckbox);
    }
    actionCell.appendChild(locationButton);
  }
  row.appendChild(actionCell);

  const pathCell = document.createElement("td");
  pathCell.className = "result-tree-cell";
  pathCell.style.setProperty("--result-depth", depth);
  let toggle = null;
  if (node.children?.length) {
    toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = "row-toggle";
    toggle.textContent = "▸";
    toggle.addEventListener("click", () => toggleResultNode(node));
    pathCell.appendChild(toggle);
  } else {
    const spacer = document.createElement("span");
    spacer.className = "row-toggle-spacer";
    pathCell.appendChild(spacer);
  }
  const nodeLabel = node.url ? document.createElement("a") : document.createElement("span");
  nodeLabel.textContent = node.type === "passedGroup" ? t("passedGroup") : node.formattedId || node.name;
  if (node.formattedId) nodeLabel.className = "result-id";
  if (node.url) {
    nodeLabel.href = node.url;
    nodeLabel.target = "_blank";
    nodeLabel.rel = "noopener noreferrer";
    nodeLabel.title = t("openInAqua", { id: node.formattedId });
  }
  pathCell.appendChild(nodeLabel);
  row.appendChild(pathCell);

  const nameCell = document.createElement("td");
  nameCell.className = "result-name-cell";
  nameCell.textContent = ["project", "folder", "passedGroup"].includes(node.type) ? "" : node.name;
  nameCell.title = nameCell.textContent;
  row.appendChild(nameCell);

  const totals = node.totals;
  const isTestCase = node.type === "testCase";
  const isPassedGroup = node.type === "passedGroup";
  const countKeys = ["total", "P", "X", "F", "N", "N?", "A", "NE", "B", "NC", "NA", "?"];
  countKeys.forEach((key) => {
    const value = totals ? totals[key] || 0 : null;
    const hideZero = (isTestCase || isPassedGroup) && value === 0;
    appendMetric(row, key, value === null || hideZero ? "" : String(value));
  });
  ["P", "X", "F", "N", "N?"].forEach((key) => appendMetric(
    row,
    key,
    totals && !isTestCase && (!isPassedGroup || key === "P")
      ? formatRate(totals[key] || 0, totals.total)
      : "",
  ));

  scenarioTable.appendChild(row);
  resultRows.set(node, { row, toggle, expanded: false });
  (node.children || []).forEach((child) => appendResultNode(child, depth + 1, false, nodePath));
}

function renderReport(data) {
  scenarioTable.replaceChildren();
  resultRows.clear();
  scenarioCount.textContent = String(data.scenarios.length);
  scenarioStatus.textContent = data.scenarios.length
    ? t("evaluated", { count: data.totals.total })
    : t("noScenarios");
  if (data.tree) appendResultNode(data.tree);
  if (failedOnlyFilter.checked) resultFilterWasActive = false;
  applyResultFilter();
  renderMarkdownPreview(data.markdown?.[currentLanguage] || "");
}

function appendInlineMarkdown(parent, source) {
  const pattern = /(\*\*([^*]+)\*\*|\[([^\]]+)\]\((https?:\/\/[^)]+)\))/g;
  let offset = 0;
  for (const match of source.matchAll(pattern)) {
    parent.append(document.createTextNode(unescapeMarkdownText(source.slice(offset, match.index))));
    if (match[2]) {
      const strong = document.createElement("strong");
      strong.textContent = unescapeMarkdownText(match[2]);
      parent.append(strong);
    } else {
      const link = document.createElement("a");
      link.textContent = unescapeMarkdownText(match[3]);
      link.href = match[4];
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      parent.append(link);
    }
    offset = match.index + match[0].length;
  }
  parent.append(document.createTextNode(unescapeMarkdownText(source.slice(offset))));
}

function unescapeMarkdownText(value) {
  return value
    .replaceAll("\\[", "[")
    .replaceAll("\\]", "]")
    .replaceAll("\\|", "|")
    .replaceAll("\\\\", "\\");
}

function splitMarkdownRow(line) {
  return line.slice(1, -1).replaceAll("\\|", "\u0000").split("|")
    .map((cell) => cell.trim().replaceAll("\u0000", "|"));
}

function renderMarkdownPreview(markdown) {
  reportPreview.replaceChildren();
  const lines = markdown.split(/\r?\n/);
  for (let index = 0; index < lines.length;) {
    const line = lines[index];
    if (!line.trim()) { index += 1; continue; }

    const heading = line.match(/^(#{1,4})\s+(.+)$/);
    if (heading) {
      const element = document.createElement(`h${heading[1].length}`);
      appendInlineMarkdown(element, heading[2]);
      reportPreview.append(element);
      index += 1;
      continue;
    }

    if (line.startsWith("| ") && lines[index + 1]?.match(/^\|[\s:|-]+\|$/)) {
      const table = document.createElement("table");
      const header = document.createElement("thead");
      const headerRow = document.createElement("tr");
      splitMarkdownRow(line).forEach((value) => {
        const cell = document.createElement("th");
        appendInlineMarkdown(cell, value);
        headerRow.append(cell);
      });
      header.append(headerRow);
      table.append(header);
      const body = document.createElement("tbody");
      index += 2;
      while (index < lines.length && lines[index].startsWith("| ")) {
        const row = document.createElement("tr");
        splitMarkdownRow(lines[index]).forEach((value) => {
          const cell = document.createElement("td");
          appendInlineMarkdown(cell, value);
          row.append(cell);
        });
        body.append(row);
        index += 1;
      }
      table.append(body);
      reportPreview.append(table);
      continue;
    }

    if (line.startsWith("- ")) {
      const list = document.createElement("ul");
      while (index < lines.length && lines[index].startsWith("- ")) {
        const item = document.createElement("li");
        appendInlineMarkdown(item, lines[index].slice(2));
        list.append(item);
        index += 1;
      }
      reportPreview.append(list);
      continue;
    }

    if (line.startsWith("> ")) {
      const quote = document.createElement("blockquote");
      while (index < lines.length && lines[index].startsWith("> ")) {
        if (quote.childNodes.length) quote.append(document.createElement("br"));
        appendInlineMarkdown(quote, lines[index].slice(2).replace(/\s{2}$/, ""));
        index += 1;
      }
      reportPreview.append(quote);
      continue;
    }

    const paragraph = document.createElement("p");
    appendInlineMarkdown(paragraph, line);
    reportPreview.append(paragraph);
    index += 1;
  }
}

function setResultView(view) {
  activeResultView = view;
  treeView.hidden = view !== "tree";
  reportView.hidden = view !== "report";
  resultFilters.hidden = view !== "tree";
  document.querySelectorAll(".result-view-tabs button").forEach((button) => {
    button.setAttribute("aria-selected", String(button.dataset.view === view));
  });
  if (view === "report") void updateMarkdownReport();
}

async function updateMarkdownReport() {
  if (!lastReport?.tree) return;
  downloadMarkdownButton.disabled = true;
  try {
    const data = await requestJson("/api/v1/report/markdown", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tree: lastReport.tree,
        generatedAt: lastReport.generatedAt,
        language: currentLanguage,
        summaryKeys: [...summaryFolderKeys],
      }),
    });
    lastReport.markdown[currentLanguage] = data.markdown;
    renderMarkdownPreview(data.markdown);
  } catch (error) {
    reportPreview.textContent = error.message;
  } finally {
    downloadMarkdownButton.disabled = false;
  }
}

document.querySelectorAll(".result-view-tabs button").forEach((button) => {
  button.addEventListener("click", () => setResultView(button.dataset.view));
});

downloadMarkdownButton.addEventListener("click", () => {
  if (!lastReport) return;
  const markdown = lastReport.markdown?.[currentLanguage] || "";
  const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  const baseName = (lastReport.tree?.name || "aqua-report").replace(/[^a-z0-9_-]+/gi, "-");
  link.href = url;
  link.download = `${baseName || "aqua-report"}.md`;
  link.click();
  URL.revokeObjectURL(url);
});

analyseButton.addEventListener("click", async () => {
  if (!selectedLocation) return;
  analyseButton.disabled = true;
  analyseButton.textContent = t("loadingAnalysis");
  scenarioResults.hidden = false;
  scenarioCount.textContent = "…";
  scenarioStatus.textContent = t("loadingScenarios", { name: selectedLocation.label });
  scenarioTable.replaceChildren();
  summaryFolderKeys.clear();
  try {
    lastReport = await requestJson(`/api/v1/aqua/projects/${selectedLocation.projectId}/report?folder_id=${selectedLocation.folderId}`);
    renderReport(lastReport);
    document.querySelector(".selection-panel").open = false;
  } catch (error) {
    scenarioCount.textContent = "!";
    scenarioStatus.textContent = error.message;
    scenarioStatus.classList.add("error-text");
  } finally {
    analyseButton.disabled = false;
    analyseButton.textContent = t("startAnalysis");
  }
});

setLanguage(currentLanguage);
void (async () => {
  try {
    const session = await requestJson("/api/v1/auth/session");
    if (!session.authenticated) {
      showLogin();
      return;
    }
    showApplication(session);
    await loadProjects();
  } catch (_) {
    showLogin();
  }
})();
