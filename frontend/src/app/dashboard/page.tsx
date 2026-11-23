import { Suspense } from "react";
import { logout } from "@/app/actions";
import { getCurrentAdmin } from "@/lib/auth";

export const metadata = { title: "Dashboard · Chatbot RAG UMKM" };

export default function DashboardPage() {
  // Membaca sesi = data request-time, jadi harus di dalam <Suspense>.
  return (
    <Suspense fallback={<p className="p-8 text-sm text-foreground/60">Memuat dashboard…</p>}>
      <Dashboard />
    </Suspense>
  );
}

async function Dashboard() {
  const { admin, business } = await getCurrentAdmin();

  return (
    <div className="flex flex-1 flex-col">
      <header className="flex items-center justify-between border-b border-foreground/10 px-6 py-4">
        <div>
          <p className="text-sm font-semibold">{business.name}</p>
          <p className="text-xs text-foreground/60">
            {admin.full_name} · {admin.email}
          </p>
        </div>
        <form action={logout}>
          <button
            type="submit"
            className="rounded-lg border border-foreground/20 px-3 py-1.5 text-sm transition hover:bg-foreground/5"
          >
            Keluar
          </button>
        </form>
      </header>

      <main className="flex-1 px-6 py-10">
        <h1 className="text-xl font-semibold tracking-tight">Selamat datang, {admin.full_name}</h1>
        <p className="mt-1 text-sm text-foreground/60">
          Dashboard Anda masih kosong. Knowledge, Product, dan Lead akan muncul di sini
          seiring fitur ditambahkan.
        </p>
      </main>
    </div>
  );
}
