"use client";

import { useActionState } from "react";
import { signup, type FormState } from "@/app/actions";
import { FormError, SubmitButton, TextField } from "@/components/ui";

const initialState: FormState = {};

export function SignupForm() {
  const [state, formAction, pending] = useActionState(signup, initialState);

  return (
    <form action={formAction} className="space-y-4">
      <TextField
        label="Nama Business"
        id="business_name"
        autoComplete="organization"
        defaultValue={state.values?.business_name}
        minLength={2}
        maxLength={100}
        required
      />
      <TextField
        label="Nama Anda"
        id="full_name"
        autoComplete="name"
        defaultValue={state.values?.full_name}
        minLength={2}
        maxLength={100}
        required
      />
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
        autoComplete="new-password"
        minLength={8}
        maxLength={128}
        required
      />
      <FormError message={state.error} />
      <SubmitButton pending={pending}>Daftar</SubmitButton>
    </form>
  );
}
