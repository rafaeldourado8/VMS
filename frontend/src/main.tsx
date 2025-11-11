import React from 'react';
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import { QueryProvider } from "./components/QueryProvider";
import { ToastProvider } from "./components/ToastProvider";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryProvider>
      <ToastProvider>
        <App />
      </ToastProvider>
    </QueryProvider>
  </React.StrictMode>
);
