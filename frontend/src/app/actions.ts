"use server";

import { redirect } from "next/navigation";
import { backendFetch } from "@/lib/api";
import { clearSession, setSession } from "@/lib/session";

// `values` mengembalikan isian (tanpa password) karena React 19 mengosongkan
// form setelah action selesai; tanpa ini email hilang setiap kali gagal.
export type FormState = { error?: string; values?: Record<string, string> };

const SERVER_DOWN = "Server tidak dapat dihubungi. Coba lagi sebentar lagi.";

function text(formData: FormData, key: string): string {
  return String(formData.get(key) ?? "").trim();
}

async function post(path: string, json: unknown): Promise<Response | null> {
  try {
    return await backendFetch(path, { method: "POST", json });
  } catch {
    return null;
  }
}

export async function login(_prev: FormState, formData: FormData): Promise<FormState> {
  const email = text(formData, "email");
  const password = String(formData.get("password") ?? "");
  const values = { email };
  if (!email || !password) return { error: "Email dan password wajib diisi.", values };

  const res = await post("/auth/login", { email, password });
  if (!res) return { error: SERVER_DOWN, values };
  if (res.status === 401) return { error: "Email atau password salah.", values };
  if (res.status === 422) return { error: "Format email tidak valid.", values };
  if (!res.ok) return { error: "Terjadi kesalahan. Coba lagi.", values };

  await setSession((await res.json()).access_token);
  redirect("/dashboard");
}

export async function signup(_prev: FormState, formData: FormData): Promise<FormState> {
  const business_name = text(formData, "business_name");
  const full_name = text(formData, "full_name");
  const email = text(formData, "email");
  const password = String(formData.get("password") ?? "");
  const values = { business_name, full_name, email };
  if (!business_name || !full_name || !email || !password) {
    return { error: "Semua kolom wajib diisi.", values };
  }
  if (password.length < 8) return { error: "Password minimal 8 karakter.", values };

  const res = await post("/auth/signup", { business_name, full_name, email, password });
  if (!res) return { error: SERVER_DOWN, values };
  if (res.status === 409) return { error: "Email sudah terdaftar.", values };
  if (res.status === 422) {
    return { error: "Periksa kembali isian Anda (format email, panjang nama).", values };
  }
  if (!res.ok) return { error: "Terjadi kesalahan. Coba lagi.", values };

  await setSession((await res.json()).access_token);
  redirect("/dashboard");
}

export async function logout() {
  await clearSession();
  redirect("/login");
}
