import React, { useMemo, useRef, useState } from "react";
import { Badge, Button, Card, CardContent, CardHeader, Input } from "./components/ui";
import { FileUp, Sparkles, ShieldCheck, Loader2, Download, X, CheckCircle2, AlertTriangle, Search } from "lucide-react";

type ClauseResult = {
  clause_type: string;
  found: boolean;
  summary?: string;
  risk_level?: string;
  issues?: string[];
  recommendations?: string[];
  suggested_redline?: string;
  source_text?: string;
  confidence?: number;
};

type AnalyzeResponse = {
  filename: string;
  results: ClauseResult[];
  report_pdf_base64?: string;
};

const API_BASE_DEFAULT = "http://localhost:8000";
const KEY_STORAGE = "contract_api_key";
const BASE_STORAGE = "contract_api_base";

function riskTone(risk?: string) {
  const r = (risk ?? "").toLowerCase();
  if (r.includes("high")) return "red" as const;
  if (r.includes("medium")) return "yellow" as const;
  if (r.includes("low")) return "green" as const;
  return "gray" as const;
}

function foundTone(found: boolean) {
  return found ? ("green" as const) : ("red" as const);
}

export default function App() {
  const fileRef = useRef<HTMLInputElement | null>(null);
  const [apiBase, setApiBase] = useState(localStorage.getItem(BASE_STORAGE) || API_BASE_DEFAULT);
  const [apiKey, setApiKey] = useState(localStorage.getItem(KEY_STORAGE) || "");
  const [rebuild, setRebuild] = useState(true);
  const [redline, setRedline] = useState(false);

  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<AnalyzeResponse | null>(null);

  const [query, setQuery] = useState("");
  const filtered = useMemo(() => {
    if (!data?.results) return [];
    const q = query.trim().toLowerCase();
    if (!q) return data.results;
    return data.results.filter(r =>
      (r.clause_type || "").toLowerCase().includes(q) ||
      (r.summary || "").toLowerCase().includes(q) ||
      (r.source_text || "").toLowerCase().includes(q)
    );
  }, [data, query]);

  async function callApi(path: string, makeReport: boolean) {
    if (!file) return;
    setBusy(true);
    setError(null);
    setData(null);

    localStorage.setItem(KEY_STORAGE, apiKey);
    localStorage.setItem(BASE_STORAGE, apiBase);

    try {
      const form = new FormData();
      form.append("file", file);

      const url = new URL(apiBase.replace(/\/$/, "") + path);
      url.searchParams.set("rebuild", String(rebuild));
      url.searchParams.set("redline", String(redline));

      const res = await fetch(url.toString(), {
        method: "POST",
        headers: { "X-API-Key": apiKey },
        body: form,
      });

      const json = await res.json().catch(() => null);
      if (!res.ok) {
        const msg = json?.detail || json?.message || `Request failed (${res.status})`;
        throw new Error(msg);
      }

      setData(json as AnalyzeResponse);

      if (makeReport && (json as AnalyzeResponse).report_pdf_base64) {
        downloadReport((json as AnalyzeResponse).report_pdf_base64!, (json as AnalyzeResponse).filename);
      }
    } catch (e: any) {
      setError(e?.message ?? "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  function downloadReport(b64: string, filename: string) {
    const bytes = atob(b64);
    const arr = new Uint8Array(bytes.length);
    for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i);
    const blob = new Blob([arr], { type: "application/pdf" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename.replace(/\.pdf$/i, "") + "_analysis_report.pdf";
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }

  function onPickFile(f: File | null) {
    setFile(f);
    setData(null);
    setError(null);
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="absolute inset-0 bg-grid opacity-60" />
      <div className="absolute inset-0 bg-gradient-to-b from-white/5 via-transparent to-transparent" />
      <div className="relative mx-auto max-w-6xl px-4 py-10">
        <header className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/70">
              <ShieldCheck className="h-4 w-4" />
              Secure local API • PDF → clauses • RAG + LLM
            </div>
            <h1 className="text-3xl md:text-4xl font-bold tracking-tight">
              Contract Analyzer <span className="text-white/60">Studio</span>
            </h1>
            <p className="text-white/60 max-w-2xl">
              Upload a contract PDF, run clause detection + risk analysis, and export a polished report.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="secondary" onClick={() => fileRef.current?.click()}>
              <FileUp className="h-4 w-4" />
              Choose PDF
            </Button>
            <input
              ref={fileRef}
              type="file"
              accept="application/pdf"
              className="hidden"
              onChange={(e) => onPickFile(e.target.files?.[0] ?? null)}
            />
            {file && (
              <Button variant="ghost" onClick={() => onPickFile(null)}>
                <X className="h-4 w-4" />
                Clear
              </Button>
            )}
          </div>
        </header>

        <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-12">
          <div className="md:col-span-5 space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="font-semibold">Connection</div>
                  <Badge tone="gray">Local</Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="text-sm text-white/70">API Base URL</div>
                  <Input value={apiBase} onChange={(e) => setApiBase(e.target.value)} placeholder="http://localhost:8000" />
                </div>
                <div className="space-y-2">
                  <div className="text-sm text-white/70">API Key</div>
                  <Input value={apiKey} onChange={(e) => setApiKey(e.target.value)} placeholder="X-API-Key" />
                  <div className="text-xs text-white/40">Local dev only: browser-stored key is OK.</div>
                </div>

                <div className="flex flex-wrap gap-2 pt-2">
                  <Button variant="primary" disabled={!file || !apiKey || busy} onClick={() => callApi("/analyze", false)}>
                    {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                    Analyze
                  </Button>
                  <Button variant="secondary" disabled={!file || !apiKey || busy} onClick={() => callApi("/report", true)}>
                    {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
                    Analyze + Report
                  </Button>
                </div>

                <div className="mt-4 grid grid-cols-2 gap-2">
                  <label className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm">
                    <input type="checkbox" checked={rebuild} onChange={(e) => setRebuild(e.target.checked)} />
                    Rebuild index
                  </label>
                  <label className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm">
                    <input type="checkbox" checked={redline} onChange={(e) => setRedline(e.target.checked)} />
                    Include redlines
                  </label>
                </div>

                <div className="rounded-xl border border-white/10 bg-black/20 p-3">
                  <div className="text-xs text-white/60">Selected file</div>
                  <div className="mt-1 text-sm font-medium">{file ? file.name : <span className="text-white/40">None</span>}</div>
                </div>

                {error && (
                  <div className="rounded-xl border border-rose-500/20 bg-rose-500/10 p-3 text-sm text-rose-100">
                    <div className="flex items-center gap-2 font-semibold">
                      <AlertTriangle className="h-4 w-4" />
                      Error
                    </div>
                    <div className="mt-1 text-rose-100/90">{error}</div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="font-semibold">Quick checklist</div>
                  <Badge tone="gray">No surprises</Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3 text-sm text-white/70">
                <div>• Start Ollama and pull your model (default: <span className="text-white">llama3.2</span>).</div>
                <div>• Keep <span className="text-white">Rebuild index</span> enabled per upload.</div>
                <div>• Use <span className="text-white">Analyze + Report</span> to download a PDF summary.</div>
              </CardContent>
            </Card>
          </div>

          <div className="md:col-span-7 space-y-6">
            <Card>
              <CardHeader>
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="font-semibold">Results</div>
                  <div className="flex items-center gap-2 w-full max-w-sm">
                    <div className="relative w-full">
                      <Search className="absolute left-3 top-2.5 h-4 w-4 text-white/40" />
                      <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search clause type, summary, text…" className="pl-9" />
                    </div>
                    {data?.results?.length ? <Badge tone="gray">{filtered.length}/{data.results.length}</Badge> : <Badge tone="gray">0</Badge>}
                  </div>
                </div>
              </CardHeader>

              <CardContent>
                {!data && (
                  <div className="rounded-2xl border border-white/10 bg-white/5 p-8 text-center">
                    <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-black/30">
                      <Sparkles className="h-5 w-5" />
                    </div>
                    <div className="text-base font-semibold">Ready when you are</div>
                    <div className="mt-1 text-sm text-white/60">Choose a PDF and click Analyze.</div>
                  </div>
                )}

                {data && (
                  <div className="space-y-3">
                    {filtered.map((r, idx) => (
                      <div key={idx} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <div className="text-sm font-semibold">{r.clause_type}</div>
                          <div className="flex items-center gap-2">
                            <Badge tone={foundTone(!!r.found)}>
                              {r.found ? (
                                <span className="inline-flex items-center gap-1"><CheckCircle2 className="h-3.5 w-3.5" /> Found</span>
                              ) : "Not found"}
                            </Badge>
                            <Badge tone={riskTone(r.risk_level)}>{r.risk_level ?? "Unknown risk"}</Badge>
                          </div>
                        </div>

                        {r.summary && <div className="mt-3 text-sm text-white/70 whitespace-pre-wrap">{r.summary}</div>}

                        {(r.issues?.length || r.recommendations?.length) && (
                          <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-2">
                            {r.issues?.length ? (
                              <div className="rounded-xl border border-white/10 bg-black/20 p-3">
                                <div className="text-xs font-semibold text-white/60">Issues</div>
                                <ul className="mt-2 list-disc pl-5 text-sm text-white/70 space-y-1">
                                  {r.issues.map((it, i) => <li key={i}>{it}</li>)}
                                </ul>
                              </div>
                            ) : null}
                            {r.recommendations?.length ? (
                              <div className="rounded-xl border border-white/10 bg-black/20 p-3">
                                <div className="text-xs font-semibold text-white/60">Recommendations</div>
                                <ul className="mt-2 list-disc pl-5 text-sm text-white/70 space-y-1">
                                  {r.recommendations.map((it, i) => <li key={i}>{it}</li>)}
                                </ul>
                              </div>
                            ) : null}
                          </div>
                        )}

                        {r.suggested_redline && (
                          <div className="mt-3 rounded-xl border border-white/10 bg-black/20 p-3">
                            <div className="text-xs font-semibold text-white/60">Suggested redline</div>
                            <pre className="mt-2 whitespace-pre-wrap text-sm text-white/70">{r.suggested_redline}</pre>
                          </div>
                        )}

                        {r.source_text && (
                          <details className="mt-3">
                            <summary className="cursor-pointer text-sm text-white/60 hover:text-white">Show source text</summary>
                            <div className="mt-2 rounded-xl border border-white/10 bg-black/20 p-3 text-sm text-white/70 whitespace-pre-wrap">{r.source_text}</div>
                          </details>
                        )}
                      </div>
                    ))}

                    {!filtered.length && (
                      <div className="rounded-xl border border-white/10 bg-black/20 p-6 text-sm text-white/60 text-center">
                        No matches. Try a different search.
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        <footer className="mt-10 text-center text-xs text-white/40">
          Built for local use. For deployment, move auth server-side and lock down CORS.
        </footer>
      </div>
    </div>
  );
}
