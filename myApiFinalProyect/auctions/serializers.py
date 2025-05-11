from rest_framework import serializers
from .models import Category, Auction, Bid, Rating
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


class RatingsListSerializer(serializers.ModelSerializer):
    auction = serializers.PrimaryKeyRelatedField(queryset=Auction.objects.all())
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )  # ← esta línea
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Rating
        fields = "__all__"


class AuctionListCreateSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%SZ", read_only=True
    )
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    is_open = serializers.SerializerMethodField(read_only=True)
    avg_rating = serializers.SerializerMethodField(read_only=True)

    ratings = RatingsListSerializer(many=True, read_only=True)

    def validate_closing_date(self, value):
        if self.instance:
            creation_date = self.instance.creation_date
        else:
            creation_date = timezone.now()

        if value < timezone.now():
            raise serializers.ValidationError("La fecha de cuirre debe ser futura ")

        if value - creation_date < timedelta(days=15):
            raise serializers.ValidationError(
                "deben de haber 15 dias entre la fecha de creación y la de cierre"
            )
        return value

    def create(self, validated_data):
        rating_value = validated_data.pop("rating", None)
        user = self.context["request"].user

        auction = Auction.objects.create(auctioneer=user, **validated_data)

        # Crear automáticamente el Rating si viene incluido
        if rating_value is not None:
            Rating.objects.create(
                valor_numerico=rating_value, user=user, auction=auction
            )

        return auction

    def get_avg_rating(self, obj):
        ratings = obj.ratings.all()
        if not ratings:
            return 1.0
        valor = float(0)
        for r in ratings:
            valor_numerico = float(r.valor_numerico)
            valor += valor_numerico
        return valor / float(ratings.count())

    class Meta:
        model = Auction
        fields = [
            "id",
            "title",
            "description",
            "price",
            "stock",
            "brand",
            "category",
            "thumbnail",
            "creation_date",
            "closing_date",
            "auctioneer",
            "is_open",
            "avg_rating",
            "rating",
            "ratings",
        ]
        read_only_fields = ["auctioneer"]

    @extend_schema_field(serializers.BooleanField())
    def get_is_open(self, obj):
        return obj.closing_date > timezone.now()


class AuctionDetailSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%SZ", read_only=True
    )
    closing_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")
    is_open = serializers.SerializerMethodField(read_only=True)

    auctioneer_username = serializers.CharField(
        source="auctioneer.username", read_only=True
    )

    avg_rating = serializers.SerializerMethodField(read_only=True)

    def validate_closing_date(self, value):
        if self.instance:
            creation_date = self.instance.creation_date
        else:
            creation_date = timezone.now()

        if value < timezone.now():
            raise serializers.ValidationError("La fecha de cuirre debe ser futura ")

        if value - creation_date < timedelta(days=15):
            raise serializers.ValidationError(
                "deben de haber 15 dias entre la fecha de creación y la de cierre"
            )
        return value

    class Meta:

        model = Auction
        fields = fields = [
            "id",
            "title",
            "description",
            "price",
            "stock",
            "brand",
            "category",
            "thumbnail",
            "creation_date",
            "closing_date",
            "auctioneer",
            "is_open",
            "avg_rating",
            "auctioneer_username",
        ]

    @extend_schema_field(serializers.BooleanField())
    def get_is_open(self, obj):
        return obj.closing_date > timezone.now()

    def get_avg_rating(self, obj):
        ratings = obj.ratings.all()
        if not ratings:
            return 1.0
        valor = float(0)
        for r in ratings:
            valor_numerico = float(r.valor_numerico)
            valor += valor_numerico
        return round(valor / float(ratings.count()), 2)


class BidsListCreateSerializer(serializers.ModelSerializer):

    auction = serializers.PrimaryKeyRelatedField(queryset=Auction.objects.all())
    creation_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%SZ", read_only=True
    )
    bidder = serializers.HiddenField(default=serializers.CurrentUserDefault())
    bidder_username = serializers.CharField(source="bidder.username", read_only=True)

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
    bidder_username = serializers.CharField(source="bidder.username", read_only=True)

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


class RatingsDetailSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Rating
        fields = "__all__"
