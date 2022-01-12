from django.urls import path, include
from rest_framework import authentication, permissions
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from investments.models import GuiaBolsoToken, GuiaBolsoTransaction
from django.contrib.auth.models import User
from datetime import datetime
import subprocess
import json

curl_text = """curl 'https://kasbah.guiabolso.com.br/v2/events/' \
  -H 'authority: kasbah.guiabolso.com.br' \
  -H 'pragma: no-cache' \
  -H 'cache-control: no-cache' \
  -H 'sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'content-type: application/json' \
  -H 'accept: */*' \
  -H 'origin: https://app.guiabolso.com.br' \
  -H 'sec-fetch-site: same-site' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-dest: empty' \
  -H 'referer: https://app.guiabolso.com.br/' \
  -H 'accept-language: pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7' \
  --data-raw '{"name":"users:summary:month","version":"1","payload":{"userPlatform":"GUIABOLSO","appToken":"1.1.0","os":"MacIntel","monthCode":24264},"flowId":"1c769230-9285-4c54-9a97-4c57e153fc5f","id":"d9e77702-58aa-41c0-9dca-dbffbc5a4d3c","auth":{"token":"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdXRoIjoiTWpJeVpqbGhNakZpTVRabFlUSmlNR1kyT0dVM01tRXhPR1JrTVdOaVpXTXVNemMwTXpjM01qSTFNalUwTXpneE16azJNVEkwTXprMU1URTRNekk1TVRVNE5EUTBOekl3T0RZMk1EQTVNRE13TnpRMk1UYzJPRE16TkRrNE1UWXpORE13TURnNE5qSTJNelkxTXprek5UTXlOamN5TmpBNE1ETXpORGs1TkRjd05qUTJNakl6TVRnMk9RPT0iLCJpc3MiOiJ3ZWIiLCJzZXNzaW9uVG9rZW4iOiIzNzQzNzcyMjUyNTQzODEzOTYxMjQzOTUxMTgzMjkxNTg0NDQ3MjA4NjYwMDkwMzA3NDYxNzY4MzM0OTgxNjM0MzAwODg2MjYzNjUzOTM1MzI2NzI2MDgwMzM0OTk0NzA2NDYyMjMxODY5IiwiZXhwIjoxNjQ3MTI0MjMxLCJpYXQiOjE2NDE5NDAyMzEsInBsYXRmb3JtIjoibW9iaWxlIiwiZGV2aWNlVG9rZW4iOiIyMjJmOWEyMWIxNmVhMmIwZjY4ZTcyYTE4ZGQxY2JlYyJ9.El6vWsJfImWbwE0556yeIoMUIXF07bvmwkk0seMRkN-1H9bCJbt3MCEztPJGdJ0nOTOlmdhidi9J51NkHCrDarjCB_8tLf3AROdmGSfeeObFfeQ5qyHXlERw9Vrzu4V21m8yf1gfkw81LiJhVnir8-f8CcLE5aRgEWJ1uWcD8tcIFR5e3bTxkjLfoiy0qHprwY0EfASD-8mAOVb2SdFjFfnfhrihRO4YYR8rg1mLPJbRIWSRnThHEdyn5rP_odm0paq6OyxU8NiXqh1zoHBBrC7c5btYvHYg5QMWXM60madsoGAIjoIJS6s019JoKVEq6Y8IVdSaonV-leZPC7ky6nL8B0_dXfP7lQr7yB-3AE3eN90hr1Bu0ddZTnt5lSPJjaKJYPq2e0J-RCJj5RSH9W1Cwxh6zThS_8s_156acfDmd5uIGd6nnZ_KhcLmXjyPeznOR3G7ujjQ4lGSBccL9T7t3P11lPYgLwB61K1IgXxXqIbXq94uLAFqDFLICmzjLe0_yo_ICurE_vd_ib5hWyUqwuwqZQR9ri8PyNP2MP9ddcbW2PUfCnA-i5FPbsPLY2_Hzm1YYEutQYMQfjN34QR-Lt8ju4ATQfqmWRHs7miQtcgGxyyj7HOcziEZVVY9TzWY0dUpOhm_St5ELa-7JEcoNQpBrQqfimdDX1yyNFA","sessionToken":"eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdXRoIjoiTWpJeVpqbGhNakZpTVRabFlUSmlNR1kyT0dVM01tRXhPR1JrTVdOaVpXTXVNemMwTXpjM01qSTFNalUwTXpneE16azJNVEkwTXprMU1URTRNekk1TVRVNE5EUTBOekl3T0RZMk1EQTVNRE13TnpRMk1UYzJPRE16TkRrNE1UWXpORE13TURnNE5qSTJNelkxTXprek5UTXlOamN5TmpBNE1ETXpORGs1TkRjd05qUTJNakl6TVRnMk9RPT0iLCJpc3MiOiJ3ZWIiLCJzZXNzaW9uVG9rZW4iOiIzNzQzNzcyMjUyNTQzODEzOTYxMjQzOTUxMTgzMjkxNTg0NDQ3MjA4NjYwMDkwMzA3NDYxNzY4MzM0OTgxNjM0MzAwODg2MjYzNjUzOTM1MzI2NzI2MDgwMzM0OTk0NzA2NDYyMjMxODY5IiwiZXhwIjoxNjQ3MTI0MjMxLCJpYXQiOjE2NDE5NDAyMzEsInBsYXRmb3JtIjoibW9iaWxlIiwiZGV2aWNlVG9rZW4iOiIyMjJmOWEyMWIxNmVhMmIwZjY4ZTcyYTE4ZGQxY2JlYyJ9.El6vWsJfImWbwE0556yeIoMUIXF07bvmwkk0seMRkN-1H9bCJbt3MCEztPJGdJ0nOTOlmdhidi9J51NkHCrDarjCB_8tLf3AROdmGSfeeObFfeQ5qyHXlERw9Vrzu4V21m8yf1gfkw81LiJhVnir8-f8CcLE5aRgEWJ1uWcD8tcIFR5e3bTxkjLfoiy0qHprwY0EfASD-8mAOVb2SdFjFfnfhrihRO4YYR8rg1mLPJbRIWSRnThHEdyn5rP_odm0paq6OyxU8NiXqh1zoHBBrC7c5btYvHYg5QMWXM60madsoGAIjoIJS6s019JoKVEq6Y8IVdSaonV-leZPC7ky6nL8B0_dXfP7lQr7yB-3AE3eN90hr1Bu0ddZTnt5lSPJjaKJYPq2e0J-RCJj5RSH9W1Cwxh6zThS_8s_156acfDmd5uIGd6nnZ_KhcLmXjyPeznOR3G7ujjQ4lGSBccL9T7t3P11lPYgLwB61K1IgXxXqIbXq94uLAFqDFLICmzjLe0_yo_ICurE_vd_ib5hWyUqwuwqZQR9ri8PyNP2MP9ddcbW2PUfCnA-i5FPbsPLY2_Hzm1YYEutQYMQfjN34QR-Lt8ju4ATQfqmWRHs7miQtcgGxyyj7HOcziEZVVY9TzWY0dUpOhm_St5ELa-7JEcoNQpBrQqfimdDX1yyNFA"},"metadata":{"origin":"web","appVersion":"1.0.0","utm":"site","createdAt":"2021-12-29T20:52:17.136Z"},"identity":{}}' \
  --compressed"""


class GuiaBolsoTokenViewSet(viewsets.ViewSet):
	def list(self, request, format=None):
		response = subprocess.check_output(curl_text, shell=True)
		try:
			payload = json.loads(response.decode('utf-8'))
		except Exception:
			print("Please update the curl request")
			exit()

		print(payload)

		queryset = GuiaBolsoToken.objects.all()
		return Response([token.as_json() for token in queryset])

	def create(self, request): # Here is the new update comes <<<<
		post_data = request.data
		user = post_data['user']
		data = json.loads(post_data['data'])

		for row in data:
			transaction = GuiaBolsoTransaction()
			transaction.user = User.objects.get(username=user)
			transaction.date = datetime.fromtimestamp(int(row['date'])/1000)
			transaction.value = float(row['value'])
			transaction.label = row['label']
			transaction.description = row['description']
			transaction.category = row['category']
			transaction.save()

		return Response(data="Saved %d transactions."%(len(data)))

