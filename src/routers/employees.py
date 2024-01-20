from typing import Annotated, Any, Sequence
from uuid import UUID

import src.databases.models.employees
from fastapi import APIRouter, status, Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

import src.services.authentication as auth
import src.data_access_layer.employees as dal_employees
import src.data_access_layer.general as dal_gen
import src.models.employees as mod_emp
import src.models.general as mod_gen
from src.services.general import prepare_new_user, prepare_pagination_link, add_modification_info

router = APIRouter(tags=['employees'], dependencies=[Depends(auth.validate_token)])
AsyncSessionDep = Annotated[AsyncSession, Depends(dal_gen.get_relational_async_session)]


@router.post("/employees", status_code=status.HTTP_201_CREATED, response_model=mod_emp.Employee)
async def add_employee(employee: mod_emp.NewEmployee, session: AsyncSessionDep, response: Response, request: Request)\
                       -> src.databases.models.employees.Employees:
    employee: dict[str, Any] = employee.model_dump()
    user_id = request.state.token.id
    employee = prepare_new_user(employee, user_id)
    async with session.begin():
        employee_data_access = dal_employees.Employees(session)
        try:
            new_employee = await employee_data_access.add(employee)
        except IntegrityError:
            raise HTTPException(status_code=400, detail='introduced data violate database constraints.')
    employee_id = new_employee.id
    response.headers["Location"] = f"/employees/{employee_id}"
    return new_employee


@router.get("/employees", status_code=status.HTTP_200_OK, response_model=list[mod_emp.EmployeeLocation])
async def get_employees(session: AsyncSessionDep, pagination: mod_gen.pagination_dependency, response: Response)\
                        -> Sequence[src.databases.models.employees.Employees]:
    async with session.begin():
        data_access = dal_employees.Employees(session)
        employees, employees_number = await data_access.get_many(pagination)
    if not employees:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    for employee in employees:
        employee.location = f'/employees/{employee.id}'
    link_base = '<employees?page-number={0}&page-size={1}>; {2}'
    links = prepare_pagination_link(link_base, pagination, employees_number)
    response.headers["Link"] = links
    return employees


@router.patch("/employees/{employee_id}", status_code=status.HTTP_200_OK,
              response_model=mod_emp.EmployeeUpdate)
async def update_employee(employee_id: UUID, employee_update: mod_emp.EmployeeUpdate, session: AsyncSessionDep,
                          request: Request) -> src.databases.models.employees.Employees:
    employee_update: dict[str, Any] = employee_update.model_dump(exclude_none=True)
    user_id = request.state.token.id
    employee_update = add_modification_info(employee_update, user_id)
    async with session.begin():
        data_access = dal_employees.Employees(session)
        employee = await data_access.update(employee_id, employee_update)
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return employee


@router.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(employee_id: UUID, session: AsyncSessionDep):
    async with session.begin():
        data_access = dal_employees.Employees(session)
        deleted_rows = await data_access.delete(employee_id)
    if deleted_rows == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
