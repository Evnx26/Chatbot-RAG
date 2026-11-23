import "server-only";

// Hanya dipakai dari server (Server Action / Server Component). Browser tidak
// pernah memanggil backend langsung pada Fase 0, jadi token tidak menyentuh JS klien.
const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

type BackendInit = {
  method?: "GET" | "POST";
  json?: unknown;
  token?: string;
};

export async function backendFetch(path: string, init: BackendInit = {}) {
  const headers: Record<string, string> = {};
  if (init.json !== undefined) headers["Content-Type"] = "application/json";
  if (init.token) headers["Authorization"] = `Bearer ${init.token}`;
  return fetch(`${BACKEND_URL}${path}`, {
    method: init.method ?? "GET",
    headers,
    body: init.json !== undefined ? JSON.stringify(init.json) : undefined,
    cache: "no-store",
  });
}
