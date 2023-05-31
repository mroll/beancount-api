from rest_framework import serializers

from .models import Account
from .models import Book
from .models import Currency
from .models import Posting
from .models import Tag
from .models import Transaction
from .models import User
from .models import Open


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = [
            "url",
            "username",
            "email",
        ]


class BookSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Book
        fields = [
            "name",
            "avg_fixed_costs_per_month",
            "avg_discretionary_spend_per_month",
            "avg_discretionary_spend_per_month_before_travel",
            "avg_income_per_month_after_taxes_and_retirement_contribution",
            "avg_expenses_per_month_after_taxes_and_insurance",
            "avg_cash_flow_per_month",
        ]


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = ["name", "open_date", "close_date", "booking", "currencies", "book"]


class CurrencySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Currency
        fields = ["name"]


class OpenSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Open
        fields = ["account", "currencies", "booking", "book"]


class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ["name"]


class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Transaction
        fields = ["date", "narration", "payee", "tags", "links", "postings"]


class PostingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Posting
        fields = [
            "account",
            "units",
            "units_number",
            "units_currency",
            "cost",
            "price",
            "flag",
        ]
