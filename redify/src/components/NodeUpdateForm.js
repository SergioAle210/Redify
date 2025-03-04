import React, { useState } from 'react';
import { useNodes } from '../context/NodesContext';
import '../styles/NodeUpdateForm.css'; // Importa el CSS

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

    // Parsear los IDs de nodos
    const nodeIdsArray = nodeIdsInput.split(',').map(id => id.trim()).filter(id => id);
    if (nodeIdsArray.length === 0) {
      setError('Debe proporcionar al menos un ID de nodo.');
      return;
    }

    // Construir objeto de propiedades
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

      setLabel('');
      setNodeIdsInput('');
      setProperties([{ key: '', value: '' }]);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="update-form-container">
      <h2>Actualizar Propiedades de Nodos</h2>
      <form onSubmit={handleSubmit} className="update-form">
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
          <label>Nuevas Propiedades:</label>
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
              {properties.length > 1 && (
                <button type="button" className="remove-btn" onClick={() => handleRemoveProperty(idx)}>❌</button>
              )}
            </div>
          ))}
          <button type="button" className="add-btn" onClick={handleAddProperty}>+ Añadir Propiedad</button>
        </div>

        <button type="submit" className="submit-btn">Actualizar</button>
      </form>

      {message && <p className="success-msg">{message}</p>}
      {error && <p className="error-msg">Error: {error}</p>}
    </div>
  );
}

export default NodeUpdateForm;
