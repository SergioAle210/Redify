import React, { useState } from 'react';
import { useNodes } from '../context/NodesContext';

function NodeCreateWithPropsForm() {
  const { createNodeWithProperties } = useNodes();
  const [label, setLabel] = useState('');
  const [properties, setProperties] = useState([
    { key: '', value: '' },
    { key: '', value: '' },
    { key: '', value: '' },
    { key: '', value: '' },
    { key: '', value: '' }
  ]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // Función para analizar un valor individualmente
  const parseItem = (item) => {
    const trimmed = item.trim();
    if (trimmed.toLowerCase() === 'true') return true;
    if (trimmed.toLowerCase() === 'false') return false;
    // Verifica si es numérico (entero o float)
    if (trimmed !== '' && !isNaN(trimmed)) {
      return Number(trimmed);
    }
    return trimmed;
  };

  // Función para analizar el valor: lista o valor simple
  const parseValue = (value) => {
    if (value.includes(',')) {
      return value
        .split(',')
        .map(item => parseItem(item))
        .filter(item => item !== '');
    } else {
      return parseItem(value);
    }
  };

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
      setError('Debe proporcionar un label.');
      return;
    }
    // Construir el objeto de propiedades
    const propsObj = {};
    let countProps = 0;
    properties.forEach(prop => {
      if (prop.key && prop.value !== '') {
        propsObj[prop.key] = parseValue(prop.value);
        countProps++;
      }
    });
    if (countProps < 5) {
      setError('Debe proporcionar al menos 5 propiedades.');
      return;
    }
    try {
      const result = await createNodeWithProperties({ label, properties: propsObj });
      if (result.node) {
        const node = result.node;
        setMessage(
          `Nodo creado. ID: ${node.id}, Labels: ${Array.isArray(node.labels) ? node.labels.join(', ') : node.labels}, Propiedades: ${JSON.stringify(node.properties)}`
        );
      } else {
        setMessage(result.message || 'Nodo con propiedades creado.');
      }
      // Reiniciar formulario
      setLabel('');
      setProperties([
        { key: '', value: '' },
        { key: '', value: '' },
        { key: '', value: '' },
        { key: '', value: '' },
        { key: '', value: '' }
      ]);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={{ marginBottom: '1rem' }}>
      <h3>Crear Nodo (con propiedades)</h3>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Label: </label>
          <input 
            type="text" 
            value={label} 
            onChange={(e) => setLabel(e.target.value)} 
            placeholder="Label del nodo" 
          />
        </div>
        <div style={{ marginTop: '0.5rem' }}>
          <label>Propiedades:</label>
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
                placeholder="Valor (usa comas para listas, 'true'/'false', números)" 
                value={prop.value} 
                onChange={(e) => {
                  const newProps = [...properties];
                  newProps[idx].value = e.target.value;
                  setProperties(newProps);
                }} 
              />
              {properties.length > 5 && (
                <button 
                  type="button" 
                  onClick={() => handleRemoveProperty(idx)} 
                  style={{ marginLeft: '0.5rem' }}
                >
                  Eliminar
                </button>
              )}
            </div>
          ))}
          <button type="button" onClick={handleAddProperty}>Añadir propiedad</button>
        </div>
        <button type="submit" style={{ marginTop: '0.5rem' }}>Crear</button>
      </form>
      {message && <p style={{ color: 'green', whiteSpace: 'pre-wrap' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
    </div>
  );
}

export default NodeCreateWithPropsForm;
