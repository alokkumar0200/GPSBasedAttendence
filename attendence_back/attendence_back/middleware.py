import urllib.parse



class GetSubdomainMiddleware:

	def __init__(self, get_response):
		self.get_response = get_response


	def __call__(self, request):
		bits = urllib.parse.urlsplit(request.META['HTTP_HOST'])[2].split('.')
		# print(request.META)
		if not(len(bits) == 2):
			request.subdomain = ''
		else:
			request.subdomain = bits[0]

		#print(request.subdomain)

		response = self.get_response(request)

		return response