import { NextRequest } from "next/server";
import { auth } from "@/lib/auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Proxy ChatKit requests to the FastAPI backend.
 * Reads the httpOnly Better Auth session cookie, fetches a JWT token,
 * and forwards the request with Authorization: Bearer <jwt>.
 */
export async function POST(request: NextRequest) {
  const session = await auth.api.getSession({
    headers: request.headers,
  });

  if (!session) {
    return new Response(JSON.stringify({ detail: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Get JWT token from Better Auth token endpoint
  const tokenRes = await fetch(
    `${request.nextUrl.origin}/api/auth/token`,
    {
      headers: {
        cookie: request.headers.get("cookie") || "",
      },
    }
  );

  if (!tokenRes.ok) {
    return new Response(JSON.stringify({ detail: "Failed to get token" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  const tokenData = await tokenRes.json();
  const jwt = tokenData.token;

  if (!jwt) {
    return new Response(JSON.stringify({ detail: "No token available" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Forward request to FastAPI backend
  const body = await request.text();
  const backendRes = await fetch(`${API_BASE}/chatkit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${jwt}`,
    },
    body,
  });

  // Stream the response back for SSE or NDJSON streaming responses
  const contentType = backendRes.headers.get("content-type") || "";
  const isStreaming =
    contentType.includes("text/event-stream") ||
    contentType.includes("application/x-ndjson");

  console.log("[chatkit proxy] backend status:", backendRes.status, "content-type:", contentType, "streaming:", isStreaming);

  if (isStreaming) {
    return new Response(backendRes.body, {
      status: backendRes.status,
      headers: {
        "Content-Type": contentType,
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
  }

  const responseBody = await backendRes.text();
  console.log("[chatkit proxy] non-streaming response body:", responseBody.slice(0, 500));
  return new Response(responseBody, {
    status: backendRes.status,
    headers: {
      "Content-Type": contentType || "application/json",
    },
  });
}
