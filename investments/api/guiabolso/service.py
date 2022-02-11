import subprocess
import json
from time import time
from django.db.models.expressions import F
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
from .consts import curl_text
from investments.models import GuiaBolsoToken, GuiaBolsoTransaction, GuiaBolsoCategory, GuiaBolsoCategoryBudget
from django.utils import timezone

categories = {}

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

class GuiaBolsoService:

	def __init__(self, user):
		self.user = user
		self.update_categories_as_dict()

	def merge_or_set(self, merged, df):
		if merged is None:
			return df
		if df is None or df.shape[0] == 0:
			return merged
		return pd.concat([merged, df])

	def format_df(self, df):
		if df.shape[0] == 0:
			return df

		for column in ['date', 'modified', 'created']:
			df[column] = pd.to_datetime(df[column], unit='ms')

		return df

	def update_categories_as_dict(self):
		categories = GuiaBolsoCategory.objects.filter(user=self.user)
		categories_dict = {}
		for category in categories:
			categories_dict[category.code] = category
		self.categories = categories_dict

	def create_category_budgets(self, month, categories_df, budgets_df):
		GuiaBolsoCategoryBudget.objects.filter(month=month.month, year=month.year).delete()

		categories_budgets = []

		# Create categories budgets
		for i in range(categories_df.shape[0]):
			row = categories_df.iloc[i]
			category = None
			try:
				category = self.categories[row['id']]
			except GuiaBolsoCategory.DoesNotExist:
				continue
			_budget = budgets_df.loc[row['id']]
			budget = GuiaBolsoCategoryBudget()
			budget.category = category
			budget.goal = _budget["goal"]
			budget.spent = _budget["spent"]
			budget.year = month.year
			budget.month = month.month
			categories_budgets.append(budget)

		self.batch_insert(categories_budgets, GuiaBolsoCategoryBudget)

	def transactions_for_month(self, token, month, is_month_first):
		month_code = self.get_code_for_month(month)
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
		budgets = payload["payload"]["userMonthHistory"]["userBudgets"]
		categoryTypes = payload["payload"]["rawData"]["categoryTypes"]

		budgets_df = pd.DataFrame(budgets).set_index('categoryId')
		categories_df = None

		# Getting categories inside categoryTypes as a dataframe
		for categoryType in categoryTypes:
			categories = categoryType['categories']
			df = pd.DataFrame(categories)
			df['color'] = categoryType['color']
			df['type'] = categoryType['name']
			categories_df = self.merge_or_set(categories_df, df)

		categories = []

		if is_month_first:
			# Create categories from the dataframe
			for i in range(categories_df.shape[0]):
				row = categories_df.iloc[i]
				category = GuiaBolsoCategory()
				category.code = row['id']
				category.user = self.user
				category.name = row['name']
				category.color = row['color']
				category.type = row['type']
				categories.append(category)

			self.batch_insert(categories, GuiaBolsoCategory)
			self.update_categories_as_dict()

		self.create_category_budgets(month, categories_df, budgets_df)

		merged_df = None

		for statement in statements:
			transactions = statement["transactions"]
			df = pd.DataFrame(transactions)

			merged_df = self.merge_or_set(merged_df, df)

		return self.format_df(merged_df)

	def months_diff(self, date_after, date_before):
		return (date_after.year - date_before.year)*12 + (date_after.month - date_before.month)

	def get_code_for_month(self, date):
		december = datetime.datetime(2021, 12, 1)
		december_code = 24263
		return december_code + self.months_diff(date, december)

	def get_months_for_token(self, token, start_month=None, end_month=datetime.datetime.now()):
		if start_month is None:
			# start_month = datetime.datetime.now() - relativedelta(years=1)
			start_month = datetime.datetime.now() - relativedelta(years=2, months=6)
			# start_month = datetime.datetime.now() - relativedelta(months=1)

		start_month = start_month.replace(day=1, tzinfo=None)
		end_month = end_month.replace(tzinfo=None)

		month = end_month
		merged_df = None
		is_first = True

		while month > start_month:
			df = self.transactions_for_month(token, month, is_first)
			if df is None and merged_df is None:
				return None, start_month
			merged_df = self.merge_or_set(merged_df, df)

			month = month - relativedelta(months=1)
			is_first = False

		if merged_df is not None and merged_df.shape[0] > 0:
			merged_df = merged_df[~merged_df["deleted"]]
			merged_df = merged_df[~merged_df["duplicated"]]
			merged_df = merged_df[['id', 'label', 'date', 'currency', 'description', 'value', 'categoryId']]

		return merged_df, start_month

	def batch_insert(self, objs, Model, batch_size=100, ignore_conflicts=True):
		start = 0
		while start < len(objs):
			if start + batch_size > len(objs):
				end = len(objs)
			else:
				end = start + batch_size
			batch = objs[start:end]
			Model.objects.bulk_create(batch, batch_size, ignore_conflicts=ignore_conflicts)
			start = end

	def update_transactions(self, startdate = None, enddate = None):
		try:
			token = GuiaBolsoToken.objects.get(user=self.user)
		except GuiaBolsoToken.DoesNotExist:
			return -1

		if not token.valid:
			return -1

		start_month = token.last_transaction_date
		end_month = datetime.datetime.now()

		if startdate is not None:
			start_month = startdate

		if enddate is not None:
			end_month = enddate

		df, start_month = self.get_months_for_token(token.token, start_month, end_month)

		if df is None:
			token.valid = False 
			token.save()
			return -1

		transactions = GuiaBolsoTransaction.objects.filter(user=self.user, date__gte=start_month)
		transactions_dict = {}
		for transaction in transactions:
			transactions_dict[transaction.code] = transaction

		transactions = []
		for i in range(df.shape[0]):
			row = df.iloc[i]
			transaction = GuiaBolsoTransaction()
			transaction.code = row['id']
			transaction.user = self.user
			transaction.date = row['date'].replace(tzinfo=zoneinfo.ZoneInfo('America/Sao_Paulo'))
			transaction.value = float(row['value'])
			transaction.label = row['label']
			transaction.description = row['description']
			transaction.category = self.categories[row['categoryId']]

			if transaction.code in transactions_dict:
				old_transaction = transactions_dict[transaction.code]
				transaction.exclude_from_variable = old_transaction.exclude_from_variable

			transactions.append(transaction)

		deleted = GuiaBolsoTransaction.objects.filter(user=self.user, date__gte=start_month, date__lte=end_month).delete()[0]
		self.batch_insert(transactions, GuiaBolsoTransaction)

		token.last_updated = timezone.now()
		token.save()

		return len(transactions) - deleted