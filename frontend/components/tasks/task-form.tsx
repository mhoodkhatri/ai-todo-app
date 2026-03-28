"use client";

import { useState } from "react";
import { taskCreateSchema } from "@/lib/validations";
import { createTask } from "@/lib/api";

interface TaskFormProps {
  onTaskCreated: () => void;
}

export function TaskForm({ onTaskCreated }: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [errors, setErrors] = useState<{ title?: string; description?: string }>({});
  const [submitting, setSubmitting] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErrors({});
    setApiError(null);

    const result = taskCreateSchema.safeParse({ title, description: description || undefined });
    if (!result.success) {
      const fieldErrors: { title?: string; description?: string } = {};
      for (const issue of result.error.issues) {
        const field = issue.path[0] as string;
        if (field === "title" || field === "description") {
          fieldErrors[field] = issue.message;
        }
      }
      setErrors(fieldErrors);
      return;
    }

    setSubmitting(true);
    try {
      await createTask({
        title: result.data.title,
        description: result.data.description || undefined,
      });
      setTitle("");
      setDescription("");
      onTaskCreated();
    } catch (err) {
      setApiError(err instanceof Error ? err.message : "Failed to create task");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mb-6 rounded-lg border border-gray-200 bg-white p-4 lg:mx-auto lg:max-w-2xl">
      <div className="mb-3">
        <input
          type="text"
          placeholder="What needs to be done?"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          disabled={submitting}
        />
        {errors.title && (
          <p className="mt-1 text-xs text-red-600">{errors.title}</p>
        )}
      </div>
      <div className="mb-3">
        <textarea
          placeholder="Description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={2}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          disabled={submitting}
        />
        {errors.description && (
          <p className="mt-1 text-xs text-red-600">{errors.description}</p>
        )}
      </div>
      {apiError && (
        <p className="mb-3 text-xs text-red-600">{apiError}</p>
      )}
      <button
        type="submit"
        disabled={submitting}
        className="min-h-[44px] w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 sm:w-auto"
      >
        {submitting ? "Adding..." : "Add Task"}
      </button>
    </form>
  );
}
