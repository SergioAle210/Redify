from django.urls import path
from .views import (
    create_node_single_label,
    create_node_multiple_labels,
    create_node_with_properties,
    search_nodes,
    get_aggregated_data,
    update_multiple_nodes_properties,
    remove_multiple_nodes_properties,
    create_relationship,
    update_bulk_relationships,
    remove_bulk_relationships,
    delete_multiple_nodes_with_checks,
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
        "remove-multiple-nodes-properties/",
        remove_multiple_nodes_properties,
        name="remove_multiple_nodes_properties",
    ),
    # Listo
    path("create-relationship/", create_relationship, name="create_relationship"),
    # Listo
    path(
        "update-bulk-relationships/",
        update_bulk_relationships,
        name="update_bulk_relationships",
    ),
    # Listo
    path(
        "remove-bulk-relationship/",
        remove_bulk_relationships,
        name="remove_bulk_relationship",
    ),
    path(
        "delete-multiple-nodes/",
        delete_multiple_nodes_with_checks,
        name="delete_multiple_nodes_with_checks",
    ),
]
