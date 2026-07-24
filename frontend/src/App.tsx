import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import "./App.css";
import { DashboardPage } from "./pages/DashboardPage";
import { ShortenPage } from "./pages/ShortenPage";

const queryClient = new QueryClient();

type Tab = "shorten" | "dashboard";

function AppShell() {
  const [tab, setTab] = useState<Tab>("shorten");

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>URL Shortener</h1>
        <nav className="tabs">
          <button
            type="button"
            className={tab === "shorten" ? "tab active" : "tab"}
            onClick={() => setTab("shorten")}
          >
            Shorten
          </button>
          <button
            type="button"
            className={tab === "dashboard" ? "tab active" : "tab"}
            onClick={() => setTab("dashboard")}
          >
            Dashboard
          </button>
        </nav>
      </header>
      <main>{tab === "shorten" ? <ShortenPage /> : <DashboardPage />}</main>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppShell />
    </QueryClientProvider>
  );
}
