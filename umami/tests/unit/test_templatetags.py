# -*- coding: utf-8 -*-
import pytest
from django.template import Context, Template


@pytest.fixture
def template():
    return Template("{% load navigation %}" "{% active 'account_login' %} - {% active '/accounts/login/' %}")


def test_naviagtion_active_match(rf, template):
    request = rf.get('/accounts/login/')
    context = Context({'request': request})
    assert 'active - active' in template.render(context)


def test_naviagtion_active_nomatch(rf, template):
    request = rf.get('/accounts/signup/')
    context = Context({'request': request})
    assert 'active - active' not in template.render(context)
