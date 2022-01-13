from rest_framework import viewsets
from rest_framework.response import Response
from django.views.decorators.cache import cache_page
from django.urls import reverse
from .service import update_transactions
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.utils.decorators import method_decorator

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

class GuiaBolsoTokenViewSet(viewsets.ViewSet):

	@method_decorator(cache_page(CACHE_TTL))
	def list(self, request, format=None):
		amount_inserted = update_transactions(request.user)

		if amount_inserted < 0:
			return Response("Token invalid or not created, please visit: %s"%request.build_absolute_uri(reverse('list_guiabolso')))

		return Response("%d transactions created"%amount_inserted)