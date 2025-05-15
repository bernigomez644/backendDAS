from django.db.models import Avg


from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)

from .permissions import (
    IsBidOwnerOrAdmin,
    IsOwnerOrAdmin,
    IsAdminOrReadOnly,
    IsRatingOwnerOrAdmin,
    isCommentaryownerorReadonly,
)
from django.utils import timezone

# Create your views here.
from django.db.models import Q
from rest_framework import generics, status
from .models import Category, Auction, Bid, Rating, Comentario
from .serializers import (
    CategoryListCreateSerializer,
    CategoryDetailSerializer,
    AuctionListCreateSerializer,
    AuctionDetailSerializer,
    BidsListCreateSerializer,
    BidsDetailSerializer,
    RatingsListSerializer,
    RatingsDetailSerializer,
    CommentDetailSerializer,
    CommentListCreateSerializer,
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

        price_min = params.get("priceMin", None)
        price_max = params.get("priceMax", None)

        rating = params.get("rating", None)

        is_open = params.get("is_open", None)

        if is_open is not None:
            is_open = is_open.lower() == "true"  # convierte el string a booleano

            if is_open:
                query_set = query_set.filter(closing_date__gte=timezone.now())
            else:
                query_set = query_set.filter(closing_date__lte=timezone.now())
        if rating:
            query_set = query_set.annotate(avg_rating=Avg("ratings__valor_numerico"))
            rating = float(rating)
            if rating < 0:
                raise ValidationError({"rating": "Debe de ser un valor positivo"})
            query_set = query_set.filter(avg_rating__gte=rating)

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
        auction_id = self.kwargs["auction_id"]
        return Bid.objects.filter(auction=auction_id)

    def perform_create(self, serializer):
        auction = Auction.objects.get(id=self.kwargs["auction_id"])
        serializer.save(bidder=self.request.user, auction=auction)


class BidsRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsBidOwnerOrAdmin]
    serializer_class = BidsDetailSerializer

    def get_queryset(self):
        return Bid.objects.filter(auction=self.kwargs["auction_id"])


class RatingsListCReate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    serializer_class = RatingsListSerializer

    def get_queryset(self):
        auction = Auction.objects.get(id=self.kwargs["auction_id"])
        return auction.ratings.all()

    def perform_create(self, serializer):
        auction = Auction.objects.get(id=self.kwargs["auction_id"])
        serializer.save(user=self.request.user, auction=auction)


class RatingsRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsRatingOwnerOrAdmin]

    serializer_class = RatingsDetailSerializer

    def get_queryset(self):
        auction = Auction.objects.get(id=self.kwargs["auction_id"])
        return auction.ratings.all()


class ComentListCreate(generics.ListCreateAPIView):
    serializer_class = CommentListCreateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comentario.objects.filter(auction=self.kwargs["auction_id"])

    def perform_create(self, serializer):
        auction = Auction.objects.get(id=self.kwargs["auction_id"])
        fecha_ultima_modificacion = timezone.now()
        serializer.save(
            usuario=self.request.user,
            auction=auction,
            fecha_ultima_modificacion=fecha_ultima_modificacion,
        )


class ComentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [isCommentaryownerorReadonly]
    serializer_class = CommentDetailSerializer

    def get_queryset(self):
        return Comentario.objects.filter(auction=self.kwargs["auction_id"])


class UserAuctionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Obtener las subastas del usuario autenticado
        user_auctions = Auction.objects.filter(auctioneer=request.user)
        serializer = AuctionListCreateSerializer(user_auctions, many=True)
        return Response(serializer.data)


class UserRatingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_ratings = Rating.objects.filter(user=self.request.user)
        serializer = RatingsListSerializer(user_ratings, many=True)
        return Response(serializer.data)


class UserComentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_comments = Comentario.objects.filter(usuario=self.request.user)
        serializer = CommentListCreateSerializer(user_comments, many=True)
        return Response(serializer.data)
