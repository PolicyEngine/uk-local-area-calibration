import pytest
from policyengine_core.country_template import CountryTaxBenefitSystem
from policyengine_core.reforms import Reform

from reform_parameters import parse_reform_parameters


def test_parses_each_parameter_with_its_values_by_period():
    reform_parameters_json = """{
        "gov.hmrc.income_tax.rates.uk[0].rate": {"2025": 0.21},
        "gov.hmrc.income_tax.allowances.personal_allowance.amount": {
            "2025-01-01.2025-12-31": 13000
        }
    }"""

    assert parse_reform_parameters(reform_parameters_json) == {
        "gov.hmrc.income_tax.rates.uk[0].rate": {"2025": 0.21},
        "gov.hmrc.income_tax.allowances.personal_allowance.amount": {
            "2025-01-01.2025-12-31": 13000
        },
    }


def test_empty_object_is_current_law():
    assert parse_reform_parameters("{}") == {}


def test_rejects_text_that_is_not_json():
    with pytest.raises(ValueError, match="not valid JSON"):
        parse_reform_parameters("{'single quotes': 1}")


@pytest.mark.parametrize(
    "reform_parameters_json", ["[]", "1", '"text"', "null"]
)
def test_rejects_json_that_is_not_an_object(reform_parameters_json):
    with pytest.raises(ValueError, match="must be a JSON object"):
        parse_reform_parameters(reform_parameters_json)


def test_parsed_parameters_apply_through_reform_from_dict():
    reform_parameters = parse_reform_parameters(
        '{"taxes.income_tax_rate": {"2025-01-01.2025-12-31": 0.3}}'
    )

    reform = Reform.from_dict(reform_parameters, country_id="uk")
    reformed_parameters = reform(CountryTaxBenefitSystem()).parameters

    assert reformed_parameters.taxes.income_tax_rate("2025-06-01") == 0.3
    assert reformed_parameters.taxes.income_tax_rate("2026-06-01") == 0.15
