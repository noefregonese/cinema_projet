/* ============================================================================
   main.jsx — Point d'entrée : monte l'application React dans la page.
   ============================================================================ */

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
