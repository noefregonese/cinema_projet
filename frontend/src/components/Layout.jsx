/* ============================================================================
   components/Layout.jsx — En-tête de navigation + cadre de page
   ============================================================================ */

import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const loc = useLocation();
  const nav = useNavigate();

  const lien = (to, label) => (
    <Link
      to={to}
      style={{
        padding: "6px 2px",
        color: loc.pathname === to ? "var(--texte)" : "var(--texte-doux)",
        borderBottom:
          loc.pathname === to ? "2px solid var(--texte)" : "2px solid transparent",
        fontWeight: 500,
        transition: "color .15s ease",
      }}
    >
      {label}
    </Link>
  );

  return (
    <>
      <header
        style={{
          borderBottom: "1px solid var(--bordure)",
          background: "var(--surface)",
          position: "sticky",
          top: 0,
          zIndex: 10,
        }}
      >
        <div
          className="conteneur"
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            height: 68,
          }}
        >
          <Link
            to="/"
            style={{
              fontFamily: "var(--font-titre)",
              fontWeight: 600,
              fontSize: "1.5rem",
              letterSpacing: "-0.02em",
            }}
          >
            Cinéma<span style={{ color: "var(--etoile)" }}>.</span>
          </Link>

          <nav style={{ display: "flex", gap: 28, alignItems: "center" }}>
            {user && lien("/", "Recommandations")}
            {user && lien("/enrichir", "Enrichir mon profil")}
            {user && lien("/j-ai-visionne", "J'ai visionné")}
            {user && lien("/ma-filmotheque", "Ma filmothèque")}
            {user ? (
              <button className="btn btn-fantome" onClick={() => { logout(); nav("/login"); }}>
                Déconnexion
              </button>
            ) : (
              <Link to="/login" className="btn">Connexion</Link>
            )}
          </nav>
        </div>
      </header>

      <main className="conteneur" style={{ padding: "40px 24px 80px" }}>
        {children}
      </main>
    </>
  );
}
