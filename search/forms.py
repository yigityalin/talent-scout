from django import forms
from .models import Search


class SearchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            attrs = {
                "placeholder": 'What are you looking for?',
            }
            self.fields[field].widget.attrs.update(attrs)

    class Meta:
        model = Search
        fields = ['query', 'by']
