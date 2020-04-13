from django import forms
from django.core.exceptions import ValidationError

from .models import Image

image_formats = ('.jpg', '.jpeg', '.png', '.gif', '.webp')


class UploadForm(forms.ModelForm):
	image = forms.ImageField(required=False, label='Choose image')
	url = forms.URLField(max_length=500, required=False, label='Enter image URL')

	class Meta:
		model = Image
		fields = ('image', 'url')

	def clean(self):
		cleaned_data = super().clean()
		url = cleaned_data.get('url')
		image = cleaned_data.get('image')
		if url and image:
			raise forms.ValidationError("Choose single upload option")
		if not url and not image:
			raise forms.ValidationError("Load image or specify image URL")
		if url and not url.endswith(image_formats):
			raise ValidationError("Enter correct image URL")
		return cleaned_data
