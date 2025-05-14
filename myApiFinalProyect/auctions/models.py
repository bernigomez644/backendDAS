from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=50, blank=False, unique=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.name


class Auction(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=1,
    )
    stock = models.IntegerField(validators=[MinValueValidator(1)])
    brand = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category, related_name="auctions", on_delete=models.CASCADE
    )
    thumbnail = models.URLField()
    creation_date = models.DateTimeField(auto_now_add=True)
    closing_date = models.DateTimeField()
    auctioneer = models.ForeignKey(
        CustomUser, related_name="auctions", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return self.title


class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    bidder = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="bids"
    )
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-price",)

    def __str__(self):
        return f"{self.bidder} - {self.price}€ on {self.auction.title}"


class Rating(models.Model):
    valor_numerico = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    user = models.ForeignKey(
        CustomUser, related_name="ratings", on_delete=models.CASCADE
    )
    auction = models.ForeignKey(
        Auction, related_name="ratings", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ("id",)
        unique_together = ("user", "auction")


class Comentario(models.Model):
    titulo = models.CharField(max_length=50)
    campo_de_texto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ultima_modificacion = models.DateTimeField()
    usuario = models.ForeignKey(
        CustomUser, related_name="comments", on_delete=models.CASCADE
    )
    auction = models.ForeignKey(
        Auction, related_name="comments", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ("id",)
        unique_together = ("usuario", "auction")
