from rest_framework import serializers
from .models import Category, Auction, Bid
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from datetime import timedelta


class CategoryListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class AuctionListCreateSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%SZ", read_only=True
    )
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    is_open = serializers.SerializerMethodField(read_only=True)

    class Meta:

        model = Auction
        fields = "__all__"

    def validate_closing_date(self, value):
        if self.instance:
            creation_date = self.instance.creation_date
        else:
            creation_date = timezone.now()

        if value - creation_date < timedelta(days=15):
            raise serializers.ValidationError("deben de haber pasaado 15 dias")
        if value < timezone.now():
            raise serializers.ValidationError("Closing date nom")
        return value

    @extend_schema_field(serializers.BooleanField())
    def get_is_open(self, obj):
        return obj.closing_date > timezone.now()


class AuctionDetailSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%SZ", read_only=True
    )
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    is_open = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Auction
        fields = "__all__"

    def validate_closing_date(self, value):
        if self.instance:
            creation_date = self.instance.creation_date
        else:
            creation_date = timezone.now()

        if value - creation_date < timedelta(days=15):
            raise serializers.ValidationError("deben de haber pasaado 15 dias")
        if value < timezone.now():
            raise serializers.ValidationError("Closing date nom")
        return value

    @extend_schema_field(serializers.BooleanField())
    def get_is_open(self, obj):
        return obj.closing_date > timezone.now()


class BidsListCreateSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%SZ", read_only=True
    )

    class Meta:
        model = Bid
        fields = "__all__"

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor que 0.")
        return value

    def validate(self, data):
        auction = data["auction"]
        new_price = data["price"]

        # Obtener la puja más alta actual
        highest_bid = auction.bids.order_by("-price").first()
        if highest_bid and new_price <= highest_bid.price:
            raise serializers.ValidationError(
                "La puja debe ser mayor que la actual más alta."
            )

        return data


class BidsDetailSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%SZ", read_only=True
    )

    class Meta:
        model = Bid
        fields = "__all__"

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor que 0.")
        return value

    def validate(self, data):
        auction = data["auction"]
        new_price = data["price"]

        # Obtener la puja más alta actual
        highest_bid = auction.bids.order_by("-price").first()
        if highest_bid and new_price <= highest_bid.price:
            raise serializers.ValidationError(
                "La puja debe ser mayor que la actual más alta."
            )

        return data
