from beancount.loader import load_string

from rest_framework.serializers import Serializer, FileField
from rest_framework.settings import api_settings
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response

from .converters import converter_map
from .models import Account
from .models import Book
from .models import Currency
from .models import Open
from .models import Posting
from .models import Transaction
from .models import User
from .serializers import UserSerializer
from .serializers import AccountSerializer
from .serializers import BookSerializer
from .serializers import CurrencySerializer
from .serializers import OpenSerializer
from .serializers import TransactionSerializer
from .serializers import PostingSerializer


class CreateModelWithHooksMixin:
    """
    Create a model instance.
    """

    def before_create_hook(self, serializer):
        pass

    def after_create_hook(self, instance):
        pass

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.before_create_hook(serializer)
        instance = self.perform_create(serializer)
        self.after_create_hook(instance)

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        return serializer.save()

    def get_success_headers(self, data):
        try:
            return {"Location": str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]


class OpenViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Open.objects.all().order_by("-date")
    serializer_class = OpenSerializer


class AccountViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    CreateModelWithHooksMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint that allows accounts to be viewed or edited.
    """

    queryset = Account.objects.all().order_by("-open_date")
    serializer_class = AccountSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def after_create_hook(self, account):
        self.create_open(account)

    def create_open(self, account):
        open = Open(
            date=account.open_date,
            account=account,
            booking=account.booking,
            book=account.book,
        )
        open.save()

        for currency in account.currencies.all():
            open.currencies.add(currency)

        open.save()


class BookViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows books to be viewed or edited.
    """

    queryset = Book.objects.all().order_by("-name")
    serializer_class = BookSerializer
    # permission_classes = [permissions.IsAuthenticated]


class PostingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows books to be viewed or edited.
    """

    queryset = Posting.objects.all().order_by("-account")
    serializer_class = PostingSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows books to be viewed or edited.
    """

    queryset = Transaction.objects.all().order_by("-date")
    serializer_class = TransactionSerializer
    # permission_classes = [permissions.IsAuthenticated]


# Serializers define the API representation.
class UploadSerializer(Serializer):
    file_uploaded = FileField()

    class Meta:
        fields = ["file_uploaded"]


class PlaintextBookViewSet(viewsets.ViewSet):
    serializer_class = UploadSerializer

    def create(self, request):
        file_uploaded = request.FILES.get("file_uploaded")

        data = file_uploaded.file.read()

        entries, _, _ = load_string(data)

        book = Book(name="Test Book")
        book.save()

        for entry in entries:
            convert = converter_map[type(entry)]
            try:
                convert(entry, book)
            except Exception as err:
                print(entry)
                print(err)

        return Response("success")

    def list(self, request):
        return Response("GET API")


class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows accounts to be viewed or edited.
    """

    queryset = Currency.objects.all().order_by("-name")
    serializer_class = CurrencySerializer


from rest_framework.views import APIView

from .models import Balance


class BalanceSheet(APIView):
    def get(self, request, format=None):
        balances = Balance.objects.all()
        return Response(balances)
