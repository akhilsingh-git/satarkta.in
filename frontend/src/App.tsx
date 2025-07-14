import React from 'react';
// Fix: Check if your file is Dashboard.tsx (capital D) or dashboard.tsx (lowercase d)
import Dashboard from '../components/dashboard/Dashboard'; // Adjust path based on actual file name
import './App.css';

function App() {
  return (
    <div className="App">
      <Dashboard />
    </div>
  );
}

export default App;