import { Link } from "react-router-dom";
import {
  ArrowUpRight,
  Activity,
  ClipboardList,
  ChartNoAxesCombined,
  ArrowRight,
  HeartPulse,
} from "lucide-react";
import { Disclaimer } from "../components/Common";
export default function Home() {
  return (
    <>
      <section className="hero container">
        <div className="hero-copy">
          <span className="pill">
            <span className="dot" /> RESEARCH, MADE EXPLORABLE
          </span>
          <h1>
            A clearer view of your <em>health profile.</em>
          </h1>
          <p>
            Understand cardiovascular health profiles through machine learning.
            Explore health and lifestyle indicators with a model trained on CDC
            BRFSS 2021 survey data.
          </p>
          <div className="actions">
            <Link className="button" to="/assessment">
              Start Assessment <ArrowUpRight size={19} />
            </Link>
            <Link className="button secondary" to="/model">
              Explore the Model <ArrowRight size={18} />
            </Link>
          </div>
          <div className="hero-note">
            <span>14 thoughtful inputs</span>
            <span>Research use only</span>
            <span>No account needed</span>
          </div>
        </div>
        <div
          className="hero-art"
          aria-label="Illustration of a research health profile"
        >
          <div className="art-grid" />
          <div className="floating-tag">
            <span className="icon-box">
              <HeartPulse />
            </span>
            <div>
              <strong>Cardiovascular profile</strong>
              <small>A research perspective</small>
            </div>
            <span className="tiny-dot" />
          </div>
          <div className="heart-orbit">
            <HeartPulse size={104} strokeWidth={1.3} />
          </div>
          <svg className="pulse-line" viewBox="0 0 460 100" aria-hidden="true">
            <path d="M0 55H95L110 42 127 65 150 12 171 88 192 55H250L265 39 281 66 302 55H460" />
          </svg>
          <div className="art-bottom">
            <span>
              <Activity size={18} /> Data-informed exploration
            </span>
            <strong>
              BRFSS <span>2021</span>
            </strong>
          </div>
        </div>
      </section>
      <section className="container stats-strip">
        {[
          ["434K+", "Cleaned survey profiles"],
          ["14", "Health & lifestyle inputs"],
          ["CatBoost", "Frozen research model"],
          ["0.8468", "Independent-test ROC-AUC"],
        ].map(([v, l]) => (
          <div key={l}>
            <strong>{v}</strong>
            <small>{l}</small>
          </div>
        ))}
      </section>
      <section className="container section">
        <div className="section-heading">
          <div>
            <span className="eyebrow">FROM INPUT TO INSIGHT</span>
            <h2>Thoughtful by design. Simple to explore.</h2>
          </div>
          <p>A guided experience, with the research context always in view.</p>
        </div>
        <div className="three-grid">
          {[
            [
              ClipboardList,
              "01",
              "Build your profile",
              "Enter health information in a short, guided assessment. Use Unknown whenever you need to.",
            ],
            [
              Activity,
              "02",
              "Let the model analyze",
              "Your inputs are sent to the existing, frozen CatBoost model through the research API.",
            ],
            [
              ChartNoAxesCombined,
              "03",
              "Explore the association",
              "Review the model association score alongside your inputs and its research limitations.",
            ],
          ].map(([Icon, n, title, text]) => {
            const I = Icon as typeof Activity;
            return (
              <article className="card how-card" key={String(n)}>
                <div className="row">
                  <span className="icon-box">
                    <I />
                  </span>
                  <span className="step-number">{String(n)}</span>
                </div>
                <h3>{String(title)}</h3>
                <p>{String(text)}</p>
              </article>
            );
          })}
        </div>
      </section>
      <section className="container section">
        <Disclaimer />
      </section>
    </>
  );
}
