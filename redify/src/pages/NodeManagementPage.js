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
import './styles/NodeManagementPage.css';

function NodeManagementPage() {
  return (
    <div className="node-management">
      <h1 className="page-title">Gestión de Nodos</h1>
      
      <section>
        <h2>Buscar Nodos</h2>
        <NodeSearchForm />
        <NodeList />
      </section>

      <section>
        <h2>Datos Agregados</h2>
        <NodeAggregatedForm />
      </section>

      <section>
        <h2>Crear Nodos</h2>
        <NodeCreateSingleForm />
        <NodeCreateMultiForm />
        <NodeCreateWithPropsForm />
      </section>

      <section>
        <h2>Actualizar Nodos</h2>
        <NodeUpdateForm />
      </section>

      <section>
        <h2>Remover Propiedades</h2>
        <NodeRemovePropsForm />
      </section>

      <section>
        <h2>Eliminar Nodos</h2>
        <NodeDeleteForm />
      </section>
    </div>
  );
}

export default NodeManagementPage;
