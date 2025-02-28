
import { useState, useEffect } from "react";
import { toast } from "@/components/ui/use-toast";
import Dashboard from "@/components/Dashboard";

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-blue-50">
      <header className="bg-white/80 backdrop-blur-sm shadow-sm py-4 px-6 mb-6">
        <div className="container mx-auto flex items-center justify-between">
          <h1 className="text-2xl md:text-3xl font-bold text-green-700 flex items-center gap-2">
            <span className="text-3xl">🌱</span> GreenGuard
            <span className="text-green-500 hidden md:inline">Smart Irrigation System</span>
          </h1>
          <div className="text-sm text-gray-500">Powered by AI</div>
        </div>
      </header>

      <main>
        <Dashboard />
      </main>
      
      <footer className="mt-12 py-6 bg-white/60 backdrop-blur-sm border-t border-gray-100">
        <div className="container mx-auto text-center text-gray-500 text-sm">
          <p>© 2025 GreenGuard - AI-Powered Smart Irrigation System</p>
          <p className="mt-1">Saving water, one drop at a time.</p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
