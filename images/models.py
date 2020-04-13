from django.db import models
from django.urls import reverse

from .utils import compress, get_hash, get_image


class Image(models.Model):
	slug = models.SlugField(max_length=32, unique=True)
	image = models.ImageField(verbose_name='Image')
	url = models.URLField(max_length=500, verbose_name='URL-address')

	def save(self, *args, **kwargs):
		if self.url:
			image = get_image(self.url)
			self.image = image
			self.slug = get_hash(image.read())
		else:
			self.url = 'Loaded from file'
			self.slug = get_hash(self.image.instance.image.read())
		if Image.objects.filter(slug=self.slug):
			return self.get_absolute_url()		
		new_image = compress(self.image)
		self.image = new_image
		super().save(*args, **kwargs)

	def get_absolute_url(self):
		return reverse('image', args=[self.slug])