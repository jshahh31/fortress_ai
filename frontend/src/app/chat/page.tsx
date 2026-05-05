"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { conversationsApi } from "@/lib/api";

export default function ChatRedirect() {
  const router = useRouter();

  useEffect(() => {
    async function initChat() {
      try {
        const api = await conversationsApi.create({ title: "New Analysis" });
        router.replace(`/chat/${api.id}`);
      } catch (err) {
        // Fallback to a local ID if backend fails
        const localId = Math.random().toString(36).substring(2, 11);
        router.replace(`/chat/${localId}`);
      }
    }
    initChat();
  }, [router]);

  return (
    <div className="flex h-screen items-center justify-center bg-background">
      <div className="flex flex-col items-center gap-4">
        <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        <p className="text-muted-foreground animate-pulse font-mono text-sm uppercase tracking-widest">
          Initializing Fortress AI...
        </p>
      </div>
    </div>
  );
}
