/* ============================================================================
   pages/Login.jsx — Connexion / Inscription
   ============================================================================ */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login, register } = useAuth();
  const nav = useNavigate();
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [email, setEmail] = useState("");
  const [mdp, setMdp] = useState("");
  const [pseudo, setPseudo] = useState("");
  const [erreur, setErreur] = useState("");
  const [charge, setCharge] = useState(false);

  async function soumettre(e) {
    e.preventDefault();
    setErreur("");
    setCharge(true);
    try {
      if (mode === "login") await login(email, mdp);
      else await register(email, mdp, pseudo || null);
      nav("/");
    } catch (err) {
      setErreur(err.message);
    } finally {
      setCharge(false);
    }
  }

  return (
    <div style={{ maxWidth: 380, margin: "60px auto", textAlign: "center" }}>
      <h1 style={{ marginBottom: 8 }}>
        {mode === "login" ? "Bon retour" : "Créer un compte"}
      </h1>
      <p className="muet" style={{ marginBottom: 32 }}>
        {mode === "login"
          ? "Connecte-toi pour retrouver tes films."
          : "Quelques secondes pour commencer ta cinémathèque."}
      </p>

      <form onSubmit={soumettre} style={{ display: "flex", flexDirection: "column", gap: 12, textAlign: "left" }}>
        {mode === "register" && (
          <input
            className="champ"
            placeholder="Pseudo (optionnel)"
            value={pseudo}
            onChange={(e) => setPseudo(e.target.value)}
          />
        )}
        <input
          className="champ"
          type="email"
          placeholder="Email"
          value={email}
          required
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          className="champ"
          type="password"
          placeholder="Mot de passe (8 caractères min.)"
          value={mdp}
          required
          minLength={8}
          onChange={(e) => setMdp(e.target.value)}
        />

        {erreur && <span className="erreur">{erreur}</span>}

        <button className="btn" disabled={charge} style={{ marginTop: 8 }}>
          {charge ? "..." : mode === "login" ? "Se connecter" : "S'inscrire"}
        </button>
      </form>

      <p className="muet" style={{ marginTop: 24, fontSize: ".92rem" }}>
        {mode === "login" ? "Pas encore de compte ?" : "Déjà inscrit ?"}{" "}
        <button
          onClick={() => { setMode(mode === "login" ? "register" : "login"); setErreur(""); }}
          style={{ background: "none", border: "none", color: "var(--texte)", fontWeight: 600, textDecoration: "underline" }}
        >
          {mode === "login" ? "Inscris-toi" : "Connecte-toi"}
        </button>
      </p>
    </div>
  );
}
