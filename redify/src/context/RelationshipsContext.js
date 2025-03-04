import React, { createContext, useContext } from 'react';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api/';

// Utility request function (same as in NodesContext)
const request = async (endpoint, method = 'GET', data = null) => {
  const options = { method, headers: {} };
  if (data) {
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(data);
  }
  const res = await fetch(BASE_URL + endpoint, options);
  let resData;
  try {
    resData = await res.json();
  } catch (error) {
    resData = null;
  }
  if (!res.ok) {
    const errorMsg = resData?.error || (resData?.errors ? JSON.stringify(resData.errors) : res.statusText);
    throw new Error(errorMsg);
  }
  return resData;
};

const RelationshipsContext = createContext(null);

export const RelationshipsProvider = ({ children }) => {
  // Create a relationship between two nodes
  const createRelationship = async ({ label1, node1_id, label2, node2_id, rel_type, properties }) => {
    return await request('create-relationship/', 'POST', { label1, node1_id, label2, node2_id, rel_type, properties });
  };

  // Bulk update/create relationships
  const updateBulkRelationships = async ({ relationships }) => {
    return await request('update-bulk-relationships/', 'PUT', { relationships });
  };

  // Bulk remove properties from relationships
  const removeBulkRelationships = async ({ relationships }) => {
    return await request('remove-bulk-relationship/', 'PUT', { relationships });
  };

  // Bulk delete relationships
  const deleteBulkRelationships = async ({ relationships }) => {
    return await request('delete-bulk-relationships/', 'DELETE', { relationships });
  };

  return (
    <RelationshipsContext.Provider value={{
      createRelationship,
      updateBulkRelationships,
      removeBulkRelationships,
      deleteBulkRelationships
    }}>
      {children}
    </RelationshipsContext.Provider>
  );
};

export const useRelationships = () => useContext(RelationshipsContext);
