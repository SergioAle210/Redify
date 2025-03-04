import React, { useState } from 'react';
import { useRelationships } from '../context/RelationshipsContext';

function RelationshipUpdateForm() {
  const { updateBulkRelationships } = useRelationships();
  const [relationships, setRelationships] = useState([{
    label1: '', node1Id: '', label2: '', node2Id: '', relType: '',
    properties: [{ key: '', value: '' }]
  }]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // Función para convertir un string a número (entero o float) si es numérico
  const parseItem = (item) => {
    const trimmed = item.trim();
    if (trimmed !== '' && !isNaN(trimmed)) {
      return trimmed.includes('.') ? parseFloat(trimmed) : parseInt(trimmed, 10);
    }
    return trimmed;
  };

  // Función para determinar si el valor es una lista (separada por comas) o un valor simple
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

  // Función para convertir el ID a entero si es numérico
  const convertId = (value) => {
    const n = parseInt(value, 10);
    return isNaN(n) ? value : n;
  };

  const handleAddRelationship = () => {
    setRelationships([...relationships, {
      label1: '', node1Id: '', label2: '', node2Id: '', relType: '',
      properties: [{ key: '', value: '' }]
    }]);
  };

  const handleRemoveRelationship = (index) => {
    setRelationships(relationships.filter((_, i) => i !== index));
  };

  const handleAddProperty = (relIndex) => {
    const newRelationships = [...relationships];
    newRelationships[relIndex].properties.push({ key: '', value: '' });
    setRelationships(newRelationships);
  };

  const handleRemoveProperty = (relIndex, propIndex) => {
    const newRelationships = [...relationships];
    newRelationships[relIndex].properties.splice(propIndex, 1);
    setRelationships(newRelationships);
  };

  const handleChangeRelField = (index, field, value) => {
    const newRelationships = [...relationships];
    newRelationships[index][field] = value;
    setRelationships(newRelationships);
  };

  const handleChangePropField = (relIndex, propIndex, field, value) => {
    const newRelationships = [...relationships];
    newRelationships[relIndex].properties[propIndex][field] = value;
    setRelationships(newRelationships);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');
    // Validar que cada relación tenga los campos requeridos
    for (let rel of relationships) {
      if (!rel.label1 || !rel.node1Id || !rel.label2 || !rel.node2Id || !rel.relType) {
        setError('Complete todos los campos requeridos para cada relación.');
        return;
      }
      const filledProps = rel.properties.filter(p => p.key && p.value !== '');
      if (filledProps.length === 0) {
        setError('Cada relación debe tener al menos una propiedad para actualizar.');
        return;
      }
    }
    // Construir el payload, aplicando la conversión de valores a cada propiedad
    const payloadRels = relationships.map(rel => {
      const relObj = {
        label1: rel.label1,
        node1_id: convertId(rel.node1Id),
        label2: rel.label2,
        node2_id: convertId(rel.node2Id),
        rel_type: rel.relType
      };
      // Agregar las propiedades convertidas
      rel.properties.forEach(p => {
        if (p.key && p.value !== '') {
          relObj[p.key] = parseValue(p.value);
        }
      });
      return relObj;
    });
    try {
      const result = await updateBulkRelationships({ relationships: payloadRels });
      let successMsg = result.message || 'Actualización completada.';
      if (result.updatedCount !== undefined) {
        successMsg += ` Relaciones actualizadas: ${result.updatedCount}.`;
      }
      setMessage(successMsg);
      if (result.errors && result.errors.length > 0) {
        setError(result.errors.join(' ; '));
      }
      // Resetear formulario
      setRelationships([{
        label1: '', node1Id: '', label2: '', node2Id: '', relType: '',
        properties: [{ key: '', value: '' }]
      }]);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={{ marginBottom: '1rem' }}>
      <h3>Actualizar/crear relaciones (bulk)</h3>
      <form onSubmit={handleSubmit}>
        {relationships.map((rel, idx) => (
          <div key={idx} style={{ marginBottom: '1rem', padding: '0.5rem', border: '1px solid #ccc' }}>
            <div>
              <label>Relación {idx + 1} - Nodo 1 Label: </label>
              <input 
                type="text" 
                value={rel.label1} 
                onChange={(e) => handleChangeRelField(idx, 'label1', e.target.value)} 
                placeholder="Label nodo 1" 
              />
              <label style={{ marginLeft: '0.5rem' }}>ID1: </label>
              <input 
                type="text" 
                value={rel.node1Id} 
                onChange={(e) => handleChangeRelField(idx, 'node1Id', e.target.value)} 
                placeholder="ID nodo 1" 
                style={{ width: '80px' }}
              />
            </div>
            <div style={{ marginTop: '0.25rem' }}>
              <label>Nodo 2 Label: </label>
              <input 
                type="text" 
                value={rel.label2} 
                onChange={(e) => handleChangeRelField(idx, 'label2', e.target.value)} 
                placeholder="Label nodo 2" 
              />
              <label style={{ marginLeft: '0.5rem' }}>ID2: </label>
              <input 
                type="text" 
                value={rel.node2Id} 
                onChange={(e) => handleChangeRelField(idx, 'node2Id', e.target.value)} 
                placeholder="ID nodo 2" 
                style={{ width: '80px' }}
              />
            </div>
            <div style={{ marginTop: '0.25rem' }}>
              <label>Tipo relación: </label>
              <input 
                type="text" 
                value={rel.relType} 
                onChange={(e) => handleChangeRelField(idx, 'relType', e.target.value)} 
                placeholder="Tipo (ej: AMIGOS)" 
              />
            </div>
            <div style={{ marginTop: '0.25rem' }}>
              <label>Propiedades:</label>
              {rel.properties.map((prop, pidx) => (
                <div key={pidx} style={{ marginLeft: '1rem', marginBottom: '0.25rem' }}>
                  <input 
                    type="text" 
                    placeholder="Clave" 
                    value={prop.key} 
                    onChange={(e) => handleChangePropField(idx, pidx, 'key', e.target.value)} 
                    style={{ marginRight: '0.5rem' }}
                  />
                  <input 
                    type="text" 
                    placeholder="Valor" 
                    value={prop.value} 
                    onChange={(e) => handleChangePropField(idx, pidx, 'value', e.target.value)} 
                  />
                  {rel.properties.length > 1 && (
                    <button type="button" onClick={() => handleRemoveProperty(idx, pidx)} style={{ marginLeft: '0.5rem' }}>
                      Eliminar prop
                    </button>
                  )}
                </div>
              ))}
              <button type="button" onClick={() => handleAddProperty(idx)}>Añadir prop</button>
            </div>
            {relationships.length > 1 && (
              <button type="button" onClick={() => handleRemoveRelationship(idx)} style={{ marginTop: '0.25rem' }}>
                Eliminar relación {idx + 1}
              </button>
            )}
          </div>
        ))}
        <button type="button" onClick={handleAddRelationship} style={{ marginBottom: '0.5rem' }}>
          Añadir otra relación
        </button><br/>
        <button type="submit">Actualizar relaciones</button>
      </form>
      {message && <p style={{ color: 'green', whiteSpace: 'pre-wrap' }}>{message}</p>}
      {error && <p style={{ color: 'red', whiteSpace: 'pre-wrap' }}>Error: {error}</p>}
    </div>
  );
}

export default RelationshipUpdateForm;
