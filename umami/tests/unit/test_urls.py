# -*- coding: utf-8 -*-
from django.urls import resolve


def test_admin():
    resolver = resolve('/admin/')
    assert resolver.app_name == 'admin'


def test_local_signup():
    resolver = resolve('/accounts/signup/')
    assert resolver.view_name == 'account_signup'


def test_local_login():
    resolver = resolve('/accounts/login/')
    assert resolver.view_name == 'account_login'


def test_local_logout():
    resolver = resolve('/accounts/logout/')
    assert resolver.view_name == 'account_logout'


def test_discord_login():
    resolver = resolve('/accounts/discord/login/')
    assert resolver.view_name == 'discord_login'
