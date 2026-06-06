/* ============================================================================
   context/AuthContext.jsx — État global d'authentification
   ----------------------------------------------------------------------------
   Fournit à toute l'application : l'utilisateur connecté (ou null), et les
   fonctions login / register / logout. N'importe quel composant peut faire
   `const { user, login } = useAuth()`.
   ============================================================================ */

import { createContext, useContext, useEffect, useState } from "react";
import { api, setToken, getToken } from "../lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [pret, setPret] = useState(false); // a-t-on fini de vérifier le token ?

  // Au démarrage : si un token existe déjà, on récupère l'utilisateur.
  useEffect(() => {
    async function init() {
      if (getToken()) {
        try {
          setUser(await api.moi());
        } catch {
          setToken(null); // token expiré/invalide
        }
      }
      setPret(true);
    }
    init();
  }, []);

  async function login(email, mdp) {
    const { access_token } = await api.login(email, mdp);
    setToken(access_token);
    setUser(await api.moi());
  }

  async function register(email, mdp, pseudo) {
    await api.register(email, mdp, pseudo);
    await login(email, mdp); // connecte directement après inscription
  }

  function logout() {
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, pret, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
