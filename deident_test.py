import google.cloud.dlp_v2


def deidentify_with_redact(
    project: str,
    input_str: str,
    # info_types: list[str],
) -> None:
    """Uses the Data Loss Prevention API to deidentify sensitive data in a
    string by redacting matched input values.
    Args:
        project: The Google Cloud project id to use as a parent resource.
        input_str: The string to deidentify (will be treated as text).
        info_types: A list of strings representing info types to look for.
    Returns:
        None; the response from the API is printed to the terminal.
    """

    # Instantiate a client
    dlp = google.cloud.dlp_v2.DlpServiceClient()

    # Convert the project id into a full resource id.
    parent = f"projects/{project}/locations/global"

    # Construct inspect configuration dictionary
    inspect_config = {} # {"info_types": [{"name": info_type} for info_type in info_types]}

    # Construct deidentify configuration dictionary
    deidentify_config = {
        "info_type_transformations": {
            "transformations": [{
                "primitive_transformation": {
                    "redact_config": {},
                    "replace_config": {"new_value": {"string_value": "*****"}}
                },
            }]
        }
    }

    # Construct item
    item = {"value": input_str}

    # Call the API
    response = dlp.deidentify_content(
        request={
            "parent": parent,
            "deidentify_config": deidentify_config,
            "inspect_config": inspect_config,
            "item": item,
        }
    )

    # Print out the results.
    print(response.item.value)



deidentify_with_redact(project="eavefyi-dev", input_str="my SSN is: 777-90-0145. Have fun!")