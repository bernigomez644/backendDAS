from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)

from .permissions import IsBidOwnerOrAdmin, IsOwnerOrAdmin, IsAdminOrReadOnly

# Create your views here.
from django.db.models import Q
from rest_framework import generics, status
from .models import Category, Auction, Bid
from .serializers import (
    CategoryListCreateSerializer,
    CategoryDetailSerializer,
    AuctionListCreateSerializer,
    AuctionDetailSerializer,
    BidsListCreateSerializer,
    BidsDetailSerializer,
)

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class CategoryListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.all()
    serializer_class = CategoryListCreateSerializer


class CategoryRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer


class AuctionListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = AuctionListCreateSerializer

    def get_queryset(self):
        query_set = Auction.objects.all()
        params = self.request.query_params
        search = params.get("search", None)
        if search and len(search) < 3:
            raise ValidationError(
                {"debe tener mas de longitud 3"}, code=status.HTTP_400_BAD_REQUEST
            )
        if search:
            query_set = query_set.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        category = params.get("category", None)

        price_min = params.get("priceMin")
        price_max = params.get("priceMax")

        if price_min:

            price_min = float(price_min)
            if price_min < 0:
                raise ValidationError({"priceMin": "Price must be a positive number."})
            query_set = query_set.filter(price__gte=price_min)

        if price_max:

            price_max = float(price_max)
            if price_max < 0:
                raise ValidationError({"priceMax": "Price must be a positive number."})
            query_set = query_set.filter(price__lte=price_max)

        if price_min and price_max and price_max < price_min:
            raise ValidationError(
                {"price": "Maximum price must be greater than minimum price."}
            )

        if category:
            if not Category.objects.filter(id=category).exists():
                raise ValidationError({"category": "Category does not exist."})
            query_set = query_set.filter(category=category)
        return query_set

    def perform_create(self, serializer):
        serializer.save(auctioneer=self.request.user)


class AuctionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrAdmin]
    queryset = Auction.objects.all()
    serializer_class = AuctionDetailSerializer


class BidsListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = BidsListCreateSerializer

    def get_queryset(self):
        auction_id = self.kwargs["pk"]
        return Bid.objects.filter(auction=auction_id)

    def perform_create(self, serializer):
        serializer.save(bidder=self.request.user)


class BidsRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsBidOwnerOrAdmin]
    serializer_class = BidsDetailSerializer

    def get_queryset(self):
        return Bid.objects.filter(auction=self.kwargs["auction_id"])


class UserAuctionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Obtener las subastas del usuario autenticado
        user_auctions = Auction.objects.filter(auctioneer=request.user)
        serializer = AuctionListCreateSerializer(user_auctions, many=True)
        return Response(serializer.data)
