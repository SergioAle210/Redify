import React from 'react';
import { useNodes } from '../context/NodesContext';

function NodeList() {
  const { nodes, loading, error, searched } = useNodes();

  if (loading) {
    return <p>Cargando nodos...</p>;
  }
  if (error) {
    return <p style={{ color: 'red' }}>Error: {error}</p>;
  }
  if (!searched) {
    return <p>Realice una búsqueda para ver nodos.</p>;
  }
  if (nodes.length === 0) {
    return <p>No se encontraron nodos.</p>;
  }

  return (
    <div>
      <table border="1" cellPadding="5" cellSpacing="0">
        <thead>
          <tr>
            <th>ID</th>
            <th>Labels</th>
            <th>Propiedades</th>
          </tr>
        </thead>
        <tbody>
          {nodes.map(node => (
            <tr key={node.id}>
              <td>{node.id}</td>
              <td>{Array.isArray(node.labels) ? node.labels.join(', ') : node.labels}</td>
              <td>
                {node.properties 
                  ? Object.entries(node.properties).map(([key, val]) => (
                      <div key={key}><strong>{key}:</strong> {String(val)}</div>
                    ))
                  : '(Sin propiedades)'
                }
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default NodeList;
