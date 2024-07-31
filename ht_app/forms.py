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
    class Meta:
        fields = ['Name', 'Line', 'Shift', 'Plant', 'Operation', 'Type_training', 'Week_start', 'Week_end', 'Technician', 'StartDate']
        widgets = {
            'StartDate': forms.DateInput(attrs={'type': 'date'}),
        }
