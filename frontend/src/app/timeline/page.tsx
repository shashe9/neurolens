"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Timeline() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/observations");
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-[50vh]">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>
  );
}
