import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

const sessionCookie = "knowbridge_session";

type RouteContext = {
  params: Promise<{ path: string[] }>;
};

async function forward(request: NextRequest, context: RouteContext) {
  const { path } = await context.params;
  const backendBase =
    process.env.KNOWBRIDGE_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL;

  if (!backendBase) {
    return NextResponse.json(
      { error: { code: "configuration_error", message: "Backend API URL is not configured." } },
      { status: 503 },
    );
  }

  const route = path.join("/");
  const cookieStore = await cookies();
  if (request.method === "POST" && route === "auth/logout") {
    cookieStore.delete(sessionCookie);
    return NextResponse.json({ data: { signed_out: true } });
  }
  if (!route || route.split("/").some((segment) => segment === "." || segment === "..")) {
    return NextResponse.json(
      { error: { code: "invalid_route", message: "Invalid API route." } },
      { status: 400 },
    );
  }
  const sessionToken = cookieStore.get(sessionCookie)?.value;
  const backendUrl = new URL(route, `${backendBase.replace(/\/+$/, "")}/`);
  backendUrl.search = request.nextUrl.search;

  const headers = new Headers();
  const contentType = request.headers.get("content-type");
  if (contentType) headers.set("Content-Type", contentType);
  headers.set("Accept", "application/json");
  if (sessionToken) headers.set("Authorization", `Bearer ${sessionToken}`);

  let upstream: Response;
  try {
    upstream = await fetch(backendUrl, {
      method: request.method,
      headers,
      body:
        request.method === "GET" || request.method === "HEAD"
          ? undefined
          : await request.arrayBuffer(),
      cache: "no-store",
    });
  } catch {
    return NextResponse.json(
      { error: { code: "backend_unavailable", message: "The API could not be reached." } },
      { status: 503 },
    );
  }

  if (request.method === "POST" && (route === "auth/login" || route === "auth/register")) {
    const body = (await upstream.json().catch(() => null)) as
      | { data?: { access_token?: string } }
      | null;
    const token = body?.data?.access_token;
    if (upstream.ok && token) {
      const responseBody = structuredClone(body) as {
        data?: Record<string, unknown>;
      };
      if (responseBody.data) delete responseBody.data.access_token;
      const response = NextResponse.json(responseBody, { status: upstream.status });
      response.cookies.set(sessionCookie, token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        path: "/",
        maxAge: Number(process.env.KNOWBRIDGE_ACCESS_TOKEN_EXPIRE_MINUTES ?? 30) * 60,
      });
      return response;
    }
    return NextResponse.json(body, { status: upstream.status });
  }

  const responseBody = await upstream.arrayBuffer();
  return new NextResponse(responseBody.byteLength ? responseBody : null, {
    status: upstream.status,
    headers: {
      "Content-Type": upstream.headers.get("content-type") ?? "application/json",
      "Cache-Control": "no-store",
    },
  });
}

export const GET = forward;
export const POST = forward;
export const PATCH = forward;
export const DELETE = forward;
