import React from 'react';
import RelationshipCreateForm from '../components/RelationshipCreateForm';
import RelationshipUpdateForm from '../components/RelationshipUpdateForm';
import RelationshipRemovePropsForm from '../components/RelationshipRemovePropsForm';
import RelationshipDeleteForm from '../components/RelationshipDeleteForm';
import './styles/NodeManagementPage.css';


function RelationshipManagementPage() {
  return (
    <div className="relationship-management">
      <h1 className="page-title">Gestión de Relaciones</h1>

      <section>
        <h2>Crear Relación</h2>
        <RelationshipCreateForm />
      </section>

      <section>
        <h2>Actualizar Relaciones</h2>
        <RelationshipUpdateForm />
      </section>

      <section>
        <h2>Remover Propiedades</h2>
        <RelationshipRemovePropsForm />
      </section>

      <section>
        <h2>Eliminar Relaciones</h2>
        <RelationshipDeleteForm />
      </section>
    </div>
  );
}

export default RelationshipManagementPage;
