"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";

export interface Child {
  id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string | null;
  deleted_at?: string | null;
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
}

const ActiveChildContext = createContext<ActiveChildContextType | undefined>(undefined);

export const ActiveChildProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeChild, setActiveChild] = useState<Child | null>(null);
  const [activeParentId, setActiveParentId] = useState<string | null>(null);
  const [childrenList, setChildrenList] = useState<Child[]>([]);
  const [loading, setLoading] = useState(true);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const refreshContext = useCallback(async () => {
    try {
      // 1. Resolve Sandbox Parent
      const parentRes = await fetch(`${apiUrl}/children/parent/sandbox`);
      if (!parentRes.ok) throw new Error("Failed to resolve sandbox parent.");
      const parentData: Parent = await parentRes.json();
      setActiveParentId(parentData.id);

      // Save parent_id to localStorage explicitly as part of sandbox requirements
      localStorage.setItem("neurolens_parent_id", parentData.id);

      // 2. Fetch children linked to parent
      const childrenRes = await fetch(`${apiUrl}/children?parent_id=${parentData.id}`);
      if (!childrenRes.ok) throw new Error("Failed to load child profiles.");
      const list: Child[] = await childrenRes.json();
      setChildrenList(list);

      // 3. Resolve Active Child selection from LocalStorage
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
        // Find if the persisted child ID is in the active list
        const activeMatch = list.find((c) => c.id === selectedChildId);
        if (activeMatch) {
          setActiveChild(activeMatch);
        } else {
          // Default to the first child (e.g. Sample Child) if no selection is saved
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
  }, [apiUrl]);

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

  useEffect(() => {
    refreshContext();
  }, [refreshContext]);

  return (
    <ActiveChildContext.Provider
      value={{
        activeChild,
        activeParentId,
        childrenList,
        loading,
        selectActiveChild,
        refreshContext,
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
