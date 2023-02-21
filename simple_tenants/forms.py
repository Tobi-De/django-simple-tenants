from django import forms


def call_if_callable(value):
    return value() if callable(value) else value


class LazyModelChoiceField(forms.Field):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        super().__init__()

    def make_real_field(self):
        return forms.ModelChoiceField(
            *(call_if_callable(arg) for arg in self.args),
            **{name: call_if_callable(arg) for name, arg in self.kwargs.items()},
        )


class TenantAwareFormMixin:
    def __init__(self, *args, **kwargs):
        for name, field in self.base_fields.items():
            if isinstance(field, forms.ModelChoiceField):
                self.base_fields[name].queryset = field.queryset.model._meta.default_manager.all()
            if isinstance(field, LazyModelChoiceField):
                self.base_fields[name] = field.make_real_field()
        super().__init__(*args, **kwargs)
