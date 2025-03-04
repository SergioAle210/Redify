import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import NodeManagementPage from './pages/NodeManagementPage';
import RelationshipManagementPage from './pages/RelationshipManagementPage';
import "./index.css"
function App() {
  return (
    <Router>
      <div>
        <nav className="navbar">
          <Link to="/nodes" className="nav-link">Gestionar Nodos</Link>
          <Link to="/relationships" className="nav-link">Gestionar Relaciones</Link>
        </nav>
        <div style={{ padding: '1rem' }}>
          <Routes>
            <Route path="/" element={<Navigate to="/nodes" replace />} />
            <Route path="/nodes" element={<NodeManagementPage />} />
            <Route path="/relationships" element={<RelationshipManagementPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
