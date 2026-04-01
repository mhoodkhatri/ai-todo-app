import Link from "next/link";
import { headers } from "next/headers";
import { auth } from "@/lib/auth";
import { SignOutButton } from "@/components/auth/sign-out-button";
import { ChatInterface } from "@/components/chat/chat-interface";

export default async function ChatPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  return (
    <div className="flex min-h-screen flex-col bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="mx-auto flex max-w-4xl flex-col gap-3 px-4 py-4 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-3">
            <Link
              href="/dashboard"
              className="text-sm text-indigo-600 hover:text-indigo-800 transition-colors"
            >
              &larr; Dashboard
            </Link>
            <h1 className="text-lg font-bold text-gray-900 md:text-xl">
              AI Chat
            </h1>
          </div>
          <div className="flex items-center gap-3 md:gap-4">
            <span className="text-sm text-gray-600">
              Hello, {session?.user?.name}
            </span>
            <SignOutButton />
          </div>
        </div>
      </header>
      <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col px-4 py-4">
        <div className="flex-1 rounded-lg border border-gray-200 bg-white shadow-sm overflow-hidden" style={{ minHeight: "60vh" }}>
          <ChatInterface />
        </div>
      </main>
    </div>
  );
}
