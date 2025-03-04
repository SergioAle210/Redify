import React, { useState } from 'react';
import { useNodes } from '../context/NodesContext';
import '../styles/NodeRemovePropsForm.css'; // Importa el CSS

function NodeRemovePropsForm() {
  const { removeNodesProperties } = useNodes();
  const [label, setLabel] = useState('');
  const [nodeIdsInput, setNodeIdsInput] = useState('');
  const [propsToRemove, setPropsToRemove] = useState(['']);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleAddProp = () => {
    setPropsToRemove([...propsToRemove, '']);
  };

  const handleRemovePropField = (index) => {
    setPropsToRemove(propsToRemove.filter((_, i) => i !== index));
  };

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

    const propsArray = propsToRemove.map(p => p.trim()).filter(p => p);
    if (propsArray.length === 0) {
      setError('Proporcione al menos una propiedad a remover.');
      return;
    }

    try {
      const result = await removeNodesProperties({ label, node_ids: nodeIdsArray, properties: propsArray });
      if (result.updatedCount !== undefined) {
        setMessage(`Propiedades eliminadas en ${result.updatedCount} nodo(s).`);
      } else {
        setMessage(result.message || 'Propiedades eliminadas.');
      }
      setLabel('');
      setNodeIdsInput('');
      setPropsToRemove(['']);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="remove-form-container">
      <h2>Eliminar Propiedades de Nodos</h2>
      <form onSubmit={handleSubmit} className="remove-form">
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

        <div className="properties-container">
          <label>Propiedades a Remover:</label>
          {propsToRemove.map((prop, idx) => (
            <div key={idx} className="property-group">
              <input 
                type="text" 
                placeholder="Nombre de propiedad" 
                value={prop} 
                onChange={(e) => {
                  const newProps = [...propsToRemove];
                  newProps[idx] = e.target.value;
                  setPropsToRemove(newProps);
                }} 
              />
              {propsToRemove.length > 1 && (
                <button type="button" className="remove-btn" onClick={() => handleRemovePropField(idx)}>❌</button>
              )}
            </div>
          ))}
          <button type="button" className="add-btn" onClick={handleAddProp}>+ Añadir Propiedad</button>
        </div>

        <button type="submit" className="submit-btn">Remover</button>
      </form>

      {message && <p className="success-msg">{message}</p>}
      {error && <p className="error-msg">Error: {error}</p>}
    </div>
  );
}

export default NodeRemovePropsForm;
