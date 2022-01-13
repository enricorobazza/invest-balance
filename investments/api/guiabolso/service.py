import subprocess
import json
from time import time
from django.db.models.expressions import F
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
from .consts import curl_text
from investments.models import GuiaBolsoToken, GuiaBolsoTransaction
from django.utils import timezone

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

def merge_or_set(merged, df):
	if merged is None:
		merged = df
	else:
		merged = pd.concat([merged, df])
	return merged

def format_df(df, categories):
	for column in ['date', 'modified', 'created']:
		df[column] = pd.to_datetime(df[column], unit='ms')

	categories.rename(columns={"id": "categoryId"}, inplace=True)
	categories.rename(columns={"name": "category"}, inplace=True)

	return df.merge(categories[['categoryId', 'category']], on='categoryId', how='left')

def transactions_for_month_code(token, month_code="24263"):
	response = subprocess.check_output(curl_text%(
		month_code,
		"Bearer "+token,
		token,
	), shell=True)

	try:
		payload = json.loads(response.decode('utf-8'))
	except Exception:
		return None
	statements = payload["payload"]["userMonthHistory"]["statements"]
	categoryTypes = payload["payload"]["rawData"]["categoryTypes"]

	categories_df = None

	for categoryType in categoryTypes:
		categories = categoryType['categories']
		df = pd.DataFrame(categories)

		categories_df = merge_or_set(categories_df, df)

	merged_df = None

	for statement in statements:
		transactions = statement["transactions"]
		df = pd.DataFrame(transactions)

		merged_df = merge_or_set(merged_df, df)

	return format_df(merged_df, categories_df)

def months_diff(date_after, date_before):
	return (date_after.year - date_before.year)*12 + (date_after.month - date_before.month)

def get_code_for_month(date):
	december = datetime.datetime(2021, 12, 1)
	december_code = 24263
	return december_code + months_diff(date, december)

def get_months_for_token(token, start_month=None, end_month=datetime.datetime.now()):
	if start_month is None:
		start_month = datetime.datetime.now() - relativedelta(years=1)

	start_month = start_month.replace(day=1, tzinfo=None)

	month = end_month
	merged_df = None

	while month > start_month:
		month_code = get_code_for_month(month)
		df = transactions_for_month_code(token, month_code)
		if df is None:
			return None, start_month
		merged_df = merge_or_set(merged_df, df)

		month = month - relativedelta(months=1)

	merged_df = merged_df[~merged_df["deleted"]]
	merged_df = merged_df[~merged_df["duplicated"]]
	merged_df = merged_df[['label', 'date', 'currency', 'description', 'value', 'category']]

	return merged_df, start_month

def batch_insert(objs, Model, batch_size=100):
	start = 0
	while start < len(objs):
		if start + batch_size > len(objs):
			end = len(objs)
		else:
			end = start + batch_size
		batch = objs[start:end]
		Model.objects.bulk_create(batch, batch_size)
		start = end

def update_transactions(user):
	try:
		token = GuiaBolsoToken.objects.get(user=user)
	except GuiaBolsoToken.DoesNotExist:
		return -1

	if not token.valid:
		return -1

	start_month = token.last_transaction_date
	df, start_month = get_months_for_token(token.token, start_month)

	if df is None:
		token.valid = False 
		token.save()
		return -1

	transactions = []
	for i in range(df.shape[0]):
		row = df.iloc[i]
		transaction = GuiaBolsoTransaction()
		transaction.user = user
		transaction.date = row['date'].replace(tzinfo=zoneinfo.ZoneInfo('America/Sao_Paulo'))
		transaction.value = float(row['value'])
		transaction.label = row['label']
		transaction.description = row['description']
		transaction.category = row['category']
		transactions.append(transaction)

	deleted = GuiaBolsoTransaction.objects.filter(user=user, date__gte=start_month).delete()[0]
	batch_insert(transactions, GuiaBolsoTransaction)

	token.last_updated = timezone.now()
	token.save()

	return len(transactions) - deleted