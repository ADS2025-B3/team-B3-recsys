from fastapi import APIRouter, Depends, HTTPException

from app.models import UserPreferenceCreate, UserPreferenceRead
from app.crud.user_preference import user_preference_crud
from app.api.deps import CurrentUser, SessionDep

router = APIRouter()


@router.get("/me", response_model=UserPreferenceRead)
def get_my_preferences(session: SessionDep, current_user: CurrentUser):
    pref = user_preference_crud.get_by_user(session, current_user.id)
    if not pref:
        return UserPreferenceRead(
            id=0,
            preferred_genres=[],
            updated_at=None
        )
    return UserPreferenceRead(
        id=pref.id,
        preferred_genres=pref.preferred_genres.split("|") if pref.preferred_genres else [],
        updated_at=pref.updated_at
    )


@router.post("/", response_model=UserPreferenceRead)
def create_or_update_preferences(
    pref_in: UserPreferenceCreate, 
    session: SessionDep, 
    current_user: CurrentUser
):
    pref = user_preference_crud.set_preferences(
        session=session,
        user_id=current_user.id,
        genres=pref_in.preferred_genres
    )
    return UserPreferenceRead(
        id=pref.id,
        preferred_genres=pref.preferred_genres.split("|") if pref.preferred_genres else [],
        updated_at=pref.updated_at
    )


@router.put("/", response_model=UserPreferenceRead)
def update_preferences(
    pref_in: UserPreferenceCreate, 
    session: SessionDep, 
    current_user: CurrentUser
):
    pref = user_preference_crud.update_preferences(
        session=session,
        user_id=current_user.id,
        genres=pref_in.preferred_genres
    )
    if not pref:
        raise HTTPException(status_code=404, detail="Preferences do not exist for this user")
    return UserPreferenceRead(
        id=pref.id,
        preferred_genres=pref.preferred_genres.split("|") if pref.preferred_genres else [],
        updated_at=pref.updated_at
    )