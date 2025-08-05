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
        <div className="logo-skeleton shimmer"></div>

        <form className="login-form-skeleton">
          <div className="input-wrapper-skeleton">
            <div className="input-icon-skeleton shimmer" />
            <div className="input-line-skeleton shimmer" />
          </div>

          <div className="input-wrapper-skeleton">
            <div className="input-icon-skeleton shimmer" />
            <div className="input-line-skeleton shimmer" />
          </div>

          <div className="button-skeleton shimmer" />

          <div className="forgot-password-skeleton shimmer" />
        </form>
      </main>
    </div>
  );
}

export default LoginSkeleton;
