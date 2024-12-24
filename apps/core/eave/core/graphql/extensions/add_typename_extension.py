from collections.abc import Iterator
from typing import override

from graphql import ExecutableDefinitionNode, FieldNode, NameNode, SelectionSetNode
from strawberry.extensions import SchemaExtension


class AddTypenameExtension(SchemaExtension):
    """
    Adds __typename to all selection sets in the document.
    This probably negatively impacts performance. Prefer to do this in the client if possible.
    """

    def _add_typename_recursive(self, node: SelectionSetNode) -> None:
        node.selections += (
            FieldNode(
                name=NameNode(value="__typename"),
                alias=None,
                selection_set=None,
                arguments=(),
            ),
        )

        for selection in node.selections:
            if isinstance(selection, FieldNode) and selection.selection_set is not None:
                self._add_typename_recursive(selection.selection_set)

    @override
    def on_parse(self) -> Iterator[None]:
        yield

        graphql_document = self.execution_context.graphql_document

        if graphql_document:
            for definition in graphql_document.definitions:
                if isinstance(definition, ExecutableDefinitionNode):
                    self._add_typename_recursive(definition.selection_set)
