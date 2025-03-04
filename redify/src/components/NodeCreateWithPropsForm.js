import React, { useState } from 'react';
import { useNodes } from '../context/NodesContext';
import '../styles/NodeCreateWithPropsForm.css'; // Importa el CSS

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
    <div className="props-form-container">
      <h2>Crear Nodo con Propiedades</h2>
      <form onSubmit={handleSubmit} className="props-form">
        <div className="input-group">
          <label>Label del Nodo:</label>
          <input 
            type="text" 
            value={label} 
            onChange={(e) => setLabel(e.target.value)} 
            placeholder="Ej: Usuario, Producto"
          />
        </div>

        <div className="properties-container">
          <label>Propiedades:</label>
          {properties.map((prop, idx) => (
            <div key={idx} className="property-group">
              <input 
                type="text" 
                placeholder="Clave" 
                value={prop.key} 
                onChange={(e) => {
                  const newProps = [...properties];
                  newProps[idx].key = e.target.value;
                  setProperties(newProps);
                }} 
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
                  className="remove-btn" 
                  onClick={() => handleRemoveProperty(idx)} 
                  style={{ marginLeft: '0.5rem' }}
                >
                  Eliminar
                </button>

              )}
            </div>
          ))}
          <button type="button" className="add-btn" onClick={handleAddProperty}>+ Añadir Propiedad</button>
        </div>

        <button type="submit" className="submit-btn">Crear</button>
      </form>

      {message && <p className="success-msg">{message}</p>}
      {error && <p className="error-msg">Error: {error}</p>}
    </div>
  );
}

export default NodeCreateWithPropsForm;
