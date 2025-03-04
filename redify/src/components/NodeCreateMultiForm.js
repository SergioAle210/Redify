import React, { useState } from 'react';
import { useNodes } from '../context/NodesContext';

function NodeCreateMultiForm() {
  const { createNodeMultiple } = useNodes();
  const [labelsInput, setLabelsInput] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    const labelsArray = labelsInput.split(',').map(lbl => lbl.trim()).filter(lbl => lbl);
    if (labelsArray.length < 2) {
      setError('Proporcione al menos dos labels.');
      return;
    }
    try {
      const result = await createNodeMultiple({ labels: labelsArray });
      if (result.node) {
        setMessage(`Nodo creado. ID: ${result.node.id}, Labels: ${result.node.labels.join(', ')}`);
      } else {
        setMessage(result.message || 'Nodo con múltiples labels creado.');
      }
      setLabelsInput('');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={{ marginBottom: '1rem' }}>
      <h3>Crear Nodo (múltiples labels)</h3>
      <form onSubmit={handleSubmit}>
        <input 
          type="text" 
          value={labelsInput} 
          onChange={(e) => setLabelsInput(e.target.value)} 
          placeholder="Labels separados por coma" 
        />
        <button type="submit">Crear</button>
      </form>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
    </div>
  );
}

export default NodeCreateMultiForm;
