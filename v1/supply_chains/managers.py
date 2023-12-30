from django.db import models


class EntityCardQuerySet(models.QuerySet):
    """A custom QuerySet for the EntityCard model that provides additional
    functionality."""

    def deactivate_other_entities(self, card):
        """Deactivates all other entities associated with the given card.

        Args:
            card (EntityCard): The EntityCard object for which to deactivate
                other entities.

        Returns:
            int: The number of entities that were deactivated.
        """
        qs = self.filter(card=card)
        for entity_card in qs:
            entity_card.is_active = False
            entity_card.save()
        return qs
