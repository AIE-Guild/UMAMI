import pytest
from guildmaster.models import Client
from guildmaster.models.clients import ClientAdapterControl


def test_registry(adapter):
    assert adapter in Client._adapter_classes
    assert adapter == Client._adapter_class(adapter._control.id)


def test_registry_lookup_fail():
    assert Client._adapter_class('dummy') is None


@pytest.fixture()
def control_data():
    def f(required=True, optional=True):
        opt = ['revocation_url', 'verification_url']
        fields = {
            'id': 'test',
            'authorization_url': 'https://example.com/oauth/authorize',
            'token_url': 'https://example.com/oauth/token',
            'resource_url': 'https://example.com/profile',
            'resource_key': 'id',
            'revocation_url': 'https://example.com/oauth/revoke',
            'verification_url': 'https://example.com/oauth/verify',
        }
        candidates = [x for x in fields if x not in opt and required] + [x for x in fields if x in opt and optional]
        return {k: fields[k] for k in candidates}

    return f


def test_adapter_control(control_data):
    data = control_data()
    control = ClientAdapterControl(**data)
    for field in data:
        assert getattr(control, field) == data[field]


def test_adapter_control_required(control_data):
    data = control_data()
    required = control_data(optional=False)
    for field in required:
        del data[field]
        with pytest.raises(TypeError):
            ClientAdapterControl(**data)


def test_adapter_control_optional(control_data):
    data = control_data()
    optional = control_data(required=False)
    for field in optional:
        del data[field]
        control = ClientAdapterControl(**data)
        assert getattr(control, field) is None
