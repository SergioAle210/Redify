import React, { useState } from 'react';
import { useNodes } from '../context/NodesContext';

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
      // Clear form
      setLabel('');
      setNodeIdsInput('');
      setPropsToRemove(['']);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={{ marginBottom: '1rem' }}>
      <h3>Eliminar propiedades de nodos</h3>
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
        <div style={{ marginTop: '0.5rem' }}>
          <label>Propiedades a remover:</label>
          {propsToRemove.map((prop, idx) => (
            <div key={idx} style={{ marginLeft: '1rem', marginBottom: '0.25rem' }}>
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
                <button type="button" onClick={() => handleRemovePropField(idx)} style={{ marginLeft: '0.5rem' }}>
                  Eliminar
                </button>
              )}
            </div>
          ))}
          <button type="button" onClick={handleAddProp}>Añadir propiedad</button>
        </div>
        <button type="submit" style={{ marginTop: '0.5rem' }}>Remover</button>
      </form>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
    </div>
  );
}

export default NodeRemovePropsForm;
