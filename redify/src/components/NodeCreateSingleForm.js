import React, { useState } from 'react';
import { useNodes } from '../context/NodesContext';

function NodeCreateSingleForm() {
  const { createNodeSingle } = useNodes();
  const [label, setLabel] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    if (!label) {
      setError('Debe proporcionar un label.');
      return;
    }
    try {
      const result = await createNodeSingle({ label });
      if (result.node) {
        setMessage(`Nodo creado. ID: ${result.node.id}, Labels: ${result.node.labels.join(', ')}`);
      } else {
        setMessage(result.message || 'Nodo creado.');
      }
      setLabel('');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={{ marginBottom: '1rem' }}>
      <h3>Crear Nodo (un solo label)</h3>
      <form onSubmit={handleSubmit}>
        <input 
          type="text" 
          value={label} 
          onChange={(e) => setLabel(e.target.value)} 
          placeholder="Label del nodo" 
        />
        <button type="submit">Crear</button>
      </form>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
    </div>
  );
}

export default NodeCreateSingleForm;
