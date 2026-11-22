"use client";

import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { Film, Loader2, Link2, ShieldCheck, RefreshCw, Download, ExternalLink } from "lucide-react";

type Clip = {
  title?: string;
  video_url?: string;
  download_url?: string;
  start?: number;
  end?: number;
};

type EngineStatus = {
  configured: boolean;
  reachable: boolean;
  mode?: string;
  message?: string;
  service?: string;
};

type JobStatus = {
  status: string;
  logs?: unknown[];
  clips?: Clip[];
  error?: string | null;
};

function readableError(error: unknown) {
  return error instanceof Error ? error.message : "Unexpected API error";
}

export default function OpenShortsPage() {
  const [engine, setEngine] = useState<EngineStatus | null>(null);
  const [sourceUrl, setSourceUrl] = useState("");
  const [rightsConfirmed, setRightsConfirmed] = useState(false);
  const [targetClips, setTargetClips] = useState("4");
  const [minimumSeconds, setMinimumSeconds] = useState(15);
  const [maximumSeconds, setMaximumSeconds] = useState(60);
  const [jobId, setJobId] = useState("");
  const [job, setJob] = useState<JobStatus | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("Checking the private OpenShorts connection...");

  const checkEngine = useCallback(async () => {
    try {
      const response = await apiFetch("/api/openshorts/status");
      const data = (await response.json()) as EngineStatus;
      setEngine(data);
      setMessage(data.reachable ? "OpenShorts is reachable." : data.message || "OpenShorts is not configured.");
    } catch (error) {
      setEngine(null);
      setMessage(readableError(error));
    }
  }, []);

  useEffect(() => {
    void checkEngine();
  }, [checkEngine]);

  const pollJob = useCallback(async (id: string) => {
    const response = await apiFetch(`/api/openshorts/jobs/${encodeURIComponent(id)}`);
    const data = (await response.json()) as JobStatus;
    setJob(data);
    if (["completed", "failed"].includes(data.status)) {
      setBusy(false);
      setMessage(data.status === "completed" ? "Clips are ready." : data.error || "OpenShorts processing failed.");
    } else {
      setMessage(`OpenShorts: ${data.status}. Processing runs on your configured private service.`);
    }
  }, []);

  useEffect(() => {
    if (!jobId || !busy) return;
    let active = true;
    const poll = async () => {
      if (!active) return;
      try {
        const response = await apiFetch(`/api/openshorts/jobs/${encodeURIComponent(jobId)}`);
        const data = (await response.json()) as JobStatus;
        if (!active) return;
        setJob(data);
        if (["completed", "failed"].includes(data.status)) {
          setBusy(false);
          setMessage(data.status === "completed" ? "Clips are ready." : data.error || "OpenShorts processing failed.");
        } else {
          setMessage(`OpenShorts: ${data.status}. Checking again in 30 seconds.`);
        }
      } catch (error) {
        if (active) setMessage(readableError(error));
      }
    };
    void poll();
    const timer = window.setInterval(() => void poll(), 30_000);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [jobId, busy]);

  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!engine?.reachable) {
      setMessage("Configure and test the private OpenShorts service first.");
      return;
    }
    if (!rightsConfirmed) {
      setMessage("Confirm that you own or have permission to process this video.");
      return;
    }
    setBusy(true);
    setJob(null);
    setJobId("");
    setMessage("Submitting video to your private OpenShorts service...");
    try {
      const payload = {
        url: sourceUrl.trim(),
        acknowledged: true,
        output_format: "vertical",
        clip_min_seconds: minimumSeconds,
        clip_max_seconds: maximumSeconds,
        ...(targetClips ? { target_clips: Number(targetClips) } : {}),
      };
      const response = await apiFetch("/api/openshorts/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = (await response.json()) as { job_id: string; status: string };
      setJobId(data.job_id);
      setMessage(`Job ${data.job_id} queued.`);
    } catch (error) {
      setBusy(false);
      setMessage(readableError(error));
    }
  };

  const terminal = job?.status === "completed" || job?.status === "failed";

  return (
    <main className="mx-auto flex min-h-[calc(100vh-6rem)] max-w-6xl flex-col gap-6 pb-16">
      <header>
        <div className="flex items-center gap-3">
          <Film className="h-8 w-8 text-[#66fcf1]" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white">OpenShorts AI</h1>
            <p className="mt-1 text-sm text-zinc-400">Turn long videos into vertical Shorts and Reels using your own self-hosted clip engine.</p>
          </div>
        </div>
      </header>

      <section className="glass-card flex flex-col gap-4 p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-bold uppercase tracking-widest text-white">Private engine connection</h2>
            <p className="mt-1 text-xs text-zinc-400">Hosted OpenShorts is blocked by default to prevent unexpected charges.</p>
          </div>
          <button onClick={() => void checkEngine()} className="flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-xs font-bold text-white hover:bg-white/10">
            <RefreshCw className="h-4 w-4" /> Test connection
          </button>
        </div>
        <div className="rounded-xl border border-white/10 bg-black/30 p-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-white">
            <span className={`h-2.5 w-2.5 rounded-full ${engine?.reachable ? "bg-emerald-400" : "bg-amber-400"}`} />
            {engine?.reachable ? "Connected" : engine?.configured ? "Configured, not reachable" : "Not configured"}
            {engine?.mode && <span className="text-xs font-normal text-zinc-500">· {engine.mode}</span>}
          </div>
          <p className="mt-2 break-words text-xs text-zinc-400">{message}</p>
        </div>
      </section>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
        <section className="glass-card p-6 lg:col-span-2">
          <h2 className="mb-5 text-sm font-bold uppercase tracking-widest text-white">Create vertical clips</h2>
          <form onSubmit={submit} className="space-y-5">
            <div>
              <label className="mb-2 block text-xs font-bold uppercase tracking-wider text-zinc-400">Public HTTPS video URL</label>
              <input value={sourceUrl} onChange={(event) => setSourceUrl(event.target.value)} type="url" required placeholder="https://www.youtube.com/watch?v=..." className="modern-input w-full" disabled={busy} />
            </div>
            <div>
              <label className="mb-2 block text-xs font-bold uppercase tracking-wider text-zinc-400">Target clips (optional)</label>
              <select value={targetClips} onChange={(event) => setTargetClips(event.target.value)} className="modern-input w-full" disabled={busy}>
                <option value="">Let OpenShorts decide</option>
                {[2, 3, 4, 5, 6, 8, 10].map((count) => <option value={count} key={count}>{count} clips</option>)}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="mb-2 block text-xs font-bold uppercase tracking-wider text-zinc-400">Min seconds</label>
                <input type="number" min={5} max={maximumSeconds - 5} value={minimumSeconds} onChange={(event) => setMinimumSeconds(Math.min(maximumSeconds - 5, Math.max(5, Number(event.target.value))))} className="modern-input w-full" disabled={busy} />
              </div>
              <div>
                <label className="mb-2 block text-xs font-bold uppercase tracking-wider text-zinc-400">Max seconds</label>
                <input type="number" min={minimumSeconds + 5} max={180} value={maximumSeconds} onChange={(event) => setMaximumSeconds(Math.min(180, Math.max(minimumSeconds + 5, Number(event.target.value))))} className="modern-input w-full" disabled={busy} />
              </div>
            </div>
            <label className="flex items-start gap-3 rounded-xl border border-white/10 bg-black/30 p-3 text-xs text-zinc-300">
              <input type="checkbox" checked={rightsConfirmed} onChange={(event) => setRightsConfirmed(event.target.checked)} className="mt-0.5 accent-[#66fcf1]" disabled={busy} />
              I own this video or have permission to process it.
            </label>
            <button type="submit" disabled={busy || !engine?.reachable} className="flex w-full items-center justify-center gap-2 rounded-xl bg-[#66fcf1] px-4 py-3 font-bold text-black transition hover:bg-[#45f3e5] disabled:cursor-not-allowed disabled:opacity-40">
              {busy ? <Loader2 className="h-5 w-5 animate-spin" /> : <Film className="h-5 w-5" />}
              {busy ? "Processing..." : "Generate Shorts"}
            </button>
          </form>
        </section>

        <section className="glass-card min-h-[420px] p-6 lg:col-span-3">
          <h2 className="mb-4 text-sm font-bold uppercase tracking-widest text-white">Job & results</h2>
          {jobId ? (
            <div className="mb-4 rounded-lg border border-white/10 bg-black/30 p-3 text-xs text-zinc-400">Job ID: <span className="font-mono text-white">{jobId}</span></div>
          ) : null}
          {job ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between gap-3 text-sm">
                <span className="font-semibold text-white">{job.status.toUpperCase()}</span>
                {terminal && <span className="text-xs text-zinc-400">Finished</span>}
              </div>
              {job.error && <p className="rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-300">{job.error}</p>}
              {!!job.clips?.length && <div className="space-y-3">
                {job.clips.map((clip, index) => {
                  const href = clip.download_url || clip.video_url;
                  return (
                    <div key={`${index}-${href || ""}`} className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/10 bg-black/30 p-4">
                      <div>
                        <p className="font-semibold text-white">{clip.title || `Clip ${index + 1}`}</p>
                        {typeof clip.start === "number" && typeof clip.end === "number" && <p className="mt-1 text-xs text-zinc-500">{Math.round(clip.start)}s – {Math.round(clip.end)}s</p>}
                      </div>
                      {href && <a href={href} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 rounded-lg bg-[#66fcf1] px-3 py-2 text-xs font-bold text-black"><Download className="h-4 w-4" /> Open / download <ExternalLink className="h-3 w-3" /></a>}
                    </div>
                  );
                })}
              </div>}
              {!!job.logs?.length && <details className="rounded-lg border border-white/10 p-3">
                <summary className="cursor-pointer text-xs font-semibold text-zinc-400">Processing log</summary>
                <pre className="mt-2 max-h-40 overflow-auto whitespace-pre-wrap text-[11px] text-zinc-500">{job.logs.map((item) => typeof item === "string" ? item : JSON.stringify(item)).join("\n")}</pre>
              </details>}
            </div>
          ) : (
            <div className="flex min-h-[300px] flex-col items-center justify-center gap-3 text-center text-zinc-500">
              <Link2 className="h-10 w-10 opacity-30" />
              <p className="max-w-sm text-sm">Submit a video URL to start a clipping job. Processing is asynchronous and results will appear here when ready.</p>
            </div>
          )}
        </section>
      </div>

      <footer className="flex items-start gap-3 rounded-xl border border-white/10 bg-black/20 p-4 text-xs text-zinc-500">
        <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-[#66fcf1]" />
        <p>Self-hosted OpenShorts is MIT-licensed. Video processing uses your own machine/server and local model resources. This MATANGI adapter does not publish to social accounts or enable paid hosted usage.</p>
      </footer>
    </main>
  );
}
