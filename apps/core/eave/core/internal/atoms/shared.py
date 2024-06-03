from google.cloud.bigquery import SchemaField, SqlTypeNames

from eave.core.internal.atoms.table_handle import BigQueryFieldMode

def key_value_record_field(*, name: str, description: str ) -> SchemaField:
    return SchemaField(
        name=name,
        description=description,
        field_type=SqlTypeNames.RECORD,
        mode=BigQueryFieldMode.REPEATED,
        fields=(
            SchemaField(
                name="key",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.REQUIRED,
            ),
            SchemaField(
                name="value",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
        ),
    )

def insert_timestamp_field() -> SchemaField:
    return SchemaField(
        name="insert_timestamp",
        description="When this record was inserted into BigQuery. This is an internal field and not reliable for exploring user journeys.",
        field_type=SqlTypeNames.TIMESTAMP,
        mode=BigQueryFieldMode.REQUIRED,
        default_value_expression="CURRENT_TIMESTAMP",
    )

def timestamp_field() -> SchemaField:
    return SchemaField(
        name="timestamp",
        description="When this event occurred.",
        field_type=SqlTypeNames.TIMESTAMP,
        mode=BigQueryFieldMode.NULLABLE,
    )

def session_field() -> SchemaField:
    return SchemaField(
        name="session",
        description="Details about the user session during which this event occurred.",
        field_type=SqlTypeNames.RECORD,
        mode=BigQueryFieldMode.NULLABLE,
        fields=(
            SchemaField(
                name="id",
                description="A unique ID given to this session by Eave.",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="start_timestamp",
                description="When this session started.",
                field_type=SqlTypeNames.TIMESTAMP,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="duration_ms",
                description="The duration of the session at the time the user triggered this event.",
                field_type=SqlTypeNames.INTEGER,
                mode=BigQueryFieldMode.NULLABLE,
            ),
        ),
    )

def user_field() -> SchemaField:
    return SchemaField(
        name="user",
        description="User properties.",
        field_type=SqlTypeNames.RECORD,
        mode=BigQueryFieldMode.NULLABLE,
        fields=(
            SchemaField(
                name="id",
                description="The user ID, as determined by Eave.",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="visitor_id",
                description="A unique visitor ID assigned by Eave.",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
        ),
    )

def discovery_field() -> SchemaField:
    return SchemaField(
        name="discovery",
        description="UTM Parameters and related discovery details.",
        field_type=SqlTypeNames.RECORD,
        mode=BigQueryFieldMode.NULLABLE,
        fields=(
            SchemaField(
                name="timestamp",
                description="When these discovery details were captured.",
                field_type=SqlTypeNames.TIMESTAMP,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="browser_referrer",
                description="The page referrer reported by the browser.",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="gclid",
                description="Query parameter gclid",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="fbclid",
                description="Query parameter fbclid",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="msclkid",
                description="Query parameter msclkid",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="campaign",
                description="Query parameter utm_campaign",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="source",
                description="Query parameter utm_source",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="medium",
                description="Query parameter utm_medium",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="term",
                description="Query parameter utm_term",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),
            SchemaField(
                name="content",
                description="Query parameter utm_content",
                field_type=SqlTypeNames.STRING,
                mode=BigQueryFieldMode.NULLABLE,
            ),

            key_value_record_field(name="extra_utm_params", description="Catch-all for additional utm_* query params."),
        ),
    )

class ViewSchemaField:
    name: str
    definition: str
    field: SchemaField

class ViewSchema:
    fields: tuple[ViewSchemaField, ...]

    def __init__(self, fields: tuple[ViewSchemaField, ...]) -> None:
        self.fields = fields

    def to_select_fields(self) -> str:
        return ", ".join(f"{field.definition} as {field.name}" for field in self.fields)
