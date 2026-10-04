import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, ArrowRight, Check, LockKeyhole } from "lucide-react";
import {
  fields,
  groups,
  toProfile,
  type FormValues,
} from "../constants/fields";
import { predict } from "../api/client";
import type { HealthProfile, PredictionResponse } from "../api/types";
import {
  Disclaimer,
  ErrorCard,
  FieldInput,
  ProfileSummary,
} from "../components/Common";
export default function Assessment({
  form,
  setForm,
  onResult,
}: {
  form: FormValues;
  setForm: (f: FormValues) => void;
  onResult: (p: HealthProfile, r: PredictionResponse) => void;
}) {
  const [step, setStep] = useState(0),
    [error, setError] = useState(""),
    [loading, setLoading] = useState(false);
  const heading = useRef<HTMLHeadingElement>(null);
  const navigate = useNavigate();
  const mounted = useRef(true);
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);
  function move(n: number) {
    try {
      toProfile(form);
      setError("");
      setStep(n);
      setTimeout(() => heading.current?.focus(), 0);
    } catch (e) {
      setError((e as Error).message);
    }
  }
  async function submit() {
    setError("");
    setLoading(true);
    try {
      const profile = toProfile(form);
      const result = await predict({
        profile,
        threshold_profile: "research_balanced",
      });
      if (!mounted.current) return;
      onResult(profile, result);
      navigate("/results");
    } catch (e) {
      if (mounted.current) setError((e as Error).message);
    } finally {
      if (mounted.current) setLoading(false);
    }
  }
  let profile: HealthProfile | undefined;
  try {
    profile = toProfile(form);
  } catch {}
  return (
    <main className="container page">
      <header className="page-heading">
        <span className="eyebrow">YOUR PROFILE, YOUR PACE</span>
        <h1>Health profile assessment</h1>
        <p>
          A few questions. A research perspective. You can select Unknown for
          any input.
        </p>
      </header>
      <div className="assessment-layout">
        <aside className="wizard-sidebar">
          <ol className="steps">
            {[...groups.map((g) => g.title), "Review"].map((title, i) => (
              <li
                key={title}
                className={i === step ? "active" : i < step ? "complete" : ""}
                aria-current={i === step ? "step" : undefined}
              >
                <span>{i < step ? <Check size={16} /> : i + 1}</span>
                <div>
                  <strong>{title}</strong>
                  <small>
                    {
                      [
                        "The essentials",
                        "Health & habits",
                        "Reported conditions",
                        "Check your answers",
                      ][i]
                    }
                  </small>
                </div>
              </li>
            ))}
          </ol>
          <div className="privacy-note">
            <LockKeyhole size={18} />
            <p>
              Assessment state stays in this browser’s memory. No patient
              database or account.
            </p>
          </div>
        </aside>
        <section className="card wizard-card">
          <span className="eyebrow">STEP {step + 1} OF 4</span>
          <h2 ref={heading} tabIndex={-1}>
            {step < 3 ? groups[step].title : "Review your profile"}
          </h2>
          <p>
            {step < 3
              ? groups[step].description
              : "Check the values below before sending them to the research model."}
          </p>
          <fieldset disabled={loading}>
            {step < 3 ? (
              <div className="form-grid">
                {groups[step].fields.map((name) => (
                  <FieldInput
                    key={name}
                    field={fields.find((f) => f.name === name)!}
                    value={form[name]}
                    onChange={(value) => {
                      setForm({ ...form, [name]: value });
                      setError("");
                    }}
                  />
                ))}
              </div>
            ) : (
              profile && <ProfileSummary profile={profile} edit={move} />
            )}
          </fieldset>
          {error && (
            <ErrorCard
              message={error}
              retry={step === 3 ? submit : undefined}
            />
          )}
          <div className="wizard-actions">
            <button
              className="button secondary"
              disabled={step === 0 || loading}
              onClick={() => move(step - 1)}
            >
              <ArrowLeft size={17} /> Back
            </button>
            <span>
              {step < 3
                ? "Unknown answers are welcome"
                : "Default research operating point"}
            </span>
            {step < 3 ? (
              <button className="button" onClick={() => move(step + 1)}>
                Continue <ArrowRight size={17} />
              </button>
            ) : (
              <button className="button" disabled={loading} onClick={submit}>
                {loading ? (
                  <>
                    <span className="spinner" /> Analyzing profile…
                  </>
                ) : (
                  "Analyze Profile"
                )}
              </button>
            )}
          </div>
        </section>
      </div>
      <Disclaimer />
    </main>
  );
}
