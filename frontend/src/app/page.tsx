import Link from "next/link";

// Placeholder. Landing page fashion Toko Demo dibangun di Fase 2.
export default function Home() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-6 px-4 text-center">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Toko Demo</h1>
        <p className="mt-2 text-sm text-foreground/60">Landing page fashion menyusul di Fase 2.</p>
      </div>
      <div className="flex gap-3 text-sm">
        <Link href="/login" className="rounded-lg bg-foreground px-4 py-2 font-medium text-background">
          Masuk
        </Link>
        <Link href="/signup" className="rounded-lg border border-foreground/20 px-4 py-2 font-medium">
          Daftar
        </Link>
      </div>
    </main>
  );
}
