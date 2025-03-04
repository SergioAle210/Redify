import React, { useState } from 'react';
import { useNodes } from '../context/NodesContext';
import '../styles/NodeCreateSingleForm.css'; // Importa el CSS

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
    <div className="create-form-container">
      <h2>Crear Nodo</h2>
      <form onSubmit={handleSubmit} className="create-form">
        <div className="input-group">
          <label>Label del Nodo:</label>
          <input 
            type="text" 
            value={label} 
            onChange={(e) => setLabel(e.target.value)} 
            placeholder="Ej: Usuario, Producto"
          />
        </div>
        <button type="submit" className="submit-btn">Crear</button>
      </form>

      {message && <p className="success-msg">{message}</p>}
      {error && <p className="error-msg">Error: {error}</p>}
    </div>
  );
}

export default NodeCreateSingleForm;
