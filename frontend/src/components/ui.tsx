import type { ComponentProps, ReactNode } from "react";

export function AuthCard({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
  footer: ReactNode;
}) {
  return (
    <main className="flex flex-1 items-center justify-center px-4 py-12">
      <div className="w-full max-w-sm">
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        <p className="mt-1 text-sm text-foreground/60">{subtitle}</p>
        <div className="mt-8">{children}</div>
        <p className="mt-6 text-center text-sm text-foreground/60">{footer}</p>
      </div>
    </main>
  );
}

export function TextField({
  label,
  id,
  ...props
}: { label: string; id: string } & ComponentProps<"input">) {
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium">
        {label}
      </label>
      <input
        id={id}
        name={id}
        {...props}
        className="mt-1.5 block w-full rounded-lg border border-foreground/20 bg-background px-3 py-2 text-sm outline-none transition focus:border-foreground focus:ring-2 focus:ring-foreground/10"
      />
    </div>
  );
}

export function SubmitButton({
  pending,
  children,
}: {
  pending: boolean;
  children: ReactNode;
}) {
  return (
    <button
      type="submit"
      disabled={pending}
      className="w-full rounded-lg bg-foreground px-4 py-2.5 text-sm font-medium text-background transition hover:opacity-90 disabled:opacity-50"
    >
      {pending ? "Memproses…" : children}
    </button>
  );
}

export function FormError({ message }: { message?: string }) {
  return (
    <p
      role="alert"
      aria-live="polite"
      className={message ? "rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-600 dark:text-red-400" : "hidden"}
    >
      {message}
    </p>
  );
}
