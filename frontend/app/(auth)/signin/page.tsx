import Link from "next/link";
import { SignInForm } from "@/components/auth/signin-form";

export default function SignInPage({
  searchParams,
}: {
  searchParams: Promise<{ expired?: string }>;
}) {
  return (
    <>
      <h1 className="mb-6 text-center text-2xl font-bold text-gray-900">
        Sign In
      </h1>
      <ExpiredMessage searchParams={searchParams} />
      <SignInForm />
      <p className="mt-4 text-center text-sm text-gray-600">
        Don&apos;t have an account?{" "}
        <Link href="/signup" className="text-blue-600 hover:underline">
          Sign up
        </Link>
      </p>
    </>
  );
}

async function ExpiredMessage({
  searchParams,
}: {
  searchParams: Promise<{ expired?: string }>;
}) {
  const { expired } = await searchParams;
  if (expired !== "true") return null;
  return (
    <div className="mb-4 rounded-md bg-yellow-50 p-3 text-sm text-yellow-700">
      Session expired, please sign in again.
    </div>
  );
}
