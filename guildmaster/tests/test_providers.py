import pytest


def test_providers(tf_provider):
    if tf_provider.name == 'discord':
        assert tf_provider.description == 'Discord'
    else:
        pytest.fail(f"unknown provider: {tf_provider.name}")
