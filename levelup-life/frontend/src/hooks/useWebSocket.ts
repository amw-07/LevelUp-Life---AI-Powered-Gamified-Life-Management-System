import { useEffect, useRef, useCallback } from "react";
import { useAuthStore } from "../store/authStore";
import type { WsEvent, WsEventType } from "../types";

type EventHandler = (payload: Record<string, unknown>) => void;

interface UseWebSocketOptions {
  userId: string | null;
  onEvent?: (event: WsEvent) => void;
  handlers?: Partial<Record<WsEventType, EventHandler>>;
}

const RECONNECT_DELAY_MS = 3000;
const MAX_RECONNECT_ATTEMPTS = 10;

export function useWebSocket({ userId, onEvent, handlers }: UseWebSocketOptions) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isMounted = useRef(true);
  const token = useAuthStore((s) => s.token);

  const connect = useCallback(() => {
    if (!userId || !token || !isMounted.current) return;

    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const host = window.location.host;
    const url = `${protocol}://${host}/ws/${userId}`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      reconnectAttempts.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const data: WsEvent = JSON.parse(event.data as string);
        onEvent?.(data);
        handlers?.[data.type]?.(data.payload);
      } catch {
        // ignore malformed messages
      }
    };

    ws.onclose = () => {
      if (!isMounted.current) return;
      if (reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts.current += 1;
        reconnectTimeout.current = setTimeout(connect, RECONNECT_DELAY_MS);
      }
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [userId, token, onEvent, handlers]);

  useEffect(() => {
    isMounted.current = true;
    connect();

    return () => {
      isMounted.current = false;
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      wsRef.current?.close();
    };
  }, [connect]);

  const send = useCallback((data: Record<string, unknown>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  return { send };
}
