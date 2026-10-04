import { useEffect, useState } from "react";
import { Link, NavLink, Route, Routes, useLocation } from "react-router-dom";
import { HeartPulse, Menu, X, ArrowUpRight } from "lucide-react";
import Home from "./pages/Home";
import Assessment from "./pages/Assessment";
import Results from "./pages/Results";
import ModelInfo from "./pages/ModelInfo";
import ResearchQA from "./pages/ResearchQA";
import { ErrorBoundary } from "./components/Common";
import { emptyForm } from "./constants/fields";
import type { HealthProfile, PredictionResponse } from "./api/types";
export default function App() {
  const [menu, setMenu] = useState(false),
    [form, setForm] = useState(emptyForm),
    [analysis, setAnalysis] = useState<{
      profile: HealthProfile;
      result: PredictionResponse;
    }>(),
    [toast, setToast] = useState("");
  const location = useLocation();
  useEffect(() => {
    function closeOnEscape(event: KeyboardEvent) {
      if (event.key === "Escape") setMenu(false);
    }
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, []);
  useEffect(() => {
    setMenu(false);
    window.scrollTo(0, 0);
  }, [location.pathname]);
  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(""), 4000);
    return () => clearTimeout(timer);
  }, [toast]);
  return (
    <ErrorBoundary>
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <header className="site-header">
        <div className="container nav-inner">
          <Link className="brand" to="/">
            <span className="brand-mark">
              <HeartPulse size={24} />
            </span>
            <span>
              <strong>
                CardioRisk <b>AI</b>
              </strong>
              <small>Cardiovascular Profile Intelligence</small>
            </span>
          </Link>
          <button
            className="menu-button"
            aria-label={menu ? "Close navigation" : "Open navigation"}
            aria-expanded={menu}
            aria-controls="main-nav"
            onClick={() => setMenu(!menu)}
          >
            {menu ? <X /> : <Menu />}
          </button>
          <nav
            id="main-nav"
            className={menu ? "open" : ""}
            aria-label="Main navigation"
          >
            {[
              ["/", "Home"],
              ["/assessment", "Assessment"],
              ["/model", "About the Model"],
              ["/qa", "Research / QA"],
            ].map(([to, text]) => (
              <NavLink key={to} to={to} end={to === "/"}>
                {text}
              </NavLink>
            ))}
            <Link className="nav-cta" to="/assessment">
              Get started <ArrowUpRight size={16} />
            </Link>
          </nav>
        </div>
      </header>
      <div id="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route
            path="/assessment"
            element={
              <Assessment
                form={form}
                setForm={(f) => {
                  setForm(f);
                  setAnalysis(undefined);
                }}
                onResult={(profile, result) => setAnalysis({ profile, result })}
              />
            }
          />
          <Route
            path="/results"
            element={<Results analysis={analysis} notify={setToast} />}
          />
          <Route path="/model" element={<ModelInfo />} />
          <Route path="/qa" element={<ResearchQA notify={setToast} />} />
          <Route
            path="*"
            element={
              <main className="container page">
                <h1>Page not found</h1>
                <Link className="button" to="/">
                  Return home
                </Link>
              </main>
            }
          />
        </Routes>
      </div>
      <footer className="container footer">
        <span>
          <strong>CardioRisk AI</strong> · Research application
        </span>
        <small>CDC BRFSS 2021 · Frozen model v1.0.0 · Local research use</small>
        <Link to="/model">Understand the limitations ↗</Link>
      </footer>
      {toast && (
        <div className="toast" role="status">
          {toast}
        </div>
      )}
    </ErrorBoundary>
  );
}
