"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useRouter, usePathname } from "next/navigation";
import { API_BASE_URL } from "@/config";

export interface Child {
  id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string | null;
  deleted_at?: string | null;
  created_at?: string | null;
}

export interface Parent {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
}

interface ActiveChildContextType {
  activeChild: Child | null;
  activeParentId: string | null;
  childrenList: Child[];
  loading: boolean;
  selectActiveChild: (childId: string) => void;
  refreshContext: () => Promise<void>;
  token: string | null;
  setToken: (token: string | null) => void;
  logout: () => void;
  fetchWithAuth: (input: string, init?: RequestInit) => Promise<Response>;
}

const ActiveChildContext = createContext<ActiveChildContextType | undefined>(undefined);

export const ActiveChildProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeChild, setActiveChild] = useState<Child | null>(null);
  const [activeParentId, setActiveParentId] = useState<string | null>(null);
  const [childrenList, setChildrenList] = useState<Child[]>([]);
  const [loading, setLoading] = useState(true);
  const [token, setTokenState] = useState<string | null>(null);

  const router = useRouter();
  const pathname = usePathname();
  const apiUrl = API_BASE_URL;

  const setToken = useCallback((newToken: string | null) => {
    setTokenState(newToken);
    if (newToken) {
      localStorage.setItem("neurolens_auth_token", newToken);
    } else {
      localStorage.removeItem("neurolens_auth_token");
    }
  }, []);

  const logout = useCallback(() => {
    setTokenState(null);
    setActiveChild(null);
    setActiveParentId(null);
    setChildrenList([]);
    localStorage.removeItem("neurolens_auth_token");
    localStorage.removeItem("neurolens_active_selection");
    localStorage.removeItem("neurolens_parent_id");
    router.push("/login");
  }, [router]);

  const fetchWithAuth = useCallback(async (url: string, init?: RequestInit): Promise<Response> => {
    const savedToken = localStorage.getItem("neurolens_auth_token") || token;
    
    // Build headers with bearer token and default application/json Content-Type
    const headers: Record<string, string> = {
      ...(savedToken ? { "Authorization": `Bearer ${savedToken}` } : {})
    };

    // If init contains headers, merge them
    if (init?.headers) {
      if (init.headers instanceof Headers) {
        init.headers.forEach((value, key) => {
          headers[key] = value;
        });
      } else if (Array.isArray(init.headers)) {
        init.headers.forEach(([key, value]) => {
          headers[key] = value;
        });
      } else {
        Object.assign(headers, init.headers);
      }
    }

    // Default to application/json if Content-Type not set and method is POST/PUT
    const method = init?.method?.toUpperCase() || "GET";
    if (!headers["Content-Type"] && !headers["content-type"] && (method === "POST" || method === "PUT" || method === "PATCH")) {
      headers["Content-Type"] = "application/json";
    }

    const res = await fetch(url, {
      ...init,
      headers
    });
    
    if (res.status === 401 && !url.includes("/auth/login")) {
      logout();
    }
    return res;
  }, [token, logout]);

  const refreshContext = useCallback(async () => {
    const savedToken = localStorage.getItem("neurolens_auth_token") || token;
    if (!savedToken) {
      setLoading(false);
      return;
    }

    try {
      // Fetch children linked to parent
      const childrenRes = await fetchWithAuth(`${apiUrl}/children`);
      if (childrenRes.status === 401) {
        logout();
        return;
      }
      if (!childrenRes.ok) throw new Error("Failed to load child profiles.");
      const rawList: Child[] = await childrenRes.json();
      const list = rawList.map((c) => {
        if (c.first_name === "Demo Child" && c.last_name === "A") {
          return { ...c, first_name: "Rohan", last_name: "Verma" };
        }
        if (c.first_name === "Demo Child" && c.last_name === "B") {
          return { ...c, first_name: "Emma", last_name: "Smith" };
        }
        if (c.first_name === "Demo Child" && c.last_name === "C") {
          return { ...c, first_name: "Liam", last_name: "Carter" };
        }
        return c;
      });
      setChildrenList(list);

      const parentId = localStorage.getItem("neurolens_parent_id");
      if (parentId) {
        setActiveParentId(parentId);
      }

      // Resolve Active Child selection from LocalStorage
      const persistedStateRaw = localStorage.getItem("neurolens_active_selection");
      let selectedChildId: string | null = null;
      
      if (persistedStateRaw) {
        try {
          const parsed = JSON.parse(persistedStateRaw);
          if (parsed && parsed.activeChildId) {
            selectedChildId = parsed.activeChildId;
          }
        } catch (e) {
          console.warn("Failed to parse persisted active child state", e);
        }
      }

      if (list.length > 0) {
        const activeMatch = list.find((c) => c.id === selectedChildId);
        if (activeMatch) {
          setActiveChild(activeMatch);
        } else {
          setActiveChild(list[0]);
          localStorage.setItem(
            "neurolens_active_selection",
            JSON.stringify({
              activeChildId: list[0].id,
              lastSelectedAt: new Date().toISOString(),
            })
          );
        }
      } else {
        setActiveChild(null);
      }
    } catch (err) {
      console.warn("Could not connect to Neurolens API.", err);
    } finally {
      setLoading(false);
    }
  }, [apiUrl, logout, fetchWithAuth, token]);

  const selectActiveChild = (childId: string) => {
    const matched = childrenList.find((c) => c.id === childId);
    if (matched) {
      setActiveChild(matched);
      localStorage.setItem(
        "neurolens_active_selection",
        JSON.stringify({
          activeChildId: childId,
          lastSelectedAt: new Date().toISOString(),
        })
      );
    }
  };

  // Sync token from localStorage on mount
  useEffect(() => {
    const savedToken = localStorage.getItem("neurolens_auth_token");
    if (savedToken) {
      setTokenState(savedToken);
    } else {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const savedToken = localStorage.getItem("neurolens_auth_token") || token;
    if (savedToken) {
      refreshContext();
    }
  }, [token, refreshContext]);

  // Protect pages: redirect to login if not authenticated
  useEffect(() => {
    const savedToken = localStorage.getItem("neurolens_auth_token");
    if (!loading && !savedToken && pathname !== "/login") {
      router.push("/login");
    }
  }, [loading, pathname, router, token]);

  return (
    <ActiveChildContext.Provider
      value={{
        activeChild,
        activeParentId,
        childrenList,
        loading,
        selectActiveChild,
        refreshContext,
        token,
        setToken,
        logout,
        fetchWithAuth,
      }}
    >
      {children}
    </ActiveChildContext.Provider>
  );
};

export const useActiveChild = () => {
  const context = useContext(ActiveChildContext);
  if (context === undefined) {
    throw new Error("useActiveChild must be used within an ActiveChildProvider");
  }
  return context;
};
