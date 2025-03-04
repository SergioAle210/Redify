import React, { useState } from 'react';
import { useNodes } from '../context/NodesContext';
import '../styles/NodeSearchForm.css'; 

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
    let labelsArray = labelsInput.trim() ? labelsInput.split(',').map(lbl => lbl.trim()) : [];
    const filtersObj = {};
    filters.forEach(f => {
      if (f.property && f.operator && f.value !== '') {
        let val = f.value;
        if ((f.operator === 'IN' || f.operator === 'CONTAINS') && f.value.includes(',')) {
          val = f.value.split(',').map(v => v.trim()).filter(v => v !== '');
        }
        filtersObj[f.property] = { operator: f.operator, value: val };
      }
    });

    try {
      await searchNodes({ labels: labelsArray, filters: filtersObj, limit: Number(limit) || 100 });
    } catch (err) {}
  };

  return (
    <div className="search-form-container">
      <h2>Búsqueda de Nodos</h2>
      <form onSubmit={handleSubmit} className="search-form">
        <div className="input-group">
          <label>Labels (separados por coma):</label>
          <input 
            type="text" 
            value={labelsInput} 
            onChange={(e) => setLabelsInput(e.target.value)} 
            placeholder="Ej: Usuario, Cliente"
          />
        </div>

        <div className="filters-container">
          <label>Filtros:</label>
          {filters.map((f, idx) => (
            <div key={idx} className="filter-group">
              <input 
                type="text" 
                placeholder="Propiedad" 
                value={f.property} 
                onChange={(e) => {
                  const newFilters = [...filters];
                  newFilters[idx].property = e.target.value;
                  setFilters(newFilters);
                }}
              />
              <select 
                value={f.operator} 
                onChange={(e) => {
                  const newFilters = [...filters];
                  newFilters[idx].operator = e.target.value;
                  setFilters(newFilters);
                }}
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
              />
              {filters.length > 1 && (
                <button type="button" className="remove-btn" onClick={() => handleRemoveFilter(idx)}>
                  ❌
                </button>
              )}
            </div>
          ))}
          <button type="button" className="add-btn" onClick={handleAddFilter}>+ Añadir filtro</button>
        </div>

        <div className="input-group">
          <label>Límite:</label>
          <input 
            type="number" 
            value={limit} 
            onChange={(e) => setLimit(e.target.value)}
          />
        </div>

        <button type="submit" disabled={loading} className="submit-btn">
          {loading ? 'Buscando...' : 'Buscar'}
        </button>
      </form>
    </div>
  );
}

export default NodeSearchForm;
