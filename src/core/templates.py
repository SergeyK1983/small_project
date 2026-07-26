from fastapi import APIRouter, Request, status
from fastapi.templating import Jinja2Templates


index_router = APIRouter(prefix="/dev", tags=["homepage"])

templates = Jinja2Templates(directory="src/templates")


@index_router.get("", name="homepage")
async def index_page(request: Request): 
    return templates.TemplateResponse(request=request, name="index.html", status_code=status.HTTP_200_OK)


@index_router.get("/user", name="user_page")
async def user_page(request: Request): 
    return templates.TemplateResponse(request=request, name="user/profile.html", status_code=status.HTTP_200_OK)


@index_router.get("/user/update", name="user_update_page")
async def patch_user(request: Request): 
    return templates.TemplateResponse(request=request, name="user/update.html", status_code=status.HTTP_200_OK)


@index_router.get("/user/change-password", name="user_change_psw_page")
async def change_user_psw(request: Request): 
    return templates.TemplateResponse(request=request, name="user/change_password.html", status_code=status.HTTP_200_OK)


@index_router.get("/accounts", name="accounts_page")
async def get_cash_accounts(request: Request): 
    return templates.TemplateResponse(request=request, name="pay/accounts.html", status_code=status.HTTP_200_OK)


@index_router.get("/accounts/{account_id}/payments", name="payments_page")
async def get_cash_payments(request: Request): 
    return templates.TemplateResponse(request=request, name="pay/payments.html", status_code=status.HTTP_200_OK)


@index_router.get("/payment-operation", name="payment_page")
async def get_payment_amount(request: Request): 
    return templates.TemplateResponse(request=request, name="pay/payment.html", status_code=status.HTTP_200_OK)
