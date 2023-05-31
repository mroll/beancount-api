from dateutil.relativedelta import relativedelta
from datetime import datetime as dt

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    pass


class Book(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(User, related_name="books")

    def _avg_per_month(
        self,
        start_date,
        end_date=None,
        include_tags=[],
        exclude_tags=[],
        include_account_regex=r"^Expenses:.*",
        exclude_account_regex=None,
        net=False,
    ):
        if end_date is None:
            end_date = dt.now().strftime("%Y-%m-%d")

        txn_query = Transaction.objects.filter(date__gte=start_date, date__lt=end_date)

        if include_tags:
            txn_query = txn_query.filter(tags__name__in=include_tags)

        if exclude_tags:
            txn_query = txn_query.exclude(tags__name__in=exclude_tags)

        posting_query = Posting.objects.filter(
            transaction__pk__in=models.Subquery(txn_query.values("pk"))
        )

        if include_account_regex:
            posting_query = posting_query.filter(
                account__name__regex=include_account_regex
            )

        if exclude_account_regex:
            posting_query = posting_query.exclude(
                account__name__regex=exclude_account_regex
            )

        if net is False:
            posting_query = posting_query.exclude(units__startswith="-")

        total = posting_query.aggregate(res=models.Sum("units_number"))["res"]

        delta = relativedelta(
            dt.strptime(end_date, "%Y-%m-%d"), dt.strptime(start_date, "%Y-%m-%d")
        )
        months_count = delta.years * 12 + delta.months

        return round(total / months_count, 2)

    def avg_fixed_costs_per_month(self):
        start_date, end_date = "2023-01-01", "2023-05-01"
        return self._avg_per_month(
            start_date=start_date,
            end_date=end_date,
            include_tags=["fixed-cost"],
            include_account_regex=r"^Expenses",
            net=True,
        )

    def avg_discretionary_spend_per_month(self):
        start_date, end_date = "2023-01-01", "2023-05-01"
        return self._avg_per_month(
            start_date=start_date,
            end_date=end_date,
            exclude_tags=["fixed-cost"],
            include_account_regex=r"^Expenses",
            exclude_account_regex=r"Taxes|Insurance|GroupTermLife",
        )

    def avg_discretionary_spend_per_month_before_travel(self):
        start_date, end_date = "2023-01-01", "2023-05-01"
        return self._avg_per_month(
            start_date=start_date,
            end_date=end_date,
            exclude_tags=["fixed-cost"],
            include_account_regex=r"^Expenses",
            exclude_account_regex=r"Taxes|Insurance|GroupTermLife|Travel",
        )

    def avg_income_per_month_after_taxes_and_retirement_contribution(self):
        start_date, end_date = "2023-01-01", "2023-05-01"
        return self._avg_per_month(
            start_date=start_date,
            end_date=end_date,
            include_account_regex=r"^Assets:US:Chase:Checking",
            exclude_account_regex=None,
            net=False,
        )

    def avg_expenses_per_month_after_taxes_and_insurance(self):
        start_date, end_date = "2023-01-01", "2023-05-01"
        return self._avg_per_month(
            start_date=start_date,
            end_date=end_date,
            exclude_account_regex=r"Taxes|Insurance",
        )

    def avg_cash_flow_per_month(self):
        result = (
            self.avg_income_per_month_after_taxes_and_retirement_contribution()
            - self.avg_expenses_per_month_after_taxes_and_insurance()
        )

        return round(result, 2)


class BeancountDirective(models.Model):
    meta = models.JSONField(null=True)
    date = models.DateField()


class Currency(models.Model):
    name = models.CharField(max_length=32)

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="currencies")


class Booking(models.TextChoices):
    STRICT = "ST", _("STRICT")
    NONE = "NO", _("NONE")
    AVERAGE = "AV", _("AVERAGE")
    FIFO = "FI", _("FIFO")
    LIFO = "LI", _("LIFO")
    HIFO = "HI", _("HIFO")


class Account(models.Model):
    name = models.CharField(max_length=255)
    open_date = models.DateField()
    close_date = models.DateField(null=True)
    booking = models.CharField(
        max_length=2, choices=Booking.choices, null=True, default=None
    )

    currencies = models.ManyToManyField(Currency)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="accounts")


class Open(BeancountDirective):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    currencies = models.ManyToManyField(Currency)
    booking = models.CharField(
        max_length=2, choices=Booking.choices, null=True, default=None
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="opens")


class Close(BeancountDirective):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="closes")


class Commodity(BeancountDirective):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="commodities")


class Pad(BeancountDirective):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    source_account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="pad_source_account_set"
    )

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="pads")


class Balance(BeancountDirective):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.CharField(max_length=255)
    tolerance = models.FloatField(null=True)
    diff_amount = models.CharField(max_length=255, null=True)

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="balances")


class Tag(models.Model):
    name = models.CharField(max_length=255)

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="tags")


class Link(models.Model):
    value = models.CharField(max_length=255)

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="links")


class Transaction(BeancountDirective):
    flag = models.CharField(max_length=255, null=True)
    payee = models.CharField(max_length=255, null=True)
    narration = models.CharField(max_length=255)

    tags = models.ManyToManyField(Tag, related_name="tags")
    links = models.ManyToManyField(Link)

    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="transactions"
    )


class Posting(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    units = models.CharField(max_length=255)
    units_number = models.DecimalField(max_digits=32, decimal_places=2)
    units_currency = models.CharField(max_length=32)
    cost = models.CharField(max_length=255, null=True)
    cost_spec = models.CharField(max_length=255, null=True)
    price = models.CharField(max_length=255, null=True)
    flag = models.CharField(max_length=255, null=True)
    meta = models.JSONField(null=True)

    transaction = models.ForeignKey(
        Transaction, related_name="postings", on_delete=models.CASCADE
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="postings")


class Price(BeancountDirective):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    amount = models.CharField(max_length=255)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="prices")
