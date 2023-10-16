from base.authentication.session import get_from_local
from base.authentication.session import set_to_local


def get_current_user():
    """Returns the currently authenticated user when called while processing an
    API.

    Otherwise, returns None.
    """
    from django.contrib.auth import get_user_model

    UserModel = get_user_model()

    user = get_from_local("user", None)
    current_user = UserModel.objects.filter(
        id=get_from_local("user_id")
    ).first()
    if user and user == current_user:
        return user
    user = current_user
    set_to_local("user", user)
    return user


def get_current_entity():
    """Returns the currently authenticated entity when called while processing
    an API.

    Otherwise, returns None.
    """
    from v1.entities.models import Entity

    entity = get_from_local("entity", None)
    current_entity = Entity.objects.filter(
        id=get_from_local("entity_id")
    ).first()
    if entity and entity == current_entity:
        return entity
    entity = current_entity
    set_to_local("entity", entity)
    return entity
