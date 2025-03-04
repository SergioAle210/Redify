import React, { useState } from 'react';
import { useNodes } from '../context/NodesContext';
import '../styles/NodeCreateMultiForm.css'; // Importa el CSS

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
    <div className="multi-form-container">
      <h2>Crear Nodo con Múltiples Labels</h2>
      <form onSubmit={handleSubmit} className="multi-form">
        <div className="input-group">
          <label>Labels (separados por coma):</label>
          <input 
            type="text" 
            value={labelsInput} 
            onChange={(e) => setLabelsInput(e.target.value)} 
            placeholder="Ej: Usuario, Cliente"
          />
        </div>
        <button type="submit" className="submit-btn">Crear</button>
      </form>

      {message && <p className="success-msg">{message}</p>}
      {error && <p className="error-msg">Error: {error}</p>}
    </div>
  );
}

export default NodeCreateMultiForm;
