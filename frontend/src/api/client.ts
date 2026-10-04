import { z } from "zod";
import {
  ApiError,
  profileSchema,
  responseSchema,
  modelInfoSchema,
  type PredictionRequest,
} from "./types";
export async function request<T>(
  path: string,
  schema: z.ZodType<T>,
  body?: unknown,
  timeout = 15000,
): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  try {
    const response = await fetch(
      `${import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "/api"}${path}`,
      {
        method: body ? "POST" : "GET",
        headers: body ? { "Content-Type": "application/json" } : undefined,
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      },
    );
    let data: unknown;
    try {
      data = await response.json();
    } catch {
      throw new ApiError(
        "The API returned an unreadable response. Try again.",
        response.status,
      );
    }
    if (!response.ok)
      throw new ApiError(
        response.status === 422
          ? "The API rejected this profile. Check the selected values."
          : response.status === 503
            ? "The model is not ready. Try again shortly."
            : "The API could not complete the request. Try again.",
        response.status,
      );
    const parsed = schema.safeParse(data);
    if (!parsed.success)
      throw new ApiError(
        "The API response does not match the research contract.",
      );
    return parsed.data;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(
      controller.signal.aborted
        ? "The request timed out. Try again."
        : "API unavailable. Check the local backend and try again.",
    );
  } finally {
    clearTimeout(timer);
  }
}
export const predict = (input: PredictionRequest) => {
  profileSchema.parse(input.profile);
  return request("/predict", responseSchema, input);
};
export const getInfo = () => request("/model-info", modelInfoSchema);
export const getHealth = () =>
  request("/health", z.object({ status: z.literal("ok") }));
export const getReady = () =>
  request(
    "/ready",
    z.object({ status: z.literal("ready"), model_version: z.literal("1.0.0") }),
  );
