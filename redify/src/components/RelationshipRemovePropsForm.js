import React, { useState } from 'react';
import { useRelationships } from '../context/RelationshipsContext';
import '../styles/RelationshipRemovePropsForm.css'; // Importa el CSS

function RelationshipRemovePropsForm() {
  const { removeBulkRelationships } = useRelationships();
  const [relationships, setRelationships] = useState([{
    label1: '', node1Id: '', label2: '', node2Id: '', relType: '',
    props: ['']
  }]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleAddRelationship = () => {
    setRelationships([...relationships, {
      label1: '', node1Id: '', label2: '', node2Id: '', relType: '',
      props: ['']
    }]);
  };

  const handleRemoveRelationship = (index) => {
    setRelationships(relationships.filter((_, i) => i !== index));
  };

  const handleChangeRelField = (index, field, value) => {
    const newRels = [...relationships];
    newRels[index][field] = value;
    setRelationships(newRels);
  };

  const handleAddPropField = (relIndex) => {
    const newRels = [...relationships];
    newRels[relIndex].props.push('');
    setRelationships(newRels);
  };

  const handleRemovePropField = (relIndex, propIndex) => {
    const newRels = [...relationships];
    newRels[relIndex].props.splice(propIndex, 1);
    setRelationships(newRels);
  };

  const handleChangeProp = (relIndex, propIndex, value) => {
    const newRels = [...relationships];
    newRels[relIndex].props[propIndex] = value;
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
      const filledProps = rel.props.map(p => p.trim()).filter(p => p);
      if (filledProps.length === 0) {
        setError('Cada relación debe tener al menos una propiedad a remover.');
        return;
      }
    }

    const payloadRels = relationships.map(rel => ({
      label1: rel.label1,
      node1_id: rel.node1Id,
      label2: rel.label2,
      node2_id: rel.node2Id,
      rel_type: rel.relType,
      properties: rel.props.map(p => p.trim()).filter(p => p)
    }));

    try {
      const result = await removeBulkRelationships({ relationships: payloadRels });
      let successMsg = result.message || 'Proceso completado.';
      if (result.updatedCount !== undefined) {
        successMsg += ` Relaciones actualizadas: ${result.updatedCount}.`;
      }
      setMessage(successMsg);
      if (result.errors && result.errors.length > 0) {
        setError(result.errors.join(' ; '));
      }
      setRelationships([{
        label1: '', node1Id: '', label2: '', node2Id: '', relType: '',
        props: ['']
      }]);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="relationship-remove-container">
      <h2>Remover Propiedades de Relaciones</h2>
      <form onSubmit={handleSubmit} className="relationship-remove-form">
        {relationships.map((rel, idx) => (
          <div key={idx} className="relationship-card">
            <h3>Relación {idx + 1}</h3>
            <div className="input-group">
              <label>Nodo 1 - Label:</label>
              <input type="text" value={rel.label1} onChange={(e) => handleChangeRelField(idx, 'label1', e.target.value)} placeholder="Label nodo 1" />
              <label>ID:</label>
              <input type="text" value={rel.node1Id} onChange={(e) => handleChangeRelField(idx, 'node1Id', e.target.value)} placeholder="ID nodo 1" />
            </div>

            <div className="input-group">
              <label>Nodo 2 - Label:</label>
              <input type="text" value={rel.label2} onChange={(e) => handleChangeRelField(idx, 'label2', e.target.value)} placeholder="Label nodo 2" />
              <label>ID:</label>
              <input type="text" value={rel.node2Id} onChange={(e) => handleChangeRelField(idx, 'node2Id', e.target.value)} placeholder="ID nodo 2" />
            </div>

            <div className="input-group">
              <label>Tipo de Relación:</label>
              <input type="text" value={rel.relType} onChange={(e) => handleChangeRelField(idx, 'relType', e.target.value)} placeholder="Ej: AMIGOS" />
            </div>

            <div className="properties-container">
              <label>Propiedades a Remover:</label>
              {rel.props.map((prop, pidx) => (
                <div key={pidx} className="property-group">
                  <input type="text" placeholder="Propiedad" value={prop} onChange={(e) => handleChangeProp(idx, pidx, e.target.value)} />
                  {rel.props.length > 1 && (
                    <button type="button" className="remove-btn" onClick={() => handleRemovePropField(idx, pidx)}>❌</button>
                  )}
                </div>
              ))}
              <button type="button" className="add-btn" onClick={() => handleAddPropField(idx)}>+ Añadir Propiedad</button>
            </div>

            {relationships.length > 1 && (
              <button type="button" className="remove-relationship-btn" onClick={() => handleRemoveRelationship(idx)}>❌ Eliminar Relación</button>
            )}
          </div>
        ))}

        <button type="button" className="add-btn" onClick={handleAddRelationship}>+ Añadir Otra Relación</button>
        <button type="submit" className="submit-btn">Remover Propiedades</button>
      </form>

      {message && <p className="success-msg">{message}</p>}
      {error && <p className="error-msg">Error: {error}</p>}
    </div>
  );
}

export default RelationshipRemovePropsForm;
