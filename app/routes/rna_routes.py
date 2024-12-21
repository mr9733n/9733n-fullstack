from aiohttp.web_exceptions import HTTPException
from fastapi import APIRouter, Request, Form, Query, Body

from app.services.japanese_name_service import JapaneseNameService
from app.services.password_service import PasswordService

router = APIRouter()

__version__ = '0.1.4.1'

# Роуты
@router.get("/", summary="Root endpoint for RNA Project")
async def index():
    """Возвращает базовую информацию о проекте."""
    return {"message": "Welcome to RNA Project", "version": __version__}

@router.get("/generate/password", summary="Generate random passwords")
async def generate_passwords_route(
    length: int = Query(8, ge=4, le=128, description="Password length (default: 8, min: 4, max: 128)"),
    count: int = Query(1, ge=1, le=100, description="Number of passwords to generate (default: 1)"),
    use_uppercase: bool = Query(False, description="Include uppercase letters"),
    use_lowercase: bool = Query(True, description="Include lowercase letters"),
    use_digits: bool = Query(True, description="Include digits"),
    use_symbols: bool = Query(False, description="Include symbols"),
    decorate: bool = Query(False, description="Decorate passwords with separators"),
    secret: str = Query("", description="Optional secret for unique variations"),
):
    """
    Generates random passwords with optional settings.
    """
    try:
        passwords = PasswordService.generate_passwords(
            count=count,
            length=length,
            use_uppercase=use_uppercase,
            use_lowercase=use_lowercase,
            use_digits=use_digits,
            use_symbols=use_symbols,
            decorate=decorate,
            secret=secret,
        )
        return {"passwords": passwords}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/generate/names", summary="Generate Japanese Names")
async def japanese_names_route(
    num_names: int = Query(1, ge=1, description="Number of names to generate"),
    sex: str = Query("male", pattern="^(male|female)$", description="Gender of names (male or female)"),

    firstname_rarity: str = Query("very_rare", description="Rarity of the first name (e.g., common, rare, very_rare)"),
    lastname_rarity: str = Query("very_rare", description="Rarity of the last name (e.g., common, rare, very_rare)")
):
    """
    Generate Japanese names based on the provided parameters.

    - `num_names`: Number of names to generate (default: 1).
    - `sex`: Gender of the names (male or female, default: male).
    - `firstname_rarity`: Rarity of the first name (default: very_rare).
    - `lastname_rarity`: Rarity of the last name (default: very_rare).
    """
    names = JapaneseNameService.generate_names(
        num_names=num_names,
        sex=sex,
        firstname_rarity=firstname_rarity,
        lastname_rarity=lastname_rarity
    )
    return {"names": names}