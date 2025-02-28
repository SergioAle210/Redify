from django.urls import path
from .views import (
    create_node_single_label,
    create_node_multiple_labels,
    create_node_with_properties,
    search_nodes,
    get_aggregated_data,
    update_node_properties,
    update_multiple_nodes_properties,
    remove_single_node_properties,
    remove_multiple_nodes_properties,
    create_relationship,
    update_single_relationship_properties,
    update_multiple_relationships_properties,
    remove_single_relationship_properties,
    remove_multiple_relationships_properties,
    delete_single_node,
    delete_multiple_nodes,
)

urlpatterns = [
    # Listo
    path(
        "create-node-single-label/",
        create_node_single_label,
        name="create_node_single_label",
    ),
    # Listo
    path(
        "create-node-multiple-labels/",
        create_node_multiple_labels,
        name="create_node_multiple_labels",
    ),
    # Listo
    path(
        "create-node-with-properties/",
        create_node_with_properties,
        name="create_node_with_properties",
    ),
    # Listo
    path("search-nodes/", search_nodes, name="search_nodes"),
    # Listo
    path("get-aggregated-data/", get_aggregated_data, name="get_aggregated_data"),
    # Listo
    path(
        "update-multiple-nodes-properties/",
        update_multiple_nodes_properties,
        name="update_multiple_nodes_properties",
    ),
    path(
        "remove-single-node-properties/",
        remove_single_node_properties,
        name="remove_single_node_properties",
    ),
    path(
        "remove-multiple-nodes-properties/",
        remove_multiple_nodes_properties,
        name="remove_multiple_nodes_properties",
    ),
    path("create-relationship/", create_relationship, name="create_relationship"),
    path(
        "update-single-relationship-properties/",
        update_single_relationship_properties,
        name="update_single_relationship_properties",
    ),
    path(
        "update-multiple-relationship-properties/",
        update_multiple_relationships_properties,
        name="update_multiple_relationships_properties",
    ),
    path(
        "remove-single-relationship-properties/",
        remove_single_relationship_properties,
        name="remove_single_relationship_properties",
    ),
    path(
        "remove-multiple-relationship-properties/",
        remove_multiple_relationships_properties,
        name="remove_multiple_relationships_properties",
    ),
    path("delete-single-node/", delete_single_node, name="delete_single_node"),
    path("delete-multiple-nodes/", delete_multiple_nodes, name="delete_multiple_nodes"),
]
