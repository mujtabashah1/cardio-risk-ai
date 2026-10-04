import { z } from "zod";
export const policies = [
  "research_balanced",
  "high_sensitivity_80",
  "high_sensitivity_90",
  "youden",
  "conventional_050",
] as const;
export type ThresholdProfile = (typeof policies)[number];
const binary = z.union([z.literal(0), z.literal(1)]).nullable();
export const profileSchema = z
  .object({
    age_group: z.number().int().min(1).max(13).nullable(),
    sex: z.union([z.literal(1), z.literal(2)]).nullable(),
    bmi: z.number().min(12).max(99.99).nullable(),
    general_health: z.number().int().min(1).max(5).nullable(),
    physical_activity: binary,
    smoking_status: z.number().int().min(1).max(4).nullable(),
    diabetes: z.number().int().min(1).max(4).nullable(),
    stroke_history: binary,
    kidney_disease: binary,
    asthma: binary,
    difficulty_walking: binary,
    high_cholesterol: binary,
    high_blood_pressure: binary,
    alcohol_use: binary,
  })
  .strict();
export type HealthProfile = z.infer<typeof profileSchema>;
export type FieldName = keyof HealthProfile;
export interface PredictionRequest {
  profile: HealthProfile;
  threshold_profile: ThresholdProfile;
}
export const responseSchema = z.object({
  profile_score: z.number().min(0).max(1),
  classification: z.enum([
    "lower_model_association",
    "elevated_model_association",
  ]),
  threshold: z.number().min(0).max(1),
  threshold_profile: z.enum(policies),
  model_version: z.literal("1.0.0"),
  model_name: z.string(),
  model_context: z.string(),
});
export type PredictionResponse = z.infer<typeof responseSchema>;
export const modelInfoSchema = z.object({
  model_name: z.string(),
  model_family: z.string(),
  model_version: z.literal("1.0.0"),
  feature_count: z.literal(14),
  feature_names: z.array(z.string()),
  default_threshold_profile: z.enum(policies),
  supported_threshold_profiles: z.array(z.enum(policies)),
  intended_use: z.string(),
  model_context: z.string(),
  limitations_summary: z.array(z.string()),
});
export type ModelInfo = z.infer<typeof modelInfoSchema>;
export class ApiError extends Error {
  constructor(
    message: string,
    public status = 0,
  ) {
    super(message);
    this.name = "ApiError";
  }
}
