import { Component, type ReactNode } from "react";
import { AlertCircle, Copy, ShieldCheck } from "lucide-react";
import {
  fields,
  groups,
  answer,
  type FormValues,
  type Field,
} from "../constants/fields";
import type { HealthProfile, PredictionResponse } from "../api/types";
export class ErrorBoundary extends Component<
  { children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? (
      <main className="container">
        <ErrorCard
          message="This view could not be displayed. Reload to recover."
          retry={() => location.reload()}
        />
      </main>
    ) : (
      this.props.children
    );
  }
}
export function Disclaimer() {
  return (
    <aside className="disclaimer">
      <ShieldCheck size={21} />
      <p>
        <strong>Built for research. Interpreted with care.</strong> This score
        reflects patterns associated with existing self-reported CHD/MI in BRFSS
        2021. It is not a diagnosis or future cardiovascular-risk estimate.
      </p>
    </aside>
  );
}
export function ErrorCard({
  message,
  retry,
}: {
  message: string;
  retry?: () => void;
}) {
  return (
    <div className="error" role="alert">
      <AlertCircle />
      <div>
        <strong>Something needs attention</strong>
        <p>{message}</p>
        {retry && (
          <button className="button secondary" onClick={retry}>
            Try again
          </button>
        )}
      </div>
    </div>
  );
}
export function FieldInput({
  field,
  value,
  onChange,
}: {
  field: Field;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="field">
      <label htmlFor={field.name}>{field.label}</label>
      <p id={`${field.name}-question`}>{field.question}</p>
      {field.options ? (
        <select
          id={field.name}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          aria-describedby={`${field.name}-question ${field.name}-help`}
        >
          <option value="">Unknown</option>
          {field.options.map(([n, s]) => (
            <option key={n} value={n}>
              {s}
            </option>
          ))}
        </select>
      ) : (
        <>
          <input
            id={field.name}
            inputMode="decimal"
            value={value}
            placeholder="Unknown · e.g. 28.5"
            onChange={(e) => onChange(e.target.value)}
            aria-describedby={`${field.name}-help`}
          />
          <button
            className="text-button"
            type="button"
            onClick={() => onChange("")}
          >
            Set BMI to Unknown
          </button>
        </>
      )}
      {field.help && <small id={`${field.name}-help`}>{field.help}</small>}
    </div>
  );
}
export function ProfileSummary({
  profile,
  edit,
}: {
  profile: HealthProfile;
  edit?: (step: number) => void;
}) {
  return (
    <div className="summary-grid">
      {groups.map((g, i) => (
        <section key={g.title} className="summary-group">
          <div className="row">
            <h3>{g.title}</h3>
            {edit && (
              <button className="text-button" onClick={() => edit(i)}>
                Edit {g.title}
              </button>
            )}
          </div>
          <dl>
            {g.fields.map((name) => {
              const f = fields.find((f) => f.name === name)!;
              return (
                <div key={name}>
                  <dt>{f.label}</dt>
                  <dd>{answer(f, profile)}</dd>
                </div>
              );
            })}
          </dl>
        </section>
      ))}
    </div>
  );
}
export const classificationLabel = (r: PredictionResponse) =>
  r.classification === "elevated_model_association"
    ? "Elevated model association"
    : "Lower model association";
export function ScoreCard({ result }: { result: PredictionResponse }) {
  const percent = result.profile_score * 100;
  return (
    <section className="card score-card">
      <span className="eyebrow">PROFILE ANALYSIS</span>
      <div
        className="gauge"
        style={{
          background: `conic-gradient(var(--primary) ${percent * 3.6}deg,var(--border) 0deg)`,
        }}
      >
        <div>
          <strong>
            {percent.toFixed(1)}
            <span>%</span>
          </strong>
          <small>Model Profile Score</small>
        </div>
      </div>
      <span
        className={`badge ${result.classification === "elevated_model_association" ? "warning" : ""}`}
      >
        {classificationLabel(result)}
      </span>
      <p>
        Patterns in a research dataset, interpreted for this submitted profile.
      </p>
      <div className="metadata">
        <span>
          Threshold <strong>{(result.threshold * 100).toFixed(2)}%</strong>
        </span>
        <span>
          Model version <strong>{result.model_version}</strong>
        </span>
      </div>
    </section>
  );
}
export function TechnicalDetails({
  request,
  response,
  notify,
}: {
  request: unknown;
  response: unknown;
  notify: (s: string) => void;
}) {
  async function copy() {
    try {
      await navigator.clipboard.writeText(
        JSON.stringify({ request, response }, null, 2),
      );
      notify("Technical details copied.");
    } catch {
      notify("Copy unavailable. Select the JSON text instead.");
    }
  }
  return (
    <details className="card technical">
      <summary>Technical details</summary>
      <button className="text-button" onClick={copy}>
        <Copy size={15} /> Copy JSON
      </button>
      <h4>Request JSON</h4>
      <pre>{JSON.stringify(request, null, 2)}</pre>
      <h4>Response JSON</h4>
      <pre>{JSON.stringify(response, null, 2)}</pre>
    </details>
  );
}
