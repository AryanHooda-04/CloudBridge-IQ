const form = document.querySelector("#analysisForm");
const appShell = document.querySelector(".app-shell");
const fileInput = document.querySelector("#fileInput");
const fileMeta = document.querySelector("#fileMeta");
const dropZone = document.querySelector("#dropZone");
const previewFrame = document.querySelector("#previewFrame");
const demoSampleGrid = document.querySelector("#demoSampleGrid");
const demoSampleSummary = document.querySelector("#demoSampleSummary");
const intakeFaqSection = document.querySelector("#intakeFaqSection");
const apiStatus = document.querySelector("#apiStatus");
const resultTitle = document.querySelector("#resultTitle");
const reportBreadcrumbs = document.querySelector("#reportBreadcrumbs");
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
const startNewRunButton = document.querySelector("#startNewRunButton");
const collapseIntakeButton = document.querySelector("#collapseIntakeButton");
const qualityGates = document.querySelector("#qualityGates");
const projectNameInput = document.querySelector("#projectName");
const reviewerNameInput = document.querySelector("#reviewerName");
const decisionOwnerInput = document.querySelector("#decisionOwner");
const approvalTargetDateInput = document.querySelector("#approvalTargetDate");
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
const authSubmitIdle = document.querySelector("#authSubmitIdle");
const authSubmitLoading = document.querySelector("#authSubmitLoading");
const authError = document.querySelector("#authError");
const authThemeToggle = document.querySelector("#authThemeToggle");
const authRoleCards = Array.from(document.querySelectorAll("[data-auth-role-card]"));
const userChip = document.querySelector("#userChip");
const userAvatar = document.querySelector("#userAvatar");
const userRoleLabel = document.querySelector("#userRoleLabel");
const userDisplayName = document.querySelector("#userDisplayName");
const logoutButton = document.querySelector("#logoutButton");
const assessmentDashboard = document.querySelector("#assessmentDashboard");
const assessmentCompareDialog = document.querySelector("#assessmentCompareDialog");
const assessmentCompareContent = document.querySelector("#assessmentCompareContent");
const assessmentCompareSubtitle = document.querySelector("#assessmentCompareSubtitle");
const dashboardHelpDialog = document.querySelector("#dashboardHelpDialog");
const dashboardHelpContent = document.querySelector("#dashboardHelpContent");
const wizardBackButton = document.querySelector("#wizardBackButton");
const wizardNextButton = document.querySelector("#wizardNextButton");
const intakeStepPanels = Array.from(document.querySelectorAll("[data-intake-step]"));
const wizardButtons = Array.from(document.querySelectorAll("[data-wizard-target]"));
const API_BASE = window.location.protocol === "file:" ? "http://127.0.0.1:8000" : "";
const HISTORY_KEY = "cloudMigrationAssessments.v2";
const AUTH_THEME_KEY = "cloudbridge.auth.theme";
const INTAKE_DRAFT_KEY = "cloudbridge.intakeDraft.v1";
const LAST_REPORT_KEY = "cloudbridge.lastReport.v1";
const DASHBOARD_FILTER_KEY = "cloudbridge.dashboardFilters.v1";
const ASSESSMENT_TIMEOUT_MS = 120000;
const DASHBOARD_FAQS = [
  {
    question: "What should I use CloudBridge IQ for day to day?",
    answer:
      "Use it as a migration intake and review workspace: capture a diagram, confirm the route and goals, generate an assessment, then review risks, mappings, and reports with architects.",
  },
  {
    question: "Do I need a perfect architecture diagram?",
    answer:
      "No. A clear PNG or PDF with service labels is enough for a first pass. Low-confidence mappings are flagged so an architect can validate assumptions before approval.",
  },
  {
    question: "When should I use Compare?",
    answer:
      "Use Compare when you have more than one assessment and want a portfolio-level delta: readiness movement, verdict changes, blockers, and what changed between two runs.",
  },
  {
    question: "Where do reports and drafts live?",
    answer:
      "Completed assessments appear in Recent Runs. The dashboard keeps last opened report recovery, and the New Run workflow autosaves route, goals, and selected sample context while you work.",
  },
];
const DAILY_HELP_STEPS = [
  {
    title: "Start from the Dashboard",
    detail: "Check current status, recent runs, readiness trends, and any report you opened last.",
  },
  {
    title: "Create or resume a New Run",
    detail: "Pick a bundled sample for demos or upload a real diagram. The route, intent, goals, and pattern are saved while you work.",
  },
  {
    title: "Confirm route and goals",
    detail: "Set source and target cloud, choose the architecture pattern, and state the migration objective in plain business language.",
  },
  {
    title: "Run the assessment",
    detail: "CloudBridge IQ produces mappings, risks, readiness, target design, governance signals, and a review-ready report.",
  },
  {
    title: "Review like an architect",
    detail: "Open the report tabs, inspect low-confidence mappings, ask the migration agent focused questions, and capture reviewer notes.",
  },
  {
    title: "Share and compare",
    detail: "Use Compare for portfolio deltas, export PDF/Markdown/PNG for stakeholders, and return to All reports whenever you need history.",
  },
];
const TAB_GROUPS = {
  architecture: ["source", "diagram", "plan"],
  "risk-cost": ["risks", "cost"],
  review: ["gate", "agent"],
};

let currentUser = null;
let latestResult = null;
let latestPreviewUrl = null;
let latestDiagramUrl = null;
let mermaidModulePromise = null;
let mermaidRenderSequence = 0;
let selectedHistoryId = null;
let selectedEnterpriseAssessmentId = null;
let viewMode = "executive";
let timelineTimer = null;
let timelineIndex = 0;
let diagramZoom = 1;
let diagramPanState = null;
let previewPanState = null;
let selectedCanvasComponentId = null;
let agentChatHistory = [];
let exportObjectUrls = [];
let demoSamples = [];
let selectedDemoSampleId = "";
let activeIntakeStep = 0;
let selectedAuthRoleCard = authRequestedRole?.value || "reviewer";
let lastAuthThemeToggleAt = 0;
let latestComparisonBrief = "";
let dashboardRenderSignature = "";
let demoSampleRenderSignature = "";
let runReadinessSignature = "";
let dashboardFilters = loadDashboardFilters();
let dashboardFilterFrame = 0;
let intakeDraftRestoreAttempted = false;
let isRestoringIntakeDraft = false;
let intakeDraftSaveTimer = 0;
let activeWorkspaceTab = "overview";
let renderedPanelTokens = {};
let comparisonPhaseTimer = null;
let agentPhaseTimer = null;
let snapshotCondensedState = null;
let snapshotFrameRequest = 0;
let currentResultRenderToken = 0;
let diagramAssetsRenderToken = 0;
let reportAssetsRenderToken = 0;
let reviewState = {
  reviewed: false,
  status: "ai_draft",
  notes: "",
  comments: "",
  projectName: "",
  reviewer: "",
  decisionOwner: "",
  approvalTargetDate: "",
  sectionComments: {},
  evidence: {},
};

const TIMELINE_STEPS = [
  ["ingest", "Ingest Diagram"],
  ["detect", "Detect Services"],
  ["map", "Map Equivalents"],
  ["design", "Design Target"],
  ["risks", "Score Risks"],
  ["report", "Build Decision Pack"],
];

initializeAuthTheme();
syncAuthRoleCards();
checkHealth();
initializeAuth();
loadDemoSamples();
renderSupportedProviders();
enhanceProviderRouteSelects();
enhanceArchitectureSelects();
syncProviderRouteBadges();
syncAppFrame();
renderHistory();
renderAssessmentDashboard();
renderIntakeFaqSection();
setActiveIntakeStep(0);
setViewMode(viewMode);
syncReviewMetadataInputs();
resetAgentChat();
syncSnapshotCondensed();

setReviewRailCollapsed(true);
enterDashboardMode();

window.addEventListener("cloudbridge-modern-ui-ready", () => {
  renderDemoSampleCards();
  renderAssessmentDashboard();
});
window.addEventListener("scroll", requestSnapshotCondensedSync, { passive: true });
window.addEventListener("resize", requestSnapshotCondensedSync);
window.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && assessmentCompareDialog && !assessmentCompareDialog.hidden) {
    closeComparisonDrawer();
  }
  if (event.key === "Escape" && dashboardHelpDialog && !dashboardHelpDialog.hidden) {
    closeDashboardHelp();
  }
});

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => activateTab(tab.dataset.tab));
});

document.querySelectorAll("[data-navigate-tab]").forEach((button) => {
  button.addEventListener("click", () => activateTab(button.dataset.navigateTab));
});

document.querySelectorAll("[data-view-mode]").forEach((button) => {
  button.addEventListener("click", () => setViewMode(button.dataset.viewMode || "executive"));
});

wizardButtons.forEach((button) => {
  button.addEventListener("click", () => setActiveIntakeStep(Number(button.dataset.wizardTarget || 0)));
});

wizardBackButton?.addEventListener("click", () => setActiveIntakeStep(activeIntakeStep - 1));
wizardNextButton?.addEventListener("click", () => setActiveIntakeStep(activeIntakeStep + 1));

toggleReviewRailButton?.addEventListener("click", () => {
  const collapsed = appShell?.classList.contains("review-rail-collapsed") ?? true;
  setReviewRailCollapsed(!collapsed);
});

closeReviewRailButton?.addEventListener("click", () => setReviewRailCollapsed(true));

toggleIntakeButton?.addEventListener("click", () => enterDashboardMode());
startNewRunButton?.addEventListener("click", () => startNewRun());
collapseIntakeButton?.addEventListener("click", () => toggleIntakePanel(true));

authForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  await signIn();
});

bindThemeToggle(authThemeToggle);

authRoleCards.forEach((card) => {
  card.addEventListener("click", () => selectAuthRoleCard(card.dataset.authRoleCard || "reviewer"));
});

authRequestedRole?.addEventListener("change", () => {
  selectedAuthRoleCard = authRequestedRole.value || "reviewer";
  syncAuthRoleCards();
});

[authDisplayName, authEmail, authAdminPassword].forEach((control) => {
  control?.addEventListener("input", () => control.classList.remove("auth-input-error"));
});

logoutButton?.addEventListener("click", signOut);

async function signOut() {
  try {
    await apiFetch(`${API_BASE}/api/session`, { method: "DELETE" });
  } finally {
    currentUser = null;
    applyRoleUi();
    showAuthOverlay("Signed out. Sign in to continue.");
  }
}

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

  const themeToggle = event.target.closest("[data-theme-toggle]");
  if (themeToggle) {
    event.preventDefault();
    requestAuthThemeToggle();
    return;
  }

  const navigateButton = event.target.closest("[data-navigate-tab]");
  if (navigateButton) {
    activateTab(navigateButton.dataset.navigateTab);
    return;
  }

  const viewModeButton = event.target.closest("[data-view-mode]");
  if (viewModeButton) {
    setViewMode(viewModeButton.dataset.viewMode || "executive");
    return;
  }

  const retryButton = event.target.closest("[data-retry-assessment]");
  if (retryButton) {
    form?.requestSubmit();
    return;
  }

  const dashboardButton = event.target.closest("[data-dashboard-action]");
  if (dashboardButton) {
    const id = dashboardButton.dataset.dashboardId || "";
    if (dashboardButton.dataset.dashboardAction === "open") {
      openDashboardReport(id);
    } else if (dashboardButton.dataset.dashboardAction === "compare") {
      await compareDashboardReport(id);
    } else if (dashboardButton.dataset.dashboardAction === "all") {
      enterDashboardMode({ focusReports: true });
    }
    return;
  }

  if (event.target.closest("[data-dashboard-filter-clear]")) {
    clearDashboardFilters();
    return;
  }

  const reportNavButton = event.target.closest("[data-report-nav]");
  if (reportNavButton) {
    const action = reportNavButton.dataset.reportNav;
    if (action === "dashboard") {
      enterDashboardMode();
    } else if (action === "all") {
      enterDashboardMode({ focusReports: true });
    } else if (action === "last") {
      openLastReportFromDashboard();
    }
    return;
  }

  if (event.target.closest("[data-help-open]")) {
    openDashboardHelp();
    return;
  }

  if (event.target.closest("[data-help-close]")) {
    closeDashboardHelp();
    return;
  }

  const compareClose = event.target.closest("[data-compare-close]");
  if (compareClose) {
    closeComparisonDrawer();
    return;
  }

  const compareCopy = event.target.closest("[data-compare-copy]");
  if (compareCopy) {
    await copyComparisonBrief(compareCopy);
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
      await compareHistoryItem(id);
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

  const fullscreenAction = event.target.closest("[data-canvas-fullscreen]");
  if (fullscreenAction) {
    await toggleDiagramFullscreen();
    return;
  }

  const canvasNode = event.target.closest("[data-arch-node]");
  if (canvasNode) {
    selectCanvasComponent(canvasNode.dataset.archNode);
    return;
  }

  const evidenceAction = event.target.closest("[data-evidence-action]");
  if (evidenceAction) {
    await attachGateEvidence(evidenceAction.dataset.gateKey || "");
    return;
  }

  const costAction = event.target.closest("[data-cost-model-action]");
  if (costAction) {
    await saveCalculatorCostModel();
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
    event.target === reviewerNameInput ||
    event.target === decisionOwnerInput ||
    event.target === approvalTargetDateInput
  ) {
    reviewState.notes = architectNotes.value;
    reviewState.comments = reviewComments.value;
    reviewState.projectName = projectNameInput.value;
    reviewState.reviewer = reviewerNameInput.value;
    reviewState.decisionOwner = decisionOwnerInput?.value || "";
    reviewState.approvalTargetDate = approvalTargetDateInput?.value || "";
    promoteReviewAfterArchitectComment(event.target);
    updateSelectedHistoryReviewState();
    syncAppFrame();
    if (latestResult && (event.target === architectNotes || event.target === reviewComments)) {
      refreshReviewStatusViews(latestResult);
    }
    scheduleIntakeDraftSave();
  }
  if (event.target.matches("[data-dashboard-filter]")) {
    updateDashboardFilter(event.target.dataset.dashboardFilter, event.target.value);
    return;
  }
});

document.addEventListener("change", async (event) => {
  if (!(event.target instanceof HTMLInputElement || event.target instanceof HTMLSelectElement)) {
    return;
  }
  if (event.target === workflowStatus) {
    if (!hasPermission("can_architect_review")) {
      workflowStatus.value = reviewState.status;
      showToast("Only an admin or architect can change workflow status.", "error");
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
    await persistReviewStateToSql();
    syncAppFrame();
    if (latestResult) {
      refreshReviewStatusViews(latestResult);
    }
    return;
  }
  if (event.target === sourceProvider || event.target === targetProvider) {
    syncProviderRouteBadges();
    setProviderTheme(latestResult || {});
    syncRunReadiness();
    scheduleIntakeDraftSave();
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
    scheduleIntakeDraftSave();
    return;
  }
  if (event.target === architectureVariant) {
    syncRunReadiness();
    scheduleIntakeDraftSave();
    return;
  }
  if (event.target.matches("[data-dashboard-filter]")) {
    updateDashboardFilter(event.target.dataset.dashboardFilter, event.target.value);
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

goalsInput.addEventListener("input", () => {
  syncPresetStates();
  syncRunReadiness();
  scheduleIntakeDraftSave();
});

migrationIntent?.addEventListener("input", () => {
  syncRunReadiness();
  scheduleIntakeDraftSave();
});

fileInput.addEventListener("change", () => {
  const file = fileInput.files?.[0];
  if (file) {
    selectedDemoSampleId = "";
    renderDemoSampleCards();
    renderDemoSampleSummary(null);
  }
  setFilePreview(file);
  syncRunReadiness();
  scheduleIntakeDraftSave();
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
  selectedDemoSampleId = "";
  renderDemoSampleCards();
  renderDemoSampleSummary(null);
  setFilePreview(file);
  syncRunReadiness();
  scheduleIntakeDraftSave();
});

previewFrame?.addEventListener("pointerdown", (event) => {
  if (!previewFrame.classList.contains("is-pannable") || event.button !== 0) {
    return;
  }
  previewPanState = {
    pointerId: event.pointerId,
    startX: event.clientX,
    startY: event.clientY,
    scrollLeft: previewFrame.scrollLeft,
    scrollTop: previewFrame.scrollTop,
  };
  previewFrame.classList.add("is-dragging");
  previewFrame.setPointerCapture?.(event.pointerId);
  event.preventDefault();
});

previewFrame?.addEventListener("pointermove", (event) => {
  if (!previewPanState || previewPanState.pointerId !== event.pointerId) {
    return;
  }
  previewFrame.scrollLeft = previewPanState.scrollLeft - (event.clientX - previewPanState.startX);
  previewFrame.scrollTop = previewPanState.scrollTop - (event.clientY - previewPanState.startY);
});

["pointerup", "pointercancel", "lostpointercapture"].forEach((eventName) => {
  previewFrame?.addEventListener(eventName, (event) => {
    if (previewPanState && "pointerId" in event && previewPanState.pointerId !== event.pointerId) {
      return;
    }
    previewPanState = null;
    previewFrame.classList.remove("is-dragging");
  });
});

demoSampleGrid?.addEventListener("click", async (event) => {
  const card = event.target.closest("[data-demo-sample-id]");
  if (!card || !hasPermission("can_assess")) {
    return;
  }
  await applyDemoSample(card.dataset.demoSampleId || "");
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

  enterAssessmentWorkspace("overview");
  setLoading(true);
  startAssessmentTimeline();
  hideError();
  resultTitle.textContent = "Analyzing";

  try {
    const fileBase64 = await readFileAsBase64(file);
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), ASSESSMENT_TIMEOUT_MS);
    const response = await apiFetch(`${API_BASE}/api/session`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
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
    }).finally(() => window.clearTimeout(timeoutId));
    const payload = await readApiPayload(response);
    if (!response.ok) {
      throw new Error(payload.detail || "Migration analysis failed.");
    }
    selectedHistoryId = null;
    selectedEnterpriseAssessmentId = null;
    reviewState = {
      reviewed: false,
      status: "needs_review",
      notes: "",
      comments: "",
      projectName: projectNameInput.value || buildHistoryTitle(payload),
      reviewer: reviewerNameInput.value || "",
      decisionOwner: decisionOwnerInput.value || "",
      approvalTargetDate: approvalTargetDateInput.value || "",
      sectionComments: {},
      evidence: {},
    };
    syncReviewMetadataInputs();
    workflowStatus.value = reviewState.status;
    latestResult = payload;
    renderResult(payload);
    enableActions(true);
    resultTitle.textContent = "Assessment Complete";
    showToast("Assessment complete. Review the decision snapshot and architecture workspace.", "success");
    enterAssessmentWorkspace("overview");
    rememberCompletedRun();
    clearIntakeDraft();
  } catch (error) {
    if (error.name === "AbortError") {
      showError("Assessment is taking longer than expected. The request was stopped after 120 seconds so the workspace stays responsive. Try again, or use a smaller diagram for the demo run.");
    } else {
      showError(error.message || "Migration analysis failed.");
    }
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

downloadReportButton.addEventListener("click", async () => {
  if (!latestResult?.markdown_report) {
    return;
  }
  hideError();
  try {
    const saved = await downloadText("migration-assessment.md", buildExportMarkdown(), "text/markdown");
    if (saved) {
      showToast("Markdown report export started.", "success");
    }
  } catch (error) {
    showError(error.message || "Markdown export failed.");
  }
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
    const response = await apiFetch(`${API_BASE}/api/session`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
      body: JSON.stringify({
        action: "report_pdf",
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
    const blob = await readExpectedBlob(response, "application/pdf", "PDF generation failed.");
    const saved = await downloadBlob("migration-assessment.pdf", blob);
    if (saved) {
      showToast("PDF report export started.", "success");
    }
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
    const response = await apiFetch(`${API_BASE}/api/session`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "diagram_png",
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
    const blob = await readExpectedBlob(response, "image/png", "Architecture PNG generation failed.");
    const saved = await downloadBlob(`${targetProvider.value || "target"}-architecture.png`, blob);
    if (saved) {
      showToast("Architecture PNG export started.", "success");
    }
  } catch (error) {
    showError(error.message || "AWS diagram generation failed.");
  } finally {
    downloadDiagramButton.disabled = false;
    downloadDiagramButton.textContent = original;
  }
});

saveAssessmentButton.addEventListener("click", async () => {
  if (!latestResult) {
    return;
  }
  if (!hasPermission("can_review")) {
    showToast("Viewer access cannot save assessment reviews.", "error");
    return;
  }
  await saveCurrentAssessment();
  pulseButton(saveAssessmentButton, "Saved");
});

markReviewedButton.addEventListener("click", async () => {
  if (!latestResult) {
    return;
  }
  if (!hasPermission("can_architect_review")) {
    showToast("Only an admin or architect can mark architect review.", "error");
    return;
  }
  reviewState.reviewed = !reviewState.reviewed;
  reviewState.status = reviewState.reviewed ? "reviewed" : "needs_review";
  workflowStatus.value = reviewState.status;
  markReviewedButton.textContent = reviewState.reviewed ? "Reviewed" : "Mark";
  updateSelectedHistoryReviewState();
  await persistReviewStateToSql();
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

function initializeAuthTheme() {
  setAuthTheme("light");
}

function setAuthTheme(theme) {
  const useDark = theme === "dark";
  document.documentElement.classList.toggle("dark", useDark);
  const themeToggles = [authThemeToggle, ...document.querySelectorAll("[data-theme-toggle]")].filter(Boolean);
  themeToggles.forEach((toggle) => {
    toggle.setAttribute("aria-pressed", String(useDark));
    toggle.setAttribute("title", useDark ? "Switch to light mode" : "Switch to dark mode");
  });
  try {
    localStorage.setItem(AUTH_THEME_KEY, useDark ? "dark" : "light");
  } catch {
    // Theme persistence is a nice-to-have in local demos.
  }
}

function toggleAuthTheme() {
  const currentlyDark = document.documentElement.classList.contains("dark");
  setAuthTheme(currentlyDark ? "light" : "dark");
}

function bindThemeToggle(toggle) {
  if (!toggle) {
    return;
  }
  toggle.addEventListener("pointerdown", (event) => {
    event.preventDefault();
    requestAuthThemeToggle();
  });
  toggle.addEventListener("click", (event) => {
    event.preventDefault();
    requestAuthThemeToggle();
  });
  toggle.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" && event.key !== " ") {
      return;
    }
    event.preventDefault();
    requestAuthThemeToggle();
  });
}

function requestAuthThemeToggle() {
  setAuthTheme("light");
}

function selectAuthRoleCard(role) {
  selectedAuthRoleCard = role;
  if (role === "viewer") {
    authRequestedRole.value = "viewer";
  } else {
    authRequestedRole.value = "reviewer";
  }
  if (role === "admin" && !authDisplayName.value.trim()) {
    authDisplayName.value = "admin";
  }
  syncAuthRoleCards();
  if (role === "admin") {
    authAdminPassword?.focus();
  } else {
    authDisplayName?.focus();
  }
}

function syncAuthRoleCards() {
  authRoleCards.forEach((card) => {
    const active = card.dataset.authRoleCard === selectedAuthRoleCard;
    card.classList.toggle("active", active);
    card.setAttribute("aria-pressed", String(active));
  });
}

function setAuthSubmitState(isLoading) {
  if (!authSubmitButton) {
    return;
  }
  authSubmitButton.disabled = isLoading;
  authSubmitButton.setAttribute("aria-busy", String(isLoading));
  if (authSubmitIdle && authSubmitLoading) {
    authSubmitIdle.hidden = isLoading;
    authSubmitLoading.classList.toggle("hidden", !isLoading);
    authSubmitLoading.classList.toggle("inline-flex", isLoading);
  } else {
    authSubmitButton.textContent = isLoading ? "Signing in" : "Sign in";
  }
}

async function signIn() {
  hideAuthError();
  setAuthSubmitState(true);
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
    setAuthSubmitState(false);
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

async function loadDemoSamples() {
  if (!demoSampleGrid) {
    return;
  }
  try {
    const response = await apiFetch(`${API_BASE}/api/demo-samples`);
    const payload = await readApiPayload(response);
    if (!response.ok) {
      throw new Error(payload.detail || "Demo samples could not be loaded.");
    }
    demoSamples = Array.isArray(payload) ? payload : [];
    renderDemoSampleCards();
    renderDemoSampleSummary(selectedDemoSample());
    restoreIntakeDraftAfterSamples();
  } catch (error) {
    demoSamples = [];
    demoSampleGrid.innerHTML = '<div class="demo-sample-empty">Samples unavailable.</div>';
    if (demoSampleSummary) {
      demoSampleSummary.textContent = error.message || "Demo samples could not be loaded.";
    }
  }
}

function renderDemoSampleCards() {
  if (!demoSampleGrid) {
    return;
  }
  const signature = JSON.stringify({
    mode: window.CloudBridgeModernUI?.renderDemoSamples ? "modern" : "native",
    selectedDemoSampleId,
    canAssess: hasPermission("can_assess"),
    samples: demoSamples.map((sample) => [sample.id, sample.title, sample.image_url]),
  });
  if (signature === demoSampleRenderSignature) {
    return;
  }
  demoSampleRenderSignature = signature;
  if (window.CloudBridgeModernUI?.renderDemoSamples) {
    window.CloudBridgeModernUI.renderDemoSamples(demoSampleGrid, {
      samples: demoSamples,
      selectedId: selectedDemoSampleId,
      apiBase: API_BASE,
      canSelect: hasPermission("can_assess"),
      onSelect: async (sampleId) => {
        if (!hasPermission("can_assess")) {
          showToast("Your role cannot load samples or edit assessments.", "error");
          return;
        }
        await applyDemoSample(sampleId);
      },
    });
    return;
  }
  if (!demoSamples.length) {
    demoSampleGrid.innerHTML = '<div class="demo-sample-empty">No bundled samples found.</div>';
    return;
  }
  demoSampleGrid.innerHTML = demoSamples
    .map(
      (sample) => `
        <button type="button" class="demo-sample-card ${sample.id === selectedDemoSampleId ? "active" : ""}" data-demo-sample-id="${escapeAttribute(sample.id)}">
          <span class="demo-thumb"><img src="${escapeAttribute(API_BASE + (sample.image_url || ""))}" alt="" loading="lazy" /></span>
          <span class="demo-card-copy">
            <span class="demo-card-route">${providerLogoLockup(sample.source_provider, { compact: true })}<i></i>${providerLogoLockup(sample.target_provider, { compact: true })}</span>
            <strong>${escapeHtml(sample.title)}</strong>
            <small>${escapeHtml(sample.pattern_label)}</small>
            <span>${escapeHtml((sample.goals || []).slice(0, 3).join(", "))}</span>
          </span>
        </button>
      `,
    )
    .join("");
}

function selectedDemoSample() {
  return demoSamples.find((sample) => sample.id === selectedDemoSampleId) || null;
}

function renderDemoSampleSummary(sample) {
  if (!demoSampleSummary) {
    return;
  }
  if (!sample) {
    demoSampleSummary.textContent = "Select a sample.";
    return;
  }
  demoSampleSummary.innerHTML = `
    <strong>${escapeHtml(sample.pattern_label || sample.title)}</strong>
    <span>${escapeHtml(sample.route_label)} | ${escapeHtml((sample.goals || []).join(", "))}</span>
  `;
}

async function applyDemoSample(sampleId, options = {}) {
  const sample = demoSamples.find((item) => item.id === sampleId);
  if (!sample) {
    return;
  }
  selectedDemoSampleId = sample.id;
  demoSampleRenderSignature = "";
  renderDemoSampleCards();
  renderDemoSampleSummary(sample);
  demoSampleGrid?.setAttribute("aria-busy", "true");
  hideError();
  try {
    const response = await apiFetch(`${API_BASE}${sample.image_url || `/api/demo-samples/${sample.id}/image`}`);
    if (!response.ok) {
      const payload = await readApiPayload(response);
      throw new Error(payload.detail || "Demo sample image could not be loaded.");
    }
    const blob = await response.blob();
    const file = new File([blob], sample.filename, {
      type: blob.type || "image/png",
      lastModified: Date.now(),
    });
    const transfer = new DataTransfer();
    transfer.items.add(file);
    fileInput.files = transfer.files;
    setFilePreview(file);
    sourceProvider.value = sample.source_provider || "auto";
    targetProvider.value = sample.target_provider || "aws";
    goalsInput.value = (sample.goals || []).join(", ");
    migrationIntent.value = sample.migration_intent || "";
    setSelectValue(architectureVariant, sample.architecture_variant || "balanced");
    setSelectValue(architecturePattern, sample.architecture_pattern || "auto");
    architecturePattern?.closest("details")?.setAttribute("open", "");
    if (projectNameInput) {
      projectNameInput.value = sample.title || "";
      reviewState.projectName = projectNameInput.value;
    }
    syncPresetStates();
    syncProviderRouteBadges();
    setProviderTheme({
      source_architecture: { provider: sample.source_provider },
      target_architecture: { provider: sample.target_provider },
    });
    syncAppFrame();
    syncRunReadiness();
    if (!options.keepStep) {
      setActiveIntakeStep(1);
    }
    scheduleIntakeDraftSave();
    saveIntakeDraft();
    if (!options.silent) {
      showToast(`${sample.title} loaded.`, "success");
    }
  } catch (error) {
    showError(error.message || "Demo sample could not be loaded.");
  } finally {
    demoSampleGrid?.removeAttribute("aria-busy");
  }
}

function setSelectValue(select, value) {
  if (!select) {
    return;
  }
  const hasOption = Array.from(select.options).some((option) => option.value === value);
  select.value = hasOption ? value : select.options[0]?.value || "";
  select.dispatchEvent(new Event("change", { bubbles: true }));
  syncArchitectureSelectControl(select);
}

function setActiveIntakeStep(step) {
  const maxStep = Math.max(0, Math.max(...intakeStepPanels.map((panel) => Number(panel.dataset.intakeStep || 0))));
  const nextStep = clamp(Number(step), 0, maxStep);
  if (nextStep > activeIntakeStep && !canAdvanceFromIntakeStep(activeIntakeStep)) {
    return;
  }
  activeIntakeStep = nextStep;
  intakeStepPanels.forEach((panel) => {
    panel.classList.toggle("active", Number(panel.dataset.intakeStep || 0) === activeIntakeStep);
  });
  wizardButtons.forEach((button) => {
    const target = Number(button.dataset.wizardTarget || 0);
    button.classList.toggle("active", target === activeIntakeStep);
    button.classList.toggle("complete", target < activeIntakeStep);
    if (target === activeIntakeStep) {
      button.setAttribute("aria-current", "step");
    } else {
      button.removeAttribute("aria-current");
    }
  });
  if (wizardBackButton) {
    wizardBackButton.disabled = activeIntakeStep === 0 || !hasPermission("can_assess");
  }
  if (wizardNextButton) {
    wizardNextButton.hidden = activeIntakeStep >= maxStep;
    wizardNextButton.disabled = !hasPermission("can_assess");
  }
  syncRunReadiness();
  scheduleIntakeDraftSave();
}

function canAdvanceFromIntakeStep(step) {
  if (step === 0 && !fileInput.files?.[0]) {
    showToast("Choose a sample or upload an architecture diagram first.", "error");
    return false;
  }
  if (step === 2 && !migrationIntent.value.trim() && !goalsInput.value.trim()) {
    showToast("Add migration intent or goals before the final review step.", "error");
    return false;
  }
  return true;
}

function syncRunReadiness() {
  const card = document.querySelector("#runReadinessCard");
  if (!card) {
    return;
  }
  const file = fileInput.files?.[0];
  const goals = parseGoals(goalsInput.value);
  const route = `${formatProvider(sourceProvider.value || "auto")} to ${formatProvider(targetProvider.value || "aws")}`;
  const signature = JSON.stringify({
    file: file ? [file.name, file.size, file.lastModified] : null,
    goals,
    route,
    intent: migrationIntent.value.trim(),
  });
  if (signature === runReadinessSignature) {
    return;
  }
  runReadinessSignature = signature;
  const items = [
    {
      label: "Diagram",
      value: file ? file.name : "Not selected",
      ready: Boolean(file),
    },
    {
      label: "Route",
      value: route,
      ready: Boolean(sourceProvider.value && targetProvider.value),
    },
    {
      label: "Intent",
      value: migrationIntent.value.trim() || "Needs migration intent",
      ready: Boolean(migrationIntent.value.trim()),
    },
    {
      label: "Goals",
      value: goals.length ? goals.join(", ") : "Optional",
      ready: true,
    },
  ];
  const allReady = items.every((item) => item.ready);
  card.innerHTML = `
    <div class="run-status-banner ${allReady ? "ready" : "missing"}">
      <span class="run-status-icon" aria-hidden="true">${runStatusIcon(allReady)}</span>
      <div>
        <strong>${allReady ? "Ready to run enterprise assessment" : "Complete the intake before running"}</strong>
        <small>${
          allReady
            ? "The assessment will use this diagram, route, intent, and goal set to generate mappings, risks, target design, and report outputs."
            : "Add the missing intake details before moving this assessment into generation."
        }</small>
      </div>
    </div>
    <div class="run-readiness-list">
      ${items
        .map(
          (item) => `
            <article class="run-summary-card ${item.ready ? "ready" : "missing"}">
              <span class="run-summary-icon" aria-hidden="true">${runSummaryIcon(item.label)}</span>
              <span class="run-summary-label">${escapeHtml(item.label)}</span>
              <strong class="run-summary-value">${escapeHtml(item.value)}</strong>
            </article>
          `,
        )
        .join("")}
    </div>
  `;
}

function runStatusIcon(ready) {
  if (ready) {
    return `
      <svg viewBox="0 0 24 24" fill="none">
        <path d="M20 6 9 17l-5-5" />
      </svg>
    `;
  }
  return `
    <svg viewBox="0 0 24 24" fill="none">
      <path d="M12 8v5" />
      <path d="M12 17h.01" />
      <path d="M10.3 4.3a2 2 0 0 1 3.4 0l7.1 12.5a2 2 0 0 1-1.7 3H4.9a2 2 0 0 1-1.7-3l7.1-12.5Z" />
    </svg>
  `;
}

function runSummaryIcon(label) {
  const key = String(label || "").toLowerCase();
  if (key === "diagram") {
    return `
      <svg viewBox="0 0 24 24" fill="none">
        <path d="M7 3.5h7l3 3v14H7v-17Z" />
        <path d="M14 3.5v4h4" />
        <path d="M9.5 12h5" />
        <path d="M9.5 15.5h4" />
      </svg>
    `;
  }
  if (key === "route") {
    return `
      <svg viewBox="0 0 24 24" fill="none">
        <path d="M4 7h13" />
        <path d="m14 4 3 3-3 3" />
        <path d="M20 17H7" />
        <path d="m10 14-3 3 3 3" />
      </svg>
    `;
  }
  if (key === "intent") {
    return `
      <svg viewBox="0 0 24 24" fill="none">
        <path d="M5 4.5h14v15H5v-15Z" />
        <path d="M8 9h8" />
        <path d="M8 12.5h8" />
        <path d="M8 16h5" />
      </svg>
    `;
  }
  return `
    <svg viewBox="0 0 24 24" fill="none">
      <path d="M12 21a9 9 0 1 0-9-9" />
      <path d="M12 17a5 5 0 1 0-5-5" />
      <path d="M12 13a1 1 0 1 0-1-1" />
      <path d="M3 21l6-6" />
    </svg>
  `;
}

function renderAssessmentDashboard() {
  if (!assessmentDashboard) {
    return;
  }
  const history = loadHistory();
  const allReports = buildDashboardReports(history);
  const reports = getFilteredDashboardReports(allReports);
  const lastReport = loadLastReport();
  const currentReadiness = latestResult?.assessment_insights?.scores?.overall_readiness?.value;
  const currentVerdict = latestResult?.final_verdict?.recommendation || "not_run";
  const currentTarget = latestResult?.target_architecture?.provider || targetProvider.value || "aws";
  const currentTitle = projectNameInput?.value?.trim() || (latestResult ? buildHistoryTitle(latestResult) : "No assessment selected");
  const total = allReports.length;
  const needsReview = allReports.filter((item) => ["needs_review", "ai_draft"].includes(item.status || "ai_draft")).length;
  const approved = allReports.filter((item) => item.status === "approved").length;
  const readinessValues = allReports
    .map((item) => item.result?.assessment_insights?.scores?.overall_readiness?.value)
    .filter((value) => Number.isFinite(Number(value)))
    .map(Number);
  const avgReadiness = readinessValues.length
    ? Math.round(readinessValues.reduce((sum, value) => sum + value, 0) / readinessValues.length)
    : latestResult?.assessment_insights?.scores?.overall_readiness?.value || 0;
  const signature = JSON.stringify({
    mode: window.CloudBridgeModernUI?.renderDashboard ? "modern" : "native",
    user: currentUser ? [currentUser.display_name, currentUser.primary_role] : null,
    currentTitle,
    currentReadiness,
    currentVerdict,
    currentTarget,
    reviewStatus: reviewState.status,
    selectedHistoryId,
    filters: dashboardFilters,
    lastReport,
    filteredCount: reports.length,
    reports: reports.map((item) => [
      item.id,
      item.title,
      item.status,
      item.reviewer,
      item.last_modified_at,
      item.result?.assessment_insights?.scores?.overall_readiness?.value,
    ]),
    total,
    needsReview,
    approved,
    avgReadiness,
  });
  if (signature === dashboardRenderSignature) {
    return;
  }
  dashboardRenderSignature = signature;
  if (window.CloudBridgeModernUI?.renderDashboard) {
    window.CloudBridgeModernUI.renderDashboard(assessmentDashboard, {
      current: {
        title: currentTitle,
        subtitle: latestResult ? formatVerdict(currentVerdict) : "Pick a sample to start",
        target: currentTarget,
        readiness: Number.isFinite(Number(currentReadiness)) ? `${Math.round(Number(currentReadiness))}%` : "Ready",
        readinessLabel: Number.isFinite(Number(currentReadiness)) ? "readiness" : "not run",
      },
      kpis: [
        { label: "Reports", value: total, detail: "Generated" },
        { label: "Review", value: needsReview, detail: "Open" },
        { label: "Approved", value: approved, detail: "Ready" },
        { label: "Readiness", value: `${avgReadiness}%`, detail: "Avg" },
      ],
      filters: dashboardFilters,
      filterOptions: buildDashboardFilterOptions(allReports),
      resultCount: reports.length,
      totalCount: allReports.length,
      lastReport,
      rows: reports.map((item) => {
        const readiness = item.result?.assessment_insights?.scores?.overall_readiness?.value;
        return {
          id: item.id,
          title: `${item.isCurrent ? "Current: " : ""}${item.title || "Migration assessment"}`,
          status: workflowLabel(item.status || "ai_draft"),
          reviewer: item.reviewer || "Unassigned reviewer",
          owner: `${item.decisionOwner ? `Owner: ${item.decisionOwner}` : "Owner not assigned"}${
            item.approvalTargetDate ? ` | Due ${item.approvalTargetDate}` : ""
          }`,
          target: item.result?.target_architecture?.provider || item.target_provider || "aws",
          readiness: Number.isFinite(Number(readiness)) ? `${Math.round(Number(readiness))}%` : "N/A",
          updated: formatDate(item.last_modified_at || item.created_at),
        };
      }),
      onOpen: openDashboardReport,
      onCompare: compareDashboardReport,
      onReview: () => setReviewRailCollapsed(false),
      onNavigate: openLastReportFromDashboard,
      onShowAll: () => enterDashboardMode({ focusReports: true }),
      onFilterChange: updateDashboardFilter,
      onClearFilters: clearDashboardFilters,
      onHowTo: openDashboardHelp,
      onSignOut: signOut,
      session: currentUser
        ? {
            name: currentUser.display_name,
            role: roleLabel(currentUser.primary_role),
          }
        : null,
    });
    return;
  }
  const recentRows = reports.map((item) => renderDashboardHistoryRow(item)).join("");
  assessmentDashboard.innerHTML = `
    <section class="dashboard-hero">
      <div>
        <p class="eyebrow">Current Assessment</p>
        <h3>${escapeHtml(currentTitle)}</h3>
        <span>${latestResult ? escapeHtml(formatVerdict(currentVerdict)) : "Choose a sample or upload a diagram to start"}</span>
      </div>
      <div class="dashboard-hero-route">
        ${providerLogoLockup(currentTarget, { compact: true })}
        <strong>${Number.isFinite(Number(currentReadiness)) ? `${Math.round(Number(currentReadiness))}%` : "Ready"}</strong>
        <small>${Number.isFinite(Number(currentReadiness)) ? "readiness" : "not run"}</small>
      </div>
    </section>
    <div class="dashboard-command-header">
      <div>
        <p class="eyebrow">Assessment Command Center</p>
        <h3>Portfolio Snapshot</h3>
      </div>
      <div class="dashboard-command-actions">
        <button type="button" class="diagram-link" id="dashboardOpenCurrentButton">Open Report</button>
        <button type="button" class="diagram-link" id="dashboardOpenReviewButton">Review Rail</button>
      </div>
    </div>
    ${renderDashboardRecoveryStrip(lastReport, allReports)}
    <div class="dashboard-kpi-grid">
      ${renderDashboardKpi("Reports", total, "Generated report history")}
      ${renderDashboardKpi("Needs Review", needsReview, "Drafts or gated assessments")}
      ${renderDashboardKpi("Approved", approved, "Ready for planning")}
      ${renderDashboardKpi("Avg Readiness", `${avgReadiness}%`, "Report history average")}
    </div>
    ${renderDashboardFilterBar(allReports, reports)}
    <div class="dashboard-recent">
      <div class="dashboard-recent-header">
        <strong>Recent Assessments</strong>
        <span>${reports.length} of ${allReports.length} reports shown</span>
      </div>
      ${
        recentRows ||
        `<div class="dashboard-empty">
          <strong>No reports yet.</strong>
          <span>Run an assessment to populate the report dashboard.</span>
        </div>`
      }
    </div>
  `;
  document.querySelector("#dashboardOpenCurrentButton")?.addEventListener("click", openLastReportFromDashboard);
  document.querySelector("#dashboardOpenReviewButton")?.addEventListener("click", () => setReviewRailCollapsed(false));
}

function buildDashboardReports(history) {
  if (!latestResult) {
    return history;
  }
  const existing = selectedHistoryId ? history.find((item) => item.id === selectedHistoryId) : null;
  const title = projectNameInput.value.trim() || existing?.title || buildHistoryTitle(latestResult);
  const currentRecord = {
    ...(existing || {}),
    id: existing?.id || "__current_report",
    isCurrent: true,
    enterpriseId: existing?.enterpriseId || selectedEnterpriseAssessmentId || null,
    created_at: existing?.created_at || new Date().toISOString(),
    last_modified_at: new Date().toISOString(),
    title,
    projectName: title,
    reviewer: reviewerNameInput.value.trim() || existing?.reviewer || "",
    decisionOwner: decisionOwnerInput?.value.trim() || existing?.decisionOwner || "",
    approvalTargetDate: approvalTargetDateInput?.value || existing?.approvalTargetDate || "",
    reviewed: reviewState.reviewed,
    notes: architectNotes.value,
    comments: reviewComments.value,
    sectionComments: reviewState.sectionComments || {},
    evidence: reviewState.evidence || {},
    status: reviewState.status,
    variant: architectureVariant.value,
    pattern: architecturePattern.value,
    source_provider: sourceProvider.value,
    target_provider: targetProvider.value,
    goals: goalsInput.value,
    result: latestResult,
  };
  return [currentRecord, ...history.filter((item) => item.id !== currentRecord.id)];
}

function getFilteredDashboardReports(reports) {
  const query = dashboardFilters.query.trim().toLowerCase();
  const provider = dashboardFilters.provider || "all";
  const status = dashboardFilters.status || "all";
  const sort = dashboardFilters.sort || "updated_desc";

  const visible = reports.filter((item) => {
    const result = item.result || {};
    const target = normalizeProviderKey(result.target_architecture?.provider || item.target_provider || "aws");
    const source = normalizeProviderKey(result.source_architecture?.provider || item.source_provider || "auto");
    const statusKey = item.status || "ai_draft";
    const searchable = [
      item.title,
      item.projectName,
      item.reviewer,
      item.decisionOwner,
      workflowLabel(statusKey),
      target,
      source,
      item.goals,
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    const providerMatch = provider === "all" || provider === target || provider === source;
    const statusMatch = status === "all" || status === statusKey;
    const queryMatch = !query || searchable.includes(query);
    return providerMatch && statusMatch && queryMatch;
  });

  return visible.sort((a, b) => {
    if (sort === "readiness_desc" || sort === "readiness_asc") {
      const aValue = Number(a.result?.assessment_insights?.scores?.overall_readiness?.value ?? -1);
      const bValue = Number(b.result?.assessment_insights?.scores?.overall_readiness?.value ?? -1);
      return sort === "readiness_desc" ? bValue - aValue : aValue - bValue;
    }
    if (sort === "title_asc") {
      return String(a.title || "").localeCompare(String(b.title || ""));
    }
    const aDate = new Date(a.last_modified_at || a.created_at || 0).getTime();
    const bDate = new Date(b.last_modified_at || b.created_at || 0).getTime();
    return bDate - aDate;
  });
}

function buildDashboardFilterOptions(reports) {
  const providers = new Set();
  const statuses = new Set();
  reports.forEach((item) => {
    providers.add(normalizeProviderKey(item.result?.target_architecture?.provider || item.target_provider || "aws"));
    providers.add(normalizeProviderKey(item.result?.source_architecture?.provider || item.source_provider || "auto"));
    statuses.add(item.status || "ai_draft");
  });
  return {
    providers: [...providers].filter((item) => item && item !== "neutral").sort(),
    statuses: [...statuses].sort(),
  };
}

function renderDashboardRecoveryStrip(lastReport, reports) {
  const latest = reports[0];
  const cardTitle = lastReport?.title || latest?.title || "No report opened yet";
  const cardStatus = lastReport?.status ? workflowLabel(lastReport.status) : latest ? workflowLabel(latest.status || "ai_draft") : "Waiting";
  const id = lastReport?.id || latest?.id || "";
  return `
    <section class="dashboard-recovery-strip" aria-label="Report recovery">
      <div>
        <p class="eyebrow">Report Recovery</p>
        <strong>${escapeHtml(cardTitle)}</strong>
        <span>${escapeHtml(cardStatus)}${lastReport?.openedAt ? ` | Last opened ${escapeHtml(formatDate(lastReport.openedAt))}` : ""}</span>
      </div>
      <div class="dashboard-command-actions">
        <button type="button" class="diagram-link" data-dashboard-action="open" data-dashboard-id="${escapeAttribute(id)}" ${id ? "" : "disabled"}>Open last report</button>
        <button type="button" class="diagram-link" data-dashboard-action="all">All reports (${reports.length})</button>
      </div>
    </section>
  `;
}

function renderDashboardFilterBar(allReports, visibleReports) {
  const options = buildDashboardFilterOptions(allReports);
  return `
    <section class="dashboard-filter-bar" aria-label="Report filters">
      <label>
        <span>Search reports</span>
        <input data-dashboard-filter="query" value="${escapeAttribute(dashboardFilters.query)}" placeholder="Search title, reviewer, cloud, goals" />
      </label>
      <label>
        <span>Cloud</span>
        <select data-dashboard-filter="provider">
          <option value="all">All clouds</option>
          ${options.providers
            .map(
              (provider) =>
                `<option value="${escapeAttribute(provider)}" ${dashboardFilters.provider === provider ? "selected" : ""}>${escapeHtml(providerShortLabel(provider))}</option>`,
            )
            .join("")}
        </select>
      </label>
      <label>
        <span>Status</span>
        <select data-dashboard-filter="status">
          <option value="all">All statuses</option>
          ${options.statuses
            .map(
              (status) =>
                `<option value="${escapeAttribute(status)}" ${dashboardFilters.status === status ? "selected" : ""}>${escapeHtml(workflowLabel(status))}</option>`,
            )
            .join("")}
        </select>
      </label>
      <label>
        <span>Sort</span>
        <select data-dashboard-filter="sort">
          <option value="updated_desc" ${dashboardFilters.sort === "updated_desc" ? "selected" : ""}>Newest updated</option>
          <option value="readiness_desc" ${dashboardFilters.sort === "readiness_desc" ? "selected" : ""}>Readiness high to low</option>
          <option value="readiness_asc" ${dashboardFilters.sort === "readiness_asc" ? "selected" : ""}>Readiness low to high</option>
          <option value="title_asc" ${dashboardFilters.sort === "title_asc" ? "selected" : ""}>Title A to Z</option>
        </select>
      </label>
      <div>
        <strong>${visibleReports.length}</strong>
        <span>of ${allReports.length} reports</span>
        <button type="button" class="diagram-link" data-dashboard-filter-clear>Reset</button>
      </div>
    </section>
  `;
}

function renderDashboardHelpSection() {
  return `
    <section class="dashboard-help-section">
      <div class="dashboard-help-intro">
        <div>
          <p class="eyebrow">FAQ & daily workflow</p>
          <h3>Use the agent like a migration review desk</h3>
          <span>Start with intake, run the assessment, then use the report, compare, and agent views to support review meetings and follow-up actions.</span>
        </div>
      </div>
      <div class="dashboard-faq-grid">
        ${DASHBOARD_FAQS.map(
          (item) => `
            <article class="dashboard-faq-card">
              <strong>${escapeHtml(item.question)}</strong>
              <span>${escapeHtml(item.answer)}</span>
            </article>
          `,
        ).join("")}
      </div>
    </section>
  `;
}

function renderIntakeFaqSection() {
  if (!intakeFaqSection) {
    return;
  }
  intakeFaqSection.innerHTML = renderDashboardHelpSection();
}

function openDashboardHelp() {
  if (!dashboardHelpDialog || !dashboardHelpContent) {
    return;
  }
  dashboardHelpContent.innerHTML = renderDashboardHelpDialogContent();
  dashboardHelpDialog.hidden = false;
  document.body.classList.add("help-open");
  dashboardHelpDialog.querySelector("[data-help-close]")?.focus();
}

function closeDashboardHelp() {
  if (!dashboardHelpDialog) {
    return;
  }
  dashboardHelpDialog.hidden = true;
  document.body.classList.remove("help-open");
}

function renderDashboardHelpDialogContent() {
  return `
    <section class="help-hero-card">
      <p class="eyebrow">Day-to-day guide</p>
      <h3>Run CloudBridge IQ as a repeatable cloud migration review loop.</h3>
      <p>Use the app to turn diagrams into assessment evidence, keep review history searchable, and prepare stakeholder-ready migration summaries without hunting through local files.</p>
    </section>
    <section class="help-step-grid">
      ${DAILY_HELP_STEPS.map(
        (step, index) => `
          <article class="help-step-card">
            <span>${index + 1}</span>
            <div>
              <strong>${escapeHtml(step.title)}</strong>
              <p>${escapeHtml(step.detail)}</p>
            </div>
          </article>
        `,
      ).join("")}
    </section>
    <section class="help-mode-grid">
      <article>
        <span>Daily intake</span>
        <strong>Use samples for demos, uploads for real work.</strong>
        <p>When a new opportunity arrives, upload the diagram, confirm route and goals, run the assessment, and save the report.</p>
      </article>
      <article>
        <span>Architect review</span>
        <strong>Focus on low confidence, blockers, and assumptions.</strong>
        <p>Use the Agent tab for focused questions, the Gate tab for approval readiness, and notes for review evidence.</p>
      </article>
      <article>
        <span>Portfolio update</span>
        <strong>Search, filter, compare, and export.</strong>
        <p>Use dashboard filters to find assessments by cloud or status, Compare for deltas, and PDF/Markdown exports for meetings.</p>
      </article>
    </section>
    <section class="help-faq-list">
      <h3>Common questions</h3>
      ${DASHBOARD_FAQS.map(
        (item) => `
          <details>
            <summary>${escapeHtml(item.question)}</summary>
            <p>${escapeHtml(item.answer)}</p>
          </details>
        `,
      ).join("")}
    </section>
  `;
}

function openLastReportFromDashboard() {
  if (latestResult) {
    renderResult(latestResult);
    enterAssessmentWorkspace("overview");
    return;
  }
  const [latestReport] = loadHistory();
  if (latestReport) {
    openHistoryItem(latestReport.id);
    return;
  }
  showToast("Run an assessment first, then the report opens from here.", "error");
}

function openDashboardReport(id) {
  if (id === "__current_report") {
    openLastReportFromDashboard();
    return;
  }
  openHistoryItem(id);
}

async function compareDashboardReport(id) {
  await compareHistoryItem(id);
}

function resolveComparisonPair(id) {
  const reports = buildDashboardReports(loadHistory()).filter((item) => item?.result);
  if (reports.length < 2) {
    return {
      error: "Run or save at least two assessments before comparing.",
    };
  }
  const selected = reports.find((item) => item.id === id) || reports[0];
  const current = reports.find((item) => item.isCurrent) || reports[0];
  if (selected.id === current.id) {
    const baseline = reports.find((item) => item.id !== current.id);
    return baseline
      ? { baseline, current }
      : { error: "No previous assessment is available for comparison." };
  }
  return {
    baseline: selected,
    current,
  };
}

function comparisonRequestItem(record, role) {
  return {
    title: String(record.title || "Migration assessment").replace(/^Current:\s*/i, ""),
    status: workflowLabel(record.status || "ai_draft"),
    reviewer: record.reviewer || null,
    updated_at: record.last_modified_at || record.created_at || null,
    assessment: record.result,
    metadata: {
      role,
      local_id: record.id,
      enterprise_id: record.enterpriseId || null,
      version: record.version || null,
      goals: record.goals || "",
      architecture_variant: record.variant || "",
      architecture_pattern: record.pattern || "",
      decision_owner: record.decisionOwner || "",
      approval_target_date: record.approvalTargetDate || "",
      is_current: Boolean(record.isCurrent),
    },
  };
}

async function runAssessmentComparison(pair) {
  if (!pair?.baseline || !pair?.current) {
    showToast(pair?.error || "Choose two assessments to compare.", "error");
    return;
  }
  openComparisonDrawer(pair);
  renderComparisonLoading(pair);
  try {
    const response = await apiFetch(`${API_BASE}/api/session`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "compare_assessments",
        baseline: comparisonRequestItem(pair.baseline, "baseline"),
        current: comparisonRequestItem(pair.current, "current"),
        focus: "Enterprise architecture review comparison with business impact, technical deltas, risks, governance actions, and next steps.",
      }),
    });
    const payload = await readApiPayload(response);
    if (!response.ok) {
      throw new Error(payload.detail || "Assessment comparison failed.");
    }
    renderAssessmentComparison(payload, pair);
    stopComparisonPhases();
    renderComparisonReviewSignal(payload, pair);
    showToast(comparisonToastMessage(payload), "success");
  } catch (error) {
    stopComparisonPhases();
    renderComparisonError(error.message || "Assessment comparison failed.", pair);
    showToast(error.message || "Assessment comparison failed.", "error");
  }
}

function openComparisonDrawer(pair) {
  if (!assessmentCompareDialog) {
    return;
  }
  if (assessmentCompareSubtitle) {
    assessmentCompareSubtitle.textContent = `${pair.baseline.title || "Baseline"} compared with ${pair.current.title || "Current assessment"}`;
  }
  assessmentCompareDialog.hidden = false;
  document.body.classList.add("compare-open");
}

function closeComparisonDrawer() {
  if (!assessmentCompareDialog) {
    return;
  }
  assessmentCompareDialog.hidden = true;
  document.body.classList.remove("compare-open");
}

function renderComparisonLoading(pair) {
  latestComparisonBrief = "";
  if (!assessmentCompareContent) {
    return;
  }
  assessmentCompareContent.innerHTML = `
    <section class="compare-loading-card">
      <div class="compare-loading-orb" aria-hidden="true"></div>
      <div>
        <p class="eyebrow">Generating Comparison</p>
        <h3>Comparing architecture assessments</h3>
        <span>${escapeHtml(pair.baseline.title || "Baseline")} to ${escapeHtml(pair.current.title || "Current assessment")}</span>
      </div>
      <div class="ai-phase-list" data-compare-phases>
        ${renderAiPhase("Building context", "Packaging both reports, readiness scores, risks, and mappings.", true)}
        ${renderAiPhase("Calling model", "Requesting an architecture-review comparison from the LLM.")}
        ${renderAiPhase("Generating summary", "Formatting executive signal, deltas, governance actions, and next steps.")}
      </div>
      <div class="compare-loading-grid" aria-hidden="true">
        <span></span><span></span><span></span>
      </div>
    </section>
  `;
  startComparisonPhases();
}

function renderAiPhase(title, detail, active = false, done = false) {
  return `
    <div class="ai-phase ${active ? "active" : ""} ${done ? "done" : ""}">
      <span></span>
      <div>
        <strong>${escapeHtml(title)}</strong>
        <small>${escapeHtml(detail)}</small>
      </div>
    </div>
  `;
}

function startComparisonPhases() {
  stopComparisonPhases();
  let index = 0;
  const phases = () => Array.from(document.querySelectorAll("[data-compare-phases] .ai-phase"));
  const update = () => {
    phases().forEach((phase, phaseIndex) => {
      phase.classList.toggle("done", phaseIndex < index);
      phase.classList.toggle("active", phaseIndex === index);
    });
    index = Math.min(index + 1, Math.max(0, phases().length - 1));
  };
  update();
  comparisonPhaseTimer = window.setInterval(update, 1400);
}

function stopComparisonPhases() {
  if (comparisonPhaseTimer) {
    window.clearInterval(comparisonPhaseTimer);
    comparisonPhaseTimer = null;
  }
}

function renderAssessmentComparison(comparison, pair) {
  if (!assessmentCompareContent) {
    return;
  }
  const delta = Number(comparison.readiness_delta || 0);
  const deltaLabel = delta > 0 ? `+${delta}` : String(delta);
  latestComparisonBrief = buildComparisonBrief(comparison, pair);
  assessmentCompareContent.innerHTML = `
    <section class="compare-hero-card">
      <div>
        <p class="eyebrow">${escapeHtml(comparisonSourceLabel(comparison))}</p>
        <h3>${escapeHtml(comparison.decision || "Comparison generated")}</h3>
        <p>${escapeHtml(comparison.executive_summary || "No summary returned.")}</p>
      </div>
      <div class="compare-confidence">
        <span>Confidence</span>
        <strong>${Math.round(Number(comparison.comparison_confidence || 0) * 100)}%</strong>
        <small>${escapeHtml(comparisonModelLabel(comparison))}</small>
      </div>
    </section>

    <section class="compare-metric-grid">
      ${renderComparisonMetric("Baseline readiness", `${comparison.baseline_readiness ?? 0}%`, pair.baseline?.title || "Baseline")}
      ${renderComparisonMetric("Current readiness", `${comparison.current_readiness ?? 0}%`, pair.current?.title || "Current")}
      ${renderComparisonMetric("Readiness delta", `${deltaLabel} pts`, delta > 0 ? "Improved" : delta < 0 ? "Declined" : "Stable", delta > 0 ? "good" : delta < 0 ? "warn" : "")}
      ${renderComparisonMetric("Verdict movement", comparison.verdict_delta || "No verdict movement", "Decision signal")}
    </section>

    <section class="compare-route-card">
      ${renderComparisonRouteSide("Baseline", pair.baseline)}
      <span class="compare-route-arrow">vs</span>
      ${renderComparisonRouteSide("Current", pair.current)}
    </section>

    ${renderComparisonListSection("Business Impact", comparison.business_impact)}
    ${renderComparisonDeltaSection("Architecture Deltas", comparison.architecture_deltas)}
    ${renderComparisonDeltaSection("Mapping Deltas", comparison.mapping_deltas)}
    ${renderComparisonDeltaSection("Risk Deltas", comparison.risk_deltas)}
    <section class="compare-two-column">
      ${renderComparisonListSection("Governance Actions", comparison.governance_actions)}
      ${renderComparisonListSection("Recommended Next Steps", comparison.recommended_next_steps)}
    </section>
    ${renderComparisonListSection("Assumptions", comparison.assumptions, "muted")}
  `;
}

function comparisonSourceLabel(comparison) {
  if (comparison?.source === "llm") {
    return "LLM Generated";
  }
  if (comparison?.source === "llm_fallback") {
    return "LLM Fallback";
  }
  return "Deterministic Baseline";
}

function comparisonModelLabel(comparison) {
  const model = String(comparison?.model_used || "").trim();
  if (model) {
    if (comparison?.source === "llm_fallback") {
      const fallbackMatch = model.match(/^(.*?)\s+fallback\s*\(\s*([^)]+)\s*\)\s*$/i);
      const cleaned = (fallbackMatch?.[1] || model)
        .replace(/\s+unavailable:?\s*TimeoutError/i, "")
        .trim();
      const reason = String(fallbackMatch?.[2] || "").toLowerCase();
      if (reason.includes("timeout")) {
        return `${cleaned || "LLM"} timed out; local comparison used`;
      }
      if (reason.includes("json")) {
        return `${cleaned || "LLM"} returned invalid JSON; local comparison used`;
      }
      return `${cleaned || "LLM"} fallback used; local comparison generated`;
    }
    return model;
  }
  return comparison?.source === "offline" ? "Local comparison engine" : "Comparison engine";
}

function comparisonToastMessage(comparison) {
  if (comparison?.source === "llm") {
    return "AI comparison generated.";
  }
  if (comparison?.source === "llm_fallback") {
    const model = String(comparison?.model_used || "");
    if (/json/i.test(model)) {
      return "Comparison generated locally because the LLM response was not valid JSON.";
    }
    if (/timeout/i.test(model)) {
      return "Comparison generated with local fallback after the LLM did not complete in time.";
    }
    return "Comparison generated with local fallback after the LLM response could not be used.";
  }
  return "Comparison generated with local comparison engine.";
}

function renderComparisonMetric(label, value, detail, tone = "") {
  return `
    <article class="compare-metric ${tone}">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
      <small>${escapeHtml(detail)}</small>
    </article>
  `;
}

function renderComparisonRouteSide(label, record) {
  const result = record?.result || {};
  const source = result.source_architecture?.provider || record?.source_provider || "auto";
  const target = result.target_architecture?.provider || record?.target_provider || "aws";
  const readiness = result.assessment_insights?.scores?.overall_readiness?.value;
  return `
    <article>
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(String(record?.title || "Migration assessment").replace(/^Current:\s*/i, ""))}</strong>
      <div class="compare-provider-row">
        ${providerLogoLockup(source, { compact: true })}
        <i></i>
        ${providerLogoLockup(target, { compact: true })}
      </div>
      <small>${Number.isFinite(Number(readiness)) ? `${Math.round(Number(readiness))}% readiness` : "Readiness unavailable"}</small>
    </article>
  `;
}

function renderComparisonListSection(title, items, tone = "") {
  const values = Array.isArray(items) ? items.filter(Boolean) : [];
  return `
    <section class="compare-section ${tone}">
      <div class="compare-section-title">
        <h4>${escapeHtml(title)}</h4>
        <span>${values.length}</span>
      </div>
      ${
        values.length
          ? `<ul>${values.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`
          : '<p class="compare-empty">No items returned for this section.</p>'
      }
    </section>
  `;
}

function renderComparisonDeltaSection(title, deltas) {
  const values = Array.isArray(deltas) ? deltas : [];
  return `
    <section class="compare-section">
      <div class="compare-section-title">
        <h4>${escapeHtml(title)}</h4>
        <span>${values.length}</span>
      </div>
      ${
        values.length
          ? `<div class="compare-delta-grid">${values.map((delta) => renderComparisonDeltaCard(delta)).join("")}</div>`
          : '<p class="compare-empty">No material deltas returned for this area.</p>'
      }
    </section>
  `;
}

function renderComparisonDeltaCard(delta) {
  const priority = String(delta.priority || "medium").toLowerCase();
  return `
    <article class="compare-delta-card ${escapeAttribute(priority)}">
      <div>
        <strong>${escapeHtml(delta.area || "Assessment delta")}</strong>
        <span>${escapeHtml(priority)} priority</span>
      </div>
      <dl>
        <dt>Baseline</dt>
        <dd>${escapeHtml(delta.baseline || "Not available")}</dd>
        <dt>Current</dt>
        <dd>${escapeHtml(delta.current || "Not available")}</dd>
        <dt>Impact</dt>
        <dd>${escapeHtml(delta.impact || "Review required.")}</dd>
      </dl>
      <small>Owner: ${escapeHtml(delta.owner || "Architecture review board")}</small>
    </article>
  `;
}

function renderComparisonError(message, pair) {
  latestComparisonBrief = "";
  if (!assessmentCompareContent) {
    return;
  }
  assessmentCompareContent.innerHTML = `
    <section class="compare-error-card intentional-fallback">
      <p class="eyebrow">Comparison Needs Retry</p>
      <h3>The AI comparison did not complete cleanly</h3>
      <p>${escapeHtml(message)}</p>
      <div class="ai-phase-list compact">
        ${renderAiPhase("Context package", "Both assessments were selected and prepared.", false, true)}
        ${renderAiPhase("Model response", "The LLM response could not be used for this request.", true)}
        ${renderAiPhase("Next action", "Retry compare, or open both reports from the dashboard and review deltas manually.")}
      </div>
      <button type="button" data-dashboard-action="compare" data-dashboard-id="${escapeAttribute(pair?.baseline?.id || "")}">Retry Compare</button>
    </section>
  `;
}

function renderComparisonReviewSignal(comparison, pair) {
  if (!reviewNotes) {
    return;
  }
  reviewNotes.innerHTML = `
    <div class="rail-list">
      <strong>AI Comparison Ready</strong>
      <ul>
        <li>${escapeHtml(comparison.decision || "Review comparison output.")}</li>
        <li>Readiness: ${escapeHtml(pair.baseline.title || "Baseline")} ${comparison.baseline_readiness}% to ${escapeHtml(pair.current.title || "Current")} ${comparison.current_readiness}%</li>
        <li>Source: ${escapeHtml(comparison.source || "offline")} | Model: ${escapeHtml(comparison.model_used || "offline")}</li>
      </ul>
    </div>
  `;
}

async function copyComparisonBrief(button) {
  if (!latestComparisonBrief) {
    showToast("Generate a comparison first.", "error");
    return;
  }
  await navigator.clipboard.writeText(latestComparisonBrief);
  pulseButton(button, "Copied");
}

function buildComparisonBrief(comparison, pair) {
  const lines = [
    `# CloudBridge IQ Assessment Comparison`,
    "",
    `Baseline: ${pair.baseline.title || "Baseline"}`,
    `Current: ${pair.current.title || "Current"}`,
    `Decision: ${comparison.decision || "Review required"}`,
    `Readiness: ${comparison.baseline_readiness}% to ${comparison.current_readiness}% (${comparison.readiness_delta > 0 ? "+" : ""}${comparison.readiness_delta} pts)`,
    `Verdict: ${comparison.verdict_delta || "No verdict movement"}`,
    `Source: ${comparison.source || "offline"} (${comparison.model_used || "offline"})`,
    "",
    `## Executive Summary`,
    comparison.executive_summary || "No summary returned.",
    "",
    ...briefList("Business Impact", comparison.business_impact),
    ...briefDeltas("Architecture Deltas", comparison.architecture_deltas),
    ...briefDeltas("Mapping Deltas", comparison.mapping_deltas),
    ...briefDeltas("Risk Deltas", comparison.risk_deltas),
    ...briefList("Governance Actions", comparison.governance_actions),
    ...briefList("Recommended Next Steps", comparison.recommended_next_steps),
  ];
  return lines.join("\n");
}

function briefList(title, items) {
  const values = Array.isArray(items) ? items.filter(Boolean) : [];
  return [`## ${title}`, ...(values.length ? values.map((item) => `- ${item}`) : ["- None returned."]), ""];
}

function briefDeltas(title, deltas) {
  const values = Array.isArray(deltas) ? deltas.filter(Boolean) : [];
  return [
    `## ${title}`,
    ...(values.length
      ? values.map((delta) => `- ${delta.area}: ${delta.baseline} -> ${delta.current}. Impact: ${delta.impact}`)
      : ["- No material deltas returned."]),
    "",
  ];
}

function renderDashboardKpi(label, value, detail) {
  return `
    <section class="dashboard-kpi">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
      <small>${escapeHtml(detail)}</small>
    </section>
  `;
}

function renderDashboardHistoryRow(item) {
  const readiness = item.result?.assessment_insights?.scores?.overall_readiness?.value;
  const target = item.result?.target_architecture?.provider || item.target_provider || "aws";
  return `
    <article class="dashboard-row">
      <div>
        <strong>${escapeHtml(`${item.isCurrent ? "Current: " : ""}${item.title || "Migration assessment"}`)}</strong>
        <span>${escapeHtml(workflowLabel(item.status || "ai_draft"))} | ${escapeHtml(item.reviewer || "Unassigned reviewer")}</span>
        <span>${escapeHtml(item.decisionOwner ? `Owner: ${item.decisionOwner}` : "Owner not assigned")}${item.approvalTargetDate ? ` | Due ${escapeHtml(item.approvalTargetDate)}` : ""}</span>
      </div>
      <div>${providerLogoLockup(target, { compact: true })}</div>
      <div>
        <span>Readiness</span>
        <strong>${Number.isFinite(Number(readiness)) ? `${Math.round(Number(readiness))}%` : "N/A"}</strong>
      </div>
      <div>
        <span>Updated</span>
        <strong>${escapeHtml(formatDate(item.last_modified_at || item.created_at))}</strong>
      </div>
      <div class="dashboard-row-actions">
        <button type="button" data-dashboard-action="open" data-dashboard-id="${escapeAttribute(item.id)}">Open</button>
        <button type="button" data-dashboard-action="compare" data-dashboard-id="${escapeAttribute(item.id)}">Compare</button>
      </div>
    </article>
  `;
}

function compactServerMessage(value) {
  const text = String(value || "")
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&#160;/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  if (/Access Denied|Threat Protection|HCLTech/i.test(text)) {
    return "HCLTech Threat Protection blocked this app request. Refresh the app and retry; if it persists, the Render domain or export response is being blocked by policy.";
  }
  return text ? text.slice(0, 220) : "";
}

function showAuthOverlay(message = "") {
  document.body.classList.add("auth-locked");
  if (authOverlay) {
    authOverlay.hidden = false;
    authOverlay.scrollTop = 0;
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
  markAuthFieldError(message);
  authError.textContent = message;
  authError.hidden = false;
}

function hideAuthError() {
  if (!authError) {
    return;
  }
  authError.textContent = "";
  authError.hidden = true;
  clearAuthFieldErrors();
}

function markAuthFieldError(message) {
  clearAuthFieldErrors();
  const text = String(message || "").toLowerCase();
  if (text.includes("password")) {
    authAdminPassword?.classList.add("auth-input-error");
    return;
  }
  if (!authDisplayName?.value?.trim() || text.includes("name")) {
    authDisplayName?.classList.add("auth-input-error");
  }
}

function clearAuthFieldErrors() {
  [authDisplayName, authEmail, authRequestedRole, authAdminPassword].forEach((control) => {
    control?.classList.remove("auth-input-error");
  });
}

function hasPermission(permission) {
  return Boolean(currentUser?.permissions?.[permission]);
}

function applyRoleUi() {
  const signedIn = Boolean(currentUser);
  if (!signedIn) {
    showAuthOverlay();
  } else {
    setAuthTheme("light");
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
  setActiveIntakeStep(activeIntakeStep);

  saveAssessmentButton.disabled = !latestResult || !canReview;
  markReviewedButton.disabled = !latestResult || !canArchitectReview;
  markReviewedButton.title = canArchitectReview ? "" : "Only an admin or architect can mark architect review.";
  workflowStatus.disabled = !canArchitectReview;
  architectNotes.disabled = !canArchitectReview;
  reviewerNameInput.disabled = !canReview;
  projectNameInput.disabled = !canReview;
  reviewComments.disabled = !canReview;

  copyReportButton.disabled = !latestResult || !canView;
  downloadPdfButton.disabled = !latestResult || !canView;
  downloadReportButton.disabled = !latestResult || !canView;
  downloadDiagramButton.disabled = !latestResult || !canView;
  if (startNewRunButton) {
    startNewRunButton.disabled = !canAssess;
    startNewRunButton.title = canAssess
      ? "Start a new assessment run"
      : "Viewer access cannot start a new assessment run.";
  }
  agentChatInput.disabled = !canView;
  agentChatSendButton.disabled = !canView || !latestResult;

  document.body.dataset.userRole = signedIn ? currentUser.primary_role : "anonymous";
  document.body.classList.toggle("role-restricted", signedIn && !canArchitectReview);
  renderDemoSampleCards();
  renderAssessmentDashboard();
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
  previewPanState = null;
  previewFrame.classList.remove("is-pannable", "is-dragging");
  previewFrame.removeAttribute("tabindex");
  previewFrame.removeAttribute("aria-label");
  previewFrame.removeAttribute("title");

  if (!file) {
    fileMeta.textContent = "or click to upload - PNG, JPG, WEBP, GIF, BMP, or PDF";
    previewFrame.innerHTML = '<div class="preview-empty">No diagram selected</div>';
    return;
  }

  fileMeta.textContent = `${file.name} (${formatBytes(file.size)})`;
  if (file.type.startsWith("image/")) {
    latestPreviewUrl = URL.createObjectURL(file);
    previewFrame.classList.add("is-pannable");
    previewFrame.tabIndex = 0;
    previewFrame.setAttribute("aria-label", "Selected diagram preview. Drag to pan across the image.");
    previewFrame.setAttribute("title", "Drag to pan across the diagram");
    previewFrame.scrollLeft = 0;
    previewFrame.scrollTop = 0;
    previewFrame.innerHTML = `
      <div class="preview-pan-surface">
        <img
          class="preview-pan-image"
          src="${latestPreviewUrl}"
          alt="Uploaded architecture diagram preview"
          draggable="false"
        />
      </div>
    `;
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
  currentResultRenderToken += 1;
  diagramAssetsRenderToken = 0;
  reportAssetsRenderToken = 0;
  renderedPanelTokens = {};
  setProviderTheme(payload);
  syncProviderRouteBadges(payload);
  selectedCanvasComponentId = payload.target_architecture?.components?.[0]?.id || null;
  renderAssessmentDashboard();
  renderSummary(payload);
  renderAnalysisMeta(payload.analysis_metadata || {});
  renderQualityGates(payload);
  resetResultPanelPlaceholders();
  renderResultPanel("overview", payload);
  renderReviewPanel(payload);
  resetAgentChat(payload);
  setViewMode(viewMode);
  toggleIntakePanel(true);
  applyRoleUi();
  activateTab(activeWorkspaceTab || "overview");
}

function resetResultPanelPlaceholders() {
  const placeholders = {
    source: "Detected source components will render when you open this tab.",
    mapping: "Service mappings will render when you open this tab.",
    diagram: "The diagram workspace will render when you open this tab.",
    plan: "Migration waves and cutover plan will render when you open this tab.",
    risks: "Risk and readiness scoring will render when you open this tab.",
    cost: "Cost and effort indicators will render when you open this tab.",
    gate: "Decision gate checklist will render when you open this tab.",
    report: "The executive and architect report will render when you open this tab.",
  };
  Object.entries(placeholders).forEach(([name, message]) => {
    const panel = panelElementByName(name);
    if (panel) {
      panel.innerHTML = `<div class="empty-state">${escapeHtml(message)}</div>`;
    }
  });
}

function renderResultPanel(panelName, payload = latestResult) {
  if (!payload || renderedPanelTokens[panelName] === currentResultRenderToken) {
    return;
  }
  const panel = panelElementByName(panelName);
  if (!panel && panelName !== "agent") {
    return;
  }
  if (panelName === "overview") {
    overviewPanel.innerHTML = renderOverview(payload);
  } else if (panelName === "source") {
    sourcePanel.innerHTML = renderSourceArchitecture(payload);
  } else if (panelName === "mapping") {
    mappingPanel.innerHTML = renderMappings(payload.service_mappings || []);
  } else if (panelName === "diagram") {
    diagramPanel.innerHTML = renderDiagram(payload);
    updateDiagramControls();
    syncZoomControls();
  } else if (panelName === "plan") {
    planPanel.innerHTML = renderPlan(payload);
  } else if (panelName === "risks") {
    risksPanel.innerHTML = renderRisks(payload);
  } else if (panelName === "cost") {
    costPanel.innerHTML = renderCost(payload);
  } else if (panelName === "gate") {
    gatePanel.innerHTML = renderDecisionGate(payload);
  } else if (panelName === "report") {
    reportPanel.innerHTML = renderReportMemo(payload);
    injectReportProviderBrand(reportPanel, payload);
    injectGeneratedDiagramIntoReport(reportPanel, payload);
  }
  renderedPanelTokens[panelName] = currentResultRenderToken;
}

function panelElementByName(panelName) {
  const panels = {
    overview: overviewPanel,
    source: sourcePanel,
    mapping: mappingPanel,
    diagram: diagramPanel,
    plan: planPanel,
    risks: risksPanel,
    cost: costPanel,
    gate: gatePanel,
    agent: document.querySelector("#agentPanel"),
    report: reportPanel,
  };
  return panels[panelName] || null;
}

function enterDashboardMode(options = {}) {
  document.body.classList.add("dashboard-mode");
  document.body.classList.remove("workspace-mode");
  toggleIntakePanel(false);
  setReviewRailCollapsed(true);
  if (resultTitle) {
    resultTitle.textContent = "Dashboard";
  }
  syncReportNavigation();
  renderAssessmentDashboard();
  if (options.focusReports) {
    scheduleIdleWork(() => assessmentDashboard?.scrollIntoView({ behavior: "smooth", block: "start" }));
  }
  if (options.focusNewRun) {
    scheduleIdleWork(() => {
      document.querySelector(".control-panel")?.scrollIntoView({ behavior: "smooth", block: "start" });
      document.querySelector("#demoSampleGrid")?.querySelector("button, [tabindex]")?.focus?.({ preventScroll: true });
    });
  }
  syncSnapshotCondensed();
}

function enterAssessmentWorkspace(tabName = "overview") {
  document.body.classList.remove("dashboard-mode");
  document.body.classList.add("workspace-mode");
  toggleIntakePanel(true);
  if (resultTitle && latestResult) {
    resultTitle.textContent = selectedHistoryId ? "Saved Assessment" : "Assessment";
  }
  activateTab(tabName);
  syncReportNavigation(latestResult);
  syncSnapshotCondensed();
}

function startNewRun() {
  if (!hasPermission("can_assess")) {
    showToast("Your role cannot start a new assessment run.", "error");
    enterDashboardMode({ focusNewRun: true });
    return;
  }
  resetIntakeForNewRun();
  enterDashboardMode({ focusNewRun: true });
  showToast("New run ready. Choose a sample or upload a diagram.", "success");
}

function resetIntakeForNewRun() {
  window.clearTimeout(intakeDraftSaveTimer);
  selectedDemoSampleId = "";
  demoSampleRenderSignature = "";
  runReadinessSignature = "";
  if (fileInput) {
    fileInput.value = "";
  }
  setFilePreview(null);
  if (sourceProvider) {
    sourceProvider.value = "auto";
    sourceProvider.dispatchEvent(new Event("change", { bubbles: true }));
  }
  if (targetProvider) {
    targetProvider.value = "aws";
    targetProvider.dispatchEvent(new Event("change", { bubbles: true }));
  }
  if (goalsInput) {
    goalsInput.value = "";
  }
  if (migrationIntent) {
    migrationIntent.value = "";
  }
  setSelectValue(architectureVariant, "balanced");
  setSelectValue(architecturePattern, "auto");
  if (projectNameInput) {
    projectNameInput.value = "";
    reviewState.projectName = "";
  }
  renderDemoSampleCards();
  renderDemoSampleSummary(null);
  syncPresetStates();
  syncProviderRouteBadges();
  syncRunReadiness();
  setActiveIntakeStep(0);
  window.clearTimeout(intakeDraftSaveTimer);
  clearIntakeDraft();
}

function buildAgentContextChips(payload = latestResult) {
  if (!payload) {
    return [
      { label: "Context", value: "No assessment loaded" },
      { label: "Next step", value: "Run assessment first" },
    ];
  }
  const source = formatProvider(payload.source_architecture?.provider || sourceProvider?.value || "source");
  const target = formatProvider(payload.target_architecture?.provider || targetProvider?.value || "target");
  const readiness = payload.assessment_insights?.scores?.overall_readiness?.value;
  const confidence = payload.final_verdict?.confidence;
  const confidencePercent = Number(confidence) > 1 ? Number(confidence) : Number(confidence) * 100;
  const mappings = Array.isArray(payload.service_mappings)
    ? payload.service_mappings.length
    : Array.isArray(payload.mappings)
      ? payload.mappings.length
      : 0;
  const reviewFlags = buildQualityGateItems(payload).filter((gate) => ["block", "warn"].includes(gate.status)).length;
  return [
    { label: "Route", value: `${source} to ${target}` },
    { label: "Readiness", value: Number.isFinite(Number(readiness)) ? `${Math.round(Number(readiness))}%` : "Not scored" },
    { label: "Verdict", value: formatVerdict(payload.final_verdict?.recommendation || "Assessment") },
    { label: "Mappings", value: mappings ? `${mappings} reviewed` : "Mapping context" },
    {
      label: "Confidence",
      value: Number.isFinite(confidencePercent) ? `${Math.round(confidencePercent)}%` : "Evidence based",
    },
    { label: "Review flags", value: reviewFlags ? `${reviewFlags} need attention` : "No critical flags" },
  ];
}

function renderAgentContextChips(chips = []) {
  if (!chips.length) {
    return "";
  }
  return `
    <div class="agent-answer-context" aria-label="Answer context">
      ${chips
        .map(
          (chip) => `
            <span>
              <small>${escapeHtml(chip.label)}</small>
              <strong>${escapeHtml(chip.value)}</strong>
            </span>
          `,
        )
        .join("")}
    </div>
  `;
}

function renderAgentSourceRow(
  label = "Assessment-aware answer",
  detail = "Grounded in current report, active tab, reviewer notes, and target architecture context.",
) {
  return `
    <div class="agent-source-row">
      <span>${escapeHtml(label)}</span>
      <small>${escapeHtml(detail)}</small>
    </div>
  `;
}

function renderAgentFollowUps(suggestions = []) {
  const usable = suggestions.filter(Boolean).slice(0, 3);
  if (!usable.length) {
    return "";
  }
  return `
    <div class="agent-followups" aria-label="Suggested follow-up questions">
      <span>Suggested follow-ups</span>
      <div>
        ${usable
          .map(
            (suggestion) =>
              `<button type="button" data-agent-prompt="${escapeAttribute(suggestion)}">${escapeHtml(shortSuggestion(suggestion))}</button>`,
          )
          .join("")}
      </div>
    </div>
  `;
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
    <div class="agent-message assistant agent-message-premium">
      <div class="agent-message-meta">
        <span class="agent-message-avatar">CB</span>
        <strong>Migration Agent</strong>
      </div>
      ${renderAgentSourceRow(
        payload ? "Assessment context loaded" : "Ready for assessment context",
        payload
          ? "Current report, active tab, reviewer notes, and target architecture context are available."
          : "Run an assessment first; then the agent will use mappings, risks, and report context.",
      )}
      ${renderAgentContextChips(buildAgentContextChips(payload))}
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
  const thinkingMessage = appendAgentMessage("assistant", renderAgentThinkingContent(0), {
    transient: true,
    html: true,
  });
  startAgentPhases(thinkingMessage);

  try {
    const response = await apiFetch(`${API_BASE}/api/session`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "agent_ask",
        question,
        assessment: latestResult,
        chat_history: agentChatHistory.slice(-10),
        active_tab: document.querySelector(".tab.active")?.dataset.tab || "overview",
        reviewer_notes: [architectNotes?.value, reviewComments?.value].filter(Boolean).join("\n"),
      }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const requestError = new Error(payload.detail || `Migration agent chat returned ${response.status}.`);
      requestError.status = response.status;
      throw requestError;
    }
    stopAgentPhases();
    thinkingMessage?.remove();
    appendAgentMessage("assistant", payload.answer || "I could not generate an answer.", {
      contextChips: buildAgentContextChips(latestResult),
      sourceLabel: "LLM generated answer",
      suggestions: payload.suggested_questions || [],
    });
    agentChatHistory.push({ role: "assistant", content: payload.answer || "" });
    agentChatHistory = agentChatHistory.slice(-12);
    renderAgentSuggestionButtons(payload.suggested_questions || []);
    agentStatus.textContent = payload.used_assessment_context ? "Assessment aware" : "General guidance";
  } catch (error) {
    stopAgentPhases();
    thinkingMessage?.remove();
    const fallbackAnswer = buildLocalAgentFallback(question, error);
    appendAgentMessage("assistant", fallbackAnswer, {
      fallback: true,
      contextChips: buildAgentContextChips(latestResult),
      sourceLabel: "Local assessment fallback",
      suggestions: [
        "Explain the target architecture flow.",
        "Which mappings need architect review?",
        "What are the top migration risks?",
      ],
    });
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
  const isPremiumAssistant = role === "assistant" && !options.transient && (options.contextChips || options.suggestions || options.sourceLabel);
  message.className = `agent-message ${role}${options.transient ? " transient" : ""}${isPremiumAssistant ? " agent-message-premium" : ""}`;
  const label = role === "user" ? "You" : "Migration Agent";
  const messageBody = options.html
    ? content || ""
    : role === "assistant" ? renderMarkdown(content || "") : `<p>${escapeHtml(content || "")}</p>`;
  const sourceDetail = latestResult
    ? undefined
    : "No assessment is loaded yet; run an assessment to unlock report-specific grounding.";
  message.innerHTML = `
    <div class="agent-message-meta">
      <span class="agent-message-avatar">${role === "user" ? "You" : "CB"}</span>
      <strong>${label}</strong>
    </div>
    ${isPremiumAssistant ? renderAgentSourceRow(options.sourceLabel || "Assessment-aware answer", sourceDetail) : ""}
    ${isPremiumAssistant ? renderAgentContextChips(options.contextChips || buildAgentContextChips(latestResult)) : ""}
    <div class="agent-message-body ${options.fallback ? "agent-fallback-body" : ""}">${messageBody}</div>
    ${isPremiumAssistant ? renderAgentFollowUps(options.suggestions || []) : ""}
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

function renderAgentThinkingContent(activeIndex = 0) {
  const phases = [
    ["Building context", "Collecting the active report, mappings, risks, goals, and reviewer notes."],
    ["Calling model", "Asking the migration agent for an assessment-specific answer."],
    ["Grounding answer", "Checking the response shape and preparing a concise architect-style reply."],
  ];
  return `
    <div class="agent-thinking-card">
      <p class="eyebrow">Agent Working</p>
      <div class="ai-phase-list compact">
        ${phases
          .map(([title, detail], index) => renderAiPhase(title, detail, index === activeIndex, index < activeIndex))
          .join("")}
      </div>
    </div>
  `;
}

function startAgentPhases(message) {
  stopAgentPhases();
  let index = 0;
  const body = message?.querySelector(".agent-message-body");
  const update = () => {
    if (!body || !document.contains(body)) {
      stopAgentPhases();
      return;
    }
    body.innerHTML = renderAgentThinkingContent(index);
    index = Math.min(index + 1, 2);
  };
  update();
  agentPhaseTimer = window.setInterval(update, 1300);
}

function stopAgentPhases() {
  if (agentPhaseTimer) {
    window.clearInterval(agentPhaseTimer);
    agentPhaseTimer = null;
  }
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
    ? "### Local Assessment Answer\nThe live agent route is not available in this server build, so I am answering from the loaded assessment context."
    : "### Local Assessment Answer\nThe live agent did not return a usable response, so I am answering from the loaded assessment context.";

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
    toggleIntakeButton.textContent = "Dashboard";
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
  if (snapshotCondensedState === shouldCondense) {
    return;
  }
  snapshotCondensedState = shouldCondense;
  document.body.classList.toggle("snapshot-condensed", shouldCondense);
}

function requestSnapshotCondensedSync() {
  if (snapshotFrameRequest) {
    return;
  }
  snapshotFrameRequest = window.requestAnimationFrame(() => {
    snapshotFrameRequest = 0;
    syncSnapshotCondensed();
  });
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
            ${renderMappingReviewFlag(mapping)}
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

function renderMappingReviewFlag(mapping) {
  const confidence = Number(mapping.confidence || 0);
  if (confidence < 0.65) {
    return '<span class="review-flag high">Architect review required</span>';
  }
  if (confidence < 0.82) {
    return '<span class="review-flag medium">Validate mapping</span>';
  }
  return '<span class="review-flag good">Ready for review</span>';
}

function renderArchitectureComparison(payload) {
  const source = payload.source_architecture || {};
  const target = payload.target_architecture || {};
  const mappings = payload.service_mappings || [];
  const riskyMappings = mappings.filter((mapping) => Number(mapping.confidence || 0) < 0.75);
  return `
    <div class="architecture-compare">
      <div class="diagram-section-header">
        <div>
          <p class="eyebrow">Source To Target</p>
          <h3>${formatProvider(source.provider || sourceProvider.value)} architecture compared with ${formatProvider(target.provider || targetProvider.value)}</h3>
          <p>Use this comparison to explain what changed before opening the generated target diagram.</p>
        </div>
        <div class="section-header-actions">
          <span class="status-badge ${riskyMappings.length ? "watch" : "good"}">${riskyMappings.length} mappings need review</span>
          <span class="status-badge">${mappings.length} mappings</span>
        </div>
      </div>
      <div class="architecture-compare-grid">
        ${renderArchitectureCompareColumn("Source", source, source.components || [])}
        <div class="architecture-compare-bridge">
          <strong>${mappings.length}</strong>
          <span>service mappings</span>
          <small>${riskyMappings.length ? `${riskyMappings.length} below confidence threshold` : "No low-confidence mappings"}</small>
        </div>
        ${renderArchitectureCompareColumn("Target", target, target.components || [])}
      </div>
    </div>
  `;
}

function renderArchitectureCompareColumn(label, architecture, components) {
  const visibleComponents = components.slice(0, 7);
  return `
    <section class="architecture-compare-column">
      <div class="architecture-compare-title">
        <span>${escapeHtml(label)}</span>
        ${providerLogoLockup(architecture.provider || "unknown", { compact: true })}
      </div>
      <p>${escapeHtml(architecture.summary || "Architecture summary unavailable.")}</p>
      <div class="compare-component-list">
        ${
          visibleComponents.length
            ? visibleComponents
                .map(
                  (component) => `
                    <span class="${Number(component.confidence || 0) < 0.7 ? "needs-review" : ""}">
                      <b>${escapeHtml(component.name)}</b>
                      ${escapeHtml(component.service_type || component.category || "service")}
                    </span>
                  `,
                )
                .join("")
            : '<span>No components detected</span>'
        }
      </div>
    </section>
  `;
}

function renderDiagram(payload) {
  const mermaid = normalizeMermaidSource(payload.mermaid_diagram || "");
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
          <button type="button" data-canvas-zoom="reset">Reset</button>
          <button type="button" data-canvas-zoom="100">100%</button>
          <button type="button" data-canvas-zoom="125">125%</button>
          <button type="button" data-canvas-zoom="150">150%</button>
          <button type="button" data-canvas-zoom="300">300%</button>
          <button type="button" data-canvas-fullscreen>Full screen</button>
        </div>
      </section>
      <section class="diagram-section">
        ${renderArchitectureComparison(payload)}
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
              <div class="diagram-pan-hint">Drag to pan. Use zoom controls for detail review.</div>
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
            <p>Local source preview. External Mermaid render links are disabled to avoid enterprise network blocks.</p>
          </div>
          <div class="diagram-actions">
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
    ${renderCostCalculator(estimate)}
    ${renderSavedCostModel(payload)}
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

function renderCostCalculator(estimate) {
  const sourceBaseline = Math.round((estimate.sourceMonthlyLow + estimate.sourceMonthlyHigh) / 2) || 0;
  const targetBaseline = Math.round((estimate.monthlyLow + estimate.monthlyHigh) / 2) || 0;
  return `
    <section class="cost-calculator-panel">
      <div class="section-header compact">
        <div>
          <p class="eyebrow">Calculator-Style Cost Model</p>
          <h3>Replace directional estimates with workload inputs</h3>
        </div>
        <button type="button" data-cost-model-action="save">Save Cost Model</button>
      </div>
      <div class="cost-input-grid">
        ${costInput("source_monthly_baseline", "Source monthly baseline", sourceBaseline)}
        ${costInput("compute_instances", "Compute instances", 4)}
        ${costInput("avg_compute_monthly", "Avg compute / month", Math.max(250, Math.round(targetBaseline * 0.22)))}
        ${costInput("storage_gb", "Storage GB", 1000)}
        ${costInput("data_transfer_gb", "Data transfer GB", 500)}
        ${costInput("database_monthly", "Database / analytics", Math.max(0, Math.round(targetBaseline * 0.28)))}
        ${costInput("licensing_monthly", "Licensing", 0)}
        ${costInput("support_monthly", "Support", Math.max(0, Math.round(targetBaseline * 0.08)))}
        ${costInput("observability_monthly", "Observability", Math.max(0, Math.round(targetBaseline * 0.06)))}
        ${costInput("discount_percent", "Discount %", 0)}
        ${costInput("migration_months", "Dual-run months", 2)}
      </div>
      <label class="cost-notes">
        Cost model notes
        <textarea data-cost-input="notes" placeholder="Sizing assumptions, pricing calculator link, reservation or commitment notes"></textarea>
      </label>
      <p class="muted">Saved cost models go into the SQL audit store and should be based on inventory, usage, data transfer, licensing, and support assumptions.</p>
    </section>
  `;
}

function renderSavedCostModel(payload) {
  const model = payload?.enterprise_cost_model;
  if (!model) {
    return "";
  }
  return `
    <section class="cost-calculator-panel saved-cost-model">
      <div class="section-header compact">
        <div>
          <p class="eyebrow">Saved SQL Cost Model</p>
          <h3>${formatDollar(model.monthly_target_estimate)} monthly target</h3>
        </div>
        <span class="status-badge recommended">Audited</span>
      </div>
      <div class="cost-estimate-board">
        <section class="cost-estimate-card">
          <p class="eyebrow">Source baseline</p>
          <h3>${formatDollar(model.source_monthly_baseline)}</h3>
        </section>
        <section class="cost-estimate-card savings-estimate positive">
          <p class="eyebrow">Monthly savings</p>
          <h3>${formatDollar(model.estimated_monthly_savings)}</h3>
        </section>
        <section class="cost-estimate-card">
          <p class="eyebrow">Annual savings</p>
          <h3>${formatDollar(model.estimated_annual_savings)}</h3>
        </section>
        <section class="cost-estimate-card">
          <p class="eyebrow">Dual-run reserve</p>
          <h3>${formatDollar(model.dual_run_reserve)}</h3>
        </section>
      </div>
    </section>
  `;
}

function costInput(name, label, value) {
  return `
    <label>
      ${escapeHtml(label)}
      <input type="number" min="0" step="0.01" data-cost-input="${escapeAttribute(name)}" value="${escapeAttribute(value)}" />
    </label>
  `;
}

async function saveCalculatorCostModel() {
  if (!hasPermission("can_review")) {
    showToast("Viewer access cannot save cost models.", "error");
    return;
  }
  try {
    const assessmentId = await ensureEnterpriseAssessmentSaved();
    const response = await apiFetch(`${API_BASE}/api/session`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "save_cost_model",
        assessment_id: assessmentId,
        cost_model: collectCostModelInput(),
      }),
    });
    const payload = await readApiPayload(response);
    if (!response.ok) {
      throw new Error(payload.detail || "Cost model save failed.");
    }
    latestResult.enterprise_cost_model = payload;
    costPanel.innerHTML = renderCost(latestResult);
    showToast(
      `Cost model saved. Target: ${formatDollar(payload.monthly_target_estimate)} / month, savings: ${formatDollar(payload.estimated_monthly_savings)} / month.`,
      "success",
    );
  } catch (error) {
    showToast(error.message || "Cost model save failed.", "error");
  }
}

function collectCostModelInput() {
  const values = {};
  document.querySelectorAll("[data-cost-input]").forEach((input) => {
    const key = input.dataset.costInput;
    if (!key) {
      return;
    }
    if (input instanceof HTMLTextAreaElement) {
      values[key] = input.value.trim() || null;
    } else {
      values[key] = Number(input.value || 0);
    }
  });
  return values;
}

function formatDollar(value) {
  return `$${Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
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
      (item, index) => {
        const gateKey = gateItemKey(item.item, index);
        const evidenceItems = reviewState.evidence?.[gateKey] || [];
        return `
        <div class="gate-row ${escapeHtml(item.status)}">
          <span></span>
          <div>
            <strong>${escapeHtml(item.item)}</strong>
            <p>${escapeHtml(item.evidence)}</p>
            <div class="gate-evidence">
              <label>
                Evidence
                <textarea data-evidence-content="${escapeAttribute(gateKey)}" placeholder="Paste approval evidence, cost model link, test result, or runbook note">${escapeHtml(
                  evidenceItems[0]?.content || "",
                )}</textarea>
              </label>
              <div class="gate-evidence-actions">
                <input data-evidence-title="${escapeAttribute(gateKey)}" value="${escapeAttribute(
                  evidenceItems[0]?.title || `${item.item} evidence`,
                )}" />
                <button type="button" data-evidence-action="attach" data-gate-key="${escapeAttribute(gateKey)}">Attach Evidence</button>
              </div>
              ${
                evidenceItems.length
                  ? `<small>${evidenceItems.length} evidence item${evidenceItems.length === 1 ? "" : "s"} attached in SQL audit store.</small>`
                  : "<small>No evidence attached yet.</small>"
              }
            </div>
          </div>
        </div>
      `;
      },
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

async function toggleDiagramFullscreen() {
  const shell = document.querySelector(".architecture-hero-shell");
  if (!shell) {
    return;
  }
  try {
    if (document.fullscreenElement) {
      await document.exitFullscreen();
    } else if (shell.requestFullscreen) {
      await shell.requestFullscreen();
    } else {
      shell.classList.toggle("diagram-fullscreen-fallback");
      showToast("Fullscreen API unavailable; expanded diagram workspace instead.", "info");
    }
  } catch (error) {
    shell.classList.toggle("diagram-fullscreen-fallback");
    showToast(error.message || "Fullscreen unavailable; expanded diagram workspace instead.", "info");
  }
  requestAnimationFrame(() => updateDiagramPanAffordance());
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
  wrap.innerHTML = `
      <div class="mermaid-fallback">
        <strong>Mermaid preview could not render inline.</strong>
        <span>${escapeHtml(message)}</span>
        <span>The exported PDF still uses the generated architecture diagram, so exports remain safe.</span>
        <details class="source-toggle">
          <summary>View Mermaid source</summary>
          <pre class="diagram-code">${escapeHtml(mermaidSource)}</pre>
        </details>
      </div>
    `;
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
    const response = await apiFetch(`${API_BASE}/api/session`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "diagram_png",
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
  syncRouteSelectControls();
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
  syncReportNavigation(payload);
}

function syncReportNavigation(payload = latestResult) {
  if (!reportBreadcrumbs) {
    return;
  }
  if (document.body.classList.contains("dashboard-mode")) {
    reportBreadcrumbs.innerHTML = "";
    reportBreadcrumbs.hidden = true;
    return;
  }
  const title = projectNameInput?.value?.trim() || (payload ? buildHistoryTitle(payload) : "Assessment");
  const reportLabel = selectedHistoryId ? "Saved report" : "Current report";
  reportBreadcrumbs.hidden = false;
  reportBreadcrumbs.innerHTML = `
    <button type="button" data-report-nav="dashboard">Dashboard</button>
    <span>/</span>
    <button type="button" data-report-nav="all">All reports</button>
    <span>/</span>
    <strong>${escapeHtml(reportLabel)}: ${escapeHtml(title)}</strong>
  `;
}

function providerRouteMarkup(sourceProviderName, targetProviderName, options = {}) {
  const compactClass = options.compact ? " compact" : "";
  const routeTitle = `${formatProvider(sourceProviderName)} to ${formatProvider(targetProviderName)}`;
  return `
    <div class="provider-route-content${compactClass}">
      <div class="provider-route-heading">
        <span>Selected route</span>
        <strong>${escapeHtml(routeTitle)}</strong>
      </div>
      <div class="provider-route-lockup${compactClass}">
        ${providerLogoLockup(sourceProviderName, { compact: options.compact })}
        <span class="provider-route-arrow" aria-hidden="true">→</span>
        ${providerLogoLockup(targetProviderName, { compact: options.compact })}
      </div>
    </div>
  `;
}

function enhanceProviderRouteSelects() {
  [sourceProvider, targetProvider].forEach((select) => {
    const shell = select?.closest(".route-select-shell");
    if (!select || !shell || shell.querySelector(".route-custom-select")) {
      return;
    }
    select.classList.add("route-native-select");
    select.tabIndex = -1;
    select.setAttribute("aria-hidden", "true");
    const control = document.createElement("div");
    control.className = "route-custom-select";
    control.dataset.routeSelect = select.id;
    control.innerHTML = `
      <button class="route-select-button" type="button" aria-haspopup="listbox" aria-expanded="false"></button>
      <div class="route-select-menu" role="listbox" hidden></div>
    `;
    shell.append(control);
    const button = control.querySelector(".route-select-button");
    const menu = control.querySelector(".route-select-menu");
    button?.addEventListener("click", (event) => {
      event.stopPropagation();
      const expanded = button.getAttribute("aria-expanded") === "true";
      closeRouteSelectMenus(control);
      if (!expanded) {
        menu.hidden = false;
        button.setAttribute("aria-expanded", "true");
      }
    });
    button?.addEventListener("keydown", (event) => {
      if (!["Enter", " ", "ArrowDown"].includes(event.key)) {
        return;
      }
      event.preventDefault();
      closeRouteSelectMenus(control);
      menu.hidden = false;
      button.setAttribute("aria-expanded", "true");
      menu.querySelector("[aria-selected='true']")?.focus();
    });
    menu?.addEventListener("click", (event) => {
      const option = event.target instanceof Element ? event.target.closest("[data-route-value]") : null;
      if (!option) {
        return;
      }
      select.value = option.dataset.routeValue || select.value;
      select.dispatchEvent(new Event("change", { bubbles: true }));
      closeRouteSelectMenus();
      syncRouteSelectControl(select);
    });
    menu?.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeRouteSelectMenus();
        button?.focus();
        return;
      }
      if (!["Enter", " "].includes(event.key)) {
        return;
      }
      event.preventDefault();
      event.target?.click?.();
    });
    select.addEventListener("change", () => syncRouteSelectControl(select));
    syncRouteSelectControl(select);
  });
  if (!document.body.dataset.routeSelectOutsideClick) {
    document.body.dataset.routeSelectOutsideClick = "true";
    document.addEventListener("click", (event) => {
      if (event.target instanceof Element && event.target.closest(".route-custom-select")) {
        return;
      }
      closeRouteSelectMenus();
    });
  }
}

function syncRouteSelectControls() {
  [sourceProvider, targetProvider].forEach((select) => syncRouteSelectControl(select));
}

function syncRouteSelectControl(select) {
  if (!select) {
    return;
  }
  const control = document.querySelector(`[data-route-select="${select.id}"]`);
  if (!control) {
    return;
  }
  const selected = select.selectedOptions?.[0] || select.options[select.selectedIndex];
  const selectedLabel = selected?.textContent?.trim() || providerShortLabel(select.value);
  const button = control.querySelector(".route-select-button");
  const menu = control.querySelector(".route-select-menu");
  if (button) {
    button.innerHTML = `
      ${providerLogoLockup(select.value, { compact: true, label: selectedLabel })}
      <span class="route-select-chevron" aria-hidden="true"></span>
    `;
  }
  if (menu) {
    menu.innerHTML = Array.from(select.options)
      .map((option) => {
        const selectedState = option.value === select.value;
        return `
          <button
            class="route-select-option"
            type="button"
            role="option"
            data-route-value="${escapeAttribute(option.value)}"
            aria-selected="${selectedState ? "true" : "false"}"
          >
            ${providerLogoLockup(option.value, { compact: true, label: option.textContent.trim() })}
          </button>
        `;
      })
      .join("");
  }
}

function closeRouteSelectMenus(exceptControl = null) {
  document.querySelectorAll(".route-custom-select").forEach((control) => {
    if (exceptControl && control === exceptControl) {
      return;
    }
    control.querySelector(".route-select-menu")?.setAttribute("hidden", "");
    control.querySelector(".route-select-button")?.setAttribute("aria-expanded", "false");
  });
}

function enhanceArchitectureSelects() {
  [architectureVariant, architecturePattern].forEach((select) => {
    const shell = select?.closest(".architecture-select-shell");
    if (!select || !shell || shell.querySelector(".architecture-custom-select")) {
      return;
    }
    select.classList.add("architecture-native-select");
    select.tabIndex = -1;
    select.setAttribute("aria-hidden", "true");

    const control = document.createElement("div");
    control.className = "architecture-custom-select";
    control.dataset.architectureSelect = select.id;
    control.innerHTML = `
      <button class="architecture-select-button" type="button" aria-haspopup="listbox" aria-expanded="false"></button>
      <div class="architecture-select-menu" role="listbox" hidden></div>
    `;
    shell.append(control);

    const button = control.querySelector(".architecture-select-button");
    const menu = control.querySelector(".architecture-select-menu");
    button?.addEventListener("click", (event) => {
      event.stopPropagation();
      const expanded = button.getAttribute("aria-expanded") === "true";
      closeArchitectureSelectMenus(control);
      if (!expanded) {
        menu.hidden = false;
        button.setAttribute("aria-expanded", "true");
      }
    });
    button?.addEventListener("keydown", (event) => {
      if (!["Enter", " ", "ArrowDown"].includes(event.key)) {
        return;
      }
      event.preventDefault();
      closeArchitectureSelectMenus(control);
      menu.hidden = false;
      button.setAttribute("aria-expanded", "true");
      menu.querySelector("[aria-selected='true']")?.focus();
    });
    menu?.addEventListener("click", (event) => {
      const option = event.target instanceof Element ? event.target.closest("[data-architecture-value]") : null;
      if (!option) {
        return;
      }
      select.value = option.dataset.architectureValue || select.value;
      select.dispatchEvent(new Event("change", { bubbles: true }));
      closeArchitectureSelectMenus();
      syncArchitectureSelectControl(select);
    });
    menu?.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeArchitectureSelectMenus();
        button?.focus();
        return;
      }
      if (!["Enter", " "].includes(event.key)) {
        return;
      }
      event.preventDefault();
      event.target?.click?.();
    });
    select.addEventListener("change", () => syncArchitectureSelectControl(select));
    syncArchitectureSelectControl(select);
  });

  if (!document.body.dataset.architectureSelectOutsideClick) {
    document.body.dataset.architectureSelectOutsideClick = "true";
    document.addEventListener("click", (event) => {
      if (event.target instanceof Element && event.target.closest(".architecture-custom-select")) {
        return;
      }
      closeArchitectureSelectMenus();
    });
  }
}

function syncArchitectureSelectControls() {
  [architectureVariant, architecturePattern].forEach((select) => syncArchitectureSelectControl(select));
}

function syncArchitectureSelectControl(select) {
  if (!select) {
    return;
  }
  const control = document.querySelector(`[data-architecture-select="${select.id}"]`);
  if (!control) {
    return;
  }
  const selected = select.selectedOptions?.[0] || select.options[select.selectedIndex];
  const selectedLabel = selected?.textContent?.trim() || "";
  const eyebrow = select.id === "architectureVariant" ? "Variant" : "Pattern";
  const button = control.querySelector(".architecture-select-button");
  const menu = control.querySelector(".architecture-select-menu");
  if (button) {
    button.innerHTML = `
      <span class="architecture-select-current">
        <small>${eyebrow}</small>
        <strong>${escapeHtml(selectedLabel)}</strong>
      </span>
      <span class="architecture-select-chevron" aria-hidden="true"></span>
    `;
  }
  if (menu) {
    menu.innerHTML = Array.from(select.options)
      .map((option) => {
        const selectedState = option.value === select.value;
        return `
          <button
            class="architecture-select-option"
            type="button"
            role="option"
            data-architecture-value="${escapeAttribute(option.value)}"
            aria-selected="${selectedState ? "true" : "false"}"
          >
            <span>${escapeHtml(option.textContent.trim())}</span>
          </button>
        `;
      })
      .join("");
  }
}

function closeArchitectureSelectMenus(exceptControl = null) {
  document.querySelectorAll(".architecture-custom-select").forEach((control) => {
    if (exceptControl && control === exceptControl) {
      return;
    }
    control.querySelector(".architecture-select-menu")?.setAttribute("hidden", "");
    control.querySelector(".architecture-select-button")?.setAttribute("aria-expanded", "false");
  });
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
  const assetKey = ["aws", "azure", "gcp"].includes(providerKey) ? providerKey : "auto";
  return `<img class="provider-logo-svg" src="assets/provider-${assetKey}.svg" alt="" loading="lazy" />`;
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
    <section class="report-mode-banner">
      <div>
        <p class="eyebrow">Report Mode</p>
        <strong>Executive summary first, architect detail second</strong>
        <span class="architect-only">Architect mode adds full mappings, assumptions, risks, target design, and implementation detail after the executive brief.</span>
      </div>
      <div class="view-toggle inline-mode-toggle" aria-label="Report mode">
        <button type="button" class="${viewMode === "executive" ? "active" : ""}" data-view-mode="executive">Executive</button>
        <button type="button" class="${viewMode === "architect" ? "active" : ""}" data-view-mode="architect">Architect</button>
      </div>
    </section>

    <section class="report-section-heading">
      <p class="eyebrow">Executive Summary</p>
      <h3>Business decision signal</h3>
      <span>Use this first page for leadership review, steering committee updates, and migration go/no-go discussion.</span>
    </section>

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

    ${renderReportActionMatrix(payload)}

    <section class="report-decision-grid">
      ${renderReportDecisionCard("Decision Gate", buildQualityGateItems(payload).slice(0, 4).map((gate) => `${gate.label}: ${gate.value}`))}
      ${renderReportDecisionCard("Mapping Review", (payload.service_mappings || []).slice(0, 5).map((mapping) => `${mapping.source_service} -> ${mapping.target_service}`))}
      ${renderReportDecisionCard("Top Risks", (payload.risks || []).slice(0, 5).map((risk) => `${risk.severity}: ${risk.title}`))}
      ${renderReportDecisionCard("Next Actions", payload.assessment_insights?.review?.suggested_next_actions || [])}
    </section>

    <section class="report-architect-pack architect-only">
      <section class="report-section-heading">
        <p class="eyebrow">Architect Detail</p>
        <h3>Implementation review packet</h3>
        <span>Use this section for mapping validation, assumption burn-down, risk ownership, cutover planning, and design approval.</span>
      </section>
      <div class="section-header">
        <div>
          <p class="eyebrow">Architect Appendix</p>
          <h3>Detailed implementation packet</h3>
        </div>
      </div>
      <div class="dashboard-grid">
        ${renderReportDecisionCard("Assumptions", payload.assumptions || [])}
        ${renderReportDecisionCard("Required Changes", payload.required_changes || [])}
        ${renderReportDecisionCard("Implementation Plan", (payload.migration_strategy || []).map((phase) => `${phase.phase}: ${(phase.goals || []).join(", ")}`))}
        ${renderReportDecisionCard("Risk Mitigations", (payload.risks || []).map((risk) => `${risk.title}: ${risk.mitigation}`))}
      </div>
    </section>

    <section class="report-document architect-only">
      ${renderMarkdown(payload.markdown_report || "")}
    </section>
  `;
}

function renderReportActionMatrix(payload) {
  const gates = buildQualityGateItems(payload);
  const blockers = gates.filter((gate) => gate.status === "block");
  const warnings = gates.filter((gate) => gate.status === "warn");
  const actions = payload.assessment_insights?.review?.suggested_next_actions || [];
  return `
    <section class="report-action-matrix">
      ${renderReportDecisionCard("Approval blockers", blockers.map((gate) => `${gate.label}: ${gate.detail}`))}
      ${renderReportDecisionCard("Review warnings", warnings.map((gate) => `${gate.label}: ${gate.detail}`))}
      ${renderReportDecisionCard("Immediate actions", actions)}
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
  return `
    <div class="report-mermaid-block">
      <div class="report-mermaid-header">
        <div>
          <strong>Mermaid Architecture Source</strong>
          <span>Rendered inline when the Mermaid library is available. Use the generated diagram block for PDF and PNG exports.</span>
        </div>
        <div class="diagram-actions">
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
    const response = await apiFetch(`${API_BASE}/api/session`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "rebuild",
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

async function saveCurrentAssessment() {
  const history = loadHistory();
  const title = projectNameInput.value.trim() || buildHistoryTitle(latestResult);
  const existingVersions = history.filter((item) => (item.projectName || item.title) === title).length;
  const record = {
    id: selectedHistoryId || `assessment_${Date.now()}`,
    enterpriseId: selectedEnterpriseAssessmentId || null,
    created_at: new Date().toISOString(),
    last_modified_at: new Date().toISOString(),
    title,
    projectName: title,
    reviewer: reviewerNameInput.value.trim(),
    decisionOwner: decisionOwnerInput?.value.trim() || "",
    approvalTargetDate: approvalTargetDateInput?.value || "",
    version: selectedHistoryId
      ? history.find((item) => item.id === selectedHistoryId)?.version || existingVersions || 1
      : existingVersions + 1,
    reviewed: reviewState.reviewed,
    notes: architectNotes.value,
    comments: reviewComments.value,
    sectionComments: reviewState.sectionComments || {},
    evidence: reviewState.evidence || {},
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
  persistHistory(withoutExisting);
  selectedHistoryId = record.id;
  rememberLastReport(record);
  renderHistory();
  syncAppFrame();
  try {
    const response = await apiFetch(`${API_BASE}/api/session`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "save_assessment",
        assessment_id: selectedEnterpriseAssessmentId,
        title,
        project_name: title,
        reviewer: reviewerNameInput.value.trim() || null,
        status: reviewState.status,
        assessment: latestResult,
        review_state: {
          reviewed: reviewState.reviewed,
          status: reviewState.status,
          notes: architectNotes.value,
          comments: reviewComments.value,
          decisionOwner: decisionOwnerInput?.value || "",
          approvalTargetDate: approvalTargetDateInput?.value || "",
          sectionComments: reviewState.sectionComments || {},
          evidence: reviewState.evidence || {},
        },
        cost_model: latestResult?.enterprise_cost_model || null,
      }),
    });
    const payload = await readApiPayload(response);
    if (!response.ok) {
      throw new Error(payload.detail || "SQL save failed.");
    }
    selectedEnterpriseAssessmentId = payload.assessment_id;
    record.enterpriseId = payload.assessment_id;
    record.version = payload.version || record.version;
    const syncedHistory = loadHistory().map((item) =>
      item.id === record.id ? { ...item, enterpriseId: payload.assessment_id, version: record.version } : item,
    );
    persistHistory(syncedHistory);
    renderHistory();
    showToast("Assessment saved to SQL history and audit log.", "success");
  } catch (error) {
    showToast(error.message || "Saved locally, but SQL persistence failed.", "error");
  }
}

function rememberCompletedRun() {
  if (!latestResult) {
    return;
  }
  const history = loadHistory();
  const title = projectNameInput.value.trim() || buildHistoryTitle(latestResult);
  const existing = selectedHistoryId ? history.find((item) => item.id === selectedHistoryId) : null;
  const existingVersions = history.filter((item) => (item.projectName || item.title) === title).length;
  const record = {
    id: existing?.id || `assessment_${Date.now()}`,
    enterpriseId: existing?.enterpriseId || selectedEnterpriseAssessmentId || null,
    created_at: existing?.created_at || new Date().toISOString(),
    last_modified_at: new Date().toISOString(),
    title,
    projectName: title,
    reviewer: reviewerNameInput.value.trim(),
    decisionOwner: decisionOwnerInput?.value.trim() || "",
    approvalTargetDate: approvalTargetDateInput?.value || "",
    version: existing?.version || existingVersions + 1,
    reviewed: reviewState.reviewed,
    notes: architectNotes.value,
    comments: reviewComments.value,
    sectionComments: reviewState.sectionComments || {},
    evidence: reviewState.evidence || {},
    status: reviewState.status,
    variant: architectureVariant.value,
    pattern: architecturePattern.value,
    source_provider: sourceProvider.value,
    target_provider: targetProvider.value,
    goals: goalsInput.value,
    result: latestResult,
  };
  const withoutExisting = history.filter((item) => item.id !== record.id);
  persistHistory([record, ...withoutExisting]);
  selectedHistoryId = record.id;
  rememberLastReport(record);
  renderHistory();
  syncAppFrame();
}

function openHistoryItem(id) {
  const record = loadHistory().find((item) => item.id === id);
  if (!record) {
    return;
  }
  selectedHistoryId = record.id;
  selectedEnterpriseAssessmentId = record.enterpriseId || null;
  latestResult = record.result;
  reviewState = {
    reviewed: Boolean(record.reviewed),
    status: record.status || (record.reviewed ? "reviewed" : "needs_review"),
    notes: record.notes || "",
    comments: record.comments || "",
    projectName: record.projectName || record.title || "",
    reviewer: record.reviewer || "",
    decisionOwner: record.decisionOwner || "",
    approvalTargetDate: record.approvalTargetDate || "",
    sectionComments: record.sectionComments || {},
    evidence: record.evidence || {},
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
  rememberLastReport(record);
  renderResult(latestResult);
  enableActions(true);
  resultTitle.textContent = "Saved Assessment";
  enterAssessmentWorkspace("overview");
  renderHistory();
}

async function compareHistoryItem(id) {
  const pair = resolveComparisonPair(id);
  if (pair.error) {
    showToast(pair.error, "error");
    return;
  }
  await runAssessmentComparison(pair);
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
        decisionOwner: decisionOwnerInput?.value || "",
        approvalTargetDate: approvalTargetDateInput?.value || "",
        sectionComments: reviewState.sectionComments || {},
      evidence: reviewState.evidence || {},
      enterpriseId: selectedEnterpriseAssessmentId || item.enterpriseId || null,
      last_modified_at: new Date().toISOString(),
    };
  });
  persistHistory(nextHistory);
  renderHistory();
}

async function persistReviewStateToSql() {
  if (!selectedEnterpriseAssessmentId || !hasPermission("can_review")) {
    return;
  }
  try {
    const response = await apiFetch(`${API_BASE}/api/assessments/${encodeURIComponent(selectedEnterpriseAssessmentId)}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        status: reviewState.status,
        reviewer: reviewerNameInput.value.trim() || null,
        review_state: {
          reviewed: reviewState.reviewed,
          status: reviewState.status,
          notes: architectNotes.value,
          comments: reviewComments.value,
          decisionOwner: decisionOwnerInput?.value || "",
          approvalTargetDate: approvalTargetDateInput?.value || "",
          sectionComments: reviewState.sectionComments || {},
          evidence: reviewState.evidence || {},
        },
      }),
    });
    const payload = await readApiPayload(response);
    if (!response.ok) {
      throw new Error(payload.detail || "Review status persistence failed.");
    }
  } catch (error) {
    showToast(error.message || "Review status saved locally but not in SQL.", "error");
  }
}

function renderHistory() {
  const history = loadHistory();
  if (!history.length) {
    historyList.innerHTML = '<div class="empty-state">No saved assessments yet.</div>';
    renderAssessmentDashboard();
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
            <span>${escapeHtml(item.decisionOwner || "No decision owner")}${item.approvalTargetDate ? ` | target ${escapeHtml(item.approvalTargetDate)}` : ""}</span>
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
  renderAssessmentDashboard();
}

function gateItemKey(label, index = 0) {
  return String(label || `gate_${index}`)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 80) || `gate_${index}`;
}

async function ensureEnterpriseAssessmentSaved() {
  if (!latestResult) {
    throw new Error("Run an assessment first.");
  }
  if (!selectedEnterpriseAssessmentId) {
    await saveCurrentAssessment();
  }
  if (!selectedEnterpriseAssessmentId) {
    throw new Error("Save the assessment before attaching enterprise evidence.");
  }
  return selectedEnterpriseAssessmentId;
}

async function attachGateEvidence(gateKey) {
  if (!hasPermission("can_review")) {
    showToast("Viewer access cannot attach decision evidence.", "error");
    return;
  }
  const selectorKey = selectorValue(gateKey);
  const contentInput = document.querySelector(`[data-evidence-content="${selectorKey}"]`);
  const titleInput = document.querySelector(`[data-evidence-title="${selectorKey}"]`);
  const content = (contentInput?.value || "").trim();
  const title = (titleInput?.value || "Decision gate evidence").trim();
  if (!content) {
    showToast("Add evidence text or a reference before attaching.", "error");
    return;
  }
  try {
    const assessmentId = await ensureEnterpriseAssessmentSaved();
    const response = await apiFetch(`${API_BASE}/api/session`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "add_evidence",
        assessment_id: assessmentId,
        evidence: {
          gate_key: gateKey,
          title,
          evidence_type: inferEvidenceType(gateKey, content),
          content,
        },
      }),
    });
    const payload = await readApiPayload(response);
    if (!response.ok) {
      throw new Error(payload.detail || "Evidence save failed.");
    }
    reviewState.evidence = reviewState.evidence || {};
    reviewState.evidence[gateKey] = [payload, ...(reviewState.evidence[gateKey] || [])];
    updateSelectedHistoryReviewState();
    if (latestResult) {
      gatePanel.innerHTML = renderDecisionGate(latestResult);
      renderReviewPanel(latestResult);
    }
    showToast("Decision evidence attached and audited.", "success");
  } catch (error) {
    showToast(error.message || "Evidence save failed.", "error");
  }
}

function inferEvidenceType(gateKey, content) {
  const text = `${gateKey} ${content}`.toLowerCase();
  if (/cost|estimate|calculator|pricing/.test(text)) {
    return "cost_model";
  }
  if (/runbook|rollback|cutover/.test(text)) {
    return "runbook";
  }
  if (/test|rehears|failover|validated|passed/.test(text)) {
    return "test_result";
  }
  if (/https?:\/\//.test(text)) {
    return "link";
  }
  return "note";
}

function selectorValue(value) {
  return String(value || "").replace(/\\/g, "\\\\").replace(/"/g, '\\"');
}

function syncReviewMetadataInputs() {
  architectNotes.value = reviewState.notes || "";
  reviewComments.value = reviewState.comments || "";
  projectNameInput.value = reviewState.projectName || "";
  reviewerNameInput.value = reviewState.reviewer || "";
  if (decisionOwnerInput) {
    decisionOwnerInput.value = reviewState.decisionOwner || "";
  }
  if (approvalTargetDateInput) {
    approvalTargetDateInput.value = reviewState.approvalTargetDate || "";
  }
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

function loadDashboardFilters() {
  try {
    const raw = localStorage.getItem(DASHBOARD_FILTER_KEY);
    const parsed = raw ? JSON.parse(raw) : {};
    return {
      query: String(parsed.query || ""),
      provider: String(parsed.provider || "all"),
      status: String(parsed.status || "all"),
      sort: String(parsed.sort || "updated_desc"),
    };
  } catch {
    return { query: "", provider: "all", status: "all", sort: "updated_desc" };
  }
}

function persistDashboardFilters() {
  localStorage.setItem(DASHBOARD_FILTER_KEY, JSON.stringify(dashboardFilters));
}

function updateDashboardFilter(key, value) {
  if (!key) {
    return;
  }
  dashboardFilters = {
    ...dashboardFilters,
    [key]: value,
  };
  persistDashboardFilters();
  scheduleDashboardRender();
}

function clearDashboardFilters() {
  dashboardFilters = { query: "", provider: "all", status: "all", sort: "updated_desc" };
  persistDashboardFilters();
  scheduleDashboardRender();
}

function scheduleDashboardRender() {
  dashboardRenderSignature = "";
  if (dashboardFilterFrame) {
    return;
  }
  dashboardFilterFrame = window.requestAnimationFrame(() => {
    dashboardFilterFrame = 0;
    renderAssessmentDashboard();
  });
}

function rememberLastReport(record) {
  if (!record?.id) {
    return;
  }
  const lastReport = {
    id: record.id,
    title: String(record.title || record.projectName || "Migration assessment").replace(/^Current:\s*/i, ""),
    status: record.status || reviewState.status || "ai_draft",
    target: record.result?.target_architecture?.provider || record.target_provider || targetProvider.value || "aws",
    readiness: record.result?.assessment_insights?.scores?.overall_readiness?.value ?? null,
    openedAt: new Date().toISOString(),
  };
  localStorage.setItem(LAST_REPORT_KEY, JSON.stringify(lastReport));
}

function loadLastReport() {
  try {
    const raw = localStorage.getItem(LAST_REPORT_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function scheduleIntakeDraftSave() {
  if (isRestoringIntakeDraft) {
    return;
  }
  window.clearTimeout(intakeDraftSaveTimer);
  intakeDraftSaveTimer = window.setTimeout(saveIntakeDraft, 180);
}

function saveIntakeDraft() {
  if (isRestoringIntakeDraft) {
    return;
  }
  const file = fileInput?.files?.[0] || null;
  const draft = {
    savedAt: new Date().toISOString(),
    activeIntakeStep,
    selectedDemoSampleId,
    sourceProvider: sourceProvider?.value || "auto",
    targetProvider: targetProvider?.value || "aws",
    goals: goalsInput?.value || "",
    migrationIntent: migrationIntent?.value || "",
    architectureVariant: architectureVariant?.value || "balanced",
    architecturePattern: architecturePattern?.value || "auto",
    projectName: projectNameInput?.value || "",
    file: file
      ? {
          name: file.name,
          size: file.size,
          type: file.type,
          lastModified: file.lastModified,
          restorable: Boolean(selectedDemoSampleId),
        }
      : null,
  };
  try {
    localStorage.setItem(INTAKE_DRAFT_KEY, JSON.stringify(draft));
  } catch (error) {
    console.warn("Unable to save intake draft.", error);
  }
}

async function restoreIntakeDraftAfterSamples() {
  if (intakeDraftRestoreAttempted) {
    return;
  }
  intakeDraftRestoreAttempted = true;
  let draft = null;
  try {
    const raw = localStorage.getItem(INTAKE_DRAFT_KEY);
    draft = raw ? JSON.parse(raw) : null;
  } catch {
    draft = null;
  }
  if (!draft) {
    return;
  }

  isRestoringIntakeDraft = true;
  try {
    const sampleId = draft.selectedDemoSampleId || "";
    if (sampleId && demoSamples.some((sample) => sample.id === sampleId)) {
      await applyDemoSample(sampleId, { silent: true, keepStep: true });
    }
    if (sourceProvider) sourceProvider.value = draft.sourceProvider || sourceProvider.value;
    if (targetProvider) targetProvider.value = draft.targetProvider || targetProvider.value;
    if (goalsInput) goalsInput.value = draft.goals || goalsInput.value || "";
    if (migrationIntent) migrationIntent.value = draft.migrationIntent || migrationIntent.value || "";
    setSelectValue(architectureVariant, draft.architectureVariant || architectureVariant?.value || "balanced");
    setSelectValue(architecturePattern, draft.architecturePattern || architecturePattern?.value || "auto");
    if (projectNameInput) {
      projectNameInput.value = draft.projectName || projectNameInput.value || "";
      reviewState.projectName = projectNameInput.value;
    }
    selectedDemoSampleId = sampleId || selectedDemoSampleId;
    demoSampleRenderSignature = "";
    renderDemoSampleCards();
    renderDemoSampleSummary(selectedDemoSample());
    syncPresetStates();
    syncProviderRouteBadges();
    syncRunReadiness();
    setActiveIntakeStep(Number(draft.activeIntakeStep || 0));
    if (draft.file && !draft.file.restorable && !fileInput.files?.[0]) {
      showToast(`Draft restored. Re-select ${draft.file.name} to run the assessment.`, "info");
    } else {
      showToast("New run draft restored.", "success");
    }
  } finally {
    isRestoringIntakeDraft = false;
  }
}

function clearIntakeDraft() {
  localStorage.removeItem(INTAKE_DRAFT_KEY);
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
  if (decisionOwnerInput?.value.trim()) {
    additions.push(`- **Decision owner:** ${decisionOwnerInput.value.trim()}`);
  }
  if (approvalTargetDateInput?.value) {
    additions.push(`- **Approval target date:** ${approvalTargetDateInput.value}`);
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
  if (latestResult.enterprise_cost_model) {
    const model = latestResult.enterprise_cost_model;
    additions.push("");
    additions.push("### Saved Calculator Cost Model");
    additions.push("");
    additions.push(`- **Source monthly baseline:** ${formatDollar(model.source_monthly_baseline)}`);
    additions.push(`- **Target monthly estimate:** ${formatDollar(model.monthly_target_estimate)}`);
    additions.push(`- **Estimated monthly savings:** ${formatDollar(model.estimated_monthly_savings)}`);
    additions.push(`- **Estimated annual savings:** ${formatDollar(model.estimated_annual_savings)}`);
    additions.push(`- **Dual-run reserve:** ${formatDollar(model.dual_run_reserve)}`);
  }
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
    const active = goals.includes((button.dataset.goal || "").toLowerCase());
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
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
  activeWorkspaceTab = tabName || "overview";
  const panelNames = resolveTabPanels(tabName);
  panelNames.forEach((panelName) => renderResultPanel(panelName));
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.classList.toggle("active", tabMatches(tab.dataset.tab, tabName, panelNames));
  });
  document.querySelectorAll("[data-navigate-tab]").forEach((button) => {
    button.classList.toggle("active", tabMatches(button.dataset.navigateTab, tabName, panelNames));
  });
  document.querySelectorAll(".tab-panel").forEach((panel) => {
    panel.classList.toggle("active", panelNames.some((name) => panel.id === `${name}Panel`));
  });
  ensureAssetsForActiveTabs(tabName);
}

function ensureAssetsForActiveTabs(tabName) {
  if (!latestResult) {
    return;
  }
  const panelNames = resolveTabPanels(tabName);
  const token = currentResultRenderToken;
  if (panelNames.includes("diagram") && diagramAssetsRenderToken !== token) {
    diagramAssetsRenderToken = token;
    scheduleIdleWork(async () => {
      if (token !== currentResultRenderToken || !latestResult) {
        return;
      }
      await renderMermaidDiagram(latestResult.mermaid_diagram || "");
      if (token !== currentResultRenderToken || !latestResult) {
        return;
      }
      await renderDiagramImage(latestResult);
      updateDiagramControls();
      updateCanvasLayers();
      syncZoomControls();
    });
  }
  if (panelNames.includes("report") && reportAssetsRenderToken !== token) {
    reportAssetsRenderToken = token;
    scheduleIdleWork(async () => {
      if (token !== currentResultRenderToken || !latestResult) {
        return;
      }
      renderReportMermaidBlocks(reportPanel);
      await renderDiagramImage(latestResult);
    });
  }
}

function scheduleIdleWork(callback) {
  const run = () => {
    try {
      Promise.resolve(callback()).catch((error) => {
        console.warn("Deferred UI work skipped:", error);
      });
    } catch (error) {
      console.warn("Deferred UI work skipped:", error);
    }
  };
  if ("requestIdleCallback" in window) {
    window.requestIdleCallback(run, { timeout: 900 });
    return;
  }
  window.setTimeout(run, 32);
}

function resolveTabPanels(tabName) {
  return TAB_GROUPS[tabName] || [tabName || "overview"];
}

function tabMatches(candidate, activeTab, activePanels) {
  if (!candidate) {
    return false;
  }
  if (candidate === activeTab) {
    return true;
  }
  const candidatePanels = resolveTabPanels(candidate);
  return candidatePanels.some((name) => activePanels.includes(name));
}

function setLoading(isLoading) {
  loadingState.hidden = !isLoading;
  document.body.classList.toggle("is-loading-assessment", isLoading);
  submitButton.disabled = isLoading || !hasPermission("can_assess");
  submitButton.setAttribute("aria-busy", String(isLoading));
  const idleLabel = submitButton.querySelector(".run-submit-idle");
  const loadingLabel = submitButton.querySelector(".run-submit-loading");
  if (idleLabel && loadingLabel) {
    idleLabel.hidden = isLoading;
    loadingLabel.hidden = !isLoading;
  } else {
    submitButton.textContent = isLoading ? "Running Assessment" : "Run Assessment";
  }
  applyRoleUi();
}

function showError(message) {
  errorState.innerHTML = `
    <div class="error-card">
      <strong>Assessment needs attention</strong>
      <p>${escapeHtml(message)}</p>
      <div class="error-actions">
        <button type="button" data-retry-assessment ${fileInput.files?.[0] ? "" : "disabled"}>Retry</button>
        <button type="button" data-navigate-tab="overview">Review Inputs</button>
      </div>
    </div>
  `;
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

async function readExpectedBlob(response, expectedType, fallbackMessage) {
  const contentType = response.headers.get("content-type") || "";
  if (!contentType.toLowerCase().includes(expectedType.toLowerCase())) {
    const text = await response.text().catch(() => "");
    throw new Error(compactServerMessage(text) || fallbackMessage);
  }
  return response.blob();
}

async function downloadText(filename, text, type) {
  const blob = new Blob([text], { type });
  return downloadBlob(filename, blob);
}

async function downloadBlob(filename, blob) {
  const safeFilename = filename || "cloudbridge-export";
  const url = URL.createObjectURL(blob);
  rememberExportUrl(url);
  const link = document.createElement("a");
  link.href = url;
  link.download = safeFilename;
  link.rel = "noopener";
  document.body.appendChild(link);
  link.dispatchEvent(new MouseEvent("click", { bubbles: true, cancelable: true, view: window }));
  link.remove();
  showExportReadyToast(safeFilename, url, blob.type);
  return true;
}

function rememberExportUrl(url) {
  exportObjectUrls.push(url);
  while (exportObjectUrls.length > 5) {
    URL.revokeObjectURL(exportObjectUrls.shift());
  }
  window.setTimeout(() => {
    exportObjectUrls = exportObjectUrls.filter((item) => item !== url);
    URL.revokeObjectURL(url);
  }, 10 * 60 * 1000);
}

function showExportReadyToast(filename, url, contentType) {
  if (!toastRegion) {
    return;
  }
  const toast = document.createElement("div");
  toast.className = "toast export-toast success";

  const copy = document.createElement("div");
  copy.className = "export-toast-copy";
  const title = document.createElement("strong");
  title.textContent = "Export ready";
  const detail = document.createElement("span");
  detail.textContent = `${filename} generated. If the automatic download is blocked, use the links below.`;
  copy.append(title, detail);

  const actions = document.createElement("div");
  actions.className = "export-toast-actions";

  const downloadLink = document.createElement("a");
  downloadLink.href = url;
  downloadLink.download = filename;
  downloadLink.textContent = "Download";

  const openLink = document.createElement("a");
  openLink.href = url;
  openLink.target = "_blank";
  openLink.rel = "noopener";
  openLink.textContent = contentType?.includes("text/") ? "Open text" : "Open";

  const dismiss = document.createElement("button");
  dismiss.type = "button";
  dismiss.textContent = "Dismiss";
  dismiss.addEventListener("click", () => toast.remove());

  actions.append(downloadLink, openLink, dismiss);
  toast.append(copy, actions);
  toastRegion.appendChild(toast);
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
