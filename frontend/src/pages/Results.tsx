import { Link } from "react-router-dom";
import type { HealthProfile, PredictionResponse } from "../api/types";
import {
  Disclaimer,
  ProfileSummary,
  ScoreCard,
  TechnicalDetails,
} from "../components/Common";
export default function Results({
  analysis,
  notify,
}: {
  analysis?: { profile: HealthProfile; result: PredictionResponse };
  notify: (s: string) => void;
}) {
  if (!analysis)
    return (
      <main className="container page">
        <h1>Your analysis will appear here</h1>
        <p>
          Complete an assessment to see the submitted profile and model
          response. Refresh clears in-memory health information.
        </p>
        <Link className="button" to="/assessment">
          Start Assessment
        </Link>
      </main>
    );
  const { profile, result } = analysis;
  return (
    <main className="container page">
      <header className="page-heading row">
        <div>
          <span className="eyebrow">RESEARCH OUTPUT</span>
          <h1>Profile Analysis</h1>
          <p>A closer look at the profile you submitted.</p>
        </div>
        <Link className="button secondary" to="/assessment">
          Edit assessment
        </Link>
      </header>
      <div className="result-layout">
        <ScoreCard result={result} />
        <section className="card interpretation">
          <span className="eyebrow">READING THE RESULT</span>
          <h2>Association, with context.</h2>
          <p>
            This score reflects how closely the submitted profile resembles
            patterns associated with existing self-reported CHD/MI in the BRFSS
            2021 dataset.
          </p>
          <p>It is not a diagnosis or future cardiovascular-risk estimate.</p>
          <div className="model-meta">
            <div>
              <small>Model</small>
              <strong>CatBoost</strong>
            </div>
            <div>
              <small>Version</small>
              <strong>{result.model_version}</strong>
            </div>
            <div>
              <small>Inputs</small>
              <strong>14</strong>
            </div>
            <div>
              <small>Threshold policy</small>
              <strong>{result.threshold_profile}</strong>
            </div>
          </div>
          <Link className="text-button" to="/model">
            Understand the model →
          </Link>
        </section>
      </div>
      <section className="card supplied">
        <span className="eyebrow">SENT TO THE API</span>
        <h2>Your supplied information</h2>
        <ProfileSummary profile={profile} />
      </section>
      <TechnicalDetails
        request={{ profile, threshold_profile: result.threshold_profile }}
        response={result}
        notify={notify}
      />
      <Disclaimer />
    </main>
  );
}
