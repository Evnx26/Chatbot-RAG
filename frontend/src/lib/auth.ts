import "server-only";
import { redirect } from "next/navigation";
import { backendFetch } from "./api";
import { getSessionToken } from "./session";

export type Me = {
  admin: { id: string; email: string; full_name: string };
  business: { id: string; name: string; slug: string };
};

/**
 * Admin yang sedang login, diverifikasi ke backend pada setiap pemanggilan.
 * Harus dipanggil dari dalam <Suspense> (membaca cookie = data request-time).
 */
export async function getCurrentAdmin(): Promise<Me> {
  const token = await getSessionToken();
  if (!token) redirect("/login");

  const res = await backendFetch("/auth/me", { token });
  // Token kedaluwarsa atau tidak valid: cookie tidak bisa dihapus saat render,
  // jadi hapusnya lewat route handler lalu lanjut ke /login.
  if (res.status === 401) redirect("/session-expired");
  if (!res.ok) throw new Error(`Backend /auth/me gagal: ${res.status}`);
  return res.json();
}
