import { useEffect, useState } from "react";
import { getInfo } from "../api/client";
import type { ModelInfo as Info } from "../api/types";
import { fields } from "../constants/fields";
import { Disclaimer, ErrorCard } from "../components/Common";
export default function ModelInfo() {
  const [info, setInfo] = useState<Info>(),
    [error, setError] = useState(""),
    [loading, setLoading] = useState(true);
  async function load() {
    setLoading(true);
    setError("");
    try {
      setInfo(await getInfo());
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    void load();
  }, []);
  return (
    <main className="container page">
      <header className="page-heading">
        <span className="eyebrow">TRANSPARENT BY DESIGN</span>
        <h1>Behind the profile score</h1>
        <p>The data, decisions, and boundaries of a research model.</p>
      </header>
      {loading && <p role="status">Checking model information…</p>}
      {error && <ErrorCard message={error} retry={load} />}
      <div className="two-grid">
        <section className="card">
          <span className="eyebrow">THE DATASET</span>
          <h2>A population survey, a research lens.</h2>
          <p>
            CDC BRFSS 2021 contains self-reported health and lifestyle
            information. More than 434,000 cleaned adult survey profiles formed
            the supervised dataset.
          </p>
          <p>
            The target is existing self-reported coronary heart disease /
            myocardial infarction (CHD/MI), not a future event.
          </p>
          <a
            className="text-button"
            href="https://www.cdc.gov/brfss/annual_data/annual_2021.html"
            target="_blank"
            rel="noreferrer"
          >
            CDC BRFSS 2021 documentation ↗
          </a>
        </section>
        <section className="card">
          <span className="eyebrow">THE MODEL</span>
          <h2>CatBoost, frozen at v1.0.0.</h2>
          <p>
            Selected through existing training, comparison, and validation.
            Inference uses the same saved pipeline and feature mappings.
          </p>
          <div className="model-meta">
            <div>
              <small>Live API version</small>
              <strong>{info?.model_version ?? "Unavailable"}</strong>
            </div>
            <div>
              <small>Live API input count</small>
              <strong>{info?.feature_count ?? "Unavailable"}</strong>
            </div>
          </div>
          <p>
            No retraining or recalibration is performed by this application.
          </p>
        </section>
      </div>
      <section className="card supplied">
        <span className="eyebrow">INDEPENDENT TEST SET</span>
        <h2>Research evaluation</h2>
        <p>
          Positive CHD/MI reports are a minority. ROC-AUC alone does not show
          how many positive predictions are correct; precision and recall
          provide essential context.
        </p>
        <div className="metric-grid">
          {[
            ["ROC-AUC", 0.8468],
            ["PR-AUC", 0.3448],
            ["Precision", 0.3168],
            ["Recall", 0.5155],
            ["Specificity", 0.9015],
            ["F1", 0.3924],
          ].map(([label, value]) => (
            <div key={label}>
              <div className="row">
                <span>{label}</span>
                <strong>{Number(value).toFixed(4)}</strong>
              </div>
              <div className="metric-track">
                <span style={{ width: `${Number(value) * 100}%` }} />
              </div>
            </div>
          ))}
        </div>
        <small>
          Fixed independent-test evaluation. Precision, recall, specificity and
          F1 use research_balanced.
        </small>
      </section>
      <div className="two-grid">
        <section className="card">
          <h2>14 inputs. Exact survey meanings.</h2>
          <div className="feature-chips">
            {fields.map((f) => (
              <span key={f.name}>{f.label}</span>
            ))}
          </div>
          <p>
            Unknown categories use the saved missing category; unknown BMI uses
            the saved training median. Education and income are excluded.
          </p>
        </section>
        <section className="card">
          <h2>Thresholds are operating points.</h2>
          <p>
            The default research_balanced policy maximizes validation F1. Other
            saved policies trade false negatives against false positives,
            affecting recall and precision.
          </p>
          <p>
            These are research operating points, not clinical cutoffs. The QA
            workspace lets you compare them without changing the model score.
          </p>
        </section>
      </div>
      <section className="card supplied">
        <h2>Limitations that matter</h2>
        <ul>
          {(
            info?.limitations_summary ?? [
              "Cross-sectional self-report does not establish future risk or causation.",
              "Independent-test recall is 51.55% and precision is 31.68% at the default threshold.",
              "Subgroup performance varies and external validation is still required.",
            ]
          ).map((s) => (
            <li key={s}>{s}</li>
          ))}
        </ul>
      </section>
      <Disclaimer />
    </main>
  );
}
