import React, { useState } from 'react';
import { useRelationships } from '../context/RelationshipsContext';
import '../styles/RelationshipDeleteForm.css'; // Importa el CSS

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
    <div className="relationship-delete-container">
      <h2>Eliminar Relaciones</h2>
      <form onSubmit={handleSubmit} className="relationship-delete-form">
        {relationships.map((rel, idx) => (
          <div key={idx} className="relationship-card">
            <h3>Relación {idx + 1}</h3>
            <div className="input-group">
              <label>Nodo 1 - Label:</label>
              <input type="text" value={rel.label1} onChange={(e) => handleChangeField(idx, 'label1', e.target.value)} placeholder="Label nodo 1" />
              <label>ID:</label>
              <input type="text" value={rel.node1Id} onChange={(e) => handleChangeField(idx, 'node1Id', e.target.value)} placeholder="ID nodo 1" />
            </div>

            <div className="input-group">
              <label>Nodo 2 - Label:</label>
              <input type="text" value={rel.label2} onChange={(e) => handleChangeField(idx, 'label2', e.target.value)} placeholder="Label nodo 2" />
              <label>ID:</label>
              <input type="text" value={rel.node2Id} onChange={(e) => handleChangeField(idx, 'node2Id', e.target.value)} placeholder="ID nodo 2" />
            </div>

            <div className="input-group">
              <label>Tipo de Relación:</label>
              <input type="text" value={rel.relType} onChange={(e) => handleChangeField(idx, 'relType', e.target.value)} placeholder="Ej: AMIGOS" />
            </div>

            {relationships.length > 1 && (
              <button type="button" className="remove-relationship-btn" onClick={() => handleRemoveRelationship(idx)}>❌ Eliminar Relación</button>
            )}
          </div>
        ))}

        <button type="button" className="add-btn" onClick={handleAddRelationship}>+ Añadir Otra Relación</button>
        <button type="submit" className="submit-btn">Eliminar Relaciones</button>
      </form>

      {message && <p className="success-msg">{message}</p>}
      {error && <p className="error-msg">Error: {error}</p>}
    </div>
  );
}

export default RelationshipDeleteForm;
