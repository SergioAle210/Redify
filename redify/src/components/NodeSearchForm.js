import React, { useState } from 'react';
import { useNodes } from '../context/NodesContext';

const operatorOptions = ["=", "<", "<=", ">", ">=", "IN", "CONTAINS"];

function NodeSearchForm() {
  const { searchNodes, loading } = useNodes();
  const [labelsInput, setLabelsInput] = useState('');
  const [filters, setFilters] = useState([{ property: '', operator: '=', value: '' }]);
  const [limit, setLimit] = useState(100);

  const handleAddFilter = () => {
    setFilters([...filters, { property: '', operator: '=', value: '' }]);
  };

  const handleRemoveFilter = (index) => {
    setFilters(filters.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    // Prepare labels array
    let labelsArray = [];
    if (labelsInput.trim() !== '') {
      labelsArray = labelsInput.split(',').map(lbl => lbl.trim()).filter(lbl => lbl !== '');
    }
    // Prepare filters object
    const filtersObj = {};
    filters.forEach(f => {
      if (f.property && f.operator && f.value !== '') {
        // If operator is IN or CONTAINS and value has commas, split into array
        let val = f.value;
        if ((f.operator === 'IN' || f.operator === 'CONTAINS') && f.value.includes(',')) {
          val = f.value.split(',').map(v => v.trim()).filter(v => v !== '');
        }
        filtersObj[f.property] = { operator: f.operator, value: val };
      }
    });
    const payload = {
      labels: labelsArray,
      filters: filtersObj,
      limit: Number(limit) || 100
    };
    try {
      await searchNodes(payload);
    } catch (err) {
      // Error will be handled via context state (NodeList component)
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: '1rem' }}>
      <div>
        <label>Labels (separados por coma): </label>
        <input 
          type="text" 
          value={labelsInput} 
          onChange={(e) => setLabelsInput(e.target.value)} 
          placeholder='Ej: Usuario, Cliente' 
        />
      </div>
      <div style={{ marginTop: '0.5rem' }}>
        <label>Filtros:</label>
        {filters.map((f, idx) => (
          <div key={idx} style={{ marginBottom: '0.25rem' }}>
            <input 
              type="text" 
              placeholder="Propiedad" 
              value={f.property} 
              onChange={(e) => {
                const newFilters = [...filters];
                newFilters[idx].property = e.target.value;
                setFilters(newFilters);
              }} 
              style={{ width: '150px', marginRight: '0.5rem' }}
            />
            <select 
              value={f.operator} 
              onChange={(e) => {
                const newFilters = [...filters];
                newFilters[idx].operator = e.target.value;
                setFilters(newFilters);
              }} 
              style={{ marginRight: '0.5rem' }}
            >
              {operatorOptions.map(op => (
                <option key={op} value={op}>{op}</option>
              ))}
            </select>
            <input 
              type="text" 
              placeholder="Valor" 
              value={f.value} 
              onChange={(e) => {
                const newFilters = [...filters];
                newFilters[idx].value = e.target.value;
                setFilters(newFilters);
              }} 
              style={{ width: '150px', marginRight: '0.5rem' }}
            />
            {filters.length > 1 && (
              <button type="button" onClick={() => handleRemoveFilter(idx)}>
                Eliminar filtro
              </button>
            )}
          </div>
        ))}
        <button type="button" onClick={handleAddFilter}>Añadir filtro</button>
      </div>
      <div style={{ marginTop: '0.5rem' }}>
        <label>Límite: </label>
        <input 
          type="number" 
          value={limit} 
          onChange={(e) => setLimit(e.target.value)} 
          style={{ width: '80px' }}
        />
      </div>
      <button type="submit" disabled={loading} style={{ marginTop: '0.5rem' }}>
        {loading ? 'Buscando...' : 'Buscar'}
      </button>
    </form>
  );
}

export default NodeSearchForm;
