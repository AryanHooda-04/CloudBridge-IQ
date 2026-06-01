const form = document.querySelector("#analysisForm");
const appShell = document.querySelector(".app-shell");
const fileInput = document.querySelector("#fileInput");
const fileMeta = document.querySelector("#fileMeta");
const dropZone = document.querySelector("#dropZone");
const previewFrame = document.querySelector("#previewFrame");
const apiStatus = document.querySelector("#apiStatus");
const resultTitle = document.querySelector("#resultTitle");
const submitButton = document.querySelector("#submitButton");
const loadingState = document.querySelector("#loadingState");
const errorState = document.querySelector("#errorState");
const overviewPanel = document.querySelector("#overviewPanel");
const sourcePanel = document.querySelector("#sourcePanel");
const reportPanel = document.querySelector("#reportPanel");
const diagramPanel = document.querySelector("#diagramPanel");
const mappingPanel = document.querySelector("#mappingPanel");
const planPanel = document.querySelector("#planPanel");
const risksPanel = document.querySelector("#risksPanel");
const costPanel = document.querySelector("#costPanel");
const gatePanel = document.querySelector("#gatePanel");
const summaryGrid = document.querySelector("#summaryGrid");
const analysisMeta = document.querySelector("#analysisMeta");
const sourceProvider = document.querySelector("#sourceProvider");
const targetProvider = document.querySelector("#targetProvider");
const providerRouteBadges = document.querySelector("#providerRouteBadges");
const currentAssessmentName = document.querySelector("#currentAssessmentName");
const currentRouteSummary = document.querySelector("#currentRouteSummary");
const currentReviewStatus = document.querySelector("#currentReviewStatus");
const sidebarWorkspaceStatus = document.querySelector("#sidebarWorkspaceStatus");
const toastRegion = document.querySelector("#toastRegion");
const migrationIntent = document.querySelector("#migrationIntent");
const goalsInput = document.querySelector("#goals");
const architectureVariant = document.querySelector("#architectureVariant");
const architecturePattern = document.querySelector("#architecturePattern");
const copyReportButton = document.querySelector("#copyReportButton");
const downloadPdfButton = document.querySelector("#downloadPdfButton");
const downloadReportButton = document.querySelector("#downloadReportButton");
const downloadDiagramButton = document.querySelector("#downloadDiagramButton");
const saveAssessmentButton = document.querySelector("#saveAssessmentButton");
const markReviewedButton = document.querySelector("#markReviewedButton");
const reviewChecklist = document.querySelector("#reviewChecklist");
const reviewNotes = document.querySelector("#reviewNotes");
const architectNotes = document.querySelector("#architectNotes");
const reviewComments = document.querySelector("#reviewComments");
const workflowStatus = document.querySelector("#workflowStatus");
const historyList = document.querySelector("#historyList");
const reviewPanel = document.querySelector("#reviewPanel");
const toggleReviewRailButton = document.querySelector("#toggleReviewRailButton");
const closeReviewRailButton = document.querySelector("#closeReviewRailButton");
const toggleIntakeButton = document.querySelector("#toggleIntakeButton");
const collapseIntakeButton = document.querySelector("#collapseIntakeButton");
const qualityGates = document.querySelector("#qualityGates");
const projectNameInput = document.querySelector("#projectName");
const reviewerNameInput = document.querySelector("#reviewerName");
const assessmentTimeline = document.querySelector("#assessmentTimeline");
const agentChatForm = document.querySelector("#agentChatForm");
const agentChatInput = document.querySelector("#agentChatInput");
const agentChatLog = document.querySelector("#agentChatLog");
const agentChatSendButton = document.querySelector("#agentChatSendButton");
const agentStatus = document.querySelector("#agentStatus");
const agentSuggestions = document.querySelector(".agent-suggestions");
const agentClearButton = document.querySelector("#agentClearButton");
const authOverlay = document.querySelector("#authOverlay");
const authForm = document.querySelector("#authForm");
const authDisplayName = document.querySelector("#authDisplayName");
const authEmail = document.querySelector("#authEmail");
const authRequestedRole = document.querySelector("#authRequestedRole");
const authAdminPassword = document.querySelector("#authAdminPassword");
const authSubmitButton = document.querySelector("#authSubmitButton");
const authError = document.querySelector("#authError");
const userChip = document.querySelector("#userChip");
const userAvatar = document.querySelector("#userAvatar");
const userRoleLabel = document.querySelector("#userRoleLabel");
const userDisplayName = document.querySelector("#userDisplayName");
const logoutButton = document.querySelector("#logoutButton");
const API_BASE = window.location.protocol === "file:" ? "http://127.0.0.1:8000" : "";
const HISTORY_KEY = "cloudMigrationAssessments.v2";

let currentUser = null;
let latestResult = null;
let latestPreviewUrl = null;
let latestDiagramUrl = null;
let mermaidModulePromise = null;
let mermaidRenderSequence = 0;
let selectedHistoryId = null;
let viewMode = "executive";
let timelineTimer = null;
let timelineIndex = 0;
let diagramZoom = 1;
let diagramPanState = null;
let selectedCanvasComponentId = null;
let agentChatHistory = [];
let reviewState = {
  reviewed: false,
  status: "ai_draft",
  notes: "",
  comments: "",
  projectName: "",
  reviewer: "",
  sectionComments: {},
};

const TIMELINE_STEPS = [
  ["ingest", "Ingestion"],
  ["detect", "Detection"],
  ["map", "Mapping"],
  ["design", "Target Design"],
  ["risks", "Risks"],
  ["report", "Report"],
];

checkHealth();
initializeAuth();
renderSupportedProviders();
syncProviderRouteBadges();
syncAppFrame();
renderHistory();
setViewMode(viewMode);
syncReviewMetadataInputs();
resetAgentChat();
syncSnapshotCondensed();

setReviewRailCollapsed(true);

window.addEventListener("scroll", syncSnapshotCondensed, { passive: true });
window.addEventListener("resize", syncSnapshotCondensed);

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => activateTab(tab.dataset.tab));
});

document.querySelectorAll("[data-navigate-tab]").forEach((button) => {
  button.addEventListener("click", () => activateTab(button.dataset.navigateTab));
});

document.querySelectorAll("[data-view-mode]").forEach((button) => {
  button.addEventListener("click", () => setViewMode(button.dataset.viewMode || "executive"));
});

toggleReviewRailButton?.addEventListener("click", () => {
  const collapsed = appShell?.classList.contains("review-rail-collapsed") ?? true;
  setReviewRailCollapsed(!collapsed);
});

closeReviewRailButton?.addEventListener("click", () => setReviewRailCollapsed(true));

toggleIntakeButton?.addEventListener("click", () => toggleIntakePanel());
collapseIntakeButton?.addEventListener("click", () => toggleIntakePanel(true));

authForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  await signIn();
});

logoutButton?.addEventListener("click", async () => {
  try {
    await apiFetch(`${API_BASE}/api/session`, { method: "DELETE" });
  } finally {
    currentUser = null;
    applyRoleUi();
    showAuthOverlay("Signed out. Sign in to continue.");
  }
});

document.querySelectorAll(".preset-button").forEach((button) => {
  button.addEventListener("click", () => {
    toggleGoalPreset(button.dataset.goal || "");
    syncPresetStates();
  });
});

document.querySelectorAll("[data-agent-prompt]").forEach((button) => {
  button.addEventListener("click", () => {
    if (!agentChatInput) {
      return;
    }
    agentChatInput.value = button.dataset.agentPrompt || "";
    agentChatInput.focus();
  });
});

agentChatForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  await askMigrationAgent();
});

agentClearButton?.addEventListener("click", () => {
  resetAgentChat(latestResult);
  showToast("Agent conversation reset.", "success");
});

agentChatInput?.addEventListener("keydown", async (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
    event.preventDefault();
    await askMigrationAgent();
  }
});

document.addEventListener("click", async (event) => {
  if (!(event.target instanceof Element)) {
    return;
  }

  const agentPrompt = event.target.closest("[data-agent-prompt]");
  if (agentPrompt) {
    if (agentChatInput) {
      agentChatInput.value = agentPrompt.dataset.agentPrompt || "";
      agentChatInput.focus();
    }
    return;
  }

  const mermaidButton = event.target.closest("[data-copy-mermaid]");
  if (mermaidButton) {
    const reportSource = mermaidButton
      .closest(".report-mermaid-block")
      ?.querySelector("[data-report-mermaid-source]")
      ?.textContent;
    const source = reportSource || latestResult?.mermaid_diagram;
    if (source) {
      await navigator.clipboard.writeText(normalizeMermaidSource(source));
      pulseButton(mermaidButton, "Copied");
    }
    return;
  }

  const historyButton = event.target.closest("[data-history-action]");
  if (historyButton) {
    const id = historyButton.dataset.historyId;
    const action = historyButton.dataset.historyAction;
    if (action === "open") {
      openHistoryItem(id);
    } else if (action === "compare") {
      compareHistoryItem(id);
    } else if (action === "delete") {
      deleteHistoryItem(id);
    }
    return;
  }

  const sourceAction = event.target.closest("[data-source-action]");
  if (sourceAction) {
    if (!hasPermission("can_assess")) {
      showToast("Your role cannot edit and rebuild source architecture.", "error");
      return;
    }
    const action = sourceAction.dataset.sourceAction;
    if (action === "add") {
      addSourceComponent();
    } else if (action === "delete") {
      deleteSourceComponent(Number(sourceAction.dataset.index));
    } else if (action === "rebuild") {
      await rebuildFromEditedSource();
    }
    return;
  }

  const relationshipAction = event.target.closest("[data-relationship-action]");
  if (relationshipAction) {
    if (!hasPermission("can_assess")) {
      showToast("Your role cannot edit architecture relationships.", "error");
      return;
    }
    const action = relationshipAction.dataset.relationshipAction;
    if (action === "add") {
      addSourceRelationship();
    } else if (action === "delete") {
      deleteSourceRelationship(Number(relationshipAction.dataset.index));
    }
    return;
  }

  const zoomAction = event.target.closest("[data-canvas-zoom]");
  if (zoomAction) {
    updateCanvasZoom(zoomAction.dataset.canvasZoom || "reset");
    return;
  }

  const canvasNode = event.target.closest("[data-arch-node]");
  if (canvasNode) {
    selectCanvasComponent(canvasNode.dataset.archNode);
  }
});

document.addEventListener("pointerdown", (event) => {
  const wrap = event.target.closest("#diagramImageWrap.has-rendered-diagram");
  if (!wrap || event.button !== 0 || !canPanDiagram(wrap)) {
    return;
  }

  diagramPanState = {
    pointerId: event.pointerId,
    wrap,
    startX: event.clientX,
    startY: event.clientY,
    scrollLeft: wrap.scrollLeft,
    scrollTop: wrap.scrollTop,
  };
  wrap.classList.add("is-panning");
  wrap.setPointerCapture?.(event.pointerId);
  event.preventDefault();
});

document.addEventListener("pointermove", (event) => {
  if (!diagramPanState || diagramPanState.pointerId !== event.pointerId) {
    return;
  }

  const deltaX = event.clientX - diagramPanState.startX;
  const deltaY = event.clientY - diagramPanState.startY;
  diagramPanState.wrap.scrollLeft = diagramPanState.scrollLeft - deltaX;
  diagramPanState.wrap.scrollTop = diagramPanState.scrollTop - deltaY;
  event.preventDefault();
});

document.addEventListener("pointerup", endDiagramPan);
document.addEventListener("pointercancel", endDiagramPan);

document.addEventListener("input", (event) => {
  if (!(event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement)) {
    return;
  }
  if (event.target.matches("[data-component-field]")) {
    if (!hasPermission("can_assess")) {
      return;
    }
    updateSourceComponent(event.target);
    return;
  }
  if (event.target.matches("[data-relationship-field]")) {
    if (!hasPermission("can_assess")) {
      return;
    }
    updateSourceRelationship(event.target);
    return;
  }
  if (event.target.matches("[data-section-comment]")) {
    if (!hasPermission("can_review")) {
      return;
    }
    updateSectionComment(event.target);
    return;
  }
  if (
    event.target === architectNotes ||
    event.target === reviewComments ||
    event.target === projectNameInput ||
    event.target === reviewerNameInput
  ) {
    reviewState.notes = architectNotes.value;
    reviewState.comments = reviewComments.value;
    reviewState.projectName = projectNameInput.value;
    reviewState.reviewer = reviewerNameInput.value;
    promoteReviewAfterArchitectComment(event.target);
    updateSelectedHistoryReviewState();
    syncAppFrame();
    if (latestResult && (event.target === architectNotes || event.target === reviewComments)) {
      refreshReviewStatusViews(latestResult);
    }
  }
});

document.addEventListener("change", (event) => {
  if (!(event.target instanceof HTMLInputElement || event.target instanceof HTMLSelectElement)) {
    return;
  }
  if (event.target === workflowStatus) {
    if (!hasPermission("can_architect_review")) {
      workflowStatus.value = reviewState.status;
      showToast("Only Aryan or an architect can change workflow status.", "error");
      return;
    }
    if (workflowStatus.value === "approved" && latestResult && hasApprovalBlockers(latestResult)) {
      workflowStatus.value = "needs_review";
      reviewState.status = "needs_review";
      reviewState.reviewed = false;
      showToast("Approval blocked until quality gate blockers are resolved.", "error");
    } else {
      reviewState.status = workflowStatus.value;
      reviewState.reviewed = ["reviewed", "approved"].includes(workflowStatus.value);
    }
    updateSelectedHistoryReviewState();
    syncAppFrame();
    if (latestResult) {
      refreshReviewStatusViews(latestResult);
    }
    return;
  }
  if (event.target === sourceProvider || event.target === targetProvider) {
    syncProviderRouteBadges();
    setProviderTheme(latestResult || {});
    return;
  }
  if (event.target.matches("[data-relationship-field]")) {
    if (!hasPermission("can_assess")) {
      return;
    }
    updateSourceRelationship(event.target);
    return;
  }
  if (event.target === architecturePattern) {
    if (latestResult) {
      renderResult(latestResult);
    }
    return;
  }
  if (event.target.matches("[data-diagram-control]")) {
    updateDiagramControls();
    return;
  }
  if (event.target.matches("[data-canvas-layer]")) {
    updateCanvasLayers();
  }
});

goalsInput.addEventListener("input", syncPresetStates);

fileInput.addEventListener("change", () => {
  const file = fileInput.files?.[0];
  setFilePreview(file);
});

dropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropZone.classList.add("dragging");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragging");
});

dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropZone.classList.remove("dragging");
  const file = event.dataTransfer.files?.[0];
  if (!file) {
    return;
  }
  fileInput.files = event.dataTransfer.files;
  setFilePreview(file);
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!hasPermission("can_assess")) {
    showError("Your current role cannot run migration assessments.");
    return;
  }
  const file = fileInput.files?.[0];
  if (!file) {
    showError("Select an architecture diagram before running the assessment.");
    return;
  }

  setLoading(true);
  startAssessmentTimeline();
  hideError();
  resultTitle.textContent = "Analyzing";

  try {
    const fileBase64 = await readFileAsBase64(file);
    const response = await apiFetch(`${API_BASE}/api/session`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "assessment",
        filename: file.name || "architecture-diagram",
        content_type: file.type || null,
        file_base64: fileBase64,
        source_provider: sourceProvider.value || "auto",
        target_provider: targetProvider.value || "aws",
        migration_intent: migrationIntent.value || null,
        goals: goalsWithVariant().join(", "),
      }),
    });
    const payload = await readApiPayload(response);
    if (!response.ok) {
      throw new Error(payload.detail || "Migration analysis failed.");
    }
    selectedHistoryId = null;
    reviewState = {
      reviewed: false,
      status: "needs_review",
      notes: "",
      comments: "",
      projectName: projectNameInput.value || buildHistoryTitle(payload),
      reviewer: reviewerNameInput.value || "",
      sectionComments: {},
    };
    syncReviewMetadataInputs();
    workflowStatus.value = reviewState.status;
    latestResult = payload;
    renderResult(payload);
    enableActions(true);
    resultTitle.textContent = "Assessment Complete";
    showToast("Assessment complete. Review the decision snapshot and architecture workspace.", "success");
    activateTab("overview");
  } catch (error) {
    showError(error.message || "Migration analysis failed.");
    resultTitle.textContent = "Needs Attention";
  } finally {
    stopAssessmentTimeline();
    setLoading(false);
  }
});

copyReportButton.addEventListener("click", async () => {
  if (!latestResult?.markdown_report) {
    return;
  }
  await navigator.clipboard.writeText(buildExportMarkdown());
  pulseButton(copyReportButton, "Copied");
});

downloadReportButton.addEventListener("click", () => {
  if (!latestResult?.markdown_report) {
    return;
  }
  downloadText("migration-assessment.md", buildExportMarkdown(), "text/markdown");
});

downloadPdfButton.addEventListener("click", async () => {
  if (!latestResult?.markdown_report) {
    return;
  }
  hideError();
  downloadPdfButton.disabled = true;
  const original = downloadPdfButton.textContent;
  downloadPdfButton.textContent = "Building";
  try {
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), 120000);
    const response = await apiFetch(`${API_BASE}/api/report/pdf`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
      body: JSON.stringify({
        filename: "migration-assessment.pdf",
        markdown_report: buildExportMarkdown(),
        source_provider: latestResult.source_architecture?.provider || sourceProvider.value,
        target_provider: latestResult.target_architecture?.provider || targetProvider.value,
        target_architecture: latestResult.target_architecture,
        include_rendered_diagram: true,
        include_mermaid_diagram: false,
        mermaid_diagram_png_base64: null,
      }),
    }).finally(() => window.clearTimeout(timeoutId));
    if (!response.ok) {
      let detail = "PDF generation failed.";
      try {
        const payload = await readApiPayload(response);
        detail = payload.detail || detail;
      } catch {
        detail = response.statusText || detail;
      }
      throw new Error(detail);
    }
    const blob = await response.blob();
    downloadBlob("migration-assessment.pdf", blob);
    showToast("PDF report export started.", "success");
  } catch (error) {
    if (error.name === "AbortError") {
      showError("PDF generation timed out after 120 seconds. Try downloading the PNG diagram first, then retry the PDF export.");
    } else {
      showError(error.message || "PDF generation failed.");
    }
  } finally {
    downloadPdfButton.disabled = false;
    downloadPdfButton.textContent = original;
  }
});

downloadDiagramButton.addEventListener("click", async () => {
  if (!latestResult?.target_architecture) {
    return;
  }
  hideError();
  downloadDiagramButton.disabled = true;
  const original = downloadDiagramButton.textContent;
  downloadDiagramButton.textContent = "...";
  try {
    const response = await apiFetch(`${API_BASE}/api/diagram/png`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        filename: `${targetProvider.value || "target"}-architecture.png`,
        target_architecture: latestResult.target_architecture,
      }),
    });
    if (!response.ok) {
      let detail = "AWS diagram generation failed.";
      try {
        const payload = await readApiPayload(response);
        detail = payload.detail || detail;
      } catch {
        detail = response.statusText || detail;
      }
      throw new Error(detail);
    }
    const blob = await response.blob();
    downloadBlob(`${targetProvider.value || "target"}-architecture.png`, blob);
    showToast("Architecture PNG export started.", "success");
  } catch (error) {
    showError(error.message || "AWS diagram generation failed.");
  } finally {
    downloadDiagramButton.disabled = false;
    downloadDiagramButton.textContent = original;
  }
});

saveAssessmentButton.addEventListener("click", () => {
  if (!latestResult) {
    return;
  }
  if (!hasPermission("can_review")) {
    showToast("Viewer access cannot save assessment reviews.", "error");
    return;
  }
  saveCurrentAssessment();
  pulseButton(saveAssessmentButton, "Saved");
});

markReviewedButton.addEventListener("click", () => {
  if (!latestResult) {
    return;
  }
  if (!hasPermission("can_architect_review")) {
    showToast("Only Aryan or an architect can mark architect review.", "error");
    return;
  }
  reviewState.reviewed = !reviewState.reviewed;
  reviewState.status = reviewState.reviewed ? "reviewed" : "needs_review";
  workflowStatus.value = reviewState.status;
  markReviewedButton.textContent = reviewState.reviewed ? "Reviewed" : "Mark";
  updateSelectedHistoryReviewState();
  syncAppFrame();
  refreshReviewStatusViews(latestResult);
});

async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) {
      throw new Error("API unavailable");
    }
    apiStatus.textContent = "API Online";
    apiStatus.classList.add("ok");
    apiStatus.classList.remove("error");
  } catch {
    apiStatus.textContent = "API Offline";
    apiStatus.classList.add("error");
    apiStatus.classList.remove("ok");
  }
}

async function initializeAuth() {
  document.body.classList.add("auth-locked");
  try {
    const response = await apiFetch(`${API_BASE}/api/session`);
    if (!response.ok) {
      throw new Error("Authentication required.");
    }
    const payload = await readApiPayload(response);
    currentUser = payload.user;
    applyRoleUi();
  } catch {
    currentUser = null;
    applyRoleUi();
    showAuthOverlay();
  }
}

async function signIn() {
  hideAuthError();
  authSubmitButton.disabled = true;
  const original = authSubmitButton.textContent;
  authSubmitButton.textContent = "Signing in";
  try {
    const response = await apiFetch(`${API_BASE}/api/session`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        display_name: authDisplayName.value.trim(),
        email: authEmail.value.trim() || null,
        requested_role: authRequestedRole.value || "reviewer",
        admin_password: authAdminPassword.value || null,
      }),
    });
    const payload = await readApiPayload(response);
    if (!response.ok) {
      throw new Error(payload.detail || `Sign-in failed with HTTP ${response.status}.`);
    }
    currentUser = payload.user;
    applyRoleUi();
    showToast(`Signed in as ${roleLabel(currentUser.primary_role)}.`, "success");
  } catch (error) {
    showAuthOverlay(error.message || "Sign-in failed.");
  } finally {
    authSubmitButton.disabled = false;
    authSubmitButton.textContent = original;
  }
}

function apiFetch(url, options = {}) {
  return fetch(url, {
    credentials: "include",
    ...options,
  });
}

function readFileAsBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const value = String(reader.result || "");
      resolve(value.includes(",") ? value.split(",", 2)[1] : value);
    };
    reader.onerror = () => reject(new Error("Could not read the selected diagram file."));
    reader.readAsDataURL(file);
  });
}

async function readApiPayload(response) {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }
  const text = await response.text().catch(() => "");
  return {
    detail:
      compactServerMessage(text) ||
      `Server returned ${response.status} ${response.statusText || ""}`.trim(),
  };
}

function compactServerMessage(value) {
  const text = String(value || "")
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  return text ? text.slice(0, 220) : "";
}

function showAuthOverlay(message = "") {
  document.body.classList.add("auth-locked");
  if (authOverlay) {
    authOverlay.hidden = false;
  }
  if (message) {
    showAuthError(message);
  }
}

function hideAuthOverlay() {
  document.body.classList.remove("auth-locked");
  if (authOverlay) {
    authOverlay.hidden = true;
  }
  hideAuthError();
}

function showAuthError(message) {
  if (!authError) {
    return;
  }
  authError.textContent = message;
  authError.hidden = false;
}

function hideAuthError() {
  if (!authError) {
    return;
  }
  authError.textContent = "";
  authError.hidden = true;
}

function hasPermission(permission) {
  return Boolean(currentUser?.permissions?.[permission]);
}

function applyRoleUi() {
  const signedIn = Boolean(currentUser);
  if (!signedIn) {
    showAuthOverlay();
  } else {
    hideAuthOverlay();
  }

  if (userChip) {
    userChip.hidden = !signedIn;
  }
  if (signedIn) {
    const initials = currentUser.display_name
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase())
      .join("");
    userAvatar.textContent = initials || "U";
    userRoleLabel.textContent = roleLabel(currentUser.primary_role);
    userDisplayName.textContent = currentUser.display_name;
  }

  const canAssess = hasPermission("can_assess");
  const canReview = hasPermission("can_review");
  const canArchitectReview = hasPermission("can_architect_review");
  const canView = hasPermission("can_view");

  form?.querySelectorAll("input, select, textarea, button").forEach((control) => {
    control.disabled = !canAssess;
  });
  submitButton.disabled = !canAssess || document.body.classList.contains("is-loading-assessment");
  submitButton.title = canAssess ? "" : "Viewer access cannot run assessments.";

  saveAssessmentButton.disabled = !latestResult || !canReview;
  markReviewedButton.disabled = !latestResult || !canArchitectReview;
  markReviewedButton.title = canArchitectReview ? "" : "Only Aryan or an architect can mark architect review.";
  workflowStatus.disabled = !canArchitectReview;
  architectNotes.disabled = !canArchitectReview;
  reviewerNameInput.disabled = !canReview;
  projectNameInput.disabled = !canReview;
  reviewComments.disabled = !canReview;

  copyReportButton.disabled = !latestResult || !canView;
  downloadPdfButton.disabled = !latestResult || !canView;
  downloadReportButton.disabled = !latestResult || !canView;
  downloadDiagramButton.disabled = !latestResult || !canView;
  agentChatInput.disabled = !canView;
  agentChatSendButton.disabled = !canView || !latestResult;

  document.body.dataset.userRole = signedIn ? currentUser.primary_role : "anonymous";
  document.body.classList.toggle("role-restricted", signedIn && !canArchitectReview);
}

function roleLabel(role) {
  const labels = {
    admin: "Admin + Architect",
    architect: "Architect",
    reviewer: "Reviewer",
    viewer: "Viewer",
  };
  return labels[role] || "Signed in";
}

function setFilePreview(file) {
  if (latestPreviewUrl) {
    URL.revokeObjectURL(latestPreviewUrl);
    latestPreviewUrl = null;
  }

  if (!file) {
    fileMeta.textContent = "PNG, JPG, WEBP, GIF, BMP, or PDF";
    previewFrame.innerHTML = '<div class="preview-empty">No diagram selected</div>';
    return;
  }

  fileMeta.textContent = `${file.name} (${formatBytes(file.size)})`;
  if (file.type.startsWith("image/")) {
    latestPreviewUrl = URL.createObjectURL(file);
    previewFrame.innerHTML = `<img src="${latestPreviewUrl}" alt="Uploaded architecture diagram preview" />`;
    return;
  }

  previewFrame.innerHTML = `
    <div class="preview-empty">
      <strong>${escapeHtml(file.name)}</strong><br />
      PDF selected
    </div>
  `;
}

function renderResult(payload) {
  setProviderTheme(payload);
  syncProviderRouteBadges(payload);
  selectedCanvasComponentId = payload.target_architecture?.components?.[0]?.id || null;
  renderSummary(payload);
  renderAnalysisMeta(payload.analysis_metadata || {});
  renderQualityGates(payload);
  overviewPanel.innerHTML = renderOverview(payload);
  sourcePanel.innerHTML = renderSourceArchitecture(payload);
  mappingPanel.innerHTML = renderMappings(payload.service_mappings || []);
  diagramPanel.innerHTML = renderDiagram(payload);
  planPanel.innerHTML = renderPlan(payload);
  risksPanel.innerHTML = renderRisks(payload);
  costPanel.innerHTML = renderCost(payload);
  gatePanel.innerHTML = renderDecisionGate(payload);
  reportPanel.innerHTML = renderReportMemo(payload);
  injectReportProviderBrand(reportPanel, payload);
  injectGeneratedDiagramIntoReport(reportPanel, payload);
  renderReviewPanel(payload);
  renderReportMermaidBlocks(reportPanel);
  renderMermaidDiagram(payload.mermaid_diagram || "");
  renderDiagramImage(payload);
  updateDiagramControls();
  updateCanvasLayers();
  syncZoomControls();
  resetAgentChat(payload);
  setViewMode(viewMode);
  toggleIntakePanel(true);
  applyRoleUi();
}

function resetAgentChat(payload = latestResult) {
  agentChatHistory = [];
  if (!agentChatLog) {
    return;
  }

  const source = payload?.source_architecture?.provider
    ? formatProvider(payload.source_architecture.provider)
    : "source";
  const target = payload?.target_architecture?.provider
    ? formatProvider(payload.target_architecture.provider)
    : "target";
  const gateSummary = payload
    ? buildQualityGateItems(payload)
        .filter((gate) => ["block", "warn"].includes(gate.status))
        .slice(0, 3)
        .map((gate) => `<li>${escapeHtml(gate.label)}: ${escapeHtml(gate.value)}</li>`)
        .join("")
    : "";
  agentStatus.textContent = payload ? "Assessment loaded" : "No assessment";
  agentChatLog.innerHTML = `
    <div class="agent-message assistant">
      <div class="agent-message-meta">
        <span class="agent-message-avatar">CB</span>
        <strong>Migration Agent</strong>
      </div>
      <div class="agent-message-body">
        <p>${
          payload
            ? `I have the ${escapeHtml(source)} to ${escapeHtml(target)} assessment in context. Ask me about architecture flow, mappings, risks, cutover, costs, or the final verdict.`
            : "Run an assessment, then ask me about mappings, architecture flow, risks, cost signals, or the final verdict."
        }</p>
        ${gateSummary ? `<ul>${gateSummary}</ul>` : ""}
      </div>
    </div>
  `;
}

async function askMigrationAgent() {
  const question = (agentChatInput?.value || "").trim();
  if (!question || !agentChatLog || !agentChatSendButton) {
    return;
  }

  appendAgentMessage("user", question);
  agentChatHistory.push({ role: "user", content: question });
  agentChatInput.value = "";
  setAgentBusy(true);
  const thinkingMessage = appendAgentMessage("assistant", "Thinking through the assessment context...", {
    transient: true,
  });

  try {
    const response = await apiFetch(`${API_BASE}/api/agent/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        assessment: latestResult,
        chat_history: agentChatHistory.slice(-10),
        active_tab: document.querySelector(".tab.active")?.dataset.tab || "overview",
        reviewer_notes: [architectNotes.value, reviewComments.value].filter(Boolean).join("\n"),
      }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const requestError = new Error(payload.detail || `Migration agent chat returned ${response.status}.`);
      requestError.status = response.status;
      throw requestError;
    }
    thinkingMessage?.remove();
    appendAgentMessage("assistant", payload.answer || "I could not generate an answer.");
    agentChatHistory.push({ role: "assistant", content: payload.answer || "" });
    agentChatHistory = agentChatHistory.slice(-12);
    renderAgentSuggestionButtons(payload.suggested_questions || []);
    agentStatus.textContent = payload.used_assessment_context ? "Assessment aware" : "General guidance";
  } catch (error) {
    thinkingMessage?.remove();
    const fallbackAnswer = buildLocalAgentFallback(question, error);
    appendAgentMessage("assistant", fallbackAnswer);
    agentChatHistory.push({ role: "assistant", content: fallbackAnswer });
    agentChatHistory = agentChatHistory.slice(-12);
    renderAgentSuggestionButtons([
      "Explain the target architecture flow.",
      "Which mappings need architect review?",
      "What are the top migration risks?",
      "Summarize cost and savings signals.",
    ]);
    agentStatus.textContent = "Local context";
  } finally {
    setAgentBusy(false);
  }
}

function appendAgentMessage(role, content, options = {}) {
  if (!agentChatLog) {
    return null;
  }
  const message = document.createElement("div");
  message.className = `agent-message ${role}${options.transient ? " transient" : ""}`;
  const label = role === "user" ? "You" : "Migration Agent";
  message.innerHTML = `
    <div class="agent-message-meta">
      <span class="agent-message-avatar">${role === "user" ? "You" : "CB"}</span>
      <strong>${label}</strong>
    </div>
    <div class="agent-message-body">${
      role === "assistant" ? renderMarkdown(content || "") : `<p>${escapeHtml(content || "")}</p>`
    }</div>
  `;
  agentChatLog.appendChild(message);
  agentChatLog.scrollTop = agentChatLog.scrollHeight;
  return message;
}

function setAgentBusy(isBusy) {
  agentChatSendButton.disabled = isBusy;
  agentChatSendButton.textContent = isBusy ? "Thinking" : "Ask Agent";
  agentChatInput.disabled = isBusy;
}

function renderAgentSuggestionButtons(suggestions) {
  if (!agentSuggestions || !suggestions.length) {
    return;
  }
  agentSuggestions.innerHTML = suggestions
    .slice(0, 4)
    .map(
      (suggestion) =>
        `<button type="button" data-agent-prompt="${escapeAttribute(suggestion)}"><span>Ask</span>${escapeHtml(shortSuggestion(suggestion))}</button>`,
    )
    .join("");
}

function buildLocalAgentFallback(question, error) {
  const payload = latestResult;
  const lowerQuestion = String(question || "").toLowerCase();
  const unavailableNote = error?.status === 404
    ? "The live chat route is not available in the currently running server, so I am using the loaded assessment locally."
    : "The live chat service did not return an answer, so I am using the loaded assessment locally.";

  if (!payload) {
    return `${unavailableNote}\n\nRun an assessment first, then I can answer from the detected source architecture, target design, mappings, risks, plan, cost estimate, and verdict.`;
  }

  if (/risk|concern|issue|blocker|top/.test(lowerQuestion)) {
    return `${unavailableNote}\n\n${localAgentRiskAnswer(payload)}`;
  }

  if (/map|mapping|mapped|alternative|equivalent|why/.test(lowerQuestion)) {
    return `${unavailableNote}\n\n${localAgentMappingAnswer(payload)}`;
  }

  if (/cost|saving|budget|estimate|run.?rate|dual.?run/.test(lowerQuestion)) {
    return `${unavailableNote}\n\n${localAgentCostAnswer(payload)}`;
  }

  if (/flow|architecture|diagram|route|path|target/.test(lowerQuestion)) {
    return `${unavailableNote}\n\n${localAgentArchitectureAnswer(payload)}`;
  }

  if (/verdict|recommend|decision|gate|approve/.test(lowerQuestion)) {
    return `${unavailableNote}\n\n${localAgentVerdictAnswer(payload)}`;
  }

  return `${unavailableNote}\n\n${localAgentSummaryAnswer(payload)}`;
}

function localAgentSummaryAnswer(payload) {
  const source = formatProvider(payload.source_architecture?.provider || sourceProvider.value);
  const target = formatProvider(payload.target_architecture?.provider || targetProvider.value);
  const verdict = payload.final_verdict || {};
  const pattern = selectedArchitecturePattern(payload);
  return [
    `### Assessment Snapshot`,
    `- **Route:** ${source} to ${target}`,
    `- **Pattern:** ${pattern.label}`,
    `- **Verdict:** ${formatVerdict(verdict.recommendation || "not run")} (${Math.round((verdict.confidence || 0) * 100)}% confidence)`,
    `- **Mappings:** ${(payload.service_mappings || []).length}`,
    `- **Target components:** ${(payload.target_architecture?.components || []).length}`,
    ``,
    verdict.reasoning || payload.executive_summary || "Use the tabs to review source detection, mappings, architecture, risks, costs, and decision gate items.",
  ].join("\n");
}

function localAgentRiskAnswer(payload) {
  const severityRank = { critical: 4, high: 3, medium: 2, low: 1 };
  const risks = [...(payload.risks || [])]
    .sort((a, b) => (severityRank[b.severity] || 0) - (severityRank[a.severity] || 0))
    .slice(0, 5);
  if (!risks.length) {
    return "### Top Risks\n- No explicit risks were returned. Validate low-confidence mappings, data movement, security controls, rollback, and cost assumptions before approval.";
  }
  return [
    "### Top Migration Risks",
    ...risks.map(
      (risk) =>
        `- **${risk.title || "Risk"}** (${formatTitle(risk.severity || "unknown")}): ${risk.description || "Review needed."} Mitigation: ${risk.mitigation || "Assign an owner and validate during planning."}`,
    ),
  ].join("\n");
}

function localAgentMappingAnswer(payload) {
  const mappings = payload.service_mappings || [];
  if (!mappings.length) {
    return "### Mapping Review\n- No source-to-target mappings were returned. Re-run detection or add source components manually before architecture approval.";
  }
  const reviewItems = mappings
    .filter((mapping) => Number(mapping.confidence || 0) < 0.82 || (mapping.alternatives || []).length)
    .slice(0, 6);
  const items = (reviewItems.length ? reviewItems : mappings.slice(0, 6)).map((mapping) => {
    const alternatives = (mapping.alternatives || []).length
      ? ` Alternatives: ${mapping.alternatives.slice(0, 3).join(", ")}.`
      : "";
    return `- **${mapping.source_service || "Source service"} -> ${mapping.target_service || "Target service"}** (${Math.round((mapping.confidence || 0) * 100)}%): ${mapping.reasoning || "Mapping requires architect validation."}${alternatives}`;
  });
  return ["### Mapping Review", ...items].join("\n");
}

function localAgentArchitectureAnswer(payload) {
  const target = payload.target_architecture || {};
  const components = (target.components || []).slice(0, 8);
  const relationships = (target.relationships || []).slice(0, 8);
  const componentText = components.length
    ? components.map((component) => `- **${component.name}** (${component.category || component.service_type || "component"})`).join("\n")
    : "- No target components were returned.";
  const relationshipText = relationships.length
    ? relationships
        .map((relationship) => {
          const source = findTargetComponentName(payload, relationship.source_id);
          const targetName = findTargetComponentName(payload, relationship.target_id);
          return `- ${source} ${relationship.relationship_type || "connects to"} ${targetName}`;
        })
        .join("\n")
    : "- No target relationships were returned.";
  return [
    "### Target Architecture Flow",
    target.summary || "The target architecture summary was not returned.",
    "",
    "**Core services**",
    componentText,
    "",
    "**Flow / relationships**",
    relationshipText,
  ].join("\n");
}

function localAgentCostAnswer(payload) {
  const estimate = estimateCostRange(payload);
  const savingsLine =
    estimate.sourceBaselineAvailable && estimate.savingsHigh > 0
      ? `Estimated savings: ${formatSavingsRange(estimate.savingsLow, estimate.savingsHigh)} per month, or ${formatSavingsRange(estimate.annualSavingsLow, estimate.annualSavingsHigh)} annualized if source resources are decommissioned.`
      : "No directional savings signal is available yet; attach inventory, utilization, licensing, traffic, and data-volume assumptions.";
  return [
    "### Cost Signals",
    `- **Target monthly run-rate:** ${formatCurrencyRange(estimate.monthlyLow, estimate.monthlyHigh)}`,
    `- **Source baseline:** ${formatCurrencyRange(estimate.sourceMonthlyLow, estimate.sourceMonthlyHigh)}`,
    `- **Migration project estimate:** ${formatCurrencyRange(estimate.projectLow, estimate.projectHigh)}`,
    `- **Dual-run reserve:** ${formatCurrencyRange(estimate.dualRunLow, estimate.dualRunHigh)}`,
    `- **Savings:** ${savingsLine}`,
  ].join("\n");
}

function localAgentVerdictAnswer(payload) {
  const verdict = payload.final_verdict || {};
  const checklist = payload.assessment_insights?.decision_gate?.checklist || [];
  const openItems = checklist.filter((item) => !item.passed).slice(0, 5);
  return [
    "### Final Verdict",
    `- **Recommendation:** ${formatVerdict(verdict.recommendation || "unknown")}`,
    `- **Confidence:** ${Math.round((verdict.confidence || 0) * 100)}%`,
    `- **Reasoning:** ${verdict.reasoning || "No verdict reasoning was returned."}`,
    "",
    "**Open decision-gate items**",
    openItems.length
      ? openItems.map((item) => `- ${item.label || item.title || item.description || "Review item"}`).join("\n")
      : "- No open gate items were returned, but architect review is still recommended before execution.",
  ].join("\n");
}

function findTargetComponentName(payload, componentId) {
  const component = (payload.target_architecture?.components || []).find((item) => item.id === componentId);
  return component?.name || componentId || "component";
}

function shortSuggestion(suggestion) {
  const text = String(suggestion || "");
  return text.length > 24 ? `${text.slice(0, 21).trim()}...` : text;
}

function renderAnalysisMeta(metadata) {
  const mode = metadata.detection_mode || "unknown";
  const pdfPages = metadata.pdf_image_pages_processed || 0;
  const parts = [`Mode: ${formatMode(mode)}`];
  if (metadata.llm_detection_attempted !== undefined) {
    parts.push(`LLM: ${metadata.llm_detection_attempted ? "attempted" : "not used"}`);
  }
  if (metadata.local_text_extraction) {
    parts.push(`Local text extraction: ${metadata.local_text_extraction}`);
  }
  if (pdfPages) {
    parts.push(`PDF pages rendered: ${pdfPages}`);
  }
  if (metadata.pdf_image_conversion_error) {
    parts.push(`PDF render warning: ${compactMessage(metadata.pdf_image_conversion_error)}`);
  }
  if (metadata.llm_detection_error) {
    parts.push(`LLM warning: ${compactMessage(metadata.llm_detection_error)}`);
  }
  analysisMeta.textContent = parts.join(" | ");
}

function renderSummary(payload) {
  const verdict = payload.final_verdict?.recommendation || "unknown";
  const mappingCount = payload.service_mappings?.length || 0;
  const source = payload.source_architecture?.provider || sourceProvider.value;
  const target = payload.target_architecture?.provider || "aws";
  const readiness = payload.assessment_insights?.scores?.overall_readiness?.value ?? 0;
  const scoreStatus = payload.assessment_insights?.scores?.overall_readiness?.status || "watch";
  const confidence = Math.round((payload.final_verdict?.confidence || 0) * 100);
  const workflow = workflowLabel(reviewState.status);
  const estimate = estimateCostRange(payload);
  const highRiskCount = (payload.risks || []).filter((risk) =>
    ["high", "critical"].includes(String(risk.severity || "").toLowerCase()),
  ).length;

  summaryGrid.innerHTML = `
    <div class="metric metric-with-chart ${escapeHtml(verdict)}">
      ${renderMiniPie(confidence, verdict)}
      <div>
        <span>Verdict</span>
        <strong>${formatVerdict(verdict)}</strong>
      </div>
    </div>
    <div class="metric metric-with-chart ${escapeHtml(scoreStatus)}">
      ${renderMiniPie(readiness, scoreStatus)}
      <div>
        <span>Readiness</span>
        <strong>${readiness}%</strong>
      </div>
    </div>
    <div class="metric">
      <span>Target Run-rate</span>
      <strong>${formatCurrencyRange(estimate.monthlyLow, estimate.monthlyHigh)}</strong>
      <small>monthly estimate</small>
    </div>
    <div class="metric">
      <span>High Risks</span>
      <strong>${highRiskCount}</strong>
      <small>${mappingCount} mappings reviewed</small>
    </div>
    <div class="metric">
      <span>Target</span>
      ${providerLogoLockup(target, { compact: true })}
      <small>${escapeHtml(formatProvider(target))}</small>
    </div>
    <div class="metric">
      <span>Review Status</span>
      <strong>${escapeHtml(workflow)}</strong>
      <small>${new Date().toLocaleDateString()}</small>
    </div>
    <div class="metric route-metric">
      <span>Migration Route</span>
      ${providerRouteMarkup(source, target, { compact: true })}
    </div>
  `;
  syncAppFrame(payload);
  syncSnapshotCondensed();
}

function toggleIntakePanel(forceCollapsed = undefined) {
  const collapsed =
    typeof forceCollapsed === "boolean"
      ? forceCollapsed
      : !appShell?.classList.contains("intake-collapsed");
  appShell?.classList.toggle("intake-collapsed", collapsed);
  if (toggleIntakeButton) {
    toggleIntakeButton.textContent = collapsed ? "Show Intake" : "Intake";
    toggleIntakeButton.setAttribute("aria-expanded", String(!collapsed));
  }
  if (collapseIntakeButton) {
    collapseIntakeButton.textContent = collapsed ? "Hidden" : "Hide";
  }
}

function setReviewRailCollapsed(collapsed) {
  appShell?.classList.toggle("review-rail-collapsed", collapsed);
  if (toggleReviewRailButton) {
    toggleReviewRailButton.setAttribute("aria-expanded", String(!collapsed));
    toggleReviewRailButton.textContent = collapsed ? "Review" : "Hide Review";
  }
  closeReviewRailButton?.setAttribute("aria-expanded", String(!collapsed));
}

function promoteReviewAfterArchitectComment(changedField) {
  if (!hasPermission("can_architect_review")) {
    return;
  }
  if (changedField !== architectNotes && changedField !== reviewComments) {
    return;
  }
  if (reviewState.status !== "needs_review") {
    return;
  }
  const hasReviewComment = Boolean(
    (architectNotes?.value || "").trim() || (reviewComments?.value || "").trim(),
  );
  if (!hasReviewComment) {
    return;
  }
  reviewState.status = "reviewed";
  reviewState.reviewed = true;
  if (workflowStatus) {
    workflowStatus.value = "reviewed";
  }
  if (markReviewedButton) {
    markReviewedButton.textContent = "Reviewed";
  }
  showToast("Architect comments captured. Status moved to Reviewed.", "success");
}

function buildQualityGateItems(payload) {
  const mappings = payload?.service_mappings || [];
  const risks = payload?.risks || [];
  const missing = payload?.source_architecture?.missing_information || [];
  const assumptions = payload?.assumptions || payload?.source_architecture?.assumptions || [];
  const readiness = Number(payload?.assessment_insights?.scores?.overall_readiness?.value ?? 0);
  const costPredictability = Number(payload?.assessment_insights?.scores?.cost_predictability?.value ?? 0);
  const lowConfidenceMappings = mappings.filter((mapping) => Number(mapping.confidence || 0) < 0.75);
  const criticalRisks = risks.filter((risk) => ["critical", "high"].includes(String(risk.severity || "").toLowerCase()));
  const pattern = selectedArchitecturePattern(payload);

  return [
    {
      label: "Readiness",
      value: `${Math.round(readiness)}%`,
      status: readiness >= 70 ? "good" : readiness >= 45 ? "warn" : "block",
      detail:
        readiness >= 70
          ? "Assessment is strong enough for planning review."
          : "Improve missing inputs, risks, and owner validation before approval.",
    },
    {
      label: "Mapping Confidence",
      value: `${lowConfidenceMappings.length} open`,
      status: lowConfidenceMappings.length ? "warn" : "good",
      detail: lowConfidenceMappings.length
        ? "Low-confidence mappings need architect decisions."
        : "No low-confidence mappings are currently blocking review.",
    },
    {
      label: "Risk Gate",
      value: `${criticalRisks.length} high`,
      status: criticalRisks.length ? "block" : "good",
      detail: criticalRisks.length
        ? "High or critical risks need owners and mitigations."
        : "No high-impact risks are currently blocking the draft.",
    },
    {
      label: "Cost Confidence",
      value: `${Math.round(costPredictability)}%`,
      status: costPredictability >= 65 ? "good" : costPredictability >= 35 ? "warn" : "block",
      detail: "Cost remains directional until inventory, usage, and data volume are attached.",
    },
    {
      label: "Missing Inputs",
      value: `${missing.length}`,
      status: missing.length > 2 ? "block" : missing.length ? "warn" : "good",
      detail: missing.length
        ? "Assign owners for missing information before final signoff."
        : assumptions.length
          ? "Assumptions exist, but no explicit missing information was returned."
          : "No missing information listed by the assessment.",
    },
    {
      label: "Pattern",
      value: pattern.label,
      status: "neutral",
      detail: pattern.guardrails,
    },
  ];
}

function renderQualityGates(payload) {
  if (!qualityGates) {
    return;
  }
  const gates = buildQualityGateItems(payload);
  const blockerCount = gates.filter((gate) => gate.status === "block").length;
  const warningCount = gates.filter((gate) => gate.status === "warn").length;
  qualityGates.innerHTML = `
    <section class="quality-card ${blockerCount ? "block" : warningCount ? "warn" : "good"} quality-card-lead">
      <span>Assessment Gate</span>
      <strong>${blockerCount ? "Blocked for approval" : warningCount ? "Review required" : "Planning ready"}</strong>
      <p>${blockerCount ? `${blockerCount} blockers must be resolved before approval.` : warningCount ? `${warningCount} items need architect review.` : "No major blockers detected in the current draft."}</p>
    </section>
    ${gates
      .map(
        (gate) => `
          <section class="quality-card ${escapeHtml(gate.status)}">
            <span>${escapeHtml(gate.label)}</span>
            <strong>${escapeHtml(gate.value)}</strong>
            <p>${escapeHtml(gate.detail)}</p>
          </section>
        `,
      )
      .join("")}
  `;
}

function hasApprovalBlockers(payload) {
  return buildQualityGateItems(payload).some((gate) => gate.status === "block");
}

function refreshReviewStatusViews(payload = latestResult) {
  if (!payload) {
    return;
  }
  renderSummary(payload);
  renderQualityGates(payload);
  overviewPanel.innerHTML = renderOverview(payload);
  gatePanel.innerHTML = renderDecisionGate(payload);
  renderReviewPanel(payload);
}

function syncSnapshotCondensed() {
  const shouldCondense = Boolean(latestResult) && window.scrollY > 180 && window.innerWidth > 760;
  document.body.classList.toggle("snapshot-condensed", shouldCondense);
}

function renderOverview(payload) {
  const scores = payload.assessment_insights?.scores || {};
  const effort = payload.assessment_insights?.effort || {};
  const sourceCount = payload.source_architecture?.components?.length || 0;
  const targetCount = payload.target_architecture?.components?.length || 0;
  const targetLabel = formatProvider(payload.target_architecture?.provider || targetProvider.value);
  const sourceProviderLabel = payload.source_architecture?.provider || sourceProvider.value;
  const targetProviderLabel = payload.target_architecture?.provider || targetProvider.value;
  const pattern = selectedArchitecturePattern(payload);
  const requiredChanges = payload.required_changes || [];
  const benefits = payload.benefits || [];
  const drawbacks = payload.drawbacks || [];
  const verdict = payload.final_verdict || {};

  return `
    <div class="workspace-section">
      <div class="section-header">
        <div>
          <p class="eyebrow">Decision Snapshot</p>
          <h3>${formatVerdict(verdict.recommendation || "conditionally_recommended")}</h3>
        </div>
        <div class="section-header-actions">
          ${providerRouteMarkup(sourceProviderLabel, targetProviderLabel, { compact: true })}
          <span class="status-badge ${escapeHtml(verdict.recommendation || "watch")}">${Math.round((verdict.confidence || 0) * 100)}% confidence</span>
        </div>
      </div>
      <p class="decision-text">${escapeHtml(verdict.reasoning || "Run an assessment to generate the migration recommendation.")}</p>
      ${renderWorkflowProgress()}
      <div class="chart-board">
        ${Object.values(scores).map((score) => renderScoreCard(score, payload)).join("")}
      </div>
    </div>

    ${renderPatternFlow(payload, pattern)}

    <div class="dashboard-grid">
      <section class="info-card">
        <p class="eyebrow">Scope</p>
        <h3>${sourceCount} source components to ${targetCount} ${escapeHtml(targetLabel)} target components</h3>
        <p>${escapeHtml(payload.source_architecture?.summary || "Source architecture summary unavailable.")}</p>
      </section>
      <section class="info-card">
        <p class="eyebrow">Effort</p>
        <h3>${formatTitle(effort.t_shirt_size || "not sized")}</h3>
        <p>${escapeHtml(effort.migration_effort || "Effort will appear after analysis.")}</p>
      </section>
    </div>

    <div class="dashboard-grid">
      ${renderListCard("Required Changes", requiredChanges.slice(0, 6))}
      ${renderListCard("Benefits", benefits.slice(0, 5))}
      ${renderListCard("Drawbacks", drawbacks.slice(0, 5))}
      ${renderListCard("Complexity Drivers", effort.complexity_drivers || [])}
    </div>
  `;
}

function renderSourceArchitecture(payload) {
  const architecture = payload.source_architecture || {};
  const components = architecture.components || [];
  const rows = components
    .map(
      (component, index) => `
        <tr>
          <td><input value="${escapeAttribute(component.name)}" data-component-field="name" data-index="${index}" /></td>
          <td><input value="${escapeAttribute(component.service_type || "")}" data-component-field="service_type" data-index="${index}" placeholder="Service type" /></td>
          <td><input value="${escapeAttribute(component.category || "")}" data-component-field="category" data-index="${index}" placeholder="Category" /></td>
          <td><input type="number" min="0" max="1" step="0.01" value="${Number(component.confidence || 0).toFixed(2)}" data-component-field="confidence" data-index="${index}" /></td>
          <td><input value="${escapeAttribute(component.description || "")}" data-component-field="description" data-index="${index}" placeholder="Notes" /></td>
          <td><button type="button" class="table-action" data-source-action="delete" data-index="${index}">Remove</button></td>
        </tr>
      `,
    )
    .join("");

  return `
    <div class="workspace-section">
      <div class="section-header">
        <div>
          <p class="eyebrow">Source Architecture</p>
          <h3>${providerLogoLockup(architecture.provider || "unknown", { label: formatProvider(architecture.provider || "unknown") })}</h3>
        </div>
        <div class="diagram-actions">
          <button type="button" class="diagram-link" data-source-action="add">Add Component</button>
          <button type="button" class="diagram-link primary-link" data-source-action="rebuild">Rebuild Assessment</button>
        </div>
      </div>
      <p>${escapeHtml(architecture.summary || "No source architecture summary returned.")}</p>
      ${renderComponentEditorSummary(components)}
      <div class="table-scroll architect-only">
        <table class="mapping-table editable-table">
          <thead>
            <tr>
              <th>Component</th>
              <th>Service Type</th>
              <th>Category</th>
              <th>Confidence</th>
              <th>Notes</th>
              <th></th>
            </tr>
          </thead>
          <tbody>${rows || '<tr><td colspan="6">No components detected.</td></tr>'}</tbody>
        </table>
      </div>
      ${renderRelationshipEditor(architecture)}
      ${renderSectionComment("source", "Source architecture comments")}
    </div>
    <div class="dashboard-grid">
      ${renderListCard("Assumptions", architecture.assumptions || [])}
      ${renderListCard("Missing Information", architecture.missing_information || [])}
    </div>
  `;
}

function renderMappings(mappings) {
  if (!mappings.length) {
    return '<div class="empty-state">No service mappings returned.</div>';
  }
  const targetLabel = formatProvider(latestResult?.target_architecture?.provider || targetProvider.value);
  const rows = mappings
    .map(
      (mapping, index) => `
        <tr>
          <td>
            <strong>${escapeHtml(mapping.source_service)}</strong>
            <span class="table-subtle">Detected source service</span>
          </td>
          <td>
            <strong>${escapeHtml(mapping.target_service)}</strong>
            <span class="table-subtle">${escapeHtml(targetLabel)} recommendation</span>
          </td>
          <td>
            <div class="mapping-confidence-cell">
              ${renderMiniPie(Math.round((mapping.confidence || 0) * 100), mappingConfidenceStatus(mapping.confidence || 0))}
              <span>${Math.round((mapping.confidence || 0) * 100)}%</span>
            </div>
          </td>
          <td>${renderTags((mapping.alternatives || []).slice(0, 3))}</td>
          <td>${escapeHtml(mapping.reasoning)}</td>
          <td>
            <select class="review-select" aria-label="Mapping ${index + 1} review decision">
              <option>AI Draft</option>
              <option>Accepted</option>
              <option>Needs Review</option>
              <option>Replace Target</option>
            </select>
          </td>
        </tr>
        <tr class="mapping-review-row architect-only">
          <td colspan="6">
            <details>
              <summary>Compare alternatives and add reviewer comment</summary>
              ${renderMappingComparison(mapping)}
              ${renderSectionComment(`mapping_${index}`, "Mapping review comment", true)}
            </details>
          </td>
        </tr>
      `,
    )
    .join("");
  return `
    <div class="workspace-section">
      <div class="section-header">
        <div>
          <p class="eyebrow">Service Mapping</p>
          <h3>Source-to-${providerLogoLockup(latestResult?.target_architecture?.provider || targetProvider.value, { label: targetLabel })} Equivalence</h3>
        </div>
        <div class="section-header-actions">
          <span class="status-badge">${mappings.length} mappings</span>
          <span class="status-badge ${mappings.some((item) => Number(item.confidence || 0) < 0.75) ? "watch" : "good"}">
            ${mappings.filter((item) => Number(item.confidence || 0) < 0.75).length} need review
          </span>
        </div>
      </div>
      <div class="mapping-review-toolbar">
        <span>Recommended target services are AI-generated. Confirm alternatives before approval.</span>
        <button type="button" class="diagram-link" data-agent-prompt="Which mappings need architect review?">Ask Agent</button>
      </div>
      <div class="table-scroll">
        <table class="mapping-table mapping-review-table">
          <thead>
            <tr>
              <th>Source Service</th>
              <th>Recommended Target</th>
              <th>Confidence</th>
              <th>Alternatives</th>
              <th>Rationale</th>
              <th>Decision</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
      ${renderSectionComment("mapping", "Overall mapping comments")}
    </div>
  `;
}

function renderDiagram(payload) {
  const mermaid = normalizeMermaidSource(payload.mermaid_diagram || "");
  const mermaidSvgUrl = mermaid ? buildMermaidInkUrl(mermaid, "svg") : "";
  const mermaidPngUrl = mermaid ? buildMermaidInkUrl(mermaid, "img") : "";
  const targetComponents = payload.target_architecture?.components || [];
  const selectedComponent =
    targetComponents.find((component) => component.id === selectedCanvasComponentId) || targetComponents[0];

  return `
    <div class="diagram-card">
      <section class="diagram-control-strip" aria-label="Diagram quality controls">
        <label>
          <span>Diagram style</span>
          <select id="diagramDetailLevel" data-diagram-control>
            <option value="review">Architecture review</option>
            <option value="executive">Executive</option>
            <option value="implementation">Implementation detail</option>
          </select>
        </label>
        <label class="toggle-row">
          <input type="checkbox" data-diagram-control="mermaid" checked />
          <span>Mermaid preview</span>
        </label>
        <label class="toggle-row">
          <input type="checkbox" data-diagram-control="source" />
          <span>Editable source</span>
        </label>
        <label class="toggle-row">
          <input type="checkbox" data-canvas-layer="security" checked />
          <span>Security</span>
        </label>
        <label class="toggle-row">
          <input type="checkbox" data-canvas-layer="observability" checked />
          <span>Operations</span>
        </label>
        <div class="zoom-control" aria-label="Architecture diagram zoom">
          <button type="button" data-canvas-zoom="fit">Fit</button>
          <button type="button" data-canvas-zoom="100">100%</button>
          <button type="button" data-canvas-zoom="125">125%</button>
          <button type="button" data-canvas-zoom="150">150%</button>
          <button type="button" data-canvas-zoom="300">300%</button>
        </div>
      </section>
      <section class="diagram-section">
        <div class="diagram-section-header">
          <div>
            <h3>Rendered ${providerLogoLockup(payload.target_architecture?.provider || targetProvider.value, { label: formatProvider(payload.target_architecture?.provider || targetProvider.value) })} Diagram</h3>
            <p>Canvas-first target architecture workspace with pan, zoom, service selection, and layer controls.</p>
          </div>
        </div>
        <div class="architecture-hero-shell">
          <div class="architecture-canvas">
            <div class="diagram-viewport">
              <div class="diagram-image-wrap" id="diagramImageWrap" style="--diagram-zoom: ${diagramZoom}" tabindex="0" aria-label="Rendered architecture diagram viewport. Use scrollbars or drag after zooming.">
                <div class="diagram-render-state">Rendering target diagram preview</div>
              </div>
              <div class="diagram-minimap architect-only" aria-hidden="true">
                <span></span>
                <strong>Viewport</strong>
              </div>
            </div>
            <div class="architecture-details architect-only">
              <div class="canvas-sidebar">
                <p class="eyebrow">Services</p>
                <div class="arch-node-list">
                  ${renderArchitectureNodeList(targetComponents)}
                </div>
              </div>
              <aside class="canvas-inspector" id="canvasInspector">
                ${renderCanvasInspector(selectedComponent)}
              </aside>
            </div>
          </div>
        </div>
      </section>
      ${renderSectionComment("diagram", "Architecture diagram comments")}

      <section class="diagram-section mermaid-section architect-only">
        <div class="diagram-section-header">
          <div>
            <h3>Mermaid Diagram</h3>
            <p>Rendered preview with direct links for sharing or opening outside the app.</p>
          </div>
          <div class="diagram-actions">
            <a class="diagram-link" href="${escapeHtml(mermaidSvgUrl)}" target="_blank" rel="noopener">Open SVG</a>
            <a class="diagram-link" href="${escapeHtml(mermaidPngUrl)}" target="_blank" rel="noopener">Open PNG</a>
            <button type="button" class="diagram-link" data-copy-mermaid>Copy Source</button>
          </div>
        </div>
        <div class="mermaid-render-wrap" id="mermaidRenderWrap">
          <div class="diagram-render-state">Rendering Mermaid diagram</div>
        </div>
        <details class="source-toggle mermaid-source-toggle">
          <summary>View Mermaid source</summary>
          <pre class="diagram-code">${escapeHtml(mermaid)}</pre>
        </details>
      </section>
    </div>
  `;
}

function renderPlan(payload) {
  const planning = payload.assessment_insights?.planning || {};
  const phases = payload.migration_strategy || [];
  const waveCards = (planning.waves || [])
    .map(
      (wave) => `
        <section class="info-card">
          <p class="eyebrow">${escapeHtml(wave.wave)}</p>
          <h3>${escapeHtml(wave.scope)}</h3>
          <p><strong>Dependencies:</strong> ${escapeHtml(wave.dependencies)}</p>
          <p><strong>Exit:</strong> ${escapeHtml(wave.exit_criteria)}</p>
        </section>
      `,
    )
    .join("");

  return `
    <div class="workspace-section">
      <div class="section-header">
        <div>
          <p class="eyebrow">Migration Plan</p>
          <h3>Phased Delivery Model</h3>
        </div>
      </div>
      <div class="wave-grid">${waveCards || '<div class="empty-state">No waves returned.</div>'}</div>
    </div>
    <div class="dashboard-grid">
      ${renderListCard("Dependencies", planning.dependencies || [])}
      ${renderListCard("Cutover Plan", planning.cutover_plan || [])}
      ${renderListCard("Rollback Plan", planning.rollback_plan || [])}
      ${renderListCard("Data Migration Approach", planning.data_migration_approach || [])}
    </div>
    <div class="workspace-section">
      <h3>Generated Strategy Phases</h3>
      ${renderPhaseTable(phases)}
      ${renderSectionComment("plan", "Migration plan comments")}
    </div>
  `;
}

function renderRisks(payload) {
  const risks = payload.risks || [];
  const scores = payload.assessment_insights?.scores || {};
  const riskScores = Object.values(scores).filter((score) =>
    /risk|readiness|security|cost/i.test(score?.label || ""),
  );
  const rows = risks
    .map(
      (risk) => `
        <tr>
          <td><strong>${escapeHtml(risk.title)}</strong></td>
          <td><span class="risk-pill ${escapeHtml(risk.severity)}">${escapeHtml(risk.severity)}</span></td>
          <td>${escapeHtml(risk.description)}</td>
          <td>${escapeHtml(risk.mitigation)}</td>
        </tr>
      `,
    )
    .join("");
  return `
    <div class="workspace-section">
      <div class="section-header">
        <div>
          <p class="eyebrow">Risk Dashboard</p>
          <h3>Readiness and Risk Scores</h3>
        </div>
      </div>
      <div class="chart-board compact">
        ${riskScores.map((score) => renderScoreCard(score, payload)).join("") || Object.values(scores).map((score) => renderScoreCard(score, payload)).join("")}
      </div>
    </div>
    <div class="workspace-section architect-only">
      <div class="table-scroll">
        <table class="mapping-table">
          <thead>
            <tr>
              <th>Risk</th>
              <th>Severity</th>
              <th>Description</th>
              <th>Mitigation</th>
            </tr>
          </thead>
          <tbody>${rows || '<tr><td colspan="4">No risks returned.</td></tr>'}</tbody>
        </table>
      </div>
      ${renderSectionComment("risks", "Risk review comments")}
    </div>
  `;
}

function renderCost(payload) {
  const cost = payload.assessment_insights?.cost || {};
  const effort = payload.assessment_insights?.effort || {};
  const scores = payload.assessment_insights?.scores || {};
  const size = String(effort.t_shirt_size || "medium").toLowerCase();
  const uncertainty = scores.cost_predictability?.value ?? 50;
  const estimate = estimateCostRange(payload);
  const savings = renderSavingsCard(estimate);
  return `
    <div class="cost-estimate-board">
      <section class="cost-estimate-card primary-estimate">
        <p class="eyebrow">Estimated Monthly Run-rate</p>
        <h3>${formatCurrencyRange(estimate.monthlyLow, estimate.monthlyHigh)}</h3>
        <p>Target steady-state infrastructure, platform, observability, and managed service usage.</p>
      </section>
      ${savings}
      <section class="cost-estimate-card">
        <p class="eyebrow">Migration Project Estimate</p>
        <h3>${formatCurrencyRange(estimate.projectLow, estimate.projectHigh)}</h3>
        <p>One-time engineering, validation, cutover, rollback planning, and governance effort.</p>
      </section>
      <section class="cost-estimate-card">
        <p class="eyebrow">Dual-run Reserve</p>
        <h3>${formatCurrencyRange(estimate.dualRunLow, estimate.dualRunHigh)}</h3>
        <p>Temporary overlap for source and target environments during validation and cutover.</p>
      </section>
    </div>
    <div class="chart-board compact cost-score-board">
      ${["cost_predictability", "operational_readiness", "overall_readiness"]
        .map((key) => scores[key])
        .filter(Boolean)
        .map((score) => renderScoreCard(score, payload))
        .join("")}
    </div>
    <div class="cost-visual-board">
      <section class="info-card emphasis-card">
        <p class="eyebrow">Effort Band</p>
        <h3>${formatTitle(effort.t_shirt_size || "not sized")}</h3>
        ${renderEffortBand(size)}
        <p>${escapeHtml(effort.migration_effort || "Effort estimate unavailable.")}</p>
      </section>
      <section class="info-card">
        <p class="eyebrow">Cost Uncertainty</p>
        <h3>${Math.max(0, 100 - Math.round(uncertainty))}% open</h3>
        <div class="uncertainty-meter"><span style="width: ${clamp(100 - Number(uncertainty || 0), 0, 100)}%"></span></div>
        <p>Refine with inventory, utilization, data volume, traffic, licensing, and support assumptions.</p>
      </section>
      <section class="info-card">
        <p class="eyebrow">Dual-run</p>
        <h3>${effort.dual_run_warning ? "Budget Needed" : "Not Flagged"}</h3>
        <p>${escapeHtml(effort.dual_run_warning || "No dual-run warning returned by the assessment.")}</p>
      </section>
    </div>
    <div class="dashboard-grid">
      ${renderListCard("Cost Drivers", cost.cost_drivers || [])}
      ${renderListCard("Optimization Levers", cost.optimization_levers || [])}
      ${renderListCard("Estimation Notes", cost.estimation_notes || [])}
      ${renderListCard("Skill Readiness Gaps", effort.skill_readiness_gaps || [])}
    </div>
    ${renderSectionComment("cost", "Cost and effort comments")}
  `;
}

function renderSavingsCard(estimate) {
  const hasSavings = estimate.sourceBaselineAvailable && estimate.savingsHigh > 0;
  const title = hasSavings
    ? `${formatSavingsRange(estimate.savingsLow, estimate.savingsHigh)} / mo`
    : "No savings signal";
  const annualText = hasSavings
    ? `Annualized: ${formatSavingsRange(estimate.annualSavingsLow, estimate.annualSavingsHigh)} if source resources are decommissioned.`
    : !estimate.sourceBaselineAvailable
      ? "Savings requires a detected source baseline or attached inventory data."
    : `Target run-rate is not below the directional source baseline of ${formatCurrencyRange(
        estimate.sourceMonthlyLow,
        estimate.sourceMonthlyHigh,
      )}.`;
  return `
    <section class="cost-estimate-card savings-estimate ${hasSavings ? "positive" : "neutral"}">
      <p class="eyebrow">Estimated Savings</p>
      <h3>${escapeHtml(title)}</h3>
      <p>${escapeHtml(annualText)}</p>
    </section>
  `;
}

function renderReviewPanel(payload) {
  const review = payload.assessment_insights?.review || {};
  const checklist = review.decision_gate_checklist || [];
  reviewChecklist.innerHTML = checklist.length
    ? checklist
        .map(
          (item) => `
            <div class="check-item ${escapeHtml(item.status)}">
              <span></span>
              <div>
                <strong>${escapeHtml(item.item)}</strong>
                <p>${escapeHtml(item.evidence)}</p>
              </div>
            </div>
          `,
        )
        .join("")
    : '<div class="empty-state">Decision checklist will appear after analysis.</div>';

  const warnings = review.warnings || [];
  const nextActions = review.suggested_next_actions || [];
  const architect = review.architect_notes || [];
  reviewNotes.innerHTML = `
    ${renderRailList("Warnings", warnings)}
    ${renderRailList("Next Actions", nextActions)}
    ${renderRailList("Architect Notes", architect)}
  `;
  markReviewedButton.disabled = !latestResult || !hasPermission("can_architect_review");
  markReviewedButton.textContent = reviewState.reviewed ? "Reviewed" : "Mark";
  workflowStatus.value = reviewState.status || (reviewState.reviewed ? "reviewed" : "needs_review");
  workflowStatus.disabled = !hasPermission("can_architect_review");
  architectNotes.disabled = !hasPermission("can_architect_review");
  reviewComments.disabled = !hasPermission("can_review");
}

function renderDecisionGate(payload) {
  const review = payload.assessment_insights?.review || {};
  const checklist = review.decision_gate_checklist || [];
  const warnings = review.warnings || [];
  const readiness = payload.assessment_insights?.scores?.overall_readiness;
  const pattern = selectedArchitecturePattern(payload);
  const approvalBlocked = hasApprovalBlockers(payload);
  const gateReady = !approvalBlocked && readiness?.value >= 70 && checklist.every((item) => item.status !== "required") && !warnings.length;
  const rows = checklist
    .map(
      (item) => `
        <div class="gate-row ${escapeHtml(item.status)}">
          <span></span>
          <div>
            <strong>${escapeHtml(item.item)}</strong>
            <p>${escapeHtml(item.evidence)}</p>
          </div>
        </div>
      `,
    )
    .join("");

  return `
    <div class="workspace-section">
      <div class="section-header">
        <div>
          <p class="eyebrow">Decision Gate</p>
          <h3>${gateReady ? "Ready For Planning" : "Architect Review Required"}</h3>
        </div>
        <span class="status-badge ${gateReady ? "recommended" : "conditionally_recommended"}">${escapeHtml(workflowLabel(reviewState.status))}</span>
      </div>
      <div class="gate-summary">
        <section class="info-card">
          <p class="eyebrow">Pattern</p>
          <h3>${escapeHtml(pattern.label)}</h3>
          <p>${escapeHtml(pattern.description)}</p>
        </section>
        <section class="info-card">
          <p class="eyebrow">Approval Rule</p>
          <h3>${readiness?.value ?? 0}% readiness</h3>
          <p>Approve only after required checklist items, cost model, security review, and rollback plan are accepted.</p>
        </section>
      </div>
      <div class="approval-banner ${approvalBlocked ? "block" : "good"}">
        <strong>${approvalBlocked ? "Approval blocked" : "Approval path open"}</strong>
        <span>${approvalBlocked ? "Resolve quality gate blockers before moving this assessment to Approved For Planning." : "No blocking quality gates are currently open. Architect signoff is still required."}</span>
      </div>
      <div class="gate-list">${rows || '<div class="empty-state">No checklist returned.</div>'}</div>
      <div class="dashboard-grid">
        ${renderListCard("Warnings", warnings)}
        ${renderListCard("Next Actions", review.suggested_next_actions || [])}
      </div>
      ${renderSectionComment("final_verdict", "Final verdict comments")}
    </div>
  `;
}

function renderScoreCard(score, payload = latestResult) {
  if (!score) {
    return "";
  }
  const value = clamp(Number(score.value || 0), 0, 100);
  const status = score.status || "watch";
  const factors = explainScore(score, payload);
  return `
    <section class="score-card chart-card ${escapeHtml(status)}">
      <div class="score-pie" style="--percent: ${value}%; --pie-color: ${chartColor(status)}">
        <span>${Math.round(value)}%</span>
      </div>
      <div>
        <div class="score-card-top">
          <span>${escapeHtml(score.label || "Score")}</span>
        </div>
        <p>${escapeHtml(score.description || "")}</p>
        <ul class="score-factors">
          ${factors.map((factor) => `<li>${escapeHtml(factor)}</li>`).join("")}
        </ul>
      </div>
    </section>
  `;
}

function renderMiniPie(value, status) {
  const percent = clamp(Number(value || 0), 0, 100);
  return `
    <div class="mini-pie" style="--percent: ${percent}%; --pie-color: ${chartColor(status)}">
      <span>${Math.round(percent)}%</span>
    </div>
  `;
}

function renderWorkflowProgress() {
  const steps = [
    ["ai_draft", "AI Draft"],
    ["needs_review", "Architect Review"],
    ["reviewed", "Reviewed"],
    ["approved", "Planning Approved"],
  ];
  const currentIndex = Math.max(0, steps.findIndex(([key]) => key === reviewState.status));
  return `
    <div class="workflow-progress">
      ${steps
        .map(
          ([key, label], index) => `
            <div class="workflow-step ${index <= currentIndex ? "active" : ""} ${key === reviewState.status ? "current" : ""}">
              <span>${index + 1}</span>
              <strong>${escapeHtml(label)}</strong>
            </div>
          `,
        )
        .join("")}
    </div>
  `;
}

function renderPatternFlow(payload, pattern) {
  const sourceProviderLabel = formatProvider(payload.source_architecture?.provider || sourceProvider.value);
  const targetProviderLabel = formatProvider(payload.target_architecture?.provider || targetProvider.value);
  return `
    <div class="pattern-flow">
      <section class="pattern-card">
        <p class="eyebrow">Source Pattern</p>
        <h3>${providerLogoLockup(payload.source_architecture?.provider || sourceProvider.value, { label: pattern.label })}</h3>
        <p>${escapeHtml(sourceProviderLabel)} topology inferred from diagram components, labels, and relationships.</p>
      </section>
      <section class="pattern-card">
        <p class="eyebrow">Mapped Target Pattern</p>
        <h3>${providerLogoLockup(payload.target_architecture?.provider || targetProvider.value, { label: `${targetProviderLabel} ${pattern.label}` })}</h3>
        <p>${escapeHtml(pattern.targetDescription)}</p>
      </section>
      <section class="pattern-card">
        <p class="eyebrow">Production Guardrails</p>
        <h3>${escapeHtml(pattern.guardrailTitle)}</h3>
        <p>${escapeHtml(pattern.guardrails)}</p>
      </section>
    </div>
  `;
}

function renderComponentEditorSummary(components) {
  const total = components.length;
  const lowConfidence = components.filter((component) => Number(component.confidence || 0) < 0.7).length;
  const missingType = components.filter((component) => !(component.service_type || "").trim()).length;
  const relationshipCount = latestResult?.source_architecture?.relationships?.length || 0;
  return `
    <div class="editor-summary">
      <div><strong>${total}</strong><span>Components</span></div>
      <div><strong>${relationshipCount}</strong><span>Relationships</span></div>
      <div><strong>${lowConfidence}</strong><span>Low confidence</span></div>
      <div><strong>${missingType}</strong><span>Need service type</span></div>
    </div>
  `;
}

function renderRelationshipEditor(architecture) {
  const relationships = architecture.relationships || [];
  const components = architecture.components || [];
  const rows = relationships
    .map(
      (relationship, index) => `
        <tr>
          <td>
            <select data-relationship-field="source_id" data-index="${index}">
              ${renderComponentOptions(components, relationship.source_id)}
            </select>
          </td>
          <td><input value="${escapeAttribute(relationship.relationship_type || "")}" data-relationship-field="relationship_type" data-index="${index}" placeholder="routes to, reads from, publishes to" /></td>
          <td>
            <select data-relationship-field="target_id" data-index="${index}">
              ${renderComponentOptions(components, relationship.target_id)}
            </select>
          </td>
          <td><input value="${escapeAttribute(relationship.description || "")}" data-relationship-field="description" data-index="${index}" placeholder="Relationship notes" /></td>
          <td><button type="button" class="table-action" data-relationship-action="delete" data-index="${index}">Remove</button></td>
        </tr>
      `,
    )
    .join("");

  return `
    <div class="relationship-editor architect-only">
      <div class="section-header">
        <div>
          <p class="eyebrow">Relationship Editor</p>
          <h3>Architecture Arrows</h3>
        </div>
        <button type="button" class="diagram-link" data-relationship-action="add">Add Relationship</button>
      </div>
      <div class="table-scroll">
        <table class="mapping-table editable-table">
          <thead>
            <tr>
              <th>From</th>
              <th>Relationship</th>
              <th>To</th>
              <th>Notes</th>
              <th></th>
            </tr>
          </thead>
          <tbody>${rows || '<tr><td colspan="5">No relationships detected.</td></tr>'}</tbody>
        </table>
      </div>
    </div>
  `;
}

function renderComponentOptions(components, selectedId) {
  if (!components.length) {
    return '<option value="">No components</option>';
  }
  return components
    .map(
      (component) => `
        <option value="${escapeAttribute(component.id)}" ${component.id === selectedId ? "selected" : ""}>
          ${escapeHtml(component.name)}
        </option>
      `,
    )
    .join("");
}

function renderSectionComment(sectionKey, label, compact = false) {
  const value = reviewState.sectionComments?.[sectionKey] || "";
  return `
    <label class="section-comment ${compact ? "compact" : ""} architect-only">
      <span>${escapeHtml(label)}</span>
      <textarea data-section-comment="${escapeAttribute(sectionKey)}" rows="${compact ? 2 : 3}" placeholder="Add review comment">${escapeHtml(value)}</textarea>
    </label>
  `;
}

function renderMappingComparison(mapping) {
  const options = buildMappingOptions(mapping);
  return `
    <div class="mapping-comparison">
      ${options
        .map(
          (option) => `
            <section class="mapping-option ${option.recommended ? "recommended-option" : ""}">
              <span>${escapeHtml(option.label)}</span>
              <strong>${escapeHtml(option.service)}</strong>
              <p>${escapeHtml(option.rationale)}</p>
            </section>
          `,
        )
        .join("")}
    </div>
  `;
}

function buildMappingOptions(mapping) {
  const alternatives = [...new Set([mapping.target_service, ...(mapping.alternatives || [])].filter(Boolean))];
  const findMatch = (pattern) => alternatives.find((item) => pattern.test(item)) || alternatives[0] || mapping.target_service;
  const conservative = alternatives[1] || mapping.target_service;
  const modernized = findMatch(/ecs|aks|gke|container|app runner|app service|cloud run|databricks|managed|aurora|fabric|synapse|bigquery/i);
  const serverless = findMatch(/lambda|function|cloud run functions|app runner|container apps|eventbridge|pub\/sub|event hubs/i);
  return [
    {
      label: "Recommended",
      service: mapping.target_service || "Target service",
      rationale: "Best fit selected by the mapping engine for this assessment.",
      recommended: true,
    },
    {
      label: "Conservative",
      service: conservative,
      rationale: "Lower-change option when minimizing migration risk matters most.",
    },
    {
      label: "Modernized",
      service: modernized,
      rationale: "Managed or platform-native option for operational improvement.",
    },
    {
      label: "Serverless",
      service: serverless,
      rationale: "Useful when event-driven scale and reduced infrastructure ownership fit.",
    },
  ];
}

function renderEffortBand(size) {
  const bands = ["small", "medium", "large", "complex"];
  const normalized = bands.includes(size) ? size : size.includes("complex") ? "complex" : "medium";
  return `
    <div class="effort-band" data-effort="${escapeAttribute(normalized)}">
      ${bands.map((band) => `<span class="${band === normalized ? "active" : ""}">${escapeHtml(formatTitle(band))}</span>`).join("")}
    </div>
  `;
}

function estimateCostRange(payload) {
  const sourceComponents = payload?.source_architecture?.components || [];
  const targetComponents = payload?.target_architecture?.components || [];
  const mappings = payload?.service_mappings || [];
  const effortSize = String(payload?.assessment_insights?.effort?.t_shirt_size || "medium").toLowerCase();
  const sourceProviderKey = normalizeProviderKey(payload?.source_architecture?.provider || sourceProvider.value);
  const targetProviderKey = normalizeProviderKey(payload?.target_architecture?.provider || targetProvider.value);
  const weights = {
    compute: 420,
    application: 360,
    database: 1450,
    storage: 260,
    networking: 320,
    network: 320,
    security: 210,
    observability: 240,
    analytics: 1800,
    ai: 2200,
    ml: 2200,
    messaging: 430,
    resilience: 360,
  };
  const sourceProviderMultiplier = providerCostMultiplier(sourceProviderKey);
  const targetProviderMultiplier = providerCostMultiplier(targetProviderKey);
  const sizeMultiplier = effortSize.includes("complex")
    ? 2.25
    : effortSize.includes("large")
      ? 1.65
      : effortSize.includes("small")
        ? 0.75
        : 1.1;

  const targetComponentMonthly = estimateComponentMonthly(targetComponents, weights, 1200);
  const sourceComponentMonthly = estimateComponentMonthly(
    sourceComponents.length ? sourceComponents : targetComponents,
    weights,
    1400,
  );

  const monthlyMid = targetComponentMonthly * targetProviderMultiplier;
  const sourceMonthlyMid =
    sourceComponentMonthly * sourceProviderMultiplier * sourceBaselinePremium(payload);
  const uncertainty = 1 + clamp(100 - Number(payload?.assessment_insights?.scores?.cost_predictability?.value ?? 55), 0, 100) / 140;
  const projectMid = (mappings.length * 3600 + targetComponents.length * 2600 + 18000) * sizeMultiplier;
  const dualRunMid = monthlyMid * (effortSize.includes("complex") ? 4 : effortSize.includes("large") ? 3 : 2);
  const sourceMonthlyLow = roundCurrency(sourceMonthlyMid * 0.75);
  const sourceMonthlyHigh = roundCurrency(sourceMonthlyMid * uncertainty * 1.35);
  const monthlyLow = roundCurrency(monthlyMid * 0.65);
  const monthlyHigh = roundCurrency(monthlyMid * uncertainty * 1.35);
  const savingsLow = roundCurrency(Math.max(0, sourceMonthlyLow - monthlyHigh), 0);
  const savingsHigh = roundCurrency(Math.max(0, sourceMonthlyHigh - monthlyLow), 0);

  return {
    sourceBaselineAvailable: sourceComponents.length > 0,
    monthlyLow,
    monthlyHigh,
    sourceMonthlyLow,
    sourceMonthlyHigh,
    savingsLow: sourceComponents.length ? savingsLow : 0,
    savingsHigh: sourceComponents.length ? savingsHigh : 0,
    annualSavingsLow: sourceComponents.length ? roundCurrency(savingsLow * 12, 0) : 0,
    annualSavingsHigh: sourceComponents.length ? roundCurrency(savingsHigh * 12, 0) : 0,
    projectLow: roundCurrency(projectMid * 0.7),
    projectHigh: roundCurrency(projectMid * 1.55),
    dualRunLow: roundCurrency(dualRunMid * 0.7),
    dualRunHigh: roundCurrency(dualRunMid * 1.4),
  };
}

function estimateComponentMonthly(components, weights, base) {
  return (components || []).reduce(
    (total, component) => total + componentCostWeight(component, weights),
    base,
  );
}

function componentCostWeight(component, weights) {
  const key = String(
    `${component?.name || ""} ${component?.category || ""} ${component?.service_type || ""}`,
  ).toLowerCase();
  const serviceWeights = [
    [/redshift|bigquery|synapse|fabric|warehouse|analytics/, weights.analytics],
    [/sagemaker|bedrock|vertex ai|openai|ai foundry|machine learning|\bml\b/, weights.ai],
    [/databricks|dataflow|dataproc|emr|glue|data factory|data fusion/, 1250],
    [/kubernetes|eks|aks|gke/, 950],
    [/ec2|virtual machine|compute engine|\bvm\b/, 650],
    [/lambda|function|cloud run|app runner|container apps/, 320],
    [/rds|aurora|sql|cosmos|dynamo|datastore|firestore|neo4j|database/, weights.database],
    [/s3|blob|adls|cloud storage|storage/, weights.storage],
    [/msk|kafka|pub\/sub|event hubs|service bus|sqs|sns|messaging/, weights.messaging],
    [/vpc|vnet|subnet|gateway|router|vpn|interconnect|direct connect|network/, weights.networking],
    [/iam|entra|rbac|secret|kms|key vault|security|firewall|waf|policy/, weights.security],
    [/monitor|logging|cloudwatch|insight|observability/, weights.observability],
    [/backup|recovery|dr|resilience/, weights.resilience],
  ];
  const matchedService = serviceWeights.find(([pattern]) => pattern.test(key));
  if (matchedService) {
    return matchedService[1];
  }
  const matchedCategory = Object.entries(weights).find(([name]) => key.includes(name));
  return matchedCategory ? matchedCategory[1] : 520;
}

function providerCostMultiplier(provider) {
  return { aws: 1, azure: 1.04, gcp: 1.02, neutral: 1 }[provider] || 1;
}

function sourceBaselinePremium(payload) {
  const text = [
    migrationIntent.value,
    goalsInput.value,
    ...(payload?.benefits || []),
    ...(payload?.assessment_insights?.cost?.optimization_levers || []),
  ]
    .join(" ")
    .toLowerCase();
  let premium = 1.08;
  if (/cost|saving|optimi[sz]e|right-?size|reduce/.test(text)) {
    premium += 0.08;
  }
  if (/moderni[sz]e|serverless|managed|autoscal|lifecycle|reservation|commit/.test(text)) {
    premium += 0.07;
  }
  return premium;
}

function roundCurrency(value, minimum = 500) {
  if (value <= 0) {
    return 0;
  }
  if (value >= 100000) {
    return Math.round(value / 10000) * 10000;
  }
  if (value >= 10000) {
    return Math.round(value / 5000) * 5000;
  }
  return Math.max(minimum, Math.round(value / 500) * 500);
}

function formatCurrencyRange(low, high) {
  return `$${formatCompactNumber(low)}-${formatCompactNumber(high)}`;
}

function formatSavingsRange(low, high) {
  if (high <= 0) {
    return "$0";
  }
  if (low <= 0) {
    return `Up to $${formatCompactNumber(high)}`;
  }
  return formatCurrencyRange(low, high);
}

function formatCompactNumber(value) {
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(value >= 10000000 ? 0 : 1)}M`;
  }
  if (value >= 1000) {
    return `${Math.round(value / 1000)}K`;
  }
  return String(Math.round(value));
}

function renderArchitectureNodeList(components) {
  if (!components.length) {
    return '<div class="empty-state">No target services returned.</div>';
  }
  return components
    .map((component) => {
      const layer = componentLayer(component);
      return `
        <button type="button" class="arch-node ${component.id === selectedCanvasComponentId ? "active" : ""}" data-arch-node="${escapeAttribute(component.id)}" data-layer="${escapeAttribute(layer)}">
          <strong>${escapeHtml(component.name)}</strong>
          <span>${escapeHtml(component.category || component.service_type || layer)}</span>
        </button>
      `;
    })
    .join("");
}

function renderCanvasInspector(component) {
  if (!component) {
    return '<div class="empty-state">Select a target service to inspect it.</div>';
  }
  return `
    <p class="eyebrow">Selected Service</p>
    <h3>${escapeHtml(component.name)}</h3>
    <div class="inspector-grid">
      <span>Category</span><strong>${escapeHtml(component.category || "Unknown")}</strong>
      <span>Type</span><strong>${escapeHtml(component.service_type || "Unspecified")}</strong>
      <span>Confidence</span><strong>${Math.round(Number(component.confidence || 0) * 100)}%</strong>
    </div>
    <p>${escapeHtml(component.description || "No description returned for this component.")}</p>
    ${renderRelatedMappings(component)}
  `;
}

function renderRelatedMappings(component) {
  const matches = (latestResult?.service_mappings || []).filter((mapping) => {
    const haystack = `${mapping.source_service} ${mapping.target_service}`.toLowerCase();
    return haystack.includes(String(component.name || "").toLowerCase().split(" ")[0]);
  });
  if (!matches.length) {
    return '<p class="muted">No direct mapping rationale matched this service.</p>';
  }
  return `
    <div class="rail-list">
      <strong>Mapping Rationale</strong>
      <ul>${matches.slice(0, 3).map((mapping) => `<li>${escapeHtml(mapping.reasoning)}</li>`).join("")}</ul>
    </div>
  `;
}

function explainScore(score, payload) {
  const label = String(score?.label || "").toLowerCase();
  const mappings = payload?.service_mappings || [];
  const risks = payload?.risks || [];
  const missing = payload?.source_architecture?.missing_information || [];
  const lowConfidence = mappings.filter((mapping) => Number(mapping.confidence || 0) < 0.75).length;
  const highRisks = risks.filter((risk) => ["high", "critical"].includes(String(risk.severity || "").toLowerCase())).length;
  if (label.includes("technical")) {
    return [
      `${mappings.length} service mappings require validation.`,
      lowConfidence ? `${lowConfidence} mappings are low-confidence.` : "Most mappings have usable confidence.",
    ];
  }
  if (label.includes("security") || label.includes("compliance")) {
    return [
      highRisks ? `${highRisks} high-impact risks affect approval.` : "No critical security blocker detected in the draft.",
      missing.length ? `${missing.length} missing inputs reduce assurance.` : "Control review still needs architect signoff.",
    ];
  }
  if (label.includes("cost")) {
    return [
      "Cost is directional until inventory, traffic, and data volumes are attached.",
      "Parallel-run and migration test environments should be modeled separately.",
    ];
  }
  if (label.includes("downtime")) {
    return [
      "Cutover risk depends on data movement, routing, and rollback windows.",
      "Lower score means lower interruption risk.",
    ];
  }
  return [
    highRisks ? `${highRisks} high-impact risks are open.` : "No critical blocker detected in this draft.",
    missing.length ? `${missing.length} missing information items need owners.` : "Ready for structured architect review.",
  ];
}

function selectedArchitecturePattern(payload) {
  const override = architecturePattern.value;
  if (override && override !== "auto") {
    return patternDefinition(override);
  }
  return inferArchitecturePattern(payload);
}

function inferArchitecturePattern(payload) {
  const text = [
    payload?.source_architecture?.summary,
    payload?.target_architecture?.summary,
    ...(payload?.source_architecture?.components || []).map((component) => `${component.name} ${component.service_type || ""}`),
    ...(payload?.target_architecture?.components || []).map((component) => `${component.name} ${component.service_type || ""}`),
    ...(payload?.service_mappings || []).map((mapping) => `${mapping.source_service} ${mapping.target_service}`),
  ]
    .join(" ")
    .toLowerCase();
  if (/neo4j|graphrag|knowledge graph|graph data science|cypher|bedrock|gemini/.test(text)) {
    return patternDefinition("graphrag");
  }
  if (/expressroute|direct connect|interconnect|vpn|cloud router|transit gateway|on-prem|on premises/.test(text)) {
    return patternDefinition("hybrid-connectivity");
  }
  if (/iot|device|telemetry|sensor|pub\/sub|event hubs|iot hub|iot core|kinesis|stream analytics/.test(text)) {
    return patternDefinition("iot-data-platform");
  }
  if (/bigquery|redshift|synapse|dataflow|databricks|glue|data lake|warehouse|pub\/sub|kafka|dataproc/.test(text)) {
    return patternDefinition("data-platform");
  }
  if (/kubernetes|ecs|eks|gke|aks|container|microservice/.test(text)) {
    return patternDefinition("microservices");
  }
  if (/lambda|app service|app engine|load balancer|cloud run|api gateway|web app/.test(text)) {
    return patternDefinition("web-application");
  }
  return patternDefinition("analytics-ai");
}

function patternDefinition(key) {
  const definitions = {
    "hybrid-connectivity": {
      label: "Hybrid connectivity",
      description: "Private circuit, VPN fallback, cloud routing, and workload network segmentation.",
      targetDescription: "Preserves on-premises connectivity with provider-native routing, private access, and failover controls.",
      guardrailTitle: "Routing and failover",
      guardrails: "Validate BGP, route priority, redundant links, private endpoints, DNS, firewall policy, monitoring, and rollback.",
    },
    "data-platform": {
      label: "Data platform",
      description: "Ingestion, stream or batch processing, storage, analytics, serving, and platform controls.",
      targetDescription: "Maps ingestion, processing, storage, analytics, BI/API serving, and governance into target-native services.",
      guardrailTitle: "Data governance",
      guardrails: "Validate lineage, retention, partitioning, data quality, access controls, encryption, and dual-run reconciliation.",
    },
    "iot-data-platform": {
      label: "IoT data platform",
      description: "Device or edge ingestion, streaming, processing, storage, analytics, serving, and operational controls.",
      targetDescription: "Separates device ingress, event streaming, stream processing, lake/warehouse storage, serving, and observability.",
      guardrailTitle: "Device and stream reliability",
      guardrails: "Validate device identity, protocol compatibility, event ordering, retry/dead-letter behavior, hot partitions, retention, and downstream replay.",
    },
    graphrag: {
      label: "GraphRAG / knowledge graph",
      description: "Data extraction, graph ingestion, Neo4j knowledge graph, retrieval, LLM orchestration, and applications.",
      targetDescription: "Keeps the graph database central while modernizing AI, retrieval, app hosting, and platform controls.",
      guardrailTitle: "Grounding and graph integrity",
      guardrails: "Validate Cypher compatibility, graph schema, embeddings, model governance, prompt logging, and retrieval quality.",
    },
    "web-application": {
      label: "Web application",
      description: "Ingress, app runtime, data stores, secrets, observability, and deployment workflow.",
      targetDescription: "Maps user-facing entry, application hosting, managed data, and operational controls.",
      guardrailTitle: "Runtime readiness",
      guardrails: "Validate identity, certificates, deployment pipeline, autoscaling, session state, rollback, and health checks.",
    },
    microservices: {
      label: "Microservices",
      description: "Container orchestration, service-to-service communication, eventing, data ownership, and operations.",
      targetDescription: "Maps container workloads into managed orchestration, ingress, service identity, and observability.",
      guardrailTitle: "Service ownership",
      guardrails: "Validate service boundaries, API contracts, traffic routing, secrets, scaling, CI/CD, and incident ownership.",
    },
    "analytics-ai": {
      label: "Analytics and AI",
      description: "Analytical data, model pipelines, notebooks, serving, governance, and operational monitoring.",
      targetDescription: "Maps analytics and AI workflows into target-native data, ML, and monitoring services.",
      guardrailTitle: "Model and data controls",
      guardrails: "Validate data access, model provenance, evaluation, cost controls, monitoring, and human approval paths.",
    },
  };
  return definitions[key] || definitions["analytics-ai"];
}

function mappingConfidenceStatus(value) {
  const percent = Number(value || 0) * 100;
  if (percent >= 78) {
    return "good";
  }
  if (percent >= 60) {
    return "watch";
  }
  return "risk";
}

function workflowLabel(value) {
  const labels = {
    ai_draft: "AI Draft",
    needs_review: "Needs Architect Review",
    reviewed: "Reviewed",
    approved: "Approved For Planning",
  };
  return labels[value] || labels.ai_draft;
}

function updateDiagramControls() {
  const card = document.querySelector(".diagram-card");
  if (!card) {
    return;
  }
  const detail = document.querySelector("#diagramDetailLevel")?.value || "review";
  const showMermaid = document.querySelector('[data-diagram-control="mermaid"]')?.checked ?? true;
  const showSource = document.querySelector('[data-diagram-control="source"]')?.checked ?? false;
  card.dataset.detail = detail;
  card.classList.toggle("hide-mermaid", !showMermaid);
  card.classList.toggle("show-source", showSource);
}

function updateCanvasZoom(action) {
  const wrap = document.querySelector("#diagramImageWrap");
  const centerX = wrap?.scrollWidth
    ? (wrap.scrollLeft + wrap.clientWidth / 2) / wrap.scrollWidth
    : 0.5;
  const centerY = wrap?.scrollHeight
    ? (wrap.scrollTop + wrap.clientHeight / 2) / wrap.scrollHeight
    : 0;

  if (action === "in") {
    diagramZoom = clamp(diagramZoom + 0.25, 0.65, 3);
  } else if (action === "out") {
    diagramZoom = clamp(diagramZoom - 0.25, 0.65, 3);
  } else if (action === "fit") {
    diagramZoom = 1;
  } else if (/^\d+$/.test(action)) {
    diagramZoom = clamp(Number(action) / 100, 0.65, 3);
  } else {
    diagramZoom = 1;
  }
  if (wrap) {
    wrap.style.setProperty("--diagram-zoom", diagramZoom);
    requestAnimationFrame(() => {
      restoreDiagramScrollPosition(wrap, centerX, centerY);
      updateDiagramPanAffordance(wrap);
    });
  }
  document.querySelector('[data-canvas-zoom="reset"]')?.replaceChildren(document.createTextNode(`${Math.round(diagramZoom * 100)}%`));
  syncZoomControls();
}

function canPanDiagram(wrap) {
  return wrap.scrollWidth > wrap.clientWidth + 2 || wrap.scrollHeight > wrap.clientHeight + 2;
}

function endDiagramPan(event) {
  if (!diagramPanState || (event && diagramPanState.pointerId !== event.pointerId)) {
    return;
  }

  diagramPanState.wrap.classList.remove("is-panning");
  diagramPanState.wrap.releasePointerCapture?.(diagramPanState.pointerId);
  updateDiagramPanAffordance(diagramPanState.wrap);
  diagramPanState = null;
}

function updateDiagramPanAffordance(wrap = document.querySelector("#diagramImageWrap")) {
  if (!wrap) {
    return;
  }
  wrap.classList.toggle("can-pan", canPanDiagram(wrap));
}

function restoreDiagramScrollPosition(wrap, centerX = 0.5, centerY = 0) {
  if (!wrap) {
    return;
  }

  const maxLeft = Math.max(0, wrap.scrollWidth - wrap.clientWidth);
  const maxTop = Math.max(0, wrap.scrollHeight - wrap.clientHeight);
  wrap.scrollLeft = clamp(centerX * wrap.scrollWidth - wrap.clientWidth / 2, 0, maxLeft);
  wrap.scrollTop = clamp(centerY * wrap.scrollHeight - wrap.clientHeight / 2, 0, maxTop);
}

function updateCanvasLayers() {
  const card = document.querySelector(".diagram-card");
  if (!card) {
    return;
  }
  const showSecurity = document.querySelector('[data-canvas-layer="security"]')?.checked ?? true;
  const showObservability = document.querySelector('[data-canvas-layer="observability"]')?.checked ?? true;
  card.classList.toggle("hide-security-layer", !showSecurity);
  card.classList.toggle("hide-observability-layer", !showObservability);
}

function syncZoomControls() {
  document.querySelectorAll("[data-canvas-zoom]").forEach((button) => {
    const action = button.dataset.canvasZoom || "";
    const percent = Math.round(diagramZoom * 100);
    const isPreset =
      (action === "fit" && percent === 100) ||
      (action === "100" && percent === 100) ||
      (action === "125" && percent === 125) ||
      (action === "150" && percent === 150) ||
      (action === "300" && percent === 300);
    button.classList.toggle("active", isPreset);
  });
}

function selectCanvasComponent(componentId) {
  selectedCanvasComponentId = componentId;
  document.querySelectorAll("[data-arch-node]").forEach((node) => {
    node.classList.toggle("active", node.dataset.archNode === componentId);
  });
  const component = (latestResult?.target_architecture?.components || []).find((item) => item.id === componentId);
  const inspector = document.querySelector("#canvasInspector");
  if (inspector) {
    inspector.innerHTML = renderCanvasInspector(component);
  }
}

function componentLayer(component) {
  const text = `${component?.name || ""} ${component?.category || ""} ${component?.service_type || ""}`.toLowerCase();
  if (/iam|identity|rbac|secret|kms|key vault|security|firewall|waf|policy|armor/.test(text)) {
    return "security";
  }
  if (/monitor|logging|cloudwatch|insight|observability|backup|recovery/.test(text)) {
    return "observability";
  }
  if (/subnet|vpc|vnet|dns|route|gateway|interconnect|direct connect|vpn|network/.test(text)) {
    return "network";
  }
  if (/s3|storage|database|sql|rds|dynamo|cosmos|bigquery|synapse|redshift|neo4j|data lake/.test(text)) {
    return "data";
  }
  return "application";
}

function setViewMode(mode) {
  viewMode = mode === "architect" ? "architect" : "executive";
  document.querySelectorAll("[data-view-mode]").forEach((button) => {
    button.classList.toggle("active", button.dataset.viewMode === viewMode);
  });
  document.body.classList.toggle("view-architect", viewMode === "architect");
  document.body.classList.toggle("view-executive", viewMode !== "architect");
}

function setProviderTheme(payload) {
  const source = normalizeProviderKey(payload?.source_architecture?.provider || sourceProvider.value);
  const target = normalizeProviderKey(payload?.target_architecture?.provider || targetProvider.value);
  if (appShell) {
    appShell.dataset.sourceProvider = source;
    appShell.dataset.targetProvider = target;
  }
}

function normalizeProviderKey(value) {
  const text = String(value || "").toLowerCase();
  if (text.includes("azure")) {
    return "azure";
  }
  if (text.includes("google") || text.includes("gcp")) {
    return "gcp";
  }
  if (text.includes("aws") || text.includes("amazon")) {
    return "aws";
  }
  return "neutral";
}

function startAssessmentTimeline() {
  timelineIndex = 0;
  renderAssessmentTimeline();
  clearInterval(timelineTimer);
  timelineTimer = setInterval(() => {
    timelineIndex = Math.min(timelineIndex + 1, TIMELINE_STEPS.length - 1);
    renderAssessmentTimeline();
  }, 1600);
}

function stopAssessmentTimeline() {
  clearInterval(timelineTimer);
  timelineTimer = null;
  timelineIndex = TIMELINE_STEPS.length - 1;
  renderAssessmentTimeline();
}

function renderAssessmentTimeline() {
  if (!assessmentTimeline) {
    return;
  }
  assessmentTimeline.innerHTML = TIMELINE_STEPS.map(
    ([key, label], index) => `
      <div class="timeline-step ${index < timelineIndex ? "done" : ""} ${index === timelineIndex ? "current" : ""}" data-stage="${escapeAttribute(key)}">
        <span>${index + 1}</span>
        <strong>${escapeHtml(label)}</strong>
      </div>
    `,
  ).join("");
}

function chartColor(status) {
  if (status === "good" || status === "recommended") {
    return "var(--green)";
  }
  if (status === "risk" || status === "not_recommended") {
    return "var(--red)";
  }
  return "var(--amber)";
}

function renderListCard(title, items) {
  const content = (items || []).length
    ? `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`
    : '<p class="muted">No items returned.</p>';
  return `
    <section class="info-card">
      <h3>${escapeHtml(title)}</h3>
      ${content}
    </section>
  `;
}

function renderRailList(title, items) {
  if (!items?.length) {
    return "";
  }
  return `
    <div class="rail-list">
      <strong>${escapeHtml(title)}</strong>
      <ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
    </div>
  `;
}

function renderPhaseTable(phases) {
  if (!phases?.length) {
    return '<div class="empty-state">No migration strategy phases returned.</div>';
  }
  const rows = phases
    .map(
      (phase) => `
        <tr>
          <td><strong>${escapeHtml(phase.phase)}</strong></td>
          <td>${escapeHtml((phase.goals || []).join("; "))}</td>
          <td>${escapeHtml((phase.deliverables || []).join("; "))}</td>
          <td>${escapeHtml((phase.success_criteria || []).join("; "))}</td>
        </tr>
      `,
    )
    .join("");
  return `
    <div class="table-scroll">
      <table class="mapping-table">
        <thead>
          <tr>
            <th>Phase</th>
            <th>Goals</th>
            <th>Deliverables</th>
            <th>Success Criteria</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

async function renderMermaidDiagram(source) {
  const wrap = document.querySelector("#mermaidRenderWrap");
  if (!wrap) {
    return;
  }
  const sequence = ++mermaidRenderSequence;
  await renderMermaidIntoWrap(
    wrap,
    source,
    `assessment-mermaid-${Date.now()}-${sequence}`,
    () => sequence === mermaidRenderSequence,
  );
}

function renderReportMermaidBlocks(root) {
  root.querySelectorAll("[data-report-mermaid-render]").forEach((wrap, index) => {
    const block = wrap.closest(".report-mermaid-block");
    const source = block?.querySelector("[data-report-mermaid-source]")?.textContent || "";
    renderMermaidIntoWrap(wrap, source, `report-mermaid-${Date.now()}-${index}`);
  });
}

async function renderMermaidIntoWrap(wrap, source, renderId, isCurrent = () => true) {
  const mermaidSource = normalizeMermaidSource(source);
  if (!mermaidSource.trim()) {
    wrap.innerHTML = '<div class="empty-state">No Mermaid diagram returned.</div>';
    return;
  }

  try {
    const mermaid = await loadMermaidRenderer();
    if (!isCurrent()) {
      return;
    }
    initializeMermaidRenderer(mermaid);
    const { svg } = await mermaid.render(renderId, mermaidSource);
    if (!isCurrent() || !document.contains(wrap)) {
      return;
    }
    wrap.innerHTML = `<div class="mermaid-svg-frame">${svg}</div>`;
  } catch (error) {
    if (!document.contains(wrap)) {
      return;
    }
    renderMermaidLinkFallback(
      wrap,
      mermaidSource,
      error.message || "Inline Mermaid rendering is unavailable.",
    );
  }
}

async function renderMermaidPngBase64(source) {
  const mermaidSource = normalizeMermaidSource(source);
  if (!mermaidSource.trim()) {
    return null;
  }
  try {
    const mermaid = await promiseWithTimeout(
      loadMermaidRenderer(),
      6000,
      "Mermaid renderer did not load quickly enough for PDF export.",
    );
    initializeMermaidRenderer(mermaid);
    const renderId = `pdf-mermaid-${Date.now()}-${Math.round(Math.random() * 100000)}`;
    const { svg } = await promiseWithTimeout(
      mermaid.render(renderId, mermaidSource),
      8000,
      "Mermaid diagram rendering timed out.",
    );
    const dataUrl = await svgToPngDataUrl(svg);
    return dataUrl.split(",", 2)[1] || null;
  } catch (error) {
    console.warn("Mermaid PNG export skipped:", error);
    return null;
  }
}

function promiseWithTimeout(promise, timeoutMs, message) {
  return new Promise((resolve, reject) => {
    const timeoutId = window.setTimeout(() => {
      reject(new Error(message));
    }, timeoutMs);
    Promise.resolve(promise)
      .then((value) => {
        window.clearTimeout(timeoutId);
        resolve(value);
      })
      .catch((error) => {
        window.clearTimeout(timeoutId);
        reject(error);
      });
  });
}

function initializeMermaidRenderer(mermaid) {
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: "strict",
    theme: "base",
    themeVariables: {
      fontFamily: "Inter, Segoe UI, sans-serif",
      primaryColor: "#eef7ff",
      primaryBorderColor: "#97b7d5",
      primaryTextColor: "#18212f",
      lineColor: "#50677f",
    },
  });
}

function svgToPngDataUrl(svgSource) {
  return new Promise((resolve, reject) => {
    const { width, height } = measureSvg(svgSource);
    const svgBlob = new Blob([svgSource], { type: "image/svg+xml;charset=utf-8" });
    const svgUrl = URL.createObjectURL(svgBlob);
    const image = new Image();
    let settled = false;
    const cleanup = () => {
      URL.revokeObjectURL(svgUrl);
      window.clearTimeout(timeoutId);
    };
    const finish = (callback) => {
      if (settled) {
        return;
      }
      settled = true;
      cleanup();
      callback();
    };
    const timeoutId = window.setTimeout(() => {
      finish(() => reject(new Error("Mermaid image conversion timed out.")));
    }, 8000);
    image.onload = () => {
      const canvas = document.createElement("canvas");
      const drawWidth = image.naturalWidth || width;
      const drawHeight = image.naturalHeight || height;
      const maxDimension = 1800;
      const scale = Math.min(2, maxDimension / Math.max(drawWidth, drawHeight), 1.5);
      canvas.width = Math.max(1, Math.round(drawWidth * scale));
      canvas.height = Math.max(1, Math.round(drawHeight * scale));
      const context = canvas.getContext("2d");
      context.fillStyle = "#ffffff";
      context.fillRect(0, 0, canvas.width, canvas.height);
      context.drawImage(image, 0, 0, canvas.width, canvas.height);
      finish(() => resolve(canvas.toDataURL("image/png")));
    };
    image.onerror = () => {
      finish(() => reject(new Error("Mermaid diagram could not be rendered for PDF export.")));
    };
    image.src = svgUrl;
  });
}

function measureSvg(svgSource) {
  try {
    const doc = new DOMParser().parseFromString(svgSource, "image/svg+xml");
    const svg = doc.querySelector("svg");
    const viewBox = svg?.getAttribute("viewBox")?.split(/\s+/).map(Number) || [];
    const width = parseSvgLength(svg?.getAttribute("width")) || viewBox[2] || 1200;
    const height = parseSvgLength(svg?.getAttribute("height")) || viewBox[3] || 720;
    return { width, height };
  } catch {
    return { width: 1200, height: 720 };
  }
}

function parseSvgLength(value) {
  if (!value) {
    return 0;
  }
  const parsed = Number.parseFloat(String(value).replace("px", ""));
  return Number.isFinite(parsed) ? parsed : 0;
}

async function loadMermaidRenderer() {
  if (window.mermaid) {
    return window.mermaid;
  }
  if (!mermaidModulePromise) {
    mermaidModulePromise = import("https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs")
      .then((module) => module.default || module);
  }
  return mermaidModulePromise;
}

function renderMermaidLinkFallback(wrap, mermaidSource, message) {
  const svgUrl = buildMermaidInkUrl(mermaidSource, "svg");
  const pngUrl = buildMermaidInkUrl(mermaidSource, "img");
  const image = new Image();
  image.className = "mermaid-preview-image";
  image.alt = "Rendered Mermaid architecture diagram";
  image.onload = () => {
    const link = document.createElement("a");
    link.href = svgUrl;
    link.target = "_blank";
    link.rel = "noopener";
    link.appendChild(image);
    wrap.innerHTML = "";
    wrap.appendChild(link);
  };
  image.onerror = () => {
    wrap.innerHTML = `
      <div class="mermaid-fallback">
        <strong>Mermaid preview could not render inline.</strong>
        <span>${escapeHtml(message)}</span>
        <div class="diagram-actions">
          <a class="diagram-link" href="${escapeHtml(svgUrl)}" target="_blank" rel="noopener">Open SVG</a>
          <a class="diagram-link" href="${escapeHtml(pngUrl)}" target="_blank" rel="noopener">Open PNG</a>
        </div>
      </div>
    `;
  };
  image.src = svgUrl;
}

async function renderDiagramImage(payload) {
  const imageTargets = [
    document.querySelector("#diagramImageWrap"),
    ...document.querySelectorAll("[data-report-diagram-image]"),
  ].filter(Boolean);
  if (!imageTargets.length || !payload?.target_architecture) {
    return;
  }

  if (latestDiagramUrl) {
    URL.revokeObjectURL(latestDiagramUrl);
    latestDiagramUrl = null;
  }

  imageTargets.forEach((target) => {
    target.classList.remove("has-rendered-diagram", "can-pan", "is-panning");
    target.innerHTML = '<div class="diagram-render-state">Rendering generated architecture diagram</div>';
  });

  try {
    const response = await apiFetch(`${API_BASE}/api/diagram/png`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        filename: `${payload.target_architecture.provider || "target"}-architecture.png`,
        target_architecture: payload.target_architecture,
      }),
    });
    if (!response.ok) {
      throw new Error("Rendered AWS diagram preview is unavailable.");
    }
    const blob = await response.blob();
    latestDiagramUrl = URL.createObjectURL(blob);
    imageTargets.forEach((target) => {
      target.innerHTML = `
      <img class="rendered-diagram" src="${latestDiagramUrl}" alt="Rendered target architecture diagram" draggable="false" />
    `;
      if (target.id === "diagramImageWrap") {
        target.classList.add("has-rendered-diagram");
        const image = target.querySelector(".rendered-diagram");
        const refreshPan = () => {
          restoreDiagramScrollPosition(target, 0.5, 0);
          updateDiagramPanAffordance(target);
        };
        image?.addEventListener("load", refreshPan, { once: true });
        requestAnimationFrame(refreshPan);
      }
    });
  } catch (error) {
    imageTargets.forEach((target) => {
      target.classList.remove("has-rendered-diagram", "can-pan", "is-panning");
      target.innerHTML = `
      <div class="diagram-render-state diagram-render-error">
        ${escapeHtml(error.message || "Rendered AWS diagram preview is unavailable.")}
      </div>
    `;
    });
  }
}

function injectGeneratedDiagramIntoReport(root, payload) {
  if (!root || !payload?.target_architecture) {
    return;
  }

  const provider = formatProvider(payload.target_architecture.provider || "target");
  const block = document.createElement("section");
  block.className = "report-generated-diagram-block";
  block.innerHTML = `
    <div class="report-mermaid-header">
      <div>
        <strong>Generated ${escapeHtml(provider)} Architecture Diagram</strong>
        <span>Rendered by the provider-neutral diagram engine and embedded in the PDF export.</span>
      </div>
      <div class="diagram-actions">
        <button type="button" class="diagram-link" id="reportDiagramDownloadButton">Download PNG</button>
      </div>
    </div>
    <div class="report-generated-diagram-image" data-report-diagram-image>
      <div class="diagram-render-state">Rendering generated architecture diagram</div>
    </div>
  `;

  const mermaidBlock = root.querySelector(".report-mermaid-block");
  if (mermaidBlock) {
    mermaidBlock.insertAdjacentElement("afterend", block);
  } else {
    root.appendChild(block);
  }

  const reportDownloadButton = block.querySelector("#reportDiagramDownloadButton");
  reportDownloadButton?.addEventListener("click", () => downloadDiagramButton.click());
}

function injectReportProviderBrand(root, payload) {
  if (!root || !payload) {
    return;
  }
  const source = payload.source_architecture?.provider || sourceProvider.value;
  const target = payload.target_architecture?.provider || targetProvider.value;
  const block = document.createElement("section");
  block.className = "report-provider-brand";
  block.innerHTML = `
    <div class="report-brand-lockup">
      <img class="brand-mark" src="assets/cloudbridge-iq-mark.svg" alt="" />
      <div>
        <p class="eyebrow">CloudBridge IQ Report</p>
        <strong>Migration decision brief</strong>
      </div>
    </div>
    <div>
      <p class="eyebrow">Provider Route</p>
      ${providerRouteMarkup(source, target)}
    </div>
    <div class="provider-report-meta">
      <span>Source: ${escapeHtml(formatProvider(source))}</span>
      <span>Target: ${escapeHtml(formatProvider(target))}</span>
    </div>
  `;

  const title = root.querySelector("h1");
  if (title) {
    title.insertAdjacentElement("afterend", block);
  } else {
    root.prepend(block);
  }
}

function renderSupportedProviders() {
  document.querySelectorAll("[data-supported-providers]").forEach((container) => {
    container.innerHTML = ["aws", "azure", "gcp"]
      .map((provider) => providerLogoLockup(provider, { compact: true }))
      .join("");
  });
}

function syncProviderRouteBadges(payload = latestResult) {
  const source = payload?.source_architecture?.provider || sourceProvider.value;
  const target = payload?.target_architecture?.provider || targetProvider.value;
  if (providerRouteBadges) {
    providerRouteBadges.innerHTML = providerRouteMarkup(source, target);
  }
  syncAppFrame(payload);
}

function syncAppFrame(payload = latestResult) {
  const source = formatProvider(payload?.source_architecture?.provider || sourceProvider.value || "auto");
  const target = formatProvider(payload?.target_architecture?.provider || targetProvider.value || "aws");
  const title = projectNameInput?.value?.trim() || (payload ? buildHistoryTitle(payload) : "Untitled assessment");
  const reviewLabel = workflowLabel(reviewState.status);
  if (currentAssessmentName) {
    currentAssessmentName.textContent = title;
  }
  if (currentRouteSummary) {
    currentRouteSummary.textContent = `${source} to ${target}`;
  }
  if (currentReviewStatus) {
    currentReviewStatus.textContent = reviewLabel;
  }
  if (sidebarWorkspaceStatus) {
    sidebarWorkspaceStatus.textContent = reviewLabel;
  }
}

function providerRouteMarkup(sourceProviderName, targetProviderName, options = {}) {
  const compactClass = options.compact ? " compact" : "";
  return `
    <div class="provider-route-lockup${compactClass}">
      ${providerLogoLockup(sourceProviderName, { compact: options.compact })}
      <span class="provider-route-arrow" aria-hidden="true">→</span>
      ${providerLogoLockup(targetProviderName, { compact: options.compact })}
    </div>
  `;
}

function providerLogoLockup(provider, options = {}) {
  const key = normalizeProviderKey(provider);
  const compactClass = options.compact ? " compact" : "";
  const label = options.label || providerShortLabel(provider);
  return `
    <span class="provider-logo-lockup ${escapeAttribute(key)}${compactClass}" title="${escapeAttribute(formatProvider(provider))}">
      ${providerLogoSvg(key)}
      <span>${escapeHtml(label)}</span>
    </span>
  `;
}

function providerShortLabel(provider) {
  const key = normalizeProviderKey(provider);
  if (key === "azure") {
    return "Azure";
  }
  if (key === "gcp") {
    return "GCP";
  }
  if (key === "aws") {
    return "AWS";
  }
  if (String(provider || "").toLowerCase() === "auto") {
    return "Auto";
  }
  return formatProvider(provider);
}

function providerLogoSvg(providerKey) {
  if (providerKey === "aws") {
    return `
      <svg class="provider-logo-svg" viewBox="0 0 48 32" aria-hidden="true" focusable="false">
        <rect x="3" y="5" width="42" height="22" rx="5" fill="#101828"></rect>
        <path d="M15 17c6 4 15 4 22-1" fill="none" stroke="#ff9900" stroke-width="2.4" stroke-linecap="round"></path>
        <path d="M35 15l4 .2-2.1 3.2" fill="none" stroke="#ff9900" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path>
        <path d="M16 12h5M25 12h7M18 21h13" stroke="#ffffff" stroke-width="1.8" stroke-linecap="round"></path>
      </svg>
    `;
  }
  if (providerKey === "azure") {
    return `
      <svg class="provider-logo-svg" viewBox="0 0 48 32" aria-hidden="true" focusable="false">
        <rect x="3" y="5" width="42" height="22" rx="5" fill="#eef7ff"></rect>
        <path d="M20 8h8l-8.3 17h-7.2L20 8Z" fill="#0078d4"></path>
        <path d="M28.7 8 38 25h-9.4l-5.1-6.2L28.7 8Z" fill="#50a7f2"></path>
        <path d="M19.5 25h18.4l-9.2-5.8-4.9 1.9-4.3 3.9Z" fill="#005ba1"></path>
      </svg>
    `;
  }
  if (providerKey === "gcp") {
    return `
      <svg class="provider-logo-svg" viewBox="0 0 48 32" aria-hidden="true" focusable="false">
        <rect x="3" y="5" width="42" height="22" rx="5" fill="#ffffff"></rect>
        <path d="M18.3 23.5h15.2a6 6 0 0 0 1.1-11.9 9.5 9.5 0 0 0-17.7-2.5 7.1 7.1 0 0 0 1.4 14.4Z" fill="none" stroke="#1a73e8" stroke-width="3" stroke-linecap="round"></path>
        <path d="M17.1 9.1a9.5 9.5 0 0 1 12.3-3.4" fill="none" stroke="#ea4335" stroke-width="3" stroke-linecap="round"></path>
        <path d="M34.6 11.6a6 6 0 0 1 2.8 10.3" fill="none" stroke="#fbbc04" stroke-width="3" stroke-linecap="round"></path>
        <path d="M18.3 23.5a7.1 7.1 0 0 1-4.9-12.2" fill="none" stroke="#34a853" stroke-width="3" stroke-linecap="round"></path>
      </svg>
    `;
  }
  return `
    <svg class="provider-logo-svg" viewBox="0 0 48 32" aria-hidden="true" focusable="false">
      <rect x="3" y="5" width="42" height="22" rx="5" fill="#f2f5f8"></rect>
      <circle cx="18" cy="16" r="6" fill="#94a3b8"></circle>
      <path d="M27 12h8M27 16h8M27 20h8" stroke="#64748b" stroke-width="2" stroke-linecap="round"></path>
    </svg>
  `;
}

function renderMarkdown(markdown) {
  if (!markdown.trim()) {
    return '<div class="empty-state">No report returned.</div>';
  }

  const lines = markdown.split(/\r?\n/);
  const html = [];
  let inList = false;
  let inCode = false;
  let codeLanguage = "";
  let codeLines = [];
  let tableRows = [];

  const closeList = () => {
    if (inList) {
      html.push("</ul>");
      inList = false;
    }
  };

  const closeTable = () => {
    if (!tableRows.length) {
      return;
    }
    html.push("<table>");
    tableRows.forEach((row, index) => {
      if (/^\|\s*-+/.test(row)) {
        return;
      }
      const cells = row
        .split("|")
        .slice(1, -1)
        .map((cell) => inlineMarkdown(cell.trim()));
      const tag = index === 0 ? "th" : "td";
      html.push(`<tr>${cells.map((cell) => `<${tag}>${cell}</${tag}>`).join("")}</tr>`);
    });
    html.push("</table>");
    tableRows = [];
  };

  for (const line of lines) {
    if (line.startsWith("```")) {
      closeList();
      closeTable();
      if (!inCode) {
        inCode = true;
        codeLanguage = line.slice(3).trim().toLowerCase();
        codeLines = [];
      } else {
        inCode = false;
        html.push(renderCodeBlock(codeLines.join("\n"), codeLanguage));
        codeLanguage = "";
        codeLines = [];
      }
      continue;
    }

    if (inCode) {
      codeLines.push(line);
      continue;
    }

    if (line.startsWith("|")) {
      closeList();
      tableRows.push(line);
      continue;
    }
    closeTable();

    if (!line.trim()) {
      closeList();
      continue;
    }

    if (line.startsWith("### ")) {
      closeList();
      html.push(`<h3>${inlineMarkdown(line.slice(4))}</h3>`);
    } else if (line.startsWith("## ")) {
      closeList();
      html.push(`<h2>${inlineMarkdown(line.slice(3))}</h2>`);
    } else if (line.startsWith("# ")) {
      closeList();
      html.push(`<h1>${inlineMarkdown(line.slice(2))}</h1>`);
    } else if (line.startsWith("- ")) {
      if (!inList) {
        html.push("<ul>");
        inList = true;
      }
      html.push(`<li>${inlineMarkdown(line.slice(2))}</li>`);
    } else {
      closeList();
      html.push(`<p>${inlineMarkdown(line)}</p>`);
    }
  }

  closeList();
  closeTable();
  if (inCode) {
    html.push(renderCodeBlock(codeLines.join("\n"), codeLanguage));
  }
  return html.join("\n");
}

function renderReportMemo(payload) {
  const verdict = payload.final_verdict || {};
  const readiness = payload.assessment_insights?.scores?.overall_readiness?.value ?? 0;
  const estimate = estimateCostRange(payload);
  const highRiskCount = (payload.risks || []).filter((risk) =>
    ["high", "critical"].includes(String(risk.severity || "").toLowerCase()),
  ).length;
  const target = payload.target_architecture?.provider || targetProvider.value;
  return `
    <section class="report-memo-cover">
      <div>
        <p class="eyebrow">Enterprise Decision Memo</p>
        <h3>${providerLogoLockup(target, { label: `${formatProvider(target)} Migration Assessment` })}</h3>
        <p>${escapeHtml(payload.executive_summary || payload.source_architecture?.summary || "Assessment summary will appear after analysis.")}</p>
      </div>
      <div class="report-verdict-panel ${escapeHtml(verdict.recommendation || "watch")}">
        <span>Final Verdict</span>
        <strong>${formatVerdict(verdict.recommendation || "not run")}</strong>
        <small>${Math.round((verdict.confidence || 0) * 100)}% confidence</small>
      </div>
    </section>

    <section class="report-memo-kpis">
      <div>
        <span>Readiness</span>
        <strong>${readiness}%</strong>
      </div>
      <div>
        <span>Target Run-rate</span>
        <strong>${formatCurrencyRange(estimate.monthlyLow, estimate.monthlyHigh)}</strong>
      </div>
      <div>
        <span>High Risks</span>
        <strong>${highRiskCount}</strong>
      </div>
      <div>
        <span>Review Status</span>
        <strong>${escapeHtml(workflowLabel(reviewState.status))}</strong>
      </div>
    </section>

    <section class="report-decision-grid">
      ${renderReportDecisionCard("Decision Gate", buildQualityGateItems(payload).slice(0, 4).map((gate) => `${gate.label}: ${gate.value}`))}
      ${renderReportDecisionCard("Mapping Review", (payload.service_mappings || []).slice(0, 5).map((mapping) => `${mapping.source_service} -> ${mapping.target_service}`))}
      ${renderReportDecisionCard("Top Risks", (payload.risks || []).slice(0, 5).map((risk) => `${risk.severity}: ${risk.title}`))}
      ${renderReportDecisionCard("Next Actions", payload.assessment_insights?.review?.suggested_next_actions || [])}
    </section>

    <section class="report-document">
      ${renderMarkdown(payload.markdown_report || "")}
    </section>
  `;
}

function renderReportDecisionCard(title, items) {
  const safeItems = (items || []).filter(Boolean).slice(0, 5);
  return `
    <section class="report-decision-card">
      <p class="eyebrow">${escapeHtml(title)}</p>
      ${
        safeItems.length
          ? `<ul>${safeItems.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`
          : '<p class="muted">No items returned.</p>'
      }
    </section>
  `;
}

function renderCodeBlock(source, language) {
  if (language === "mermaid") {
    return renderReportMermaidBlock(source);
  }
  return `<pre><code>${escapeHtml(source)}</code></pre>`;
}

function renderReportMermaidBlock(source) {
  const mermaid = normalizeMermaidSource(source);
  const svgUrl = buildMermaidInkUrl(mermaid, "svg");
  const pngUrl = buildMermaidInkUrl(mermaid, "img");
  return `
    <div class="report-mermaid-block">
      <div class="report-mermaid-header">
        <div>
          <strong>Rendered Mermaid Diagram</strong>
          <span>Open it directly or expand the source if you need to edit it.</span>
        </div>
        <div class="diagram-actions">
          <a class="diagram-link" href="${escapeHtml(svgUrl)}" target="_blank" rel="noopener">Open SVG</a>
          <a class="diagram-link" href="${escapeHtml(pngUrl)}" target="_blank" rel="noopener">Open PNG</a>
          <button type="button" class="diagram-link" data-copy-mermaid>Copy Source</button>
        </div>
      </div>
      <div class="report-mermaid-render" data-report-mermaid-render>
        <div class="diagram-render-state">Rendering Mermaid diagram</div>
      </div>
      <details class="source-toggle">
        <summary>View Mermaid source</summary>
        <pre class="diagram-code" data-report-mermaid-source>${escapeHtml(mermaid)}</pre>
      </details>
    </div>
  `;
}

function addSourceComponent() {
  if (!latestResult?.source_architecture) {
    return;
  }
  const components = latestResult.source_architecture.components || [];
  const nextNumber = components.length + 1;
  components.push({
    id: `user_component_${Date.now()}`,
    name: `New component ${nextNumber}`,
    provider: latestResult.source_architecture.provider || sourceProvider.value,
    service_type: "",
    category: "application",
    confidence: 0.6,
    description: "",
  });
  latestResult.source_architecture.components = components;
  sourcePanel.innerHTML = renderSourceArchitecture(latestResult);
  renderSummary(latestResult);
}

function deleteSourceComponent(index) {
  const components = latestResult?.source_architecture?.components;
  if (!components || !Number.isInteger(index)) {
    return;
  }
  components.splice(index, 1);
  sourcePanel.innerHTML = renderSourceArchitecture(latestResult);
  renderSummary(latestResult);
}

function updateSourceComponent(input) {
  const components = latestResult?.source_architecture?.components;
  const index = Number(input.dataset.index);
  const field = input.dataset.componentField;
  if (!components || !components[index] || !field) {
    return;
  }
  components[index][field] = field === "confidence" ? clamp(Number(input.value), 0, 1) : input.value;
}

function addSourceRelationship() {
  if (!latestResult?.source_architecture) {
    return;
  }
  const components = latestResult.source_architecture.components || [];
  const relationships = latestResult.source_architecture.relationships || [];
  const source = components[0]?.id || "";
  const target = components[1]?.id || source;
  relationships.push({
    source_id: source,
    target_id: target,
    relationship_type: "routes to",
    description: "",
  });
  latestResult.source_architecture.relationships = relationships;
  sourcePanel.innerHTML = renderSourceArchitecture(latestResult);
}

function deleteSourceRelationship(index) {
  const relationships = latestResult?.source_architecture?.relationships;
  if (!relationships || !Number.isInteger(index)) {
    return;
  }
  relationships.splice(index, 1);
  sourcePanel.innerHTML = renderSourceArchitecture(latestResult);
}

function updateSourceRelationship(input) {
  const relationships = latestResult?.source_architecture?.relationships;
  const index = Number(input.dataset.index);
  const field = input.dataset.relationshipField;
  if (!relationships || !relationships[index] || !field) {
    return;
  }
  relationships[index][field] = input.value;
}

function updateSectionComment(input) {
  const section = input.dataset.sectionComment;
  if (!section) {
    return;
  }
  reviewState.sectionComments = reviewState.sectionComments || {};
  reviewState.sectionComments[section] = input.value;
  updateSelectedHistoryReviewState();
}

async function rebuildFromEditedSource() {
  if (!latestResult?.source_architecture) {
    return;
  }
  if (!hasPermission("can_assess")) {
    showError("Your current role cannot rebuild assessments.");
    return;
  }
  hideError();
  setLoading(true);
  startAssessmentTimeline();
  resultTitle.textContent = "Rebuilding";
  try {
    const response = await apiFetch(`${API_BASE}/api/assessment/rebuild`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        source_architecture: latestResult.source_architecture,
        source_provider: sourceProvider.value,
        target_provider: targetProvider.value,
        migration_intent: migrationIntent.value,
        goals: goalsWithVariant(),
        architecture_variant: architectureVariant.value,
      }),
    });
    const payload = await readApiPayload(response);
    if (!response.ok) {
      throw new Error(payload.detail || "Assessment rebuild failed.");
    }
    latestResult = payload;
    renderResult(payload);
    resultTitle.textContent = "Assessment Rebuilt";
    activateTab("source");
  } catch (error) {
    showError(error.message || "Assessment rebuild failed.");
    resultTitle.textContent = "Needs Attention";
  } finally {
    stopAssessmentTimeline();
    setLoading(false);
  }
}

function saveCurrentAssessment() {
  const history = loadHistory();
  const title = projectNameInput.value.trim() || buildHistoryTitle(latestResult);
  const existingVersions = history.filter((item) => (item.projectName || item.title) === title).length;
  const record = {
    id: selectedHistoryId || `assessment_${Date.now()}`,
    created_at: new Date().toISOString(),
    last_modified_at: new Date().toISOString(),
    title,
    projectName: title,
    reviewer: reviewerNameInput.value.trim(),
    version: selectedHistoryId
      ? history.find((item) => item.id === selectedHistoryId)?.version || existingVersions || 1
      : existingVersions + 1,
    reviewed: reviewState.reviewed,
    notes: architectNotes.value,
    comments: reviewComments.value,
    sectionComments: reviewState.sectionComments || {},
    status: reviewState.status,
    variant: architectureVariant.value,
    pattern: architecturePattern.value,
    source_provider: sourceProvider.value,
    target_provider: targetProvider.value,
    goals: goalsInput.value,
    result: latestResult,
  };
  const withoutExisting = history.filter((item) => item.id !== record.id);
  withoutExisting.unshift(record);
  persistHistory(withoutExisting.slice(0, 12));
  selectedHistoryId = record.id;
  renderHistory();
  syncAppFrame();
  showToast("Assessment saved to local history.", "success");
}

function openHistoryItem(id) {
  const record = loadHistory().find((item) => item.id === id);
  if (!record) {
    return;
  }
  selectedHistoryId = record.id;
  latestResult = record.result;
  reviewState = {
    reviewed: Boolean(record.reviewed),
    status: record.status || (record.reviewed ? "reviewed" : "needs_review"),
    notes: record.notes || "",
    comments: record.comments || "",
    projectName: record.projectName || record.title || "",
    reviewer: record.reviewer || "",
    sectionComments: record.sectionComments || {},
  };
  syncReviewMetadataInputs();
  workflowStatus.value = reviewState.status;
  if (record.variant) {
    architectureVariant.value = record.variant;
  }
  if (record.pattern) {
    architecturePattern.value = record.pattern;
  }
  if (record.source_provider) {
    sourceProvider.value = record.source_provider;
  }
  if (record.target_provider) {
    targetProvider.value = record.target_provider;
  }
  if (record.goals) {
    goalsInput.value = record.goals;
    syncPresetStates();
  }
  renderResult(latestResult);
  enableActions(true);
  resultTitle.textContent = "Saved Assessment";
  activateTab("overview");
  renderHistory();
}

function compareHistoryItem(id) {
  const record = loadHistory().find((item) => item.id === id);
  if (!record || !latestResult) {
    return;
  }
  const currentReadiness = latestResult.assessment_insights?.scores?.overall_readiness?.value ?? 0;
  const savedReadiness = record.result?.assessment_insights?.scores?.overall_readiness?.value ?? 0;
  const currentMappings = latestResult.service_mappings?.length || 0;
  const savedMappings = record.result?.service_mappings?.length || 0;
  const currentVerdict = latestResult.final_verdict?.recommendation || "unknown";
  const savedVerdict = record.result?.final_verdict?.recommendation || "unknown";
  reviewNotes.innerHTML = `
    <div class="rail-list">
      <strong>Version Compare</strong>
      <ul>
        <li>Verdict: ${escapeHtml(formatVerdict(savedVerdict))} to ${escapeHtml(formatVerdict(currentVerdict))}</li>
        <li>Readiness: ${savedReadiness}/100 to ${currentReadiness}/100</li>
        <li>Mappings: ${savedMappings} to ${currentMappings}</li>
        <li>Saved run: ${escapeHtml(formatDate(record.created_at))}</li>
      </ul>
    </div>
  `;
}

function deleteHistoryItem(id) {
  const nextHistory = loadHistory().filter((item) => item.id !== id);
  persistHistory(nextHistory);
  if (selectedHistoryId === id) {
    selectedHistoryId = null;
  }
  renderHistory();
}

function updateSelectedHistoryReviewState() {
  if (!selectedHistoryId) {
    return;
  }
  const history = loadHistory();
  const nextHistory = history.map((item) => {
    if (item.id !== selectedHistoryId) {
      return item;
    }
    return {
      ...item,
      reviewed: reviewState.reviewed,
      status: reviewState.status,
      notes: architectNotes.value,
      comments: reviewComments.value,
      projectName: projectNameInput.value,
      reviewer: reviewerNameInput.value,
      sectionComments: reviewState.sectionComments || {},
      last_modified_at: new Date().toISOString(),
    };
  });
  persistHistory(nextHistory);
  renderHistory();
}

function renderHistory() {
  const history = loadHistory();
  if (!history.length) {
    historyList.innerHTML = '<div class="empty-state">No saved assessments yet.</div>';
    return;
  }
  historyList.innerHTML = history
    .map(
      (item) => `
        <article class="history-item ${item.id === selectedHistoryId ? "active" : ""}">
          <div>
            <strong>${escapeHtml(item.title || "Migration assessment")}</strong>
            <span>v${escapeHtml(item.version || 1)} | ${escapeHtml(workflowLabel(item.status || "ai_draft"))}</span>
            <span>${escapeHtml(item.reviewer || "Unassigned reviewer")} | modified ${escapeHtml(formatDate(item.last_modified_at || item.created_at))}</span>
          </div>
          <div class="history-actions">
            <button type="button" data-history-action="open" data-history-id="${escapeAttribute(item.id)}">Open</button>
            <button type="button" data-history-action="compare" data-history-id="${escapeAttribute(item.id)}">Compare</button>
            <button type="button" data-history-action="delete" data-history-id="${escapeAttribute(item.id)}">Delete</button>
          </div>
        </article>
      `,
    )
    .join("");
}

function syncReviewMetadataInputs() {
  architectNotes.value = reviewState.notes || "";
  reviewComments.value = reviewState.comments || "";
  projectNameInput.value = reviewState.projectName || "";
  reviewerNameInput.value = reviewState.reviewer || "";
}

function loadHistory() {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    const history = raw ? JSON.parse(raw) : [];
    return Array.isArray(history) ? history : [];
  } catch {
    return [];
  }
}

function persistHistory(history) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}

function buildHistoryTitle(payload) {
  const provider = formatProvider(payload?.source_architecture?.provider || "source");
  const target = (payload?.target_architecture?.provider || "aws").toUpperCase();
  const verdict = formatVerdict(payload?.final_verdict?.recommendation || "assessment");
  return `${provider} to ${target} - ${verdict}`;
}

function buildExportMarkdown() {
  if (!latestResult?.markdown_report) {
    return "";
  }
  const additions = [];
  additions.push("## Review Workflow");
  additions.push("");
  if (projectNameInput.value.trim()) {
    additions.push(`- **Project:** ${projectNameInput.value.trim()}`);
  }
  if (reviewerNameInput.value.trim()) {
    additions.push(`- **Reviewer:** ${reviewerNameInput.value.trim()}`);
  }
  additions.push(`- **Review status:** ${workflowLabel(reviewState.status)}`);
  additions.push(`- **Architecture variant:** ${formatTitle(architectureVariant.value)}`);
  additions.push(`- **Architecture pattern:** ${selectedArchitecturePattern(latestResult).label}`);
  const estimate = estimateCostRange(latestResult);
  additions.push("");
  additions.push("### Cost Estimate Snapshot");
  additions.push("");
  additions.push(`- **Target monthly run-rate:** ${formatCurrencyRange(estimate.monthlyLow, estimate.monthlyHigh)}`);
  additions.push(`- **Source baseline run-rate:** ${formatCurrencyRange(estimate.sourceMonthlyLow, estimate.sourceMonthlyHigh)}`);
  if (estimate.sourceBaselineAvailable && estimate.savingsHigh > 0) {
    additions.push(`- **Estimated monthly savings:** ${formatSavingsRange(estimate.savingsLow, estimate.savingsHigh)}`);
    additions.push(
      `- **Estimated annualized savings:** ${formatSavingsRange(
        estimate.annualSavingsLow,
        estimate.annualSavingsHigh,
      )}`,
    );
  } else if (!estimate.sourceBaselineAvailable) {
    additions.push("- **Estimated savings:** Needs source baseline inventory before savings can be stated.");
  } else {
    additions.push("- **Estimated savings:** No directional savings signal from the current source and target model.");
  }
  additions.push(`- **Migration project estimate:** ${formatCurrencyRange(estimate.projectLow, estimate.projectHigh)}`);
  additions.push(`- **Dual-run reserve:** ${formatCurrencyRange(estimate.dualRunLow, estimate.dualRunHigh)}`);
  if (architectNotes.value.trim()) {
    additions.push(`- **Architect notes:** ${architectNotes.value.trim()}`);
  }
  if (reviewComments.value.trim()) {
    additions.push(`- **Reviewer comments:** ${reviewComments.value.trim()}`);
  }
  const sectionComments = Object.entries(reviewState.sectionComments || {}).filter(([, value]) => value.trim());
  if (sectionComments.length) {
    additions.push("");
    additions.push("### Section Comments");
    additions.push("");
    sectionComments.forEach(([section, value]) => {
      additions.push(`- **${formatTitle(section)}:** ${value.trim()}`);
    });
  }
  return `${latestResult.markdown_report.trim()}\n\n${additions.join("\n")}\n`;
}

function toggleGoalPreset(goal) {
  const goals = parseGoals(goalsInput.value);
  const normalizedGoal = goal.trim().toLowerCase();
  const exists = goals.some((item) => item.toLowerCase() === normalizedGoal);
  const nextGoals = exists
    ? goals.filter((item) => item.toLowerCase() !== normalizedGoal)
    : [...goals, goal];
  goalsInput.value = nextGoals.join(", ");
}

function syncPresetStates() {
  const goals = parseGoals(goalsInput.value).map((goal) => goal.toLowerCase());
  document.querySelectorAll(".preset-button").forEach((button) => {
    button.classList.toggle("active", goals.includes((button.dataset.goal || "").toLowerCase()));
  });
}

function goalsWithVariant() {
  const goals = parseGoals(goalsInput.value);
  const variant = architectureVariant.value;
  if (variant && variant !== "balanced") {
    goals.push(`architecture variant: ${variant}`);
  }
  const pattern = architecturePattern.value;
  if (pattern && pattern !== "auto") {
    goals.push(`architecture pattern: ${pattern}`);
  }
  return goals;
}

function parseGoals(value) {
  return String(value || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function renderConfidence(value) {
  const percent = Math.round(Number(value || 0) * 100);
  return `
    <div class="confidence">
      <span>${percent}%</span>
      <div class="score-bar small"><span style="width: ${percent}%"></span></div>
    </div>
  `;
}

function renderTags(items) {
  if (!items.length) {
    return '<span class="muted">None</span>';
  }
  return `<div class="tag-list">${items.map((item) => `<span>${escapeHtml(item)}</span>`).join("")}</div>`;
}

function inlineMarkdown(value) {
  return escapeHtml(value).replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
}

function activateTab(tabName) {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.tab === tabName);
  });
  document.querySelectorAll("[data-navigate-tab]").forEach((button) => {
    button.classList.toggle("active", button.dataset.navigateTab === tabName);
  });
  document.querySelectorAll(".tab-panel").forEach((panel) => {
    panel.classList.toggle("active", panel.id === `${tabName}Panel`);
  });
}

function setLoading(isLoading) {
  loadingState.hidden = !isLoading;
  document.body.classList.toggle("is-loading-assessment", isLoading);
  submitButton.disabled = isLoading || !hasPermission("can_assess");
  submitButton.textContent = isLoading ? "Running Assessment" : "Run Assessment";
  applyRoleUi();
}

function showError(message) {
  errorState.textContent = message;
  errorState.hidden = false;
  showToast(message, "error");
}

function hideError() {
  errorState.hidden = true;
  errorState.textContent = "";
}

function enableActions(enabled) {
  copyReportButton.disabled = !enabled || !hasPermission("can_view");
  downloadPdfButton.disabled = !enabled || !hasPermission("can_view");
  downloadReportButton.disabled = !enabled || !hasPermission("can_view");
  downloadDiagramButton.disabled = !enabled || !hasPermission("can_view");
  saveAssessmentButton.disabled = !enabled || !hasPermission("can_review");
  markReviewedButton.disabled = !enabled || !hasPermission("can_architect_review");
}

function pulseButton(button, label) {
  const original = button.textContent;
  button.textContent = label;
  showToast(label, "success");
  setTimeout(() => {
    button.textContent = original;
  }, 1200);
}

function showToast(message, tone = "info") {
  if (!toastRegion || !message) {
    return;
  }
  const toast = document.createElement("div");
  toast.className = `toast ${tone}`;
  toast.textContent = message;
  toastRegion.appendChild(toast);
  window.setTimeout(() => {
    toast.classList.add("leaving");
    window.setTimeout(() => toast.remove(), 220);
  }, 3600);
}

function downloadText(filename, text, type) {
  const blob = new Blob([text], { type });
  downloadBlob(filename, blob);
}

function downloadBlob(filename, blob) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function buildMermaidInkUrl(source, format) {
  return `https://mermaid.ink/${format}/${toBase64Url(normalizeMermaidSource(source))}`;
}

function toBase64Url(value) {
  const bytes = new TextEncoder().encode(value);
  let binary = "";
  const chunkSize = 0x8000;
  for (let index = 0; index < bytes.length; index += chunkSize) {
    binary += String.fromCharCode(...bytes.subarray(index, index + chunkSize));
  }
  return btoa(binary).replaceAll("+", "-").replaceAll("/", "_").replace(/=+$/, "");
}

function normalizeMermaidSource(source) {
  let text = String(source || "").trim();
  if (text.startsWith("```")) {
    text = text.replace(/^```(?:mermaid)?\s*/i, "").replace(/```\s*$/i, "").trim();
  }
  return text;
}

function formatVerdict(verdict) {
  return String(verdict || "unknown")
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function formatTitle(value) {
  return String(value || "")
    .replaceAll("-", " ")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatProvider(value) {
  const text = String(value || "unknown").toLowerCase();
  if (text.includes("azure")) {
    return "Microsoft Azure";
  }
  if (text.includes("gcp") || text.includes("google")) {
    return "Google Cloud";
  }
  if (text.includes("aws") || text.includes("amazon")) {
    return "AWS";
  }
  return formatTitle(value || "unknown");
}

function formatMode(mode) {
  return String(mode)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function compactMessage(message) {
  const text = String(message || "").replace(/\s+/g, " ").trim();
  return text.length > 120 ? `${text.slice(0, 117)}...` : text;
}

function formatDate(value) {
  if (!value) {
    return "Unknown date";
  }
  return new Date(value).toLocaleString([], {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatBytes(bytes) {
  if (!Number.isFinite(bytes)) {
    return "0 B";
  }
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function escapeAttribute(value) {
  return escapeHtml(value).replaceAll("`", "&#096;");
}

function clamp(value, min, max) {
  if (!Number.isFinite(value)) {
    return min;
  }
  return Math.max(min, Math.min(max, value));
}
