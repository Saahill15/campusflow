export interface ApiResponse<T = unknown> {
  success: boolean;
  message: string;
  data: T;
  meta?: Record<string, unknown>;
}

export interface ErrorResponse {
  success: false;
  message: string;
  error: {
    code: string;
    details?: Record<string, unknown> | null;
  };
  meta?: Record<string, unknown>;
}
