import {
  profileSchema,
  type FieldName,
  type HealthProfile,
} from "../api/types";
export interface Field {
  name: FieldName;
  label: string;
  question: string;
  options?: readonly (readonly [number, string])[];
  help?: string;
}
const yesNo = [
  [1, "Yes"],
  [0, "No"],
] as const;
export const groups = [
  {
    title: "Basic profile",
    description: "A few details to begin your profile.",
    fields: ["age_group", "sex", "bmi"],
  },
  {
    title: "Lifestyle",
    description: "Health and habits, in your own words.",
    fields: [
      "general_health",
      "physical_activity",
      "smoking_status",
      "alcohol_use",
    ],
  },
  {
    title: "Medical history",
    description: "Your reported history. Unknown is always an option.",
    fields: [
      "diabetes",
      "stroke_history",
      "kidney_disease",
      "asthma",
      "difficulty_walking",
      "high_cholesterol",
      "high_blood_pressure",
    ],
  },
] as const;
export const fields: Field[] = [
  {
    name: "age_group",
    label: "Age group",
    question: "Which age group are you in?",
    options: [
      "18–24",
      "25–29",
      "30–34",
      "35–39",
      "40–44",
      "45–49",
      "50–54",
      "55–59",
      "60–64",
      "65–69",
      "70–74",
      "75–79",
      "80+",
    ].map((s, i) => [i + 1, s]),
  },
  {
    name: "sex",
    label: "Sex",
    question: "What sex was recorded under the BRFSS respondent-sex question?",
    options: [
      [1, "Male"],
      [2, "Female"],
    ],
  },
  {
    name: "bmi",
    label: "Body Mass Index (BMI)",
    question: "What is your BMI?",
    help: "Enter BMI directly, such as 28.5 (12–99.99). Do not scale by 100.",
  },
  {
    name: "general_health",
    label: "General health",
    question: "How would you describe your general health?",
    options: ["Excellent", "Very good", "Good", "Fair", "Poor"].map((s, i) => [
      i + 1,
      s,
    ]),
  },
  {
    name: "physical_activity",
    label: "Physical activity",
    question: "In the past 30 days, did you exercise outside your regular job?",
    options: yesNo,
  },
  {
    name: "smoking_status",
    label: "Smoking status",
    question: "Which best describes your smoking history?",
    options: [
      [1, "Current smoker — every day"],
      [2, "Current smoker — some days"],
      [3, "Former smoker"],
      [4, "Fewer than 100 cigarettes lifetime"],
    ],
    help: "Current and former categories mean at least 100 cigarettes in your lifetime.",
  },
  {
    name: "diabetes",
    label: "Diabetes",
    question: "Have you ever been told you had diabetes?",
    options: [
      [1, "Yes"],
      [2, "Only during pregnancy"],
      [3, "No"],
      [4, "Prediabetes / borderline"],
    ],
  },
  {
    name: "stroke_history",
    label: "Stroke history",
    question: "Have you ever been told you had a stroke?",
    options: yesNo,
  },
  {
    name: "kidney_disease",
    label: "Kidney disease",
    question: "Have you been told you had kidney disease?",
    options: yesNo,
    help: "Exclude kidney stones, bladder infection and incontinence.",
  },
  {
    name: "asthma",
    label: "Asthma",
    question: "Have you ever been told you had asthma?",
    options: yesNo,
  },
  {
    name: "difficulty_walking",
    label: "Difficulty walking",
    question: "Do you have serious difficulty walking or climbing stairs?",
    options: yesNo,
  },
  {
    name: "high_cholesterol",
    label: "High cholesterol",
    question: "Has a health professional told you your cholesterol is high?",
    options: yesNo,
  },
  {
    name: "high_blood_pressure",
    label: "High blood pressure",
    question:
      "Has a health professional told you you have high blood pressure?",
    options: yesNo,
    help: "Pregnancy-only and borderline responses belong to No in this CDC category.",
  },
  {
    name: "alcohol_use",
    label: "Alcohol use",
    question: "Have you had at least one alcoholic drink in the past 30 days?",
    options: yesNo,
  },
];
export type FormValues = Record<FieldName, string>;
export const emptyForm = () =>
  Object.fromEntries(fields.map((f) => [f.name, ""])) as FormValues;
export function toProfile(form: FormValues): HealthProfile {
  const result = Object.fromEntries(
    fields.map((f) => {
      const raw = form[f.name];
      if (raw === "") return [f.name, null];
      if (typeof raw !== "string" || !/^-?(?:\d+\.?\d*|\.\d+)$/.test(raw))
        throw new Error(`${f.label}: enter a valid number.`);
      const value = Number(raw);
      if (
        !Number.isFinite(value) ||
        (f.options && !f.options.some(([n]) => n === value)) ||
        (f.name === "bmi" && (value < 12 || value > 99.99))
      )
        throw new Error(
          `${f.label}: choose an allowed value${f.name === "bmi" ? " between 12 and 99.99" : ""}.`,
        );
      return [f.name, value];
    }),
  );
  return profileSchema.parse(result);
}
export const toForm = (p: HealthProfile) =>
  Object.fromEntries(
    fields.map((f) => [f.name, p[f.name] === null ? "" : String(p[f.name])]),
  ) as FormValues;
export const answer = (f: Field, p: HealthProfile) =>
  p[f.name] === null
    ? "Unknown"
    : (f.options?.find(([n]) => n === p[f.name])?.[1] ?? String(p[f.name]));
export const low: HealthProfile = {
  age_group: 1,
  sex: 2,
  bmi: 22,
  general_health: 1,
  physical_activity: 1,
  smoking_status: 4,
  diabetes: 3,
  stroke_history: 0,
  kidney_disease: 0,
  asthma: 0,
  difficulty_walking: 0,
  high_cholesterol: 0,
  high_blood_pressure: 0,
  alcohol_use: 0,
};
export const high: HealthProfile = {
  age_group: 11,
  sex: 1,
  bmi: 34,
  general_health: 5,
  physical_activity: 0,
  smoking_status: 1,
  diabetes: 1,
  stroke_history: 1,
  kidney_disease: 1,
  asthma: 1,
  difficulty_walking: 1,
  high_cholesterol: 1,
  high_blood_pressure: 1,
  alcohol_use: 0,
};
export const presets: { name: string; profile: HealthProfile }[] = [
  { name: "Young low-association example", profile: low },
  {
    name: "Middle-aged mixed example",
    profile: {
      ...low,
      age_group: 8,
      bmi: 28.5,
      general_health: 3,
      smoking_status: 3,
      high_blood_pressure: 1,
    },
  },
  { name: "Older high-association example", profile: high },
  {
    name: "Missing-data example",
    profile: Object.fromEntries(
      fields.map((f) => [f.name, null]),
    ) as HealthProfile,
  },
];
