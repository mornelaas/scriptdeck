from fastapi import APIRouter, HTTPException

from ..dependencies import SessionDep
from ..orm.models import User
from ..schemas import UserCreate, UserOut
from ..services import EmailAlreadyRegisteredError, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def create_a_user(data: UserCreate, db: SessionDep) -> User:
    try:
        return register_user(db=db, data=data)
    except EmailAlreadyRegisteredError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
