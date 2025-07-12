from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import Annotated, List

from thaitravel.core import deps
from thaitravel import models

router = APIRouter(prefix="/province_tax", tags=["province_tax"])


# CREATE BaseProvinceTax
@router.post(
    "/base", response_model=models.BaseProvinceTax, status_code=status.HTTP_201_CREATED
)
async def create_base_province_tax(
    data: models.BaseProvinceTax,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
):
    exist = await session.exec(
        select(models.DBBaseProvinceTax).where(
            models.DBBaseProvinceTax.province == data.province
        )
    )
    if exist.first():
        raise HTTPException(status_code=409, detail="This province already exists.")
    db_item = models.DBBaseProvinceTax(province=data.province, tax=data.tax)
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return models.BaseProvinceTax.from_orm(db_item)


# READ BaseProvinceTax
@router.get("/base", response_model=List[models.ProvinceTax])
async def get_base_province_tax(
    session: Annotated[AsyncSession, Depends(models.get_session)],
):
    result = await session.exec(select(models.DBBaseProvinceTax))
    db_items = result.all()
    return [models.ProvinceTax.model_validate(item) for item in db_items]


# CREATE RegisteredProvinceTax
@router.post(
    "/register",
    response_model=models.RegisteredProvinceTax,
    status_code=status.HTTP_201_CREATED,
)
async def register_province_tax(
    data: models.RegisterProvinceTaxRequest,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
):
    # ตรวจสอบซ้ำ
    exist = await session.exec(
        select(models.DBRegisteredProvinceTax).where(
            models.DBRegisteredProvinceTax.user_id == current_user.id,
            models.DBRegisteredProvinceTax.main_province_id == data.main_province_id,
        )
    )
    if exist.first():
        raise HTTPException(
            status_code=409, detail="Already registered for this province."
        )

    # ดึง tax ของ main_province
    main_tax_result = await session.exec(
        select(models.DBBaseProvinceTax).where(
            models.DBBaseProvinceTax.id == data.main_province_id
        )
    )
    main_tax_obj = main_tax_result.first()
    if not main_tax_obj:
        raise HTTPException(status_code=404, detail="Main province not found.")

    # ดึง tax ของ secondary_province (ถ้ามี)
    secondary_tax = None
    if data.secondary_province_id:
        sec_tax_result = await session.exec(
            select(models.DBBaseProvinceTax).where(
                models.DBBaseProvinceTax.id == data.secondary_province_id
            )
        )
        sec_tax_obj = sec_tax_result.first()
        if not sec_tax_obj:
            raise HTTPException(status_code=404, detail="Secondary province not found.")
        secondary_tax = sec_tax_obj.tax

    reg = models.DBRegisteredProvinceTax(
        user_id=current_user.id,
        name=data.name,
        email=data.email,
        main_province_id=data.main_province_id,
        main_province_tax=main_tax_obj.tax,
        secondary_province_id=data.secondary_province_id,
        secondary_province_tax=secondary_tax,
    )
    session.add(reg)
    await session.commit()
    await session.refresh(reg)
    return models.RegisteredProvinceTax.model_validate(reg)


# READ RegisteredProvinceTax (เฉพาะของ user)
@router.get("/registered", response_model=List[models.RegisteredProvinceTax])
async def get_registered_province_tax(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
):
    result = await session.exec(
        select(models.DBRegisteredProvinceTax).where(
            models.DBRegisteredProvinceTax.user_id == current_user.id
        )
    )
    db_items = result.all()
    return [models.RegisteredProvinceTax.model_validate(item) for item in db_items]


# UPDATE RegisteredProvinceTax
@router.put("/registered/{reg_id}", response_model=models.RegisteredProvinceTax)
async def update_registered_province_tax(
    reg_id: int,
    data: models.RegisterProvinceTaxRequest,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
):
    reg = await session.get(models.DBRegisteredProvinceTax, reg_id)
    if not reg or reg.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Registration not found.")

    # อัปเดตข้อมูล
    reg.name = data.name
    reg.email = data.email

    # อัปเดต main province
    main_tax_result = await session.exec(
        select(models.DBBaseProvinceTax).where(
            models.DBBaseProvinceTax.id == data.main_province_id
        )
    )
    main_tax_obj = main_tax_result.first()
    if not main_tax_obj:
        raise HTTPException(status_code=404, detail="Main province not found.")
    reg.main_province_id = data.main_province_id
    reg.main_province_tax = main_tax_obj.tax

    # อัปเดต secondary province
    if data.secondary_province_id:
        sec_tax_result = await session.exec(
            select(models.DBBaseProvinceTax).where(
                models.DBBaseProvinceTax.id == data.secondary_province_id
            )
        )
        sec_tax_obj = sec_tax_result.first()
        if not sec_tax_obj:
            raise HTTPException(status_code=404, detail="Secondary province not found.")
        reg.secondary_province_id = data.secondary_province_id
        reg.secondary_province_tax = sec_tax_obj.tax
    else:
        reg.secondary_province_id = None
        reg.secondary_province_tax = None

    session.add(reg)
    await session.commit()
    await session.refresh(reg)
    return models.RegisteredProvinceTax.model_validate(reg)


# DELETE RegisteredProvinceTax
@router.delete("/registered/{reg_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_registered_province_tax(
    reg_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
):
    reg = await session.get(models.DBRegisteredProvinceTax, reg_id)
    if not reg or reg.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Registration not found.")
    await session.delete(reg)
    await session.commit()
