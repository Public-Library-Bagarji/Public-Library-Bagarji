from django import forms
from messages_requests.models import BookRequest

class BookRequestForm(forms.ModelForm):
    class Meta:
        model = BookRequest
        fields = ['book_name', 'author_name', 'message']
        widgets = {
            'book_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Book Name', 'required': True}),
            'author_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Author Name', 'required': True}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Say something...', 'rows': 3}),
        } 