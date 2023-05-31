import json
import re

from django.core.serializers.json import DjangoJSONEncoder

from beancount.core.data import Transaction as BCTransaction
from beancount.core.data import Open as BCOpen
from beancount.core.data import Price as BCPrice
from beancount.core.data import Balance as BCBalance
from beancount.core.data import Pad as BCPad

from .models import Account
from .models import Balance
from .models import Currency
from .models import Link
from .models import Open
from .models import Pad
from .models import Posting
from .models import Price
from .models import Tag
from .models import Transaction


def convert_posting(bc_posting, db_transaction, book):
    account = Account.objects.get(name=bc_posting.account)

    posting = Posting(
        account=account,
        units=bc_posting.units,
        units_number=bc_posting.units.number,
        units_currency=bc_posting.units.currency,
        cost=bc_posting.cost,
        # cost_spec=bc_posting.get("cost_spec"),
        price=bc_posting.price,
        flag=bc_posting.flag,
        meta=json.dumps(bc_posting.meta, cls=DjangoJSONEncoder),
        book=book,
        transaction=db_transaction,
    )
    posting.save()

    return posting


def convert_tag(bc_tag, book):
    try:
        db_tag = Tag.objects.get(name=bc_tag)
    except:
        db_tag = Tag(name=bc_tag, book=book)
        db_tag.save()

    return db_tag


def convert_link(bc_link, book):
    try:
        db_link = Link.objects.get(name=bc_link)
    except:
        db_link = Link(name=bc_link, book=book)
        db_link.save()

    return db_link


def convert_transaction(bc_transaction, book):
    db_transaction = Transaction(
        meta=json.dumps(bc_transaction.meta, cls=DjangoJSONEncoder),
        date=bc_transaction.date,
        flag=bc_transaction.flag,
        payee=bc_transaction.payee,
        narration=bc_transaction.narration,
        book=book,
    )
    db_transaction.save()

    db_postings = [
        convert_posting(bc_posting, db_transaction, book)
        for bc_posting in bc_transaction.postings
    ]
    db_tags = [convert_tag(bc_tag, book) for bc_tag in bc_transaction.tags]

    for db_posting in db_postings:
        db_transaction.postings.add(db_posting)

    for db_tag in db_tags:
        db_transaction.tags.add(db_tag)

    db_transaction.save()

    return db_transaction


def convert_currency(bc_currency, book):
    try:
        db_currency = Currency.objects.get(name=bc_currency)
    except:
        db_currency = Currency(name=bc_currency, book=book)
        db_currency.save()

    return db_currency


def convert_open(bc_open, book):
    if bc_open.currencies is None:
        db_currencies = []
    else:
        db_currencies = [
            convert_currency(bc_currency, book) for bc_currency in bc_open.currencies
        ]

    db_account = Account(
        book=book, name=bc_open.account, open_date=bc_open.date, booking=bc_open.booking
    )
    db_account.save()

    db_open = Open(
        book=book,
        date=bc_open.date,
        account=db_account,
        booking=bc_open.booking,
    )
    db_open.save()

    for db_currency in db_currencies:
        db_account.currencies.add(db_currency)
        db_open.currencies.add(db_currency)

    db_account.save()
    db_open.save()

    return db_open


def convert_price(bc_price, book):
    currency = Currency.objects.get(name=bc_price.currency)

    db_price = Price(
        meta=json.dumps(bc_price.meta, cls=DjangoJSONEncoder),
        date=bc_price.date,
        currency=currency,
        amount=bc_price.amount,
        book=book,
    )
    db_price.save()

    return db_price


def convert_balance(bc_balance, book):
    account = Account.objects.get(name=bc_balance.account)

    db_balance = Balance(
        account=account,
        meta=json.dumps(bc_balance.meta, cls=DjangoJSONEncoder),
        date=bc_balance.date,
        amount=bc_balance.amount,
        tolerance=bc_balance.tolerance,
        diff_amount=bc_balance.diff_amount,
        book=book,
    )
    db_balance.save()

    return db_balance


def convert_pad(bc_pad, book):
    account = Account.objects.get(name=bc_pad.account)
    source_account = Account.objects.get(name=bc_pad.source_account)

    db_pad = Pad(
        meta=json.dumps(bc_pad.meta, cls=DjangoJSONEncoder),
        date=bc_pad.date,
        account=account,
        source_account=source_account,
        book=book,
    )
    db_pad.save()

    return db_pad


converter_map = {
    BCTransaction: convert_transaction,
    BCOpen: convert_open,
    BCPrice: convert_price,
    BCBalance: convert_balance,
    BCPad: convert_pad,
}
