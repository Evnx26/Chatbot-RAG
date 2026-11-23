import Link from "next/link";
import { AuthCard } from "@/components/ui";
import { LoginForm } from "./login-form";

export const metadata = { title: "Masuk · Chatbot RAG UMKM" };

export default function LoginPage() {
  return (
    <AuthCard
      title="Masuk ke dashboard"
      subtitle="Kelola knowledge dan lihat Lead Business Anda."
      footer={
        <>
          Belum punya akun?{" "}
          <Link href="/signup" className="font-medium text-foreground underline">
            Daftarkan Business
          </Link>
        </>
      }
    >
      <LoginForm />
    </AuthCard>
  );
}
