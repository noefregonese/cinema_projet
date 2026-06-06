/* ============================================================================
   App.jsx — Routage de l'application
   ----------------------------------------------------------------------------
   Définit les pages et protège celles réservées aux utilisateurs connectés :
   si on n'est pas connecté, on est redirigé vers /login.
   ============================================================================ */

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Recommandations from "./pages/Recommandations";
import Enrichir from "./pages/Enrichir";
import JaiVisionne from "./pages/JaiVisionne";
import Filmotheque from "./pages/Filmotheque";
import Bientot from "./pages/Bientot";

// Enveloppe une page : accessible seulement si connecté.
function Protege({ children }) {
  const { user, pret } = useAuth();
  if (!pret) return <Layout><p className="muet">Chargement…</p></Layout>;
  if (!user) return <Navigate to="/login" replace />;
  return <Layout>{children}</Layout>;
}

function Routage() {
  const { user, pret } = useAuth();
  return (
    <Routes>
      <Route
        path="/login"
        element={pret && user ? <Navigate to="/" replace /> : <Layout><Login /></Layout>}
      />
      <Route path="/" element={<Protege><Recommandations /></Protege>} />
      <Route path="/enrichir" element={<Protege><Enrichir /></Protege>} />
      <Route path="/j-ai-visionne" element={<Protege><JaiVisionne /></Protege>} />
      <Route path="/ma-filmotheque" element={<Protege><Filmotheque /></Protege>} />
      <Route path="/bientot" element={<Protege><Bientot /></Protege>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routage />
      </BrowserRouter>
    </AuthProvider>
  );
}
