"use client";

import { useActionState } from "react";
import { login, type FormState } from "@/app/actions";
import { FormError, SubmitButton, TextField } from "@/components/ui";

const initialState: FormState = {};

export function LoginForm() {
  const [state, formAction, pending] = useActionState(login, initialState);

  return (
    <form action={formAction} className="space-y-4">
      <TextField
        label="Email"
        id="email"
        type="email"
        autoComplete="email"
        defaultValue={state.values?.email}
        required
      />
      <TextField
        label="Password"
        id="password"
        type="password"
        autoComplete="current-password"
        required
      />
      <FormError message={state.error} />
      <SubmitButton pending={pending}>Masuk</SubmitButton>
    </form>
  );
}
