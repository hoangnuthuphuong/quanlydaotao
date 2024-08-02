from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class SearchForm(forms.Form):
    id = forms.CharField(
        label='id',
        max_length=6,
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Nhập ID',
                'class': 'form-control',
            }
        ),
    )

    startdate = forms.DateField(
        label='startdate',
        required=False,
        widget=forms.DateInput(
            attrs={
                'placeholder': 'Nhập ngày bắt đầu',
                'class': 'form-control',
                'type': 'date',
            }
        ),
    )

    line = forms.CharField(
        label='line',
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Nhập line',
                'class': 'form-control',
            }
        ),
    )

    shift = forms.CharField(
        label='shift',
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Nhập ca',
                'class': 'form-control',
            }
        ),
    )

    class Meta:
        fields = ('id', 'startdate', 'line', 'shift')


class EditForm(forms.Form):
    Name = forms.CharField(max_length=100, required=False)
    Line = forms.CharField(max_length=100, required=False)
    Shift = forms.CharField(max_length=100, required=False)
    Plant = forms.CharField(max_length=100, required=False)
    Operation = forms.CharField(max_length=100, required=False)
    Type_training = forms.CharField(max_length=100, required=False)
    Week_start = forms.CharField(max_length=100, required=False)
    Week_end = forms.CharField(max_length=100, required=False)
    Technician = forms.CharField(max_length=100, required=False)
    StartDate = forms.CharField(max_length=100, required=False)

