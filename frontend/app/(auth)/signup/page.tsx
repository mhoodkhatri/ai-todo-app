import Link from "next/link";
import { SignUpForm } from "@/components/auth/signup-form";

export default function SignUpPage() {
  return (
    <>
      <h1 className="mb-6 text-center text-2xl font-bold text-gray-900">
        Create an Account
      </h1>
      <SignUpForm />
      <p className="mt-4 text-center text-sm text-gray-600">
        Already have an account?{" "}
        <Link href="/signin" className="text-blue-600 hover:underline">
          Sign in
        </Link>
      </p>
    </>
  );
}
