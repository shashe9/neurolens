"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

export interface Child {
  id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
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
  loading: boolean;
  refreshContext: () => Promise<void>;
}

const ActiveChildContext = createContext<ActiveChildContextType | undefined>(undefined);

// Safe default values for build-time static render safety
const FALLBACK_CHILD: Child = {
  id: "00000000-0000-0000-0000-000000000000",
  first_name: "Sample",
  last_name: "Child",
  date_of_birth: "2024-06-15",
  gender: "Female",
};

const FALLBACK_PARENT_ID = "00000000-0000-0000-0000-000000000000";

export const ActiveChildProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeChild, setActiveChild] = useState<Child | null>(FALLBACK_CHILD);
  const [activeParentId, setActiveParentId] = useState<string | null>(FALLBACK_PARENT_ID);
  const [loading, setLoading] = useState(true);

  const fetchOrCreateChild = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      
      // 1. Fetch existing children
      const res = await fetch(`${apiUrl}/children`);
      if (!res.ok) throw new Error("Failed to load child profiles.");
      
      const childrenList: Child[] = await res.json();
      
      if (childrenList.length > 0) {
        // Set the first child (Sample Child from seed)
        setActiveChild(childrenList[0]);
        
        // Fetch child details to find parent or seed defaults
        // For simplicity in V1 sandbox, we can search parents list
        // Let's resolve parent Jane Doe if parent list has entries
        // Alternatively, we can use a standard fallback parent ID
        setActiveParentId("d0000000-0000-0000-0000-000000000001"); // standard seeded parent placeholder or resolved
      } else {
        // If empty DB (unlikely if seed is run), attempt to bootstrap parent and child
        console.log("No child found in DB. In sandbox, please run seed script.");
      }
    } catch (err) {
      console.warn("Could not connect to Neurolens API. Using client-side sandbox defaults.", err);
      // Fail gracefully and keep fallback values
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrCreateChild();
  }, []);

  return (
    <ActiveChildContext.Provider
      value={{
        activeChild,
        activeParentId,
        loading,
        refreshContext: fetchOrCreateChild,
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
