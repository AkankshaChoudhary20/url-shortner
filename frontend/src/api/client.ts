import type { ApiErrorBody } from "../types/link";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

interface FieldError {
  loc: (string | number)[];
  msg: string;
}

function isFieldErrorList(value: unknown): value is FieldError[] {
  return (
    Array.isArray(value) &&
    value.every((item) => item && typeof item === "object" && "loc" in item && "msg" in item)
  );
}

export class ApiError extends Error {
  code: string;
  details: Record<string, unknown>;
  requestId: string;
  status: number;

  constructor(status: number, body: ApiErrorBody) {
    super(body.error.message);
    this.name = "ApiError";
    this.status = status;
    this.code = body.error.code;
    this.details = body.error.details;
    this.requestId = body.error.request_id;
  }

  /** A user-facing message: field-specific detail for validation errors, the server message otherwise. */
  get displayMessage(): string {
    const errors = this.details.errors;
    if (this.code === "VALIDATION_ERROR" && isFieldErrorList(errors)) {
      return errors
        .map((error) => {
          const field = error.loc.filter((part) => part !== "body").join(".");
          return field ? `${field}: ${error.msg}` : error.msg;
        })
        .join("; ");
    }
    return this.message;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const body = (await response.json()) as ApiErrorBody;
    throw new ApiError(response.status, body);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export const apiClient = {
  get: <T>(path: string) => request<T>(path, { method: "GET" }),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
};

export { API_BASE_URL };
