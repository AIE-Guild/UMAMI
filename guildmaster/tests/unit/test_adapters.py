import pytest

from guildmaster.models import Client


def test_registry(adapter):
    assert adapter in Client._adapter_classes
    assert adapter == Client._adapter_class(adapter.adapter_id)


def test_registry_lookup_fail():
    assert Client._adapter_class('dummy') is None
