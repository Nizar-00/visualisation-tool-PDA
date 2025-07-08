import React from 'react';
import './LoginSkeleton.css';


function LoginSkeleton() {
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

        <div className="skeleton-line input"></div>
        <div className="skeleton-line input"></div>
        <div className="skeleton-line button"></div>
      </main>
    </div>
    
  );
}

export default LoginSkeleton;
