import { redirect } from "next/navigation";
import { clearSession } from "@/lib/session";

// Dipanggil saat backend menolak token. Menghapus cookie lalu kembali ke login,
// supaya tidak terjadi loop /login -> /dashboard -> /login.
export async function GET() {
  await clearSession();
  redirect("/login");
}
