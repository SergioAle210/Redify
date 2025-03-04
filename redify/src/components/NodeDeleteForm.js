import React, { useState } from 'react';
import { useNodes } from '../context/NodesContext';

function NodeDeleteForm() {
  const { deleteNodes } = useNodes();
  const [label, setLabel] = useState('');
  const [nodeIdsInput, setNodeIdsInput] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    if (!label) {
      setError('Label es requerido.');
      return;
    }
    if (!nodeIdsInput.trim()) {
      setError('Proporcione al menos un ID de nodo.');
      return;
    }
    const nodeIdsArray = nodeIdsInput.split(',').map(id => id.trim()).filter(id => id);
    if (nodeIdsArray.length === 0) {
      setError('Proporcione al menos un ID de nodo.');
      return;
    }
    try {
      const result = await deleteNodes({ label, node_ids: nodeIdsArray });
      let successMsg = result.message || 'Eliminación completada.';
      if (result.deletedCount !== undefined) {
        successMsg += ` Nodos eliminados: ${result.deletedCount}.`;
      }
      setMessage(successMsg);
      if (result.errors && result.errors.length > 0) {
        setError(result.errors.join(' ; '));
      }
      // Clear form
      setLabel('');
      setNodeIdsInput('');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={{ marginBottom: '1rem' }}>
      <h3>Eliminar nodos</h3>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Label: </label>
          <input 
            type="text" 
            value={label} 
            onChange={(e) => setLabel(e.target.value)} 
            placeholder="Label de los nodos" 
          />
        </div>
        <div style={{ marginTop: '0.5rem' }}>
          <label>IDs de nodos (coma separadas): </label>
          <input 
            type="text" 
            value={nodeIdsInput} 
            onChange={(e) => setNodeIdsInput(e.target.value)} 
            placeholder="Ej: 1, 2, 3" 
          />
        </div>
        <button type="submit" style={{ marginTop: '0.5rem' }}>Eliminar</button>
      </form>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red', whiteSpace: 'pre-wrap' }}>Error: {error}</p>}
    </div>
  );
}

export default NodeDeleteForm;
