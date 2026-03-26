const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const AUTH_BASE = process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "";

export interface TaskResponse {
  id: string;
  title: string;
  description: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

async function getJwtToken(): Promise<string> {
  const res = await fetch(`${AUTH_BASE}/api/auth/token`, {
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Not authenticated");
  }
  const data = await res.json();
  if (!data?.token) {
    throw new Error("Not authenticated");
  }
  return data.token;
}

async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = await getJwtToken();
  const headers: HeadersInit = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
    ...options.headers,
  };
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    let message = `Request failed (${res.status})`;
    if (Array.isArray(body?.detail)) {
      message = body.detail
        .map((e: { msg: string }) => e.msg)
        .join(", ");
    } else if (typeof body?.detail === "string") {
      message = body.detail;
    }
    throw new Error(message);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json();
}

export async function createTask(data: {
  title: string;
  description?: string;
}): Promise<TaskResponse> {
  return apiFetch<TaskResponse>("/api/tasks", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function listTasks(): Promise<TaskResponse[]> {
  return apiFetch<TaskResponse[]>("/api/tasks");
}

export async function getTask(taskId: string): Promise<TaskResponse> {
  return apiFetch<TaskResponse>(`/api/tasks/${taskId}`);
}

export async function updateTask(
  taskId: string,
  data: { title: string; description?: string | null },
): Promise<TaskResponse> {
  return apiFetch<TaskResponse>(`/api/tasks/${taskId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function toggleTask(taskId: string): Promise<TaskResponse> {
  return apiFetch<TaskResponse>(`/api/tasks/${taskId}/toggle`, {
    method: "PATCH",
  });
}

export async function deleteTask(taskId: string): Promise<void> {
  return apiFetch<void>(`/api/tasks/${taskId}`, {
    method: "DELETE",
  });
}
