"use client";

import { useCallback, useEffect, useState } from "react";
import type { TaskResponse } from "@/lib/api";
import { listTasks } from "@/lib/api";
import { TaskItem } from "./task-item";
import { TaskForm } from "./task-form";

type Filter = "all" | "completed" | "incomplete";

export function TaskList() {
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<Filter>("all");

  const fetchTasks = useCallback(async () => {
    setError(null);
    try {
      const data = await listTasks();
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const filteredTasks = tasks.filter((task) => {
    if (filter === "completed") return task.is_completed;
    if (filter === "incomplete") return !task.is_completed;
    return true;
  });

  return (
    <div>
      <TaskForm onTaskCreated={fetchTasks} />

      <div className="mb-4 flex gap-1 rounded-lg border border-gray-200 bg-white p-1">
        {(["all", "incomplete", "completed"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`flex-1 rounded-md px-3 py-1.5 text-xs font-medium capitalize transition-colors ${
              filter === f
                ? "bg-blue-600 text-white"
                : "text-gray-600 hover:bg-gray-100"
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {loading && (
        <div className="py-12 text-center text-sm text-gray-500">
          Loading tasks...
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-center text-sm text-red-600">
          {error}
        </div>
      )}

      {!loading && !error && filteredTasks.length === 0 && (
        <div className="rounded-lg border border-dashed border-gray-300 bg-white p-12 text-center">
          {tasks.length === 0 ? (
            <p className="text-gray-500">
              No tasks yet — create your first task above!
            </p>
          ) : (
            <p className="text-gray-500">
              No {filter} tasks found.
            </p>
          )}
        </div>
      )}

      {!loading && !error && filteredTasks.length > 0 && (
        <div className="space-y-2">
          {filteredTasks.map((task) => (
            <TaskItem key={task.id} task={task} onUpdated={fetchTasks} />
          ))}
        </div>
      )}
    </div>
  );
}
