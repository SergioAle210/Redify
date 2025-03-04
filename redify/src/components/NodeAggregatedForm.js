import React, { useState } from 'react';
import { useNodes } from '../context/NodesContext';
import '../styles/NodeAggregatedForm.css'; // Importa el CSS

function NodeAggregatedForm() {
  const { getAggregatedData, aggregated, aggLoading, aggError } = useNodes();
  const [label, setLabel] = useState('');
  const [property, setProperty] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!label || !property) return;
    try {
      await getAggregatedData({ label, property });
    } catch (err) {}
  };

  return (
    <div className="aggregated-form-container">
      <h2>Análisis Agregado de Datos</h2>
      <form onSubmit={handleSubmit} className="aggregated-form">
        <div className="input-group">
          <label>Label:</label>
          <input 
            type="text" 
            value={label} 
            onChange={(e) => setLabel(e.target.value)} 
            placeholder="Ej: Persona"
          />
        </div>
        <div className="input-group">
          <label>Propiedad numérica:</label>
          <input 
            type="text" 
            value={property} 
            onChange={(e) => setProperty(e.target.value)} 
            placeholder="Ej: edad"
          />
        </div>
        <button type="submit" disabled={aggLoading} className="submit-btn">
          {aggLoading ? 'Calculando...' : 'Consultar'}
        </button>
      </form>

      {aggError && <p className="error-msg">Error: {aggError}</p>}

      {aggregated && (
        <div className="results-container">
          <p><strong>Resultados agregados:</strong></p>
          <p><span>Total nodos:</span> {aggregated.count}</p>
          <p><span>Promedio {property}:</span> {aggregated.avg}</p>
          <p><span>Máximo {property}:</span> {aggregated.max}</p>
          <p><span>Mínimo {property}:</span> {aggregated.min}</p>
          <p><span>Suma {property}:</span> {aggregated.sum}</p>
        </div>
      )}
    </div>
  );
}

export default NodeAggregatedForm;
