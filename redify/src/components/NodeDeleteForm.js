import React, { useState } from 'react';
import { useNodes } from '../context/NodesContext';
import '../styles/NodeDeleteForm.css'; // Importa el CSS

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
    <div className="delete-form-container">
      <h2>Eliminar Nodos</h2>
      <form onSubmit={handleSubmit} className="delete-form">
        <div className="input-group">
          <label>Label del Nodo:</label>
          <input 
            type="text" 
            value={label} 
            onChange={(e) => setLabel(e.target.value)} 
            placeholder="Ej: Usuario, Producto"
          />
        </div>

        <div className="input-group">
          <label>IDs de Nodos (separados por coma):</label>
          <input 
            type="text" 
            value={nodeIdsInput} 
            onChange={(e) => setNodeIdsInput(e.target.value)} 
            placeholder="Ej: 1, 2, 3"
          />
        </div>

        <button type="submit" className="delete-btn">🗑 Eliminar</button>
      </form>

      {message && <p className="success-msg">{message}</p>}
      {error && <p className="error-msg">Error: {error}</p>}
    </div>
  );
}

export default NodeDeleteForm;
