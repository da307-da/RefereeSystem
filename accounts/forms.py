from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, RefereePerformanceRating

class ExRefereeRegistrationForm(UserCreationForm):
    first_name = forms.CharField( 
        max_length=30, 
        required=True, 
        help_text="Required", 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField( 
        max_length=30, 
        required=True, 
        help_text="Required", 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    fa_certificate_id = forms.CharField(
        max_length=100,
        required=True,
        help_text="Enter your FA Referee Course Certificate ID",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    career_duration = forms.CharField(
        max_length=50,
        required=True,
        help_text="Enter your total years of officiating",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ["username", "first_name", "last_name", "email", "password1", "password2", "fa_certificate_id", "career_duration"]

class RefereeRegistrationForm(UserCreationForm):
    fa_certificate_id = forms.CharField(
        max_length=100,
        required=True,
        label="FA Referee Course Certificate ID",
        help_text="Enter your FA Referee Course Certificate ID.",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ["username", "email", "fa_certificate_id", "password1", "password2"]

    def clean_fa_certificate_id(self):
        # Ensure the FA Certificate ID is unique
        fa_certificate_id = self.cleaned_data.get('fa_certificate_id')
        if CustomUser.objects.filter(fa_certificate_id=fa_certificate_id).exists():
            raise forms.ValidationError("This FA Certificate ID is already registered.")
        return fa_certificate_id


    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'referee'
        if commit:
            user.save()
        return user

class RefereeDetailsForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['nationality', 'years_of_experience', 'is_current_referee', 'career_duration']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['career_duration'].required = False  # Make this field optional

    def clean(self):
        cleaned_data = super().clean()
        is_current_referee = cleaned_data.get('is_current_referee')
        career_duration = cleaned_data.get('career_duration')

        if not is_current_referee and not career_duration:
            raise forms.ValidationError("Please provide the duration of your career if you are an ex-referee.")
        return cleaned_data


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'user'  # Set the user_type to 'user'
        user.email = self.cleaned_data['email']  # Save the email field
        if commit:
            user.save()
        return user
    


class CustomLoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ["username", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes and placeholders to the default fields
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                field.widget.attrs['class'] += ' is-invalid'

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_picture']

class RefereeRatingForm(forms.ModelForm):
    class Meta:
        model = RefereePerformanceRating
        fields = ['rating_score', 'feedback']
        widgets = {
            'rating_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '10',
                'step': '0.1'
            }),
            'feedback': forms.Textarea(attrs={
                'class': 'form-control feedback-box white-placeholder',
                'rows': 4,
                'placeholder': 'Provide your assessment of the referee\'s performance'
            })
        }