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
  const [dashboardData, setDashboardData] = useState(null);
  const navigate = useNavigate();
  useNoPagePrecedente();
  const [entite, setEntite] = useState('');
  const [port, setPort] = useState('');
  const [pdaNumber, setPdaNumber] = useState('');

  const [entites, setEntites] = useState([]);
  const [ports, setPorts] = useState([]);

  const [loading, setLoading] = useState(true);


  useEffect(() => {
    fetch('http://localhost:5000/api/entites_mere')
      .then(res => res.json())
      .then(data => setEntites(data))
      .catch(err => console.error('Failed to fetch entites:', err));
  }, []);

 
  useEffect(() => {
    if (!entite) {
      setPorts([]);
      setPort('');
      return;
    }
    fetch(`http://localhost:5000/api/ports?entiteCode=${encodeURIComponent(entite)}`)
      .then(res => res.json())
      .then(data => setPorts(data))
      .catch(err => console.error('Failed to fetch ports:', err));
  }, [entite]);


  useEffect(() => {
    const isLoggedIn = localStorage.getItem("isLoggedIn");
    if (!isLoggedIn) {
      navigate("/", { replace: true });
    } else {
      setTimeout(() => setLoading(false), 1200);
    }
  }, [navigate]);

  
  useEffect(() => {
    const isLoggedIn = localStorage.getItem("isLoggedIn");
    if (!isLoggedIn) {
      navigate("/", { replace: true });
    }
  }, [navigate]);

  const today = new Date();
  const [startDate, setStartDate] = useState(today);
  const [endDate, setEndDate] = useState(today);

 
  const entiteName = entites.find(e => e.code === entite)?.name || '';

  function fetchDataBasedOnFilters({ entiteName, port, pdaNumber, startDate, endDate }) {
    const start_date = startDate.toISOString().split('T')[0];
    const end_date = endDate.toISOString().split('T')[0];

    if (pdaNumber && pdaNumber.trim() !== '') {
      return fetch('http://localhost:5000/api/declarations/count_par_pda', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pda_code: pdaNumber.trim(),
          start_date,
          end_date,
        }),
      }).then(res => res.json());
    }

    if (port) {

      const selectedPortName = ports.find(p => p.code === port)?.name || port;
      return fetch('http://localhost:5000/api/declarations/count_par_port', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          port_name: selectedPortName,
          start_date,
          end_date,
        }),
      }).then(res => res.json());
    }

    if (entiteName) {
      return fetch('http://localhost:5000/api/declarations/count_par_entite_mere_nom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          entite_mere_nom: entiteName,
          start_date,
          end_date,
        }),
      }).then(res => res.json());
    }

    return fetch('http://localhost:5000/api/declarations/count_par_ports_all', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        start_date,
        end_date,
      }),
    }).then(res => res.json());
  }

  useEffect(() => {
    if (!entite && !port && !pdaNumber) {
      setDashboardData(null);
      return;
    }

    fetchDataBasedOnFilters({ entiteName, port, pdaNumber, startDate, endDate })
      .then(data => {
        if (data.error) {
          setDashboardData(null);
          console.error('Backend error:', data.error);
          return;
        }

        let totalPDAs = 0;
        let pieData = [];
        let tableData = [];
        let recentPDA = pdaNumber ? `PDA ${pdaNumber.trim()}` : 'N/A';

        if (Array.isArray(data)) {
          totalPDAs = data.reduce((acc, row) => acc + (row.nombre_declarations_new_pda || 0), 0);
          pieData = data.map(row => `${row.entite_mere_nom || row.entite_nom || 'Inconnu'} - ${row.nombre_declarations_new_pda}`);
          tableData = data.map(row => [
            row.entite_mere_code || row.entite_code || '',
            row.entite_mere_nom || row.entite_nom || '',
            row.nombre_declarations_new_pda || 0,
          ]);
        } else if (typeof data === 'object') {
          totalPDAs = data.total_declarations_distinct || 0;
          pieData = [ `PDA ${pdaNumber.trim()} - ${totalPDAs}` ];
          tableData = [[ pdaNumber.trim(), 'N/A', totalPDAs ]];
        }

        setDashboardData({
          recentPDA,
          totalPDAs,
          inactivePDAs: 0, // placeholder
          pieData,
          barChartImg: '/mock_barchart.png',
          tableData,
        });
      })
      .catch(err => {
        console.error('Fetch error:', err);
        setDashboardData(null);
      });
  }, [entite, port, pdaNumber, startDate, endDate, entiteName, ports]);

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
            {entites.map(e => (
              <option key={e.code} value={e.code}>{e.name}</option>
            ))}
          </select>

          <label>Port</label>
          <select disabled={!entite} value={port} onChange={e => setPort(e.target.value)}>
            <option value="" disabled hidden>Sélectionner</option>
            {ports.map(p => (
              <option key={p.code} value={p.code}>{p.name}</option>
            ))}
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
            <button className="export-button" disabled>Exporter (à implémenter)</button>
          </div>
        </aside>

        <section className="dashboard-content">
          <div className="top-cards">
            <div className="card">
              <p className="card-title">PDA actif récent</p>
              <h3>{dashboardData?.recentPDA || '...'}</h3>
            </div>
            <div className="card">
              <p className="card-title">Nombre total des PDAs</p>
              <h3>{dashboardData?.totalPDAs ?? '...'}</h3>
            </div>
            <div className="card warning">
              <p className="card-title">Nombres de PDA Inactifs</p>
              <h3>{dashboardData?.inactivePDAs ?? '...'}</h3>
            </div>
          </div>

          <div className="charts">
            <div className="chart pie">
              <h4>Top 5 entités par volume de déclarations</h4>
              <img src="/mock_piechart.png" alt="Pie Chart" />
              <ul className="chart-legend">
                {dashboardData?.pieData?.map((item, index) => (
                  <li key={index}>{item}</li>
                )) || <li>...</li>}
              </ul>
            </div>

            <div className="chart bar">
              <h4>Déclarations totales au cours des 7 derniers jours</h4>
              <img src={dashboardData?.barChartImg || "/mock_barchart.png"} alt="Bar Chart" />
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
                {dashboardData?.tableData?.length > 0 ? (
                  dashboardData.tableData.map((row, index) => (
                    <tr key={index}>
                      <td>{row[0]}</td>
                      <td>{row[1]}</td>
                      <td>{row[2]}</td>
                    </tr>
                  ))
                ) : (
                  <tr><td colSpan="3">Aucune donnée disponible</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
}

export default Dashboard;
