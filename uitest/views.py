from uuid import uuid4

from django import forms
from django.shortcuts import render

from uitest.models import Rack


class RowTextInput(forms.TextInput):
    template_name = "uitest/rows/field.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["form"] = self.form
        context["widget"]["field"] = self.form[
            name.removeprefix(self.form.prefix + "-")
        ]
        return context


class RackAddForm(forms.ModelForm):
    class Meta:
        model = Rack

        fields = (
            "name",
            "location",
        )

        widgets = {
            "name": RowTextInput(),
            "location": RowTextInput(),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if not self.prefix:
            if self.instance.id:
                self.uuid = None
                self.prefix = f"rack-{self.instance.id}"
            else:
                self.uuid = uuid4()
                self.prefix = f"rack-new-{uuid4()}"

        for _, field in self.fields.items():
            field.widget.form = self

    def form_index(self):
        if self.instance and self.instance.id:
            return self.instance.id
        else:
            return self.uuid


def index(request):
    racks = Rack.objects.all()

    forms = [RackAddForm(instance=rack) for rack in racks]

    context = {
        "forms": forms,
    }
    return render(request, "uitest/index.html", context)


def rack_add(request):
    form = RackAddForm()
    context = {"form": form}
    return render(request, "uitest/rows/rack.html", context)


def get_form_ids(request):
    form_ids = {}
    for k, _ in request.POST.items():
        form_id = None

        if k.startswith("rack-new"):
            field_name = k[k.rindex("-") + 1 :]
            form_id = k[: -len(field_name)][:-1]
            instance_id = None
        else:
            field_name = k[k.rindex("-") + 1 :]
            form_id = k[: -len(field_name)][:-1]
            instance_id = form_id.removeprefix("rack-")

        if form_id not in form_ids:
            form_ids[form_id] = instance_id

    return form_ids


def rack_get(request, rack_id):
    instance = Rack.objects.get(pk=rack_id)
    form = RackAddForm(data=request.POST, instance=instance)

    context = {
        "form": form,
    }

    return render(request, "uitest/rows/rack.html", context)


def rack_update(request, form_index):
    # FIXME:
    # There's a bug where, after the user causes HTMX to POST with a new
    # object form, the input focus is basically lost.
    # e.g. you can't tab between inputs
    form_ids = get_form_ids(request)

    form = None
    for form_id, instance_id in form_ids.items():
        instance = Rack.objects.get(pk=instance_id) if instance_id else None
        form = RackAddForm(data=request.POST, prefix=form_id, instance=instance)

    try:
        form.save()

        # If a form for a new object (no PK yet) was saved, need to make
        # a new form reflecting the newly assigned PK.
        # TODO:
        # This is a little weird...
        # The widget prefixes seem to remain unchanged if form.prefix is altered.
        # Here a new form is created so the widget names are correct.
        # Otherwise the "rack-UUID-" form prefix will still be used.
        # Notice that the request.POST data is not reused, since 1) it's redundant
        # with the instance available and 2) it will be invalid for this form
        # instance since the prefix doesn't match.
        if form.instance and form.instance.id:
            prefix = f"rack-{form.instance.id}"
            form = RackAddForm(prefix=prefix, instance=form.instance)
    except:
        # Failed to save
        # Form will include errors
        pass

    form.form_index = form_index

    context = {
        "form": form,
    }

    return render(request, "uitest/rows/rack.html", context)
