from django import forms


class FontFilterForm(forms.Form):
    """Validate filter parameters for FontListView."""

    lang = forms.CharField(required=False, label="Language")
    family = forms.CharField(required=False, label="Family")
    style = forms.CharField(required=False, label="Style")

    GROUP_CHOICES = [
        ("", "No grouping"),
        ("lang", "Language"),
        ("family", "Family"),
        ("style", "Style"),
    ]
    group_by = forms.ChoiceField(required=False, choices=GROUP_CHOICES, label="Group by")

    def get_filters(self) -> dict:
        """Return cleaned filter values suitable for fontconfig.query."""
        if not self.is_valid():
            return {}
        return {
            key: value
            for key, value in self.cleaned_data.items()
            if key in {"lang", "family", "style"} and value
        }
