import React, { useState } from 'react';
import { useRelationships } from '../context/RelationshipsContext';

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
    <div style={{ marginBottom: '1rem' }}>
      <h3>Crear relación</h3>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Nodo 1 - Label: </label>
          <input 
            type="text" 
            value={label1} 
            onChange={(e) => setLabel1(e.target.value)} 
            placeholder="Label nodo 1" 
          />
          <label style={{ marginLeft: '0.5rem' }}>ID: </label>
          <input 
            type="text" 
            value={node1Id} 
            onChange={(e) => setNode1Id(e.target.value)} 
            placeholder="ID nodo 1" 
            style={{ width: '80px' }}
          />
        </div>
        <div style={{ marginTop: '0.5rem' }}>
          <label>Nodo 2 - Label: </label>
          <input 
            type="text" 
            value={label2} 
            onChange={(e) => setLabel2(e.target.value)} 
            placeholder="Label nodo 2" 
          />
          <label style={{ marginLeft: '0.5rem' }}>ID: </label>
          <input 
            type="text" 
            value={node2Id} 
            onChange={(e) => setNode2Id(e.target.value)} 
            placeholder="ID nodo 2" 
            style={{ width: '80px' }}
          />
        </div>
        <div style={{ marginTop: '0.5rem' }}>
          <label>Tipo de relación: </label>
          <input 
            type="text" 
            value={relType} 
            onChange={(e) => setRelType(e.target.value)} 
            placeholder="Ej: AMIGO_DE" 
          />
        </div>
        <div style={{ marginTop: '0.5rem' }}>
          <label>Propiedades de la relación:</label>
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
              {properties.length > 3 && (
                <button type="button" onClick={() => handleRemoveProperty(idx)} style={{ marginLeft: '0.5rem' }}>
                  Eliminar
                </button>
              )}
            </div>
          ))}
          <button type="button" onClick={handleAddProperty}>Añadir propiedad</button>
        </div>
        <button type="submit" style={{ marginTop: '0.5rem' }}>Crear relación</button>
      </form>
      {message && <p style={{ color: 'green', whiteSpace: 'pre-wrap' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
    </div>
  );
}

export default RelationshipCreateForm;
