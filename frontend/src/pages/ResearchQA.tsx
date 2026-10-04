import { useEffect, useRef, useState } from "react";
import { Activity, Download, Copy, RefreshCw } from "lucide-react";
import { getHealth, getReady, getInfo, predict } from "../api/client";
import {
  policies,
  type ThresholdProfile,
  type PredictionResponse,
  type HealthProfile,
} from "../api/types";
import {
  fields,
  presets,
  toForm,
  toProfile,
  type FormValues,
} from "../constants/fields";
import {
  FieldInput,
  ScoreCard,
  TechnicalDetails,
  ErrorCard,
  classificationLabel,
  Disclaimer,
} from "../components/Common";
interface Run {
  profile: HealthProfile;
  result: PredictionResponse;
}
export default function ResearchQA({
  notify,
}: {
  notify: (s: string) => void;
}) {
  const [form, setForm] = useState<FormValues>(toForm(presets[0].profile)),
    [policy, setPolicy] = useState<ThresholdProfile>("research_balanced"),
    [status, setStatus] = useState("Checking model status…"),
    [version, setVersion] = useState("Checking…"),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [run, setRun] = useState<Run>(),
    [baseline, setBaseline] = useState<Run>(),
    [records, setRecords] = useState<Run[]>([]);
  const revision = useRef(0);
  const [apiOnline, setApiOnline] = useState(false),
    [modelReady, setModelReady] = useState(false);
  async function check() {
    setStatus("Checking model status…");
    setVersion("Checking…");
    const results = await Promise.allSettled([
      getHealth(),
      getReady(),
      getInfo(),
    ]);
    setApiOnline(results[0].status === "fulfilled");
    setModelReady(results[1].status === "fulfilled");
    setStatus(
      results[0].status === "fulfilled" ? "Status checked" : "API unavailable",
    );
    if (results[2].status === "fulfilled")
      setVersion(results[2].value.model_version);
    else setVersion("Unavailable");
  }
  useEffect(() => {
    void check();
    return () => {
      revision.current++;
    };
  }, []);
  function change(next: FormValues) {
    revision.current++;
    setForm(next);
    setRun(undefined);
    setError("");
  }
  function changePolicy(p: ThresholdProfile) {
    revision.current++;
    setPolicy(p);
    setRun(undefined);
    setBaseline(undefined);
  }
  async function analyze() {
    setBusy(true);
    setError("");
    const rev = revision.current;
    try {
      const profile = toProfile(form);
      const result = await predict({ profile, threshold_profile: policy });
      if (rev !== revision.current) return;
      const next = { profile, result };
      setRun(next);
      setRecords((prev) => [...prev, next]);
    } catch (e) {
      if (rev === revision.current) {
        setError((e as Error).message);
        notify("QA request needs attention.");
      }
    } finally {
      setBusy(false);
    }
  }
  function exportResults() {
    const rows = records.map((r, i) => ({
      test_id: `REACT-${i + 1}`,
      profile: r.profile,
      ...r.result,
    }));
    const blob = new Blob([JSON.stringify(rows, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "synthetic_manual_qa.json";
    a.click();
    URL.revokeObjectURL(url);
    notify("QA results exported locally.");
  }
  const changed =
    baseline && run
      ? fields.filter((f) => baseline.profile[f.name] !== run.profile[f.name])
      : [];
  return (
    <main className="container page">
      <header className="page-heading row">
        <div>
          <span className="eyebrow">RESEARCH WORKSPACE</span>
          <h1>Explore. Compare. Verify.</h1>
          <p>Synthetic profile testing for researchers and developers.</p>
        </div>
        <button className="button secondary" onClick={check}>
          <RefreshCw size={17} /> Check API status
        </button>
      </header>
      <div className="status-strip" role="status">
        <span className={`badge ${!apiOnline ? "neutral" : ""}`}>
          <Activity size={15} />
          {apiOnline ? "API Online" : "API unavailable"}
        </span>
        <span className={`badge ${!modelReady ? "neutral" : ""}`}>
          {modelReady ? "Model Ready" : "Model unavailable"}
        </span>
        <span>
          Model version <strong>{version}</strong>
        </span>
        <small>{status}</small>
      </div>
      <div className="qa-layout">
        <div>
          <section className="card">
            <span className="eyebrow">SYNTHETIC STARTING POINTS</span>
            <h2>Choose a profile</h2>
            <div className="preset-grid">
              {presets.map((p) => (
                <button
                  className="preset"
                  key={p.name}
                  disabled={busy}
                  onClick={() => {
                    change(toForm(p.profile));
                    notify("Synthetic profile loaded.");
                  }}
                >
                  {p.name}
                </button>
              ))}
            </div>
            <label className="policy-label" htmlFor="threshold">
              Research threshold policy
            </label>
            <select
              id="threshold"
              value={policy}
              disabled={busy}
              onChange={(e) => changePolicy(e.target.value as ThresholdProfile)}
            >
              {policies.map((p) => (
                <option key={p}>{p}</option>
              ))}
            </select>
            <p className="callout">
              Changing threshold changes the classification boundary, not the
              model score. Research operating points are not clinical cutoffs.
            </p>
            <details className="qa-inputs">
              <summary>Edit profile inputs · 14 fields</summary>
              <fieldset disabled={busy}>
                <div className="form-grid">
                  {fields.map((f) => (
                    <FieldInput
                      key={f.name}
                      field={f}
                      value={form[f.name]}
                      onChange={(value) => change({ ...form, [f.name]: value })}
                    />
                  ))}
                </div>
              </fieldset>
            </details>
            {error && <ErrorCard message={error} retry={analyze} />}
            <div className="actions">
              <button className="button" disabled={busy} onClick={analyze}>
                {busy ? (
                  <>
                    <span className="spinner" /> Analyzing profile…
                  </>
                ) : (
                  "Analyze synthetic profile"
                )}
              </button>
              <button
                className="text-button"
                disabled={busy}
                onClick={() => {
                  change(toForm(presets[0].profile));
                  setBaseline(undefined);
                  setRecords([]);
                  notify("QA workspace reset.");
                }}
              >
                Reset
              </button>
            </div>
          </section>
          <section className="card supplied">
            <span className="eyebrow">ONE-FEATURE EXPLORATION</span>
            <h2>Profile A vs Profile B</h2>
            <p>
              Analyze A, duplicate it, then change one input and analyze B.
              Multiple changes are listed explicitly.
            </p>
            <button
              className="button secondary"
              disabled={!run || busy}
              onClick={() => {
                if (run) {
                  setBaseline(structuredClone(run));
                  change(toForm(run.profile));
                  notify("Profile A captured. Edit one field for Profile B.");
                }
              }}
            >
              <Copy size={17} /> Duplicate result as Profile A
            </button>
            {baseline && (
              <p>
                Profile A:{" "}
                <strong>
                  {(baseline.result.profile_score * 100).toFixed(1)}%
                </strong>{" "}
                · {classificationLabel(baseline.result)}
              </p>
            )}
            {baseline && run && (
              <div className="comparison" data-testid="comparison">
                <p>
                  Profile B:{" "}
                  <strong>
                    {(run.result.profile_score * 100).toFixed(1)}%
                  </strong>{" "}
                  · {classificationLabel(run.result)}
                </p>
                <h3>Model response difference</h3>
                <strong>
                  {(
                    (run.result.profile_score - baseline.result.profile_score) *
                    100
                  ).toFixed(4)}{" "}
                  percentage points
                </strong>
                <p>
                  Changed fields:{" "}
                  {changed.map((f) => f.label).join(", ") || "None"}
                </p>
                <small>
                  This is a model response difference, not a causal effect.
                </small>
              </div>
            )}
          </section>
        </div>
        <div>
          {run ? (
            <ScoreCard result={run.result} />
          ) : (
            <section className="card empty-result">
              <Activity size={38} />
              <h2>A space for your findings</h2>
              <p>
                Analyze a synthetic profile to see its actual model response
                here.
              </p>
            </section>
          )}
          <section className="card supplied">
            <h3>Local QA record</h3>
            <p>
              {records.length} successful requests in this session. Export is
              manual; nothing is uploaded.
            </p>
            <button
              className="button secondary"
              disabled={!records.length}
              onClick={exportResults}
            >
              <Download size={17} /> Export JSON
            </button>
          </section>
          {run && (
            <TechnicalDetails
              request={{
                profile: run.profile,
                threshold_profile: run.result.threshold_profile,
              }}
              response={run.result}
              notify={notify}
            />
          )}
        </div>
      </div>
      <Disclaimer />
    </main>
  );
}
