import React from "react";
import { createRoot } from "react-dom/client";
import "./tailwind.css";

const roots = new WeakMap();

function providerKey(provider) {
  const value = String(provider || "").toLowerCase();
  if (value.includes("azure")) return "azure";
  if (value.includes("gcp") || value.includes("google")) return "gcp";
  if (value.includes("aws") || value.includes("amazon")) return "aws";
  return "auto";
}

function providerLabel(provider) {
  const key = providerKey(provider);
  if (key === "azure") return "Azure";
  if (key === "gcp") return "GCP";
  if (key === "aws") return "AWS";
  return "Auto";
}

function providerIcon(provider) {
  return `assets/provider-${providerKey(provider)}.svg`;
}

function readinessPercent(value) {
  const numeric = Number(String(value || "").replace("%", ""));
  if (!Number.isFinite(numeric)) return 0;
  return Math.max(0, Math.min(100, Math.round(numeric)));
}

function statusTone(status = "") {
  const value = String(status).toLowerCase();
  if (value.includes("approved") || value.includes("ready")) {
    return "border-emerald-200 bg-emerald-50 text-emerald-700 shadow-emerald-900/5";
  }
  if (value.includes("review")) {
    return "border-amber-200 bg-amber-50 text-amber-700 shadow-amber-900/5";
  }
  if (value.includes("draft") || value.includes("not")) {
    return "border-slate-200 bg-slate-50 text-slate-600 shadow-slate-900/5";
  }
  return "border-sky-200 bg-sky-50 text-sky-700 shadow-sky-900/5";
}

function ProviderBadge({ provider, compact = false }) {
  return (
    <span
      className={[
        "inline-flex shrink-0 items-center gap-2 rounded-full border border-slate-200/80 bg-white/95 font-semibold text-slate-700 shadow-sm shadow-slate-950/5 backdrop-blur transition-all duration-200",
        compact ? "px-2.5 py-1 text-[11px]" : "px-3.5 py-1.5 text-xs",
      ].join(" ")}
    >
      <img className={compact ? "h-4 w-6 object-contain" : "h-5 w-8 object-contain"} src={providerIcon(provider)} alt="" loading="lazy" />
      {providerLabel(provider)}
    </span>
  );
}

function StatusBadge({ children }) {
  return (
    <span className={`inline-flex w-fit items-center rounded-full border px-2.5 py-1 text-[11px] font-bold uppercase tracking-normal shadow-sm ${statusTone(children)}`}>
      {children}
    </span>
  );
}

function RouteArrow() {
  return (
    <span className="grid h-7 w-7 shrink-0 place-items-center rounded-full border border-slate-200 bg-slate-50 text-xs font-bold text-slate-500">
      -&gt;
    </span>
  );
}

function Button({ children, variant = "secondary", className = "", ...props }) {
  const variants = {
    primary:
      "border-transparent bg-gradient-to-r from-blue-600 via-sky-600 to-indigo-600 text-white shadow-md shadow-blue-600/20 hover:scale-[1.02] hover:brightness-105 hover:shadow-lg hover:shadow-blue-600/25 active:scale-[0.98]",
    secondary:
      "border-slate-200 bg-white/90 text-slate-700 shadow-sm shadow-slate-950/5 hover:border-slate-300 hover:bg-slate-50 hover:text-slate-950 active:scale-[0.98]",
  };
  return (
    <button
      className={`inline-flex min-h-9 items-center justify-center rounded-xl border px-4 py-2 text-xs font-bold transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-sky-500/15 ${variants[variant]} ${className}`}
      type="button"
      {...props}
    >
      {children}
    </button>
  );
}

function StatCard({ label, value, detail, index }) {
  const accents = [
    { bar: "from-sky-500 to-blue-500", dot: "bg-sky-500", glow: "hover:shadow-sky-500/10" },
    { bar: "from-amber-500 to-orange-400", dot: "bg-amber-500", glow: "hover:shadow-amber-500/10" },
    { bar: "from-emerald-500 to-teal-400", dot: "bg-emerald-500", glow: "hover:shadow-emerald-500/10" },
    { bar: "from-indigo-500 to-blue-600", dot: "bg-indigo-500", glow: "hover:shadow-indigo-500/10" },
  ];
  const accent = accents[index % accents.length];
  return (
    <article className={`group relative overflow-hidden rounded-2xl border border-slate-200/75 bg-white p-5 shadow-sm shadow-slate-950/5 transition-all duration-200 hover:-translate-y-1 hover:shadow-lg ${accent.glow}`}>
      <span className={`absolute inset-x-0 top-0 h-1 bg-gradient-to-r ${accent.bar}`} />
      <div className="flex items-start justify-between gap-3">
        <span className="text-[11px] font-bold uppercase tracking-normal text-slate-500">{label}</span>
        <span className={`mt-0.5 h-2.5 w-2.5 rounded-full ${accent.dot} shadow-[0_0_0_4px_rgba(226,232,240,0.75)]`} />
      </div>
      <strong className="mt-3 block text-3xl font-bold leading-none tracking-tight text-slate-950">{value}</strong>
      <small className="mt-2 block text-sm font-medium text-slate-500">{detail}</small>
    </article>
  );
}

function CurrentAssessmentCard({ current }) {
  const readiness = readinessPercent(current?.readiness);
  const status = current?.readinessLabel === "not run" ? "Ready" : current?.subtitle;
  return (
    <section className="group relative overflow-hidden rounded-[2rem] border border-white/80 bg-white p-6 shadow-lg shadow-slate-950/5 ring-1 ring-slate-200/60 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-xl hover:shadow-sky-900/10 lg:grid lg:grid-cols-[minmax(0,1fr)_280px] lg:items-center lg:gap-6">
      <span className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-sky-300/70 to-transparent" />
      <div className="min-w-0">
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <p className="m-0 text-[11px] font-bold uppercase tracking-normal text-sky-700">Current</p>
          <StatusBadge>{status}</StatusBadge>
        </div>
        <h3 className="m-0 text-3xl font-semibold leading-tight tracking-tight text-slate-950">{current?.title}</h3>
        <span className="mt-3 block text-sm font-medium leading-6 text-slate-500">{current?.subtitle}</span>
      </div>
      <div className="relative mt-5 rounded-2xl border border-slate-200/80 bg-gradient-to-br from-slate-50 via-white to-sky-50 p-4 shadow-inner shadow-white lg:mt-0">
        <div className="mb-4 flex items-center justify-between gap-3">
          <ProviderBadge provider={current?.target} compact />
          <span className="text-[11px] font-bold uppercase text-slate-500">{current?.readinessLabel}</span>
        </div>
        <div className="flex items-end justify-between gap-4">
          <strong className="text-4xl font-semibold leading-none tracking-tight text-slate-950">{current?.readiness}</strong>
          <span className="text-xs font-semibold text-slate-500">{readiness || 0}% complete</span>
        </div>
        <span className="mt-4 block h-2 overflow-hidden rounded-full bg-white shadow-inner ring-1 ring-slate-200/80">
          <span className="block h-full rounded-full bg-gradient-to-r from-blue-500 via-sky-500 to-indigo-600 transition-all duration-700 ease-out" style={{ width: `${readiness || 0}%` }} />
        </span>
      </div>
    </section>
  );
}

function AssessmentRow({ row, onOpen, onCompare }) {
  const readiness = readinessPercent(row.readiness);
  return (
    <article className="group grid gap-4 rounded-2xl border border-slate-200/75 bg-white p-4 shadow-sm shadow-slate-950/5 transition-all duration-200 hover:-translate-y-1 hover:border-sky-200 hover:shadow-lg hover:shadow-sky-900/10 lg:grid-cols-[minmax(260px,1.55fr)_auto_130px_170px_auto] lg:items-center">
      <div className="min-w-0">
        <strong className="block truncate text-[15px] font-semibold text-slate-950">{row.title}</strong>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <StatusBadge>{row.status}</StatusBadge>
          <span className="text-xs font-medium text-slate-500">{row.reviewer}</span>
        </div>
        <span className="mt-1 block text-xs font-medium text-slate-400">{row.owner}</span>
      </div>
      <ProviderBadge provider={row.target} compact />
      <div className="min-w-[120px]">
        <span className="block text-[11px] font-bold uppercase text-slate-500">Readiness</span>
        <div className="mt-1 flex items-center gap-2">
          <strong className="text-sm font-semibold text-slate-950">{row.readiness}</strong>
          <span className="h-2 w-16 overflow-hidden rounded-full bg-slate-100 ring-1 ring-slate-200/70">
            <span className="block h-full rounded-full bg-gradient-to-r from-blue-500 via-sky-500 to-emerald-400 transition-all duration-700 ease-out" style={{ width: `${readiness || 0}%` }} />
          </span>
        </div>
      </div>
      <div>
        <span className="block text-[11px] font-bold uppercase text-slate-500">Updated</span>
        <strong className="mt-1 block text-xs font-semibold leading-5 text-slate-950">{row.updated}</strong>
      </div>
      <div className="flex flex-wrap justify-start gap-2 lg:justify-end">
        <Button className="min-h-8 px-3 py-1.5" data-dashboard-action="open" data-dashboard-id={row.id} onClick={() => onOpen?.(row.id)}>
          Open
        </Button>
        <Button className="min-h-8 px-3 py-1.5" data-dashboard-action="compare" data-dashboard-id={row.id} onClick={() => onCompare?.(row.id)}>
          Compare
        </Button>
      </div>
    </article>
  );
}

function DemoSamples({ samples = [], selectedId = "", apiBase = "", canSelect = true, onSelect }) {
  if (!samples.length) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-300 bg-white/80 p-6 text-sm font-semibold text-slate-500">
        No bundled samples found.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
      {samples.map((sample) => {
        const active = sample.id === selectedId;
        return (
          <article
            key={sample.id}
            className={[
              "group relative flex min-h-[270px] w-full flex-col overflow-hidden rounded-2xl border-2 bg-white text-left shadow-sm shadow-slate-950/5 transition-all duration-200 ease-in-out hover:-translate-y-1 hover:border-sky-300 hover:shadow-lg hover:shadow-sky-900/10 focus-within:ring-4 focus-within:ring-sky-500/15",
              active ? "border-blue-500 bg-gradient-to-br from-white to-blue-50 shadow-lg shadow-blue-200/70 ring-4 ring-blue-50" : "border-slate-200/80",
              !canSelect ? "opacity-70" : "",
            ].join(" ")}
          >
            <button
              type="button"
              data-demo-sample-id={sample.id}
              onClick={() => onSelect?.(sample.id)}
              disabled={!canSelect}
              aria-pressed={active}
              className="flex min-h-[270px] w-full cursor-pointer flex-col overflow-hidden rounded-[inherit] text-left outline-none disabled:cursor-not-allowed"
            >
              <span className="block aspect-[16/10] overflow-hidden border-b border-slate-200 bg-slate-100">
                <img className="h-full w-full object-cover transition duration-300 ease-in-out group-hover:scale-[1.04]" src={`${apiBase}${sample.image_url || ""}`} alt="" loading="lazy" />
              </span>
              <span className="flex flex-1 flex-col gap-3 p-3">
                <span className="flex flex-wrap items-center gap-1.5" aria-label={sample.route_label}>
                  <ProviderBadge provider={sample.source_provider} compact />
                  <RouteArrow />
                  <ProviderBadge provider={sample.target_provider} compact />
                </span>
                <span>
                  <strong className="block text-[15px] font-semibold leading-snug text-slate-950">{sample.title}</strong>
                  <span className="mt-1 block text-xs font-semibold leading-5 text-sky-700">{sample.pattern_label}</span>
                </span>
              </span>
            </button>
            <a
              className="absolute right-3 top-3 z-20 inline-flex h-10 w-10 items-center justify-center rounded-full border border-white/80 bg-slate-950/85 text-white opacity-0 shadow-lg shadow-slate-950/25 backdrop-blur transition-all duration-200 hover:scale-105 hover:bg-blue-600 focus:opacity-100 focus:outline-none focus:ring-4 focus:ring-blue-500/25 group-hover:opacity-100"
              href={`${apiBase}${sample.image_url || ""}`}
              target="_blank"
              rel="noopener"
              aria-label={`Open ${sample.title} sample image in a new tab`}
              title="Open image"
            >
              <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3M3 16v3a2 2 0 0 0 2 2h3m8 0h3a2 2 0 0 0 2-2v-3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M9 15 15 9m-5.5 0H15v5.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </a>
            {active ? (
              <span className="absolute left-3 top-3 z-10 rounded-full border border-blue-200 bg-white px-2.5 py-1 text-[11px] font-bold uppercase text-blue-700 shadow-sm shadow-blue-900/10">
                Selected
              </span>
            ) : null}
          </article>
        );
      })}
    </div>
  );
}

function Dashboard({
  current,
  kpis = [],
  rows = [],
  session = null,
  onOpen,
  onCompare,
  onReview,
  onNavigate,
  onSignOut,
}) {
  return (
    <div className="mx-auto grid w-full max-w-[1500px] gap-7">
      <section className="flex flex-col gap-5 rounded-[2rem] border border-white/80 bg-white/90 p-6 shadow-lg shadow-slate-950/5 ring-1 ring-slate-200/60 backdrop-blur-xl transition-all duration-200 sm:flex-row sm:items-center sm:justify-between lg:p-7">
        <div className="flex min-w-0 items-center gap-4">
          <span className="grid h-14 w-14 shrink-0 place-items-center rounded-2xl bg-slate-950 shadow-xl shadow-sky-900/15 ring-1 ring-white/10">
            <img className="h-8 w-8" src="assets/cloudbridge-iq-mark.svg" alt="" />
          </span>
          <div className="min-w-0">
            <p className="m-0 text-[11px] font-black uppercase tracking-normal text-sky-700">CloudBridge IQ</p>
            <h3 className="m-0 text-2xl font-semibold leading-tight tracking-tight text-slate-950 md:text-3xl">Dashboard</h3>
            <span className="mt-1 block text-sm font-medium text-slate-500">Enterprise cloud migration assessment workspace</span>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          {session ? (
            <span className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3.5 py-2 text-xs font-semibold text-emerald-700 shadow-sm shadow-emerald-950/5">
              <span className="h-2 w-2 rounded-full bg-emerald-500 ring-4 ring-emerald-100" />
              {session.role} | {session.name}
            </span>
          ) : null}
          <Button data-dashboard-sign-out className="px-4" onClick={onSignOut}>
            Sign out
          </Button>
        </div>
      </section>

      <CurrentAssessmentCard current={current} />

      <section className="grid gap-6 rounded-[2rem] border border-white/80 bg-white/90 p-6 shadow-lg shadow-slate-950/5 ring-1 ring-slate-200/60 backdrop-blur-xl transition-all duration-200 lg:p-7">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="mb-1 text-[11px] font-black uppercase tracking-normal text-sky-700">Portfolio</p>
            <h3 className="m-0 text-2xl font-semibold tracking-tight text-slate-950">Recent Runs</h3>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button onClick={onNavigate}>Open report</Button>
            <Button variant="primary" onClick={onReview}>
              Review
            </Button>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {kpis.map((kpi, index) => (
            <StatCard key={kpi.label} index={index} {...kpi} />
          ))}
        </div>

        <div className="grid gap-3">
          <div className="flex flex-wrap items-center justify-between gap-2 border-t border-slate-100 pt-2">
            <strong className="text-sm font-semibold text-slate-950">History</strong>
            <span className="text-xs font-semibold text-slate-500">Status, reviewer, target cloud, readiness, and quick actions</span>
          </div>
          {rows.length ? (
            rows.map((row) => <AssessmentRow key={row.id} row={row} onOpen={onOpen} onCompare={onCompare} />)
          ) : (
            <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50/80 p-8 text-center shadow-inner shadow-white">
              <strong className="block text-sm font-semibold text-slate-950">No reports yet.</strong>
              <span className="mt-1 block text-sm font-medium text-slate-500">Run an assessment to populate the report dashboard.</span>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

function renderWithRoot(container, element) {
  if (!container) return;
  let root = roots.get(container);
  if (!root) {
    root = createRoot(container);
    roots.set(container, root);
  }
  root.render(element);
}

window.CloudBridgeModernUI = {
  renderDemoSamples(container, props) {
    renderWithRoot(container, <DemoSamples {...props} />);
  },
  renderDashboard(container, props) {
    renderWithRoot(container, <Dashboard {...props} />);
  },
};

window.dispatchEvent(new Event("cloudbridge-modern-ui-ready"));
