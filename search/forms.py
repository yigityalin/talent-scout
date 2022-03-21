from django import forms
from .models import Search, Profession


class ProfessionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['skills'].delimiter = Profession.DELIMITER

    class Meta:
        model = Profession
        fields = '__all__'


class SearchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        attrs = {
            "placeholder": 'What are you looking for?',
        }
        self.fields.get('query').widget.attrs.update(attrs)

    class Meta:
        model = Search
        fields = ['query', 'by']
