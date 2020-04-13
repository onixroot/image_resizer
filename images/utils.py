from django.core.files.base import ContentFile
from django.core.files import File
from django.http import Http404

import PIL
import io
import hashlib
import requests
import subprocess

def compress(image):
	img = PIL.Image.open(image)
	if img.mode != 'RGB':
                img = img.convert('RGB')
	im_io = io.BytesIO() 
	img.save(im_io, 'JPEG', quality=95) 
	new_image = File(im_io, name=f"{'.'.join(image.name.split('.')[:-1])}.jpg")
	return new_image

def get_hash(file_content):
	return hashlib.md5(file_content).hexdigest()

def get_image(url):
	image = requests.get(url)
	if image.status_code != 200:
		raise Http404("Image not found")
	name = url.split('/')[-1]
	image_obj = ContentFile(image.content, name=name)
	return image_obj

def get_dimensions(source_width, source_height, width=None, height=None):
	'''
	Calculates new dimensions in respect to original dimensions
	If both new dimensions provided just returns int values
	'''
	if width and not height:
		wpercent = int(width) / source_width
		height = source_height * wpercent
		return int(width), int(height)
	elif height and not width:
		hpercent = int(height) / source_height
		width = source_width * hpercent
		return int(width), int(height)
	else:
		return int(width), int(height)

def jpegoptim(file, cmd_size, change=False):
	'''
	Linux console utility "jpegoptim" to optimize/compress JPEG files
	'''
	PIPE = subprocess.PIPE
	if change:
		cmd_change = f'jpegoptim -qS {cmd_size} {file}'
		p = subprocess.Popen(cmd_change, shell=True, stdout=PIPE)
		p.wait()
	else:
		cmd_check = f'jpegoptim -nbS {cmd_size} {file}'
		p = subprocess.Popen(cmd_check, shell=True, stdout=PIPE)
		p.wait()
		response = str(p.stdout.read())
		new_size = int(response.split(',')[5])
		return new_size

def set_size(file, size):
	'''
	Uses Linux console utility "jpegoptim"
	Reduce quality of the image up to provided size
	If it's impossible, reduce to the lowest possible size
	'''
	cmd_size = int(size/1024)
	new_size = jpegoptim(file, cmd_size)
	while new_size > size:
		cmd_size -= 1
		if cmd_size<=1:
			jpegoptim(file, cmd_size, True)
			return 'Minimal quality reached having current width and height' 
		new_size = jpegoptim(file, cmd_size)
	jpegoptim(file, cmd_size, True)

def is_numeric(*values):
	for value in values:
		if value and not value.isdigit():
			return False
	return True