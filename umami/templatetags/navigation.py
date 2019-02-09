# -*- coding: utf-8 -*-
import re

from django import template
from django.urls import NoReverseMatch, reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, target):
    try:
        pattern = '^' + reverse(target)
    except NoReverseMatch:
        pattern = target
    path = context['request'].path
    if re.search(pattern, path):
        return 'active'
    return ''
