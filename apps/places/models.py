from django.db import models

from apps.common.models import BaseModel
from apps.users.models import BaseUser


class PlaceTag(BaseModel):
    user = models.ForeignKey(
        BaseUser, on_delete=models.CASCADE, related_name="place_tags"
    )
    name = models.CharField(max_length=10)

    def __str__(self) -> str:
        return self.name  # type: ignore[no-any-return]

    class Meta:
        unique_together = ["user", "name"]
        ordering = ["name"]


class Place(BaseModel):
    user = models.ForeignKey(BaseUser, on_delete=models.CASCADE, related_name="places")
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, null=True)
    description = models.TextField(max_length=500, null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    favorite = models.BooleanField(default=False)
    tags = models.ManyToManyField(PlaceTag, related_name="places")

    def __str__(self) -> str:
        return self.name  # type: ignore[no-any-return]

    class Meta:
        ordering = ["-created_at"]

    @property
    def location(self) -> dict[str, float]:
        return {"latitude": self.latitude, "longitude": self.longitude}


class PlaceImage(BaseModel):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="place_images/")

    class Meta:
        ordering = ["-updated_at"]

    @property
    def image_url(self) -> str | None:
        if self.image:
            return self.image.url  # type: ignore[no-any-return]
        return None
