"use client";

import { useState } from "react";
import type { TaskResponse } from "@/lib/api";
import { updateTask, toggleTask, deleteTask } from "@/lib/api";
import { taskUpdateSchema } from "@/lib/validations";
import { DeleteDialog } from "./delete-dialog";

interface TaskItemProps {
  task: TaskResponse;
  onUpdated: () => void;
}

export function TaskItem({ task, onUpdated }: TaskItemProps) {
  const [editing, setEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || "");
  const [editErrors, setEditErrors] = useState<{ title?: string; description?: string }>({});
  const [saving, setSaving] = useState(false);
  const [toggling, setToggling] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleToggle() {
    setToggling(true);
    setError(null);
    try {
      await toggleTask(task.id);
      onUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to toggle task");
    } finally {
      setToggling(false);
    }
  }

  function startEdit() {
    setEditTitle(task.title);
    setEditDescription(task.description || "");
    setEditErrors({});
    setEditing(true);
  }

  function cancelEdit() {
    setEditing(false);
    setEditErrors({});
  }

  async function handleSaveEdit(e: React.FormEvent) {
    e.preventDefault();
    setEditErrors({});
    setError(null);

    const result = taskUpdateSchema.safeParse({
      title: editTitle,
      description: editDescription || undefined,
    });
    if (!result.success) {
      const fieldErrors: { title?: string; description?: string } = {};
      for (const issue of result.error.issues) {
        const field = issue.path[0] as string;
        if (field === "title" || field === "description") {
          fieldErrors[field] = issue.message;
        }
      }
      setEditErrors(fieldErrors);
      return;
    }

    setSaving(true);
    try {
      await updateTask(task.id, {
        title: result.data.title,
        description: result.data.description || null,
      });
      setEditing(false);
      onUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update task");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    setError(null);
    try {
      await deleteTask(task.id);
      setShowDeleteDialog(false);
      onUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete task");
      setShowDeleteDialog(false);
    }
  }

  const createdDate = new Date(task.created_at).toLocaleDateString();

  if (editing) {
    return (
      <form
        onSubmit={handleSaveEdit}
        className="rounded-lg border border-blue-200 bg-blue-50 p-4"
      >
        <div className="mb-2">
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            className="w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            disabled={saving}
          />
          {editErrors.title && (
            <p className="mt-1 text-xs text-red-600">{editErrors.title}</p>
          )}
        </div>
        <div className="mb-3">
          <textarea
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value)}
            rows={2}
            placeholder="Description (optional)"
            className="w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            disabled={saving}
          />
          {editErrors.description && (
            <p className="mt-1 text-xs text-red-600">{editErrors.description}</p>
          )}
        </div>
        {error && <p className="mb-2 text-xs text-red-600">{error}</p>}
        <div className="flex gap-2">
          <button
            type="submit"
            disabled={saving}
            className="rounded-md bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save"}
          </button>
          <button
            type="button"
            onClick={cancelEdit}
            disabled={saving}
            className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          >
            Cancel
          </button>
        </div>
      </form>
    );
  }

  return (
    <>
      <div
        className={`flex items-start gap-3 rounded-lg border bg-white p-4 ${
          task.is_completed ? "border-gray-200 opacity-60" : "border-gray-200"
        }`}
      >
        <button
          onClick={handleToggle}
          disabled={toggling}
          className={`mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded border ${
            task.is_completed
              ? "border-green-500 bg-green-500 text-white"
              : "border-gray-300 hover:border-gray-400"
          }`}
          aria-label={task.is_completed ? "Mark incomplete" : "Mark complete"}
        >
          {task.is_completed && (
            <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          )}
        </button>

        <div className="min-w-0 flex-1">
          <p
            className={`text-sm font-medium ${
              task.is_completed ? "text-gray-400 line-through" : "text-gray-900"
            }`}
          >
            {task.title}
          </p>
          {task.description && (
            <p
              className={`mt-1 text-xs ${
                task.is_completed ? "text-gray-400 line-through" : "text-gray-500"
              }`}
            >
              {task.description}
            </p>
          )}
          <p className="mt-1 text-xs text-gray-400">{createdDate}</p>
          {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
        </div>

        <div className="flex flex-shrink-0 gap-1">
          <button
            onClick={startEdit}
            className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            aria-label="Edit task"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            onClick={() => setShowDeleteDialog(true)}
            className="rounded p-1 text-gray-400 hover:bg-red-50 hover:text-red-600"
            aria-label="Delete task"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>

      {showDeleteDialog && (
        <DeleteDialog
          taskTitle={task.title}
          onConfirm={handleDelete}
          onCancel={() => setShowDeleteDialog(false)}
        />
      )}
    </>
  );
}
