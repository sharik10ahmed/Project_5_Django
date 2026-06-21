from django import forms
from .models import User


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'full_name',
            'email',
            'mobile_no',
            'alternate_mobile_no',
            'dob',
            'gender',
            'address',
            'profile_image'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'mobile_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mobile Number',
                'type': 'tel'
            }),
            'alternate_mobile_no': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Alternate Mobile Number (Optional)',
                'type': 'tel'
            }),
            'dob': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Address',
                'rows': 4
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/webp,image/jpeg,image/png,image/gif'
            })
        }

    def clean_profile_image(self):
        profile_image = self.cleaned_data.get('profile_image')

        if profile_image:
            # Check file size (5MB max)
            if profile_image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image size must not exceed 5MB')

            # Check file format
            allowed_formats = ['image/webp', 'image/jpeg', 'image/png', 'image/gif']
            if profile_image.content_type not in allowed_formats:
                raise forms.ValidationError(
                    'Only WebP, JPEG, PNG and GIF formats are supported'
                )

        return profile_image

