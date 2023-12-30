from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from base.db.models import AbstractBaseModel
from base.db.utilities import get_file_path
from v1.catalogs.models.product_models import ConnectCard
from v1.supply_chains import managers


class Entity(AbstractBaseModel):
    """Abstract base model for entities in the supply chain system.

    Fields:
    - image (ImageField): An image representing the entity.
    - description (CharField): A short description of the entity.
    - invited_by (ForeignKey): The company that invited the entity to join the
        supply chain.
    - invited_on (DateTimeField): The date and time when the entity was invited
        to join the supply chain.
    - joined_on (DateTimeField): The date and time when the entity joined the
        supply chain.
    - status (IntegerField): The current status of the entity in the supply
        chain.
    - is_verified (BooleanField): Whether the entity has been verified by the
        supply chain system.
    - buyer (ForeignKey): The company that buyying from the entity.
    """

    created_on = models.DateTimeField(
        default=timezone.now, verbose_name=_("Created On")
    )
    image = models.ImageField(
        upload_to=get_file_path,
        null=True,
        blank=True,
        verbose_name=_("Photo"),
    )
    description = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name=_("Description"),
    )
    buyer = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="%(class)s_supplers",
        null=True,
        blank=True,
        verbose_name=_("Buyer"),
    )
    entity_card = models.ForeignKey(
        "supply_chains.EntityCard",
        on_delete=models.SET_NULL,
        related_name="entities",
        null=True,
        blank=True,
        verbose_name=_("Entity Card"),
    )

    def __str__(self):
        return f"{self.name}"

    @property
    def name(self):
        """property name of the entity."""
        if hasattr(self, "company"):
            return self.company.name
        elif hasattr(self, "farmer"):
            return self.farmer.name


class EntityCard(AbstractBaseModel):
    """A model representing the relationship between a ConnectCard and an
    Entity.

    Attributes:
        card (ConnectCard): The ConnectCard associated with this EntityCard.
        entity (Entity): The Entity associated with this EntityCard.
        is_active (bool): Whether this EntityCard is currently active.

    Managers:
        objects: The default manager for EntityCard, which provides additional
            query methods.

    Constraints:
        unique_entity_card: A database constraint that ensures that each
            ConnectCard can only be associated with each Entity once.

    Methods:
        __str__: Returns a string representation of this EntityCard.
        save: Overrides the default save method to deactivate other EntityCards
            associated with the same ConnectCard if this EntityCard is active.
    """

    card = models.ForeignKey(
        ConnectCard,
        related_name="entity_cards",
        on_delete=models.CASCADE,
        verbose_name=_("Card"),
    )
    entity = models.ForeignKey(
        Entity,
        related_name="card_entities",
        on_delete=models.CASCADE,
        verbose_name=_("Entity"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    objects = managers.EntityCardQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["card", "entity"], name="unique_entity_card"
            )
        ]

    def __str__(self):
        return f"{self.card} - {self.entity.name}"

    def save(self, *args, **kwargs):
        """Overrides the save method to perform additional actions before and
        after saving."""
        if self.is_active:
            self.__class__.objects.deactivate_other_entities(self.card)

        super().save(*args, **kwargs)

        if self.is_active:
            self.set_default(self.entity)
        else:
            self.remove_default(self.entity)

    def set_default(self, entity):
        """Sets the given entity card as the default.

        Args:
            entity: The entity to be set as default.
        """
        entity.entity_card = self
        entity.save()

    def remove_default(self, entity):
        """Removes the given entity from being the default.

        Args:
            entity: The entity to be removed from default.
        """
        entity.entity_card = None
        entity.save()
