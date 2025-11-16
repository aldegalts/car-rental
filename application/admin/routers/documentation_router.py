from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse

from application.dependencies import get_current_user
from main import app

router = APIRouter(tags=["Documentation"])

@router.get("/admin/docs")
def get_admin_docs(current_user = Depends(get_current_user)):
    if current_user.role.role_name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view documentation"
        )

    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Admin API docs"
    )


@router.get("/openapi.json", include_in_schema=False)
def get_open_api(current_user = Depends(get_current_user)):
    if current_user.role.role_name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )
    return JSONResponse(app.openapi())