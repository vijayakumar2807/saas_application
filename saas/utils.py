from django.db import connection
from django.db.migrations.state import ProjectState
from django.db.migrations.operations import AddField
from django.db.models import CharField
from saas.models import clients

def add_column_without_migration():
    # Define the new field
    field = CharField(max_length=300, null=True)
    field.set_attributes_from_name('linkedin_url')

    # Create an empty project state (copy current app state)
    state = ProjectState.from_apps(clients._meta.apps)

    with connection.schema_editor() as schema_editor:
        operation = AddField(
            model_name=clients._meta.model_name,
            name='linkedin_url',
            field=field,
        )
        # Provide from_state and to_state as the same ProjectState
        operation.database_forwards(
            app_label='saas',
            schema_editor=schema_editor,
            from_state=state,
            to_state=state,
        )

# Now call your function
add_column_without_migration()
