const AUTH_BASE = process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "";

export async function getJwtToken(): Promise<string> {
  const res = await fetch(`${AUTH_BASE}/api/auth/token`, {
    credentials: "include",
  });
  if (!res.ok) {
    window.location.href = "/signin?expired=true";
    throw new Error("Session expired");
  }
  const data = await res.json();
  if (!data?.token) {
    window.location.href = "/signin?expired=true";
    throw new Error("Session expired");
  }
  return data.token;
}
