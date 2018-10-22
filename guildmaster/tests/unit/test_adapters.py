from guildmaster.adapters import Adapter


def test_registry(adapter):
    assert adapter in Adapter.adapters
    assert adapter == Adapter.adapter(adapter.id)


def test_registry_lookup_fail():
    assert Adapter.adapter('dummy') is None
