"use client";

import { useState } from "react";
import { useChatKit, ChatKit } from "@openai/chatkit-react";
import { getJwtToken } from "@/lib/chat";

export function ChatInterface() {
  const [isResponding, setIsResponding] = useState(false);

  const chatkit = useChatKit({
    api: {
      url: "/api/chatkit",
      domainKey: "local-dev",
      fetch: async (url: string | URL | Request, options?: RequestInit) => {
        const token = await getJwtToken();
        return fetch(url, {
          ...options,
          headers: {
            ...options?.headers,
            Authorization: `Bearer ${token}`,
          },
        });
      },
    },
    onResponseStart: () => setIsResponding(true),
    onResponseEnd: () => setIsResponding(false),
    onError: ({ error }: { error: Error }) => {
      console.error("ChatKit error:", error);
    },
  });

  const handleNewChat = () => {
    chatkit.setThreadId(null);
  };

  return (
    <div className="flex h-full flex-col" style={{ minHeight: "55vh" }}>
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-2">
        <span className="text-sm font-medium text-gray-700">Conversation</span>
        <button
          onClick={handleNewChat}
          className="rounded-md bg-gray-100 px-3 py-1 text-sm font-medium text-gray-700 hover:bg-gray-200 transition-colors"
        >
          New Chat
        </button>
      </div>
      <div className="flex-1 relative" style={{ minHeight: "50vh" }}>
        <ChatKit
          control={chatkit.control}
          style={{ width: "100%", height: "100%", position: "absolute", inset: 0 }}
        />
      </div>
      {isResponding && (
        <div className="px-4 py-2 text-center text-sm text-gray-500">
          Thinking...
        </div>
      )}
    </div>
  );
}
