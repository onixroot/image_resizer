from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from image_resizer.settings import MEDIA_ROOT, MEDIA_URL

import os
import PIL

from .models import Image
from .utils import get_hash

class ImageTests(TestCase):

	def setUp(self):
		if os.path.exists(MEDIA_ROOT + '/django.jpg'):
			os.remove(MEDIA_ROOT + '/django.jpg')
		with open(MEDIA_ROOT + '/test/django.webp', 'rb') as image:
			image_content = image.read()
		self.image = SimpleUploadedFile('django.webp', image_content)
		self.url = 'http://localhost:8000' + MEDIA_URL + 'test/django.webp'
		self.wrong_ext = 'http://domain.com/path/image.exe'
		self.wrong_url = 'http://domain.com/path/image.jpg'
		self.slug = get_hash(image_content)


	def test_upload_clean_both_fields(self):
		response = self.client.post(reverse('upload'), {
			'image': self.image,
			'url': self.url,
		})
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Choose single upload option')

	def test_upload_clean_empty_fields(self):
		response = self.client.post(reverse('upload'), {
			'image': '',
			'url': '',
		})
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Load image or specify image URL')

	def test_upload_clean_wrong_ext(self):
		response = self.client.post(reverse('upload'), {
			'image': '',
			'url': self.wrong_ext,
		})
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Enter correct image URL')

	def test_upload_file(self):
		response = self.client.post(reverse('upload'), {
			'image': self.image,
			'url': '',
		})
		self.assertEqual(response.status_code, 302)
		img_obj = Image.objects.first()
		self.assertEqual(img_obj.id, 1)
		self.assertEqual(img_obj.slug, self.slug)
		self.assertEqual(os.path.exists(MEDIA_ROOT + '/django.jpg'), True)
		self.sub_test_change_dimensions()
		self.sub_test_change_size()
		self.sub_test_wrong_request()		
		os.remove(MEDIA_ROOT + '/django.jpg')

	def sub_test_change_dimensions(self):
		response = self.client.get(f'/{self.slug}/?width=200&height=100')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(os.path.exists(MEDIA_ROOT + '/resized/200x100__django.jpg'), True)
		image = PIL.Image.open(MEDIA_ROOT + '/resized/200x100__django.jpg')
		self.assertEqual((image.size), (200,100))
		os.remove(MEDIA_ROOT + '/resized/200x100__django.jpg')

	def sub_test_change_size(self):
		response = self.client.get(f'/{self.slug}/?size=50000')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(os.path.exists(MEDIA_ROOT + '/resized/50000b__django.jpg'), True)
		self.assertEqual(os.path.getsize(MEDIA_ROOT + '/resized/50000b__django.jpg')<50000, True)
		os.remove(MEDIA_ROOT + '/resized/50000b__django.jpg')
		response = self.client.get(f'/{self.slug}/?size=1')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(os.path.exists(MEDIA_ROOT + '/resized/MIN__django.jpg'), True)
		self.assertContains(response, 'Minimal quality reached having current width and height')
		os.remove(MEDIA_ROOT + '/resized/MIN__django.jpg')

	def sub_test_wrong_request(self):
		response = self.client.get(f'/{self.slug}/?size=test')
		self.assertEqual(response.status_code, 400)
		response = self.client.get(f'/{self.slug}/?size=10000&width=test')
		self.assertEqual(response.status_code, 400)

	def test_upload_by_url(self):
		self.sub_test_wrong_image_url()
		print('\n\nTest "test_upload_by_url" require working Django runserver to download the image')
		answer = 'None'
		while answer not in 'yYnN':
			print('Do you want to run "test_upload_by_url" [y/N]')
			answer = input()
		if answer and answer in 'yY':
			response = self.client.post(reverse('upload'), {
				'image': '',
				'url': self.url,
			})
			self.assertEqual(response.status_code, 302)
			img_obj = Image.objects.first()
			self.assertEqual(img_obj.id, 1)
			self.assertEqual(img_obj.slug, self.slug)
			self.assertEqual(os.path.exists(MEDIA_ROOT + '/django.jpg'), True)
			os.remove(MEDIA_ROOT + '/django.jpg')

	def sub_test_wrong_image_url(self):
		response = self.client.get(self.wrong_url)
		self.assertEqual(response.status_code, 404)