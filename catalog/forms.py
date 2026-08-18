from django import forms

from .models import VenueSuggestion


class VenueSuggestionForm(forms.ModelForm):
    def __init__(self, *args, authenticated=False, **kwargs):
        super().__init__(*args, **kwargs)
        if authenticated:
            self.fields.pop("submitter_name", None)
            self.fields.pop("submitter_email", None)

    class Meta:
        model = VenueSuggestion
        fields = [
            "name",
            "city",
            "address",
            "website_url",
            "notes",
            "submitter_name",
            "submitter_email",
        ]
        labels = {
            "name": "Venue name",
            "city": "City",
            "address": "Address",
            "website_url": "Website",
            "notes": "Additional notes",
            "submitter_name": "Your name",
            "submitter_email": "Your email",
        }
        help_texts = {
            "notes": "Anything else you'd like us to know about this venue.",
            "submitter_email": "Optional — we may follow up with you.",
        }
