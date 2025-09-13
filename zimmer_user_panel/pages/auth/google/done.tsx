"use client";
import { useEffect } from "react";
import { useRouter } from "next/router";
import { setAccessToken } from "@/lib/authClient";

export default function GoogleDone() {
  const router = useRouter();
  
  useEffect(() => {
    try {
      const hash = typeof window !== "undefined" ? window.location.hash : "";
      const params = new URLSearchParams(hash.replace(/^#/, ""));
      const token = params.get("access_token");
      const error = params.get("error");
      
      if (error) {
        // Redirect back to login with error query
        router.replace(`/login?error=${encodeURIComponent(error)}`);
        return;
      }
      
      if (token) {
        setAccessToken(token); // Use in-memory setter
        // Also store in localStorage to match main API client
        if (typeof window !== 'undefined') {
          localStorage.setItem("access_token", token);
        }
        router.replace("/dashboard"); // or "/"
      } else {
        router.replace("/login?error=token_missing");
      }
    } catch {
      router.replace("/login?error=unexpected");
    }
  }, [router]);
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-green-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 text-center">
          <div className="w-20 h-20 bg-gradient-to-br from-purple-600 to-purple-700 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
            <span className="text-white font-bold text-3xl">Z</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">در حال تکمیل ورود...</h1>
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          </div>
        </div>
      </div>
    </div>
  );
}
