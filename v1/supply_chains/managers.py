from django.db import models


class EntityCardQuerySet(models.QuerySet):
    """
    A custom QuerySet for the EntityCard model that provides additional
    functionality.
    """

    def deactivate_other_entities(self, card):
        """
        Deactivates all other entities associated with the given card.

        Args:
            card (EntityCard): The EntityCard object for which to deactivate
                other entities.

        Returns:
            int: The number of entities that were deactivated.
        """
        return self.filter(card=card).update(is_active=False)
