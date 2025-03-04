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

    // Construir objeto de propiedades
    const propsObj = {};
    let countProps = 0;
    properties.forEach(prop => {
      if (prop.key && prop.value !== '') {
        propsObj[prop.key] = prop.value;
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
        setMessage(`Nodo creado. ID: ${result.node.id}, Labels: ${Array.isArray(result.node.labels) ? result.node.labels.join(', ') : result.node.labels}, Propiedades: ${JSON.stringify(result.node.properties)}`);
      } else {
        setMessage(result.message || 'Nodo con propiedades creado.');
      }
      setLabel('');
      setProperties([{ key: '', value: '' }, { key: '', value: '' }, { key: '', value: '' }, { key: '', value: '' }, { key: '', value: '' }]);
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
                placeholder="Valor" 
                value={prop.value} 
                onChange={(e) => {
                  const newProps = [...properties];
                  newProps[idx].value = e.target.value;
                  setProperties(newProps);
                }} 
              />
              {properties.length > 5 && (
                <button type="button" className="remove-btn" onClick={() => handleRemoveProperty(idx)}>❌</button>
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
