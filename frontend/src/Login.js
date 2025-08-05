import React, { useState, useEffect } from 'react';
import './Login.css';
import { FaUser, FaLock } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';

function Login() {
  const navigate = useNavigate();

  const [identifiant, setIdentifiant] = useState('');
  const [motdepasse, setMotdepasse] = useState('');
  const [erreur, setErreur] = useState(false);

  useEffect(() => {
    // Back button can’t go back from login
    window.history.pushState(null, '', window.location.href);

    const onPopState = () => {
      window.history.pushState(null, '', window.location.href);
    };

    window.addEventListener('popstate', onPopState);

    return () => {
      window.removeEventListener('popstate', onPopState);
    };
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (identifiant === 'admin' && motdepasse === 'admin') {
      setErreur(false);
      navigate('/dashboard');
      localStorage.setItem('isLoggedIn', 'true'); //  login flag
    } else {
      setErreur(true);
    }
  };

  return (
    <div className="login-page">
      <header className="login-header">
        <div className="top-banner">
          <img src="/logoMinistery.png" alt="logoMinistery" className="logoMinistery" />
          <span className="ministery-text">
            MINISTÈRE DE L'AGRICULTURE, DE LA PÊCHE MARITIME, DU<br />
            DÉVELOPPEMENT RURAL ET DES EAUX ET FORÊTS
          </span>
        </div>
      </header>

      <main className="login-box">
        <img src="/logompm.png" alt="Logo principal" className="logo" />

        <form className="login-form" onSubmit={handleSubmit}>
          <div className="input-wrapper">
            <FaUser className="input-icon" />
            <input
              placeholder="Identifiant"
              value={identifiant}
              onChange={(e) => setIdentifiant(e.target.value)}
            />
          </div>

          <div className="input-wrapper">
            <FaLock className="input-icon" />
            <input
              type="password"
              placeholder="Mot de Passe"
              value={motdepasse}
              onChange={(e) => setMotdepasse(e.target.value)}
            />
          </div>

          {erreur && <p className="error-message">Identifiants Incorrects</p>}

          <button type="submit">Se Connecter</button>

          <p className="forgot-password">Mot de passe oublié ?</p>
        </form>
      </main>
    </div>
  );
}

export default Login;
