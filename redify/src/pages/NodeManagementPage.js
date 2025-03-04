import React from 'react';
import NodeSearchForm from '../components/NodeSearchForm';
import NodeList from '../components/NodeList';
import NodeAggregatedForm from '../components/NodeAggregatedForm';
import NodeCreateSingleForm from '../components/NodeCreateSingleForm';
import NodeCreateMultiForm from '../components/NodeCreateMultiForm';
import NodeCreateWithPropsForm from '../components/NodeCreateWithPropsForm';
import NodeUpdateForm from '../components/NodeUpdateForm';
import NodeRemovePropsForm from '../components/NodeRemovePropsForm';
import NodeDeleteForm from '../components/NodeDeleteForm';

function NodeManagementPage() {
  return (
    <div>
      <h2>Buscar Nodos</h2>
      <NodeSearchForm />
      <NodeList />
      <h2>Datos Agregados</h2>
      <NodeAggregatedForm />
      <h2>Crear Nodos</h2>
      <NodeCreateSingleForm />
      <NodeCreateMultiForm />
      <NodeCreateWithPropsForm />
      <h2>Actualizar Nodos</h2>
      <NodeUpdateForm />
      <h2>Remover Propiedades de Nodos</h2>
      <NodeRemovePropsForm />
      <h2>Eliminar Nodos</h2>
      <NodeDeleteForm />
    </div>
  );
}

export default NodeManagementPage;
