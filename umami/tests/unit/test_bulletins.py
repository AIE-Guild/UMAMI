# -*- coding: utf-8 -*-
from datetime import datetime

import pytest

from umami.models import Bulletin

def test_bulletin_creation():
    bulletin = Bulletin.objects.create(title='Test Bulletin', body='# Spam')
    assert bulletin.title == 'Test Bulletin'
    assert str(bulletin) == 'Test Bulletin'
    assert bulletin.body == '# Spam'
    assert '<h1>Spam</h1>' in bulletin.as_html
    assert not bulletin.publish
    assert bulletin.published is None

def test_bulletin_publish():
    bulletin = Bulletin.objects.create(title='Test Bulletin', body='# Spam')
    bulletin.publish = True
    bulletin.save()
    assert bulletin.publish
    assert isinstance(bulletin.published, datetime)

def test_get_published():
    for i in range(20):
        Bulletin.objects.create(title=str(i), body='content', publish=bool(i % 2))
    assert len(Bulletin.objects.get_published()) == 10
    assert len(Bulletin.objects.get_published(3)) == 4
    assert all([len(x) == 5 for x in Bulletin.objects.get_published(5)])
