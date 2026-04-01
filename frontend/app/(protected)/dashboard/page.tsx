import Link from "next/link";
import { headers } from "next/headers";
import { auth } from "@/lib/auth";
import { SignOutButton } from "@/components/auth/sign-out-button";
import { TaskList } from "@/components/tasks/task-list";

export default async function DashboardPage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="mx-auto flex max-w-4xl flex-col gap-3 px-4 py-4 md:flex-row md:items-center md:justify-between">
          <h1 className="text-lg font-bold text-gray-900 md:text-xl">Todo App</h1>
          <div className="flex items-center gap-3 md:gap-4">
            <Link
              href="/chat"
              className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700 transition-colors"
            >
              AI Chat
            </Link>
            <span className="text-sm text-gray-600">
              Hello, {session?.user?.name}
            </span>
            <SignOutButton />
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-4xl px-4 py-8">
        <TaskList />
      </main>
    </div>
  );
}
