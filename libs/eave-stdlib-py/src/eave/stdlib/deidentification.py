import google.cloud.dlp_v2 as dlp
from .config import SHARED_CONFIG

client = dlp.DlpServiceClient()

# Convert the project id into a full resource id.
parent = f"projects/{SHARED_CONFIG.google_cloud_project}/locations/global"

def redact(
    data: str,
) -> str:
    """Uses the Data Loss Prevention API to deidentify sensitive data in a
    string by redacting matched input values.
    Returns the input `data` with any sensistive info found replaced with '*****'.
    """
    response = client.deidentify_content(
        request=dlp.DeidentifyContentRequest(
            parent=parent,
            deidentify_config=dlp.DeidentifyConfig(
                info_type_transformations=dlp.InfoTypeTransformations(
                    transformations=[
                        dlp.InfoTypeTransformations.InfoTypeTransformation(
                            primitive_transformation=dlp.PrimitiveTransformation(
                                replace_config=dlp.ReplaceValueConfig(new_value=dlp.Value(string_value="*****"))
                            )
                        )
                    ]
                )
            ),
            # inspect_config=inspect_config,
            item=dlp.ContentItem(value=data),
        )
    )

    return response.item.value
