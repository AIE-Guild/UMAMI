from django import forms

from guildmaster import models


class ClientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        adapter_type = self._meta.model._control.id
        if adapter_type:
            self.fields['adapter'].choices = tuple([x for x in models.Client.ADAPTER_CHOICES if x[0] == adapter_type])
            self.fields['scopes'].queryset = models.ClientScope.objects.filter(adapter=adapter_type)

    class Meta:
        model = models.Client
        exclude = []
