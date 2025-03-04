import React, { useState } from 'react';
import { useRelationships } from '../context/RelationshipsContext';
import '../styles/RelationshipCreateForm.css'; // Importa el CSS

function RelationshipCreateForm() {
  const { createRelationship } = useRelationships();
  const [label1, setLabel1] = useState('');
  const [node1Id, setNode1Id] = useState('');
  const [label2, setLabel2] = useState('');
  const [node2Id, setNode2Id] = useState('');
  const [relType, setRelType] = useState('');
  const [properties, setProperties] = useState([
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

    if (!label1 || !node1Id || !label2 || !node2Id || !relType) {
      setError('Todos los campos de nodo y tipo son requeridos.');
      return;
    }

    const propsObj = {};
    let countProps = 0;
    properties.forEach(prop => {
      if (prop.key && prop.value !== '') {
        propsObj[prop.key] = prop.value;
        countProps++;
      }
    });

    if (countProps < 3) {
      setError('Debe proporcionar al menos 3 propiedades para la relación.');
      return;
    }

    try {
      const result = await createRelationship({ 
        label1, node1_id: node1Id, 
        label2, node2_id: node2Id, 
        rel_type: relType, 
        properties: propsObj 
      });

      if (result.relationship) {
        setMessage(`Relación creada. ID: ${result.relationship.id}, Propiedades: ${JSON.stringify(result.relationship.properties)}`);
      } else {
        setMessage(result.message || 'Relación creada.');
      }

      // Reset form
      setLabel1('');
      setNode1Id('');
      setLabel2('');
      setNode2Id('');
      setRelType('');
      setProperties([{ key: '', value: '' }, { key: '', value: '' }, { key: '', value: '' }]);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="relationship-form-container">
      <h2>Crear Relación</h2>
      <form onSubmit={handleSubmit} className="relationship-form">
        <div className="input-group">
          <label>Nodo 1 - Label:</label>
          <input 
            type="text" 
            value={label1} 
            onChange={(e) => setLabel1(e.target.value)} 
            placeholder="Label nodo 1"
          />
          <label>ID:</label>
          <input 
            type="text" 
            value={node1Id} 
            onChange={(e) => setNode1Id(e.target.value)} 
            placeholder="ID nodo 1"
          />
        </div>

        <div className="input-group">
          <label>Nodo 2 - Label:</label>
          <input 
            type="text" 
            value={label2} 
            onChange={(e) => setLabel2(e.target.value)} 
            placeholder="Label nodo 2"
          />
          <label>ID:</label>
          <input 
            type="text" 
            value={node2Id} 
            onChange={(e) => setNode2Id(e.target.value)} 
            placeholder="ID nodo 2"
          />
        </div>

        <div className="input-group">
          <label>Tipo de Relación:</label>
          <input 
            type="text" 
            value={relType} 
            onChange={(e) => setRelType(e.target.value)} 
            placeholder="Ej: AMIGO_DE"
          />
        </div>

        <div className="properties-container">
          <label>Propiedades de la Relación:</label>
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
              {properties.length > 3 && (
                <button type="button" className="remove-btn" onClick={() => handleRemoveProperty(idx)}>❌</button>
              )}
            </div>
          ))}
          <button type="button" className="add-btn" onClick={handleAddProperty}>+ Añadir Propiedad</button>
        </div>

        <button type="submit" className="submit-btn">Crear Relación</button>
      </form>

      {message && <p className="success-msg">{message}</p>}
      {error && <p className="error-msg">Error: {error}</p>}
    </div>
  );
}

export default RelationshipCreateForm;
