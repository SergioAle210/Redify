import React from 'react';
import RelationshipCreateForm from '../components/RelationshipCreateForm';
import RelationshipUpdateForm from '../components/RelationshipUpdateForm';
import RelationshipRemovePropsForm from '../components/RelationshipRemovePropsForm';
import RelationshipDeleteForm from '../components/RelationshipDeleteForm';

function RelationshipManagementPage() {
  return (
    <div>
      <h2>Crear Relación</h2>
      <RelationshipCreateForm />
      <h2>Actualizar Relaciones</h2>
      <RelationshipUpdateForm />
      <h2>Remover Propiedades de Relaciones</h2>
      <RelationshipRemovePropsForm />
      <h2>Eliminar Relaciones</h2>
      <RelationshipDeleteForm />
    </div>
  );
}

export default RelationshipManagementPage;
