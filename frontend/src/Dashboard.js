import React, { useEffect, useState } from 'react';
import './Dashboard.css';
import { useNavigate } from 'react-router-dom';
import useNoPagePrecedente from './useNoPagePrecedente';
import DashboardSkeleton from './DashboardSkeleton';
import DatePicker, { registerLocale } from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { fr } from 'date-fns/locale';

registerLocale('fr', fr);



function Dashboard() {
  const navigate = useNavigate();
  useNoPagePrecedente();
  const [entite, setEntite] = useState('');
  const [port, setPort] = useState('');
  const [pdaNumber, setPdaNumber] = useState('');

const [loading, setLoading] = useState(true);

useEffect(() => {
  const isLoggedIn = localStorage.getItem("isLoggedIn");
  if (!isLoggedIn) {
    navigate("/", { replace: true });
  } else {
    setTimeout(() => setLoading(false), 1200); //loading simulated
  }
}, [navigate]);
  
const today = new Date();
const [startDate, setStartDate] = useState(today);
const [endDate, setEndDate] = useState(today); //date set by default to today's date. changed to french format from initial html integrateed date system.


  useEffect(() => {
    const isLoggedIn = localStorage.getItem("isLoggedIn");
    if (!isLoggedIn) {
      navigate("/", { replace: true });
    }
  }, [navigate]);

  const handleLogout = (e) => {
    e.preventDefault();
    localStorage.removeItem("isLoggedIn");
    navigate('/', { replace: true });
  };

  if (loading) return <DashboardSkeleton />;

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div className="top-banner">
          <img src="/logoMinistery.png" alt="logoMinistery" className="logoMinistery" />
          <span className="ministery-text">
            MINISTÈRE DE L'AGRICULTURE, DE LA PÊCHE MARITIME, DU<br />
            DÉVELOPPEMENT RURAL ET DES EAUX ET FORÊTS
          </span>

          <button className="logout-button" onClick={handleLogout}>Se déconnecter</button>
        </div>
      </header>

      <div className="dashboard-main">
<aside className="filters-panel">
  <h4>Période</h4>
  <label>Début</label>
<DatePicker
  selected={startDate}
  onChange={date => setStartDate(date)}
  dateFormat="dd/MM/yyyy"
  locale="fr"
  className="custom-datepicker"
/>  
<label>Fin</label>
  <DatePicker
  selected={endDate}
  onChange={date => setEndDate(date)}
  dateFormat="dd/MM/yyyy"
  locale="fr"
  className="custom-datepicker"
/>



<label>Entité</label>
<select value={entite} onChange={e => setEntite(e.target.value)}>
  <option value="" disabled hidden>Sélectionner</option>
  <option value="dakhla">Dakhla</option>
  <option value="agadir">Agadir</option>
  <option value="laayoune">Laayoune</option>
</select>

<label>Port</label>
<select disabled={!entite} value={port} onChange={e => setPort(e.target.value)}>
  <option value="" disabled hidden>Sélectionner</option>
  <option value="port1">Port 1</option>
  <option value="port2">Port 2</option>
</select>

<label>Numéro PDA</label>
<div className="input-prefix-wrapper">
  <span className="input-prefix">PDA</span>
  <input
    type="text"
    value={pdaNumber}
    onChange={e => setPdaNumber(e.target.value)}
    placeholder="Numéro"
  />
</div>

  <div className="export-section">
    <button className="export-button">Exporter</button>
  </div>

</aside>


        <section className="dashboard-content">
          <div className="top-cards">
            <div className="card">
              <p className="card-title">PDA actif récent</p>
              <h3>PDA 305</h3>
            </div>
            <div className="card">
              <p className="card-title">Nombre total des PDAs</p>
              <h3>390</h3>
            </div>
            <div className="card warning">
              <p className="card-title">Nombres de PDA Inactifs</p>
              <h3>16</h3>
            </div>
          </div>

          <div className="charts">
            <div className="chart pie">
              <h4>Top 5 entités par volume de déclarations</h4>
              <img src="/mock_piechart.png" alt="Pie Chart" />
              <ul className="chart-legend">
                <li>Dakhla - 22,1%</li>
                <li>Agadir - 20,7%</li>
                <li>Laayoune - 19,3%</li>
                <li>Casablanca - 17,8%</li>
                <li>Safi - 14,5%</li>
              </ul>
            </div>

            <div className="chart bar">
              <h4>Déclarations totales au cours des 7 derniers jours</h4>
              <img src="/mock_barchart.png" alt="Bar Chart" />
            </div>
          </div>

          <div className="data-table">
            <table>
              <thead>
                <tr>
                  <th>Entité</th>
                  <th>Port</th>
                  <th>Nombre de déclarations</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>Dakhla</td><td>Dakhla</td><td>58</td></tr>
                <tr><td>Casablanca</td><td>Casablanca</td><td>90</td></tr>
                <tr><td>Laayoune</td><td>Laayoune</td><td>61</td></tr>
                <tr><td>Agadir</td><td>Agadir</td><td>9</td></tr>
                <tr><td>Safi</td><td>Safi</td><td>15</td></tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
}

export default Dashboard;
