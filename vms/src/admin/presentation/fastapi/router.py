from fastapi import APIRouter, Depends, HTTPException
from admin.application.dtos import CreateUserDTO, AuthenticateDTO
from .schemas import RegisterSchema, LoginSchema, LoginResponse, UserResponse
from .dependencies import get_current_user, require_admin
from .container import container

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: RegisterSchema):
    use_case = container.get_create_user_use_case()
    try:
        user = use_case.execute(CreateUserDTO(
            email=data.email,
            name=data.name,
            password=data.password,
            city_ids=data.city_ids,
            is_admin=data.is_admin
        ))
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            city_ids=user.city_ids,
            is_admin=user.is_admin,
            is_active=user.is_active
        )
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginSchema):
    use_case = container.get_authenticate_user_use_case()
    try:
        result = use_case.execute(AuthenticateDTO(
            email=data.email,
            password=data.password
        ))
        return LoginResponse(
            token=result["token"],
            user=UserResponse(
                id=result["user"].id,
                email=result["user"].email,
                name=result["user"].name,
                city_ids=result["user"].city_ids,
                is_admin=result["user"].is_admin,
                is_active=result["user"].is_active
            )
        )
    except ValueError as e:
        raise HTTPException(401, str(e))


@router.get("/me", response_model=UserResponse)
async def get_me(user_id: str = Depends(get_current_user)):
    user = container.get_user_repository().find_by_id(user_id)
    if not user:
        raise HTTPException(404, "Usuário não encontrado")
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        city_ids=user.city_ids,
        is_admin=user.is_admin,
        is_active=user.is_active
    )


@router.put("/permissions/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin)])
async def update_permissions(user_id: str, city_ids: list[str]):
    use_case = container.get_update_user_permissions_use_case()
    try:
        user = use_case.execute(user_id, city_ids)
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            city_ids=user.city_ids,
            is_admin=user.is_admin,
            is_active=user.is_active
        )
    except ValueError as e:
        raise HTTPException(404, str(e))
