import React, { useState, useEffect } from 'react';
import Login from './Login';
import LoginSkeleton from './LoginSkeleton';
import './App.css';

function App() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 3000); // Simulate 3s loading
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="App">
      {loading ? <LoginSkeleton /> : <Login />}
    </div>
  );
}

export default App;
