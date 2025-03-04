import React, { useState } from 'react';
import { useNodes } from '../context/NodesContext';

function NodeUpdateForm() {
  const { updateNodesProperties } = useNodes();
  const [label, setLabel] = useState('');
  const [nodeIdsInput, setNodeIdsInput] = useState('');
  const [properties, setProperties] = useState([{ key: '', value: '' }]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleAddProperty = () => {
    setProperties([...properties, { key: '', value: '' }]);
  };

  const handleRemoveProperty = (index) => {
    setProperties(properties.filter((_, i) => i !== index));
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
      setError('Debe proporcionar al menos un ID de nodo.');
      return;
    }
    // parse node ids
    const nodeIdsArray = nodeIdsInput.split(',').map(id => id.trim()).filter(id => id);
    if (nodeIdsArray.length === 0) {
      setError('Debe proporcionar al menos un ID de nodo.');
      return;
    }
    // build props object
    const propsObj = {};
    let propCount = 0;
    properties.forEach(prop => {
      if (prop.key && prop.value !== '') {
        propsObj[prop.key] = prop.value;
        propCount++;
      }
    });
    if (propCount === 0) {
      setError('Proporcione al menos una propiedad para actualizar.');
      return;
    }
    try {
      const result = await updateNodesProperties({ label, node_ids: nodeIdsArray, properties: propsObj });
      if (result.updatedCount !== undefined) {
        setMessage(`Propiedades actualizadas en ${result.updatedCount} nodo(s).`);
      } else {
        setMessage(result.message || 'Actualización realizada.');
      }
      // Optionally, clear form
      setLabel('');
      setNodeIdsInput('');
      setProperties([{ key: '', value: '' }]);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={{ marginBottom: '1rem' }}>
      <h3>Actualizar propiedades de nodos</h3>
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
          <label>Nuevas propiedades:</label>
          {properties.map((prop, idx) => (
            <div key={idx} style={{ marginLeft: '1rem', marginBottom: '0.25rem' }}>
              <input 
                type="text" 
                placeholder="Clave" 
                value={prop.key} 
                onChange={(e) => {
                  const newProps = [...properties];
                  newProps[idx].key = e.target.value;
                  setProperties(newProps);
                }} 
                style={{ marginRight: '0.5rem' }}
              />
              <input 
                type="text" 
                placeholder="Valor" 
                value={prop.value} 
                onChange={(e) => {
                  const newProps = [...properties];
                  newProps[idx].value = e.target.value;
                  setProperties(newProps);
                }} 
              />
              {properties.length > 1 && (
                <button type="button" onClick={() => handleRemoveProperty(idx)} style={{ marginLeft: '0.5rem' }}>
                  Eliminar
                </button>
              )}
            </div>
          ))}
          <button type="button" onClick={handleAddProperty}>Añadir propiedad</button>
        </div>
        <button type="submit" style={{ marginTop: '0.5rem' }}>Actualizar</button>
      </form>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
    </div>
  );
}

export default NodeUpdateForm;
