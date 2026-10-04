import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, it, expect, vi } from "vitest";
import App from "../App";
import { ErrorBoundary } from "../components/Common";
import {
  fields,
  emptyForm,
  toForm,
  toProfile,
  low,
  high,
  presets,
} from "../constants/fields";
import { profileSchema, policies, responseSchema } from "../api/types";
import { request, predict } from "../api/client";
import { z } from "zod";
const result = {
  profile_score: 0.002504,
  classification: "lower_model_association",
  threshold: 0.20943938491134126,
  threshold_profile: "research_balanced",
  model_version: "1.0.0",
  model_name: "BRFSS CHD/MI Profile Score",
  model_context: "Research only",
};
const info = {
  model_name: result.model_name,
  model_family: "catboost",
  model_version: "1.0.0",
  feature_count: 14,
  feature_names: fields.map((f) => f.name),
  default_threshold_profile: "research_balanced",
  supported_threshold_profiles: [...policies],
  intended_use: "Research",
  model_context: "Research",
  limitations_summary: ["Research only"],
};
function mockAPI() {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string, options?: RequestInit) => {
      const path = String(url);
      let data: unknown = path.endsWith("/health")
        ? { status: "ok" }
        : path.endsWith("/ready")
          ? { status: "ready", model_version: "1.0.0" }
          : path.endsWith("/model-info")
            ? info
            : result;
      if (options?.body) {
        const input = JSON.parse(String(options.body));
        data = {
          ...result,
          profile_score: input.profile.age_group === 11 ? 0.831258 : 0.002504,
          threshold_profile: input.threshold_profile,
          threshold:
            input.threshold_profile === "high_sensitivity_90"
              ? 0.045767086681139546
              : result.threshold,
        };
      }
      return { ok: true, status: 200, json: async () => data };
    }),
  );
}
function app(path = "/") {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
}
describe("exact profile contract", () => {
  it("contains exactly 14 fields", () =>
    expect(fields.map((f) => f.name).sort()).toEqual(Object.keys(low).sort()));
  it("maps all unknowns to null", () =>
    expect(Object.values(toProfile(emptyForm()))).toEqual(
      Array(14).fill(null),
    ));
  it("round trips all 14 inputs without scaling", () =>
    expect(toProfile(toForm({ ...high, bmi: 28.5 }))).toEqual({
      ...high,
      bmi: 28.5,
    }));
  it.each(["NaN", "Infinity", "abc", " ", "28x", "11.99", "100"])(
    "blocks invalid BMI %s",
    (v) => expect(() => toProfile({ ...emptyForm(), bmi: v })).toThrow(),
  );
  it.each([12, 28.5, 99.99])("accepts valid BMI %s", (v) =>
    expect(toProfile({ ...emptyForm(), bmi: String(v) }).bmi).toBe(v),
  );
  it("blocks unsupported categorical values", () =>
    expect(() => toProfile({ ...emptyForm(), sex: "3" })).toThrow());
  it("retains smoking and diabetes categories", () => {
    expect(
      fields.find((f) => f.name === "smoking_status")!.options![3][1],
    ).toBe("Fewer than 100 cigarettes lifetime");
    expect(fields.find((f) => f.name === "diabetes")!.options).toHaveLength(4);
  });
  it("validates all synthetic presets", () =>
    presets.forEach((p) =>
      expect(profileSchema.safeParse(p.profile).success).toBe(true),
    ));
  it("rejects extra fields", () =>
    expect(profileSchema.safeParse({ ...low, income: 1 }).success).toBe(false));
});
describe("API client", () => {
  it("serializes validated prediction", async () => {
    mockAPI();
    expect(
      await predict({ profile: low, threshold_profile: "research_balanced" }),
    ).toEqual(result);
    expect(fetch).toHaveBeenCalledWith(
      "/api/predict",
      expect.objectContaining({
        body: JSON.stringify({
          profile: low,
          threshold_profile: "research_balanced",
        }),
      }),
    );
  });
  it.each([422, 500, 503])("handles HTTP %s", async (status) => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: false,
        status,
        json: async () => ({ error: {} }),
      })),
    );
    await expect(
      predict({ profile: low, threshold_profile: "research_balanced" }),
    ).rejects.toThrow();
  });
  it("handles disconnected API", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError()));
    await expect(
      request("/health", z.object({ status: z.string() })),
    ).rejects.toThrow("API unavailable");
  });
  it("rejects malformed response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: true,
        status: 200,
        json: async () => ({ profile_score: 9 }),
      })),
    );
    await expect(request("/predict", responseSchema)).rejects.toThrow(
      "contract",
    );
  });
  it("handles unreadable JSON", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: true,
        status: 200,
        json: async () => {
          throw new Error();
        },
      })),
    );
    await expect(
      request("/health", z.object({ status: z.string() })),
    ).rejects.toThrow("unreadable");
  });
  it("handles timeout", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        (_u: unknown, o: RequestInit) =>
          new Promise((_r, reject) =>
            o.signal?.addEventListener("abort", () => reject(new Error())),
          ),
      ),
    );
    await expect(
      request("/health", z.object({ status: z.string() }), undefined, 5),
    ).rejects.toThrow("timed out");
  });
});
describe("application flows", () => {
  it("Escape closes mobile navigation", () => {
    app();
    fireEvent.click(screen.getByRole("button", { name: "Open navigation" }));
    fireEvent.keyDown(window, { key: "Escape" });
    expect(
      screen.getByRole("button", { name: "Open navigation" }),
    ).toHaveAttribute("aria-expanded", "false");
  });
  it("component exception has a recoverable boundary", () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    function Broken(): never {
      throw new Error("Synthetic component exception");
    }
    render(
      <ErrorBoundary>
        <Broken />
      </ErrorBoundary>,
    );
    expect(screen.getByRole("alert")).toHaveTextContent("Reload to recover");
  });
  it("pending assessment cannot navigate after leaving", async () => {
    let resolveFetch!: (value: unknown) => void;
    vi.stubGlobal(
      "fetch",
      vi.fn(
        () =>
          new Promise((resolve) => {
            resolveFetch = resolve;
          }),
      ),
    );
    app("/assessment");
    for (let i = 0; i < 3; i++)
      fireEvent.click(screen.getByRole("button", { name: /Continue/ }));
    fireEvent.click(screen.getByRole("button", { name: "Analyze Profile" }));
    expect(
      screen.getByRole("button", { name: /Analyzing profile/ }),
    ).toBeDisabled();
    fireEvent.click(screen.getByRole("link", { name: "Home" }));
    resolveFetch({ ok: true, status: 200, json: async () => result });
    await waitFor(() =>
      expect(
        screen.getByRole("heading", { name: /A clearer view/ }),
      ).toBeInTheDocument(),
    );
    expect(
      screen.queryByRole("heading", { name: "Profile Analysis" }),
    ).not.toBeInTheDocument();
  });
  it("renders home and navigates", () => {
    app();
    expect(
      screen.getByRole("heading", { name: /A clearer view/ }),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByRole("link", { name: "Start Assessment" }));
    expect(screen.getByLabelText("Age group")).toBeInTheDocument();
  });
  it("mobile menu has accessible state", () => {
    app();
    fireEvent.click(screen.getByRole("button", { name: "Open navigation" }));
    expect(
      screen.getByRole("button", { name: "Close navigation" }),
    ).toHaveAttribute("aria-expanded", "true");
  });
  it("wizard back, all steps, review and success", async () => {
    mockAPI();
    app("/assessment");
    fireEvent.change(screen.getByLabelText("Body Mass Index (BMI)"), {
      target: { value: "28.5" },
    });
    fireEvent.click(screen.getByRole("button", { name: /Continue/ }));
    expect(screen.getByLabelText("Smoking status")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Back/ }));
    expect(screen.getByLabelText("Body Mass Index (BMI)")).toHaveValue("28.5");
    fireEvent.click(screen.getByRole("button", { name: /Continue/ }));
    fireEvent.click(screen.getByRole("button", { name: /Continue/ }));
    expect(screen.getByLabelText("Diabetes")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /Continue/ }));
    expect(screen.getByText("Review your profile")).toBeInTheDocument();
    expect(screen.getByText("28.5")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Analyze Profile" }));
    await screen.findByRole("heading", { name: "Profile Analysis" });
    expect(screen.getByText("Model Profile Score")).toBeInTheDocument();
    expect(screen.getByText("Lower model association")).toBeInTheDocument();
    expect(screen.getByText("0.3")).toBeInTheDocument();
  });
  it("invalid BMI gives inline error and blocks navigation", () => {
    app("/assessment");
    fireEvent.change(screen.getByLabelText("Body Mass Index (BMI)"), {
      target: { value: "NaN" },
    });
    fireEvent.click(screen.getByRole("button", { name: /Continue/ }));
    expect(screen.getByRole("alert")).toHaveTextContent("valid number");
    expect(screen.getByLabelText("Age group")).toBeInTheDocument();
  });
  it("prediction error keeps review and offers retry", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error()));
    app("/assessment");
    for (let i = 0; i < 3; i++)
      fireEvent.click(screen.getByRole("button", { name: /Continue/ }));
    fireEvent.click(screen.getByRole("button", { name: "Analyze Profile" }));
    await screen.findByRole("alert");
    expect(
      screen.getByRole("button", { name: "Try again" }),
    ).toBeInTheDocument();
  });
  it("refresh-safe empty results", () => {
    app("/results");
    expect(
      screen.getByText("Your analysis will appear here"),
    ).toBeInTheDocument();
  });
  it("model page loads metadata", async () => {
    mockAPI();
    app("/model");
    await waitFor(() => expect(screen.getByText("1.0.0")).toBeInTheDocument());
    expect(screen.getByText("0.8468")).toBeInTheDocument();
  });
  it("QA status, presets, threshold and comparison", async () => {
    mockAPI();
    app("/qa");
    await screen.findByText("API Online");
    expect(screen.getByText("Model Ready")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: presets[2].name }));
    fireEvent.click(
      screen.getByRole("button", { name: "Analyze synthetic profile" }),
    );
    await screen.findByText("83.1");
    fireEvent.click(screen.getByRole("button", { name: /Duplicate result/ }));
    fireEvent.click(screen.getByText("Edit profile inputs · 14 fields"));
    fireEvent.change(screen.getByLabelText("Stroke history"), {
      target: { value: "0" },
    });
    fireEvent.click(
      screen.getByRole("button", { name: "Analyze synthetic profile" }),
    );
    await screen.findByTestId("comparison");
    expect(screen.getByTestId("comparison")).toHaveTextContent(
      "Stroke history",
    );
    fireEvent.change(screen.getByLabelText("Research threshold policy"), {
      target: { value: "high_sensitivity_90" },
    });
    fireEvent.click(
      screen.getByRole("button", { name: "Analyze synthetic profile" }),
    );
    await waitFor(() =>
      expect(fetch).toHaveBeenLastCalledWith(
        "/api/predict",
        expect.objectContaining({
          body: expect.stringContaining("high_sensitivity_90"),
        }),
      ),
    );
  });
  it("QA outage does not crash", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error()));
    app("/qa");
    await waitFor(() =>
      expect(screen.getAllByText("API unavailable").length).toBeGreaterThan(0),
    );
    expect(screen.getByText("Explore. Compare. Verify.")).toBeInTheDocument();
  });
});
