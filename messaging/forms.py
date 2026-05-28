from django import forms


class MessageSendForm(forms.Form):
    body = forms.CharField(
        max_length=2000,
        required=True,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "class": "mk-input",
                "placeholder": "Write a message...",
            }
        ),
    )

