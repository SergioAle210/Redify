import React, { useState } from 'react';
import { useNodes } from '../context/NodesContext';

function NodeAggregatedForm() {
  const { getAggregatedData, aggregated, aggLoading, aggError } = useNodes();
  const [label, setLabel] = useState('');
  const [property, setProperty] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!label || !property) return;
    try {
      await getAggregatedData({ label, property });
    } catch (err) {
      // Error will be handled in context state
    }
  };

  return (
    <div style={{ marginBottom: '1rem' }}>
      <form onSubmit={handleSubmit}>
        <label>Label: </label>
        <input 
          type="text" 
          value={label} 
          onChange={(e) => setLabel(e.target.value)} 
          placeholder="Ej: Persona" 
        />
        <label style={{ marginLeft: '1rem' }}>Propiedad numérica: </label>
        <input 
          type="text" 
          value={property} 
          onChange={(e) => setProperty(e.target.value)} 
          placeholder="Ej: edad" 
        />
        <button type="submit" disabled={aggLoading} style={{ marginLeft: '1rem' }}>
          {aggLoading ? 'Calculando...' : 'Consultar'}
        </button>
      </form>
      {aggError && <p style={{ color: 'red' }}>Error: {aggError}</p>}
      {aggregated && (
        <div style={{ marginTop: '0.5rem' }}>
          <p><strong>Resultados agregados:</strong></p>
          <p>Total nodos: {aggregated.count}</p>
          <p>Promedio {property}: {aggregated.avg}</p>
          <p>Máximo {property}: {aggregated.max}</p>
          <p>Mínimo {property}: {aggregated.min}</p>
          <p>Suma {property}: {aggregated.sum}</p>
        </div>
      )}
    </div>
  );
}

export default NodeAggregatedForm;
