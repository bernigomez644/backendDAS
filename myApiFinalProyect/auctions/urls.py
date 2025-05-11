from django.urls import path
from .views import (
    CategoryListCreate,
    CategoryRetrieveUpdateDestroy,
    AuctionListCreate,
    AuctionRetrieveUpdateDestroy,
    BidsListCreate,
    BidsRetrieveUpdateDestroy,
    UserAuctionListView,
    RatingsListCReate,
    RatingsRetrieveUpdateDestroy,
)


app_name = "auctions"
urlpatterns = [
    path("categories/", CategoryListCreate.as_view(), name="category-list-create"),
    path(
        "categories/<int:pk>/",
        CategoryRetrieveUpdateDestroy.as_view(),
        name="category-detail",
    ),
    path("", AuctionListCreate.as_view(), name="auction-list-create"),
    path("<int:pk>/", AuctionRetrieveUpdateDestroy.as_view(), name="auction-detail"),
    path("<int:pk>/bid/", BidsListCreate.as_view(), name="bids-list-create"),
    path(
        "<int:auction_id>/bid/<int:pk>/",
        BidsRetrieveUpdateDestroy.as_view(),
        name="bids-detail",
    ),
    path("users/", UserAuctionListView.as_view(), name="action-from-users"),
    path(
        "<int:auction_id>/ratings/",
        RatingsListCReate.as_view(),
        name="ratings-list-create",
    ),
    path(
        "<int:auction_id>/ratings/<int:pk>/",
        RatingsRetrieveUpdateDestroy.as_view(),
        name="ratings-detail",
    ),
]
