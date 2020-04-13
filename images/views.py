from django.views import generic
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseBadRequest

import PIL
import os
import shutil

from .models import Image
from .forms import UploadForm
from .utils import is_numeric, get_dimensions, set_size
from image_resizer.settings import MEDIA_ROOT as MEDIA


class ImagesListView(generic.ListView):
	model = Image
	template_name = 'images_list.html'
	context_object_name = 'images'

class UploadView(generic.CreateView):
	form_class = UploadForm
	template_name = 'upload.html'

def image(request, slug):
	obj = Image.objects.get(slug=slug)
	context = {}
	width = request.GET.get('width')
	height = request.GET.get('height')
	size = request.GET.get('size')

	if any((width, height, size)):
		if not is_numeric(width, height, size):
			return HttpResponseBadRequest()
		shutil.copyfile(f'{MEDIA}/{obj.image.name}', f'{MEDIA}/_{obj.image.name}')
		obj.image.name = f'_{obj.image.name}'
		if any((width, height)):
			width, height = get_dimensions(obj.image.width, obj.image.height, width, height)
			img = PIL.Image.open(f'{MEDIA}/{obj.image.name}')
			img = img.resize((width, height))
			img.save(f'{MEDIA}/{obj.image.name}', quality=95)
			shutil.move(f'{MEDIA}/{obj.image.name}', f'{MEDIA}/{width}x{height}_{obj.image.name}')
			obj.image.name = f'{width}x{height}_{obj.image.name}'
		if size:
			result = set_size(f'{MEDIA}/{obj.image.name}', int(size))
			if result:
				messages.add_message(request, messages.INFO, result)
				shutil.move(f'{MEDIA}/{obj.image.name}', f'{MEDIA}/MIN_{obj.image.name}')
				obj.image.name = f'MIN_{obj.image.name}'
			else:
				shutil.move(f'{MEDIA}/{obj.image.name}', f'{MEDIA}/{size}b_{obj.image.name}')
				obj.image.name = f'{size}b_{obj.image.name}'
		shutil.move(f'{MEDIA}/{obj.image.name}', f'{MEDIA}/resized/{obj.image.name}')
		obj.image.name = f'resized/{obj.image.name}'
	context['image_obj'] = obj
	context['size'] = os.path.getsize(f'{MEDIA}/{obj.image.name}')
	context['width'] = width if width  else obj.image.width
	context['height'] = height if height else obj.image.height
	return render(request, 'image.html', context)
