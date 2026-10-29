import json


def parse_reform_parameters(reform_parameters_json: str) -> dict:
    """Read a reform's parameter changes from JSON text.

    The JSON object maps each parameter path to its values by period, in the
    form ``Reform.from_dict`` accepts, for example
    ``{"gov.hmrc.income_tax.rates.uk[0].rate": {"2025": 0.21}}``. A saved
    policy's ``policy_json`` has this form. An empty object is current law.

    Raises:
        ValueError: if the text is not valid JSON or not a JSON object.
    """
    try:
        reform_parameters = json.loads(reform_parameters_json)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"The reform parameters are not valid JSON: {error}"
        ) from error
    if not isinstance(reform_parameters, dict):
        raise ValueError(
            "The reform parameters must be a JSON object that maps each "
            "parameter path to its values by period."
        )
    return reform_parameters
