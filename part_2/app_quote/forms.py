from django.forms import ModelForm, CharField, TextInput, DateField, DateInput, HiddenInput, IntegerField
from .models import Tag, Quote, Author


class TagForm(ModelForm):
    name = CharField(min_length=3, max_length=50, required=True, widget=TextInput())

    class Meta:
        model = Tag
        fields = ['name']


class QuoteForm(ModelForm):
    quote  = CharField(min_length=5, max_length=2500, required=True, widget=TextInput())

    class Meta:
        model = Quote
        fields = ['quote']
        exclude = ['tags', 'author']


class AuthorForm(ModelForm):
    # id = IntegerField(widget=HiddenInput(), required=False)
    fullname = CharField(min_length=3, max_length=150, required=True, widget=TextInput())
    born_date = DateField(
        input_formats=['%Y-%m-%d', '%d-%m-%Y'], 
        widget=DateInput(attrs={'type': 'date'}),
        required=True
    )
    born_location = CharField(min_length=3, max_length=100, required=True, widget=TextInput())
    description = CharField(max_length=1000, required=False, widget=TextInput())

    class Meta:
        model = Author
        fields = ['fullname', 'born_date', 'born_location', 'description']
