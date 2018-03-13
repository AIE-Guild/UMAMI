# -*- coding: utf-8 -*-
from django import template

from umami.models import Bulletin

register = template.Library()


class GroupBulletinsNode(template.Node):
    def __init__(self, size, name):
        self.size = int(size)
        self.name = name

    def render(self, context):
        if context['user'].is_authenticated:
            query = Bulletin.objects.filter(publish=True)
        else:
            query = Bulletin.objects.filter(publish=True, public=True)
        if self.size > 0:
            context[self.name] = [tuple(query[i:i + self.size]) for i in range(0, len(query), self.size)]
        else:
            context[self.name] = query
        return ''


@register.tag('group_bulletins')
def group_bulletins(parser, token):
    tokens = token.contents.split()
    if len(tokens) != 4:
        raise template.TemplateSyntaxError("'{}' tag requires three arguments.".format(tokens[0]))
    if tokens[2] != 'as':
        raise template.TemplateSyntaxError("Second argument to '{}' tag must be 'as'.".format(tokens[2]))
    return GroupBulletinsNode(tokens[1], tokens[3])
