import React, { useState } from 'react';
import { useRelationships } from '../context/RelationshipsContext';

function RelationshipDeleteForm() {
  const { deleteBulkRelationships } = useRelationships();
  const [relationships, setRelationships] = useState([{
    label1: '', node1Id: '', label2: '', node2Id: '', relType: ''
  }]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleAddRelationship = () => {
    setRelationships([...relationships, { label1: '', node1Id: '', label2: '', node2Id: '', relType: '' }]);
  };

  const handleRemoveRelationship = (index) => {
    setRelationships(relationships.filter((_, i) => i !== index));
  };

  const handleChangeField = (index, field, value) => {
    const newRels = [...relationships];
    newRels[index][field] = value;
    setRelationships(newRels);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    for (let rel of relationships) {
      if (!rel.label1 || !rel.node1Id || !rel.label2 || !rel.node2Id || !rel.relType) {
        setError('Complete todos los campos requeridos para cada relación.');
        return;
      }
    }
    const payloadRels = relationships.map(rel => ({
      label1: rel.label1,
      node1_id: rel.node1Id,
      label2: rel.label2,
      node2_id: rel.node2Id,
      rel_type: rel.relType
    }));
    try {
      const result = await deleteBulkRelationships({ relationships: payloadRels });
      let successMsg = result.message || 'Proceso completado.';
      if (result.deletedCount !== undefined) {
        successMsg += ` Relaciones eliminadas: ${result.deletedCount}.`;
      }
      setMessage(successMsg);
      if (result.errors && result.errors.length > 0) {
        setError(result.errors.join(' ; '));
      }
      setRelationships([{ label1: '', node1Id: '', label2: '', node2Id: '', relType: '' }]);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={{ marginBottom: '1rem' }}>
      <h3>Eliminar relaciones (bulk)</h3>
      <form onSubmit={handleSubmit}>
        {relationships.map((rel, idx) => (
          <div key={idx} style={{ marginBottom: '0.5rem' }}>
            <label>Relación {idx + 1} - Label1: </label>
            <input 
              type="text" 
              value={rel.label1} 
              onChange={(e) => handleChangeField(idx, 'label1', e.target.value)} 
              placeholder="Label nodo 1" 
            />
            <label style={{ marginLeft: '0.5rem' }}>ID1: </label>
            <input 
              type="text" 
              value={rel.node1Id} 
              onChange={(e) => handleChangeField(idx, 'node1Id', e.target.value)} 
              placeholder="ID nodo 1" 
              style={{ width: '80px' }}
            />
            <label style={{ marginLeft: '0.5rem' }}>Label2: </label>
            <input 
              type="text" 
              value={rel.label2} 
              onChange={(e) => handleChangeField(idx, 'label2', e.target.value)} 
              placeholder="Label nodo 2" 
            />
            <label style={{ marginLeft: '0.5rem' }}>ID2: </label>
            <input 
              type="text" 
              value={rel.node2Id} 
              onChange={(e) => handleChangeField(idx, 'node2Id', e.target.value)} 
              placeholder="ID nodo 2" 
              style={{ width: '80px' }}
            />
            <label style={{ marginLeft: '0.5rem' }}>Tipo: </label>
            <input 
              type="text" 
              value={rel.relType} 
              onChange={(e) => handleChangeField(idx, 'relType', e.target.value)} 
              placeholder="Tipo relación" 
            />
            {relationships.length > 1 && (
              <button type="button" onClick={() => handleRemoveRelationship(idx)} style={{ marginLeft: '0.5rem' }}>
                Eliminar
              </button>
            )}
          </div>
        ))}
        <button type="button" onClick={handleAddRelationship} style={{ marginBottom: '0.5rem' }}>Añadir relación</button><br/>
        <button type="submit">Eliminar relaciones</button>
      </form>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red', whiteSpace: 'pre-wrap' }}>Error: {error}</p>}
    </div>
  );
}

export default RelationshipDeleteForm;
