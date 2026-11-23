import Link from "next/link";
import { AuthCard } from "@/components/ui";
import { SignupForm } from "./signup-form";

export const metadata = { title: "Daftar · Chatbot RAG UMKM" };

export default function SignupPage() {
  return (
    <AuthCard
      title="Daftarkan Business Anda"
      subtitle="Satu akun Admin akan dibuat bersama Business baru."
      footer={
        <>
          Sudah punya akun?{" "}
          <Link href="/login" className="font-medium text-foreground underline">
            Masuk
          </Link>
        </>
      }
    >
      <SignupForm />
    </AuthCard>
  );
}
