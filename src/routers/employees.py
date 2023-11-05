from datetime import datetime
from typing import Annotated, Any, Sequence
from uuid import UUID
from math import ceil

from fastapi import APIRouter, status, Depends, HTTPException, Response, Request

import src.authentication.token as auth
import src.data_access_layer.employees as dal_employees
import src.data_access_layer.general as dal_gen
import src.models.employees as mod_emp
import src.models.general as mod_gen
import src.authentication.helpers as auth_gen
import src.databases.models as db_mod

router = APIRouter(tags=['employees'], dependencies=[Depends(auth.validate_token)])
AsyncSessionDep = Annotated[dal_gen.db_rel.AsyncSession, Depends(dal_gen.get_relational_async_session)]


@router.post("/employees", status_code=status.HTTP_201_CREATED, response_model=mod_emp.Employee)
async def add_employee(employee: mod_emp.NewEmployee, session: AsyncSessionDep, response: Response, request: Request)\
                       -> db_mod.Employees:
    employee: dict[str, Any] = employee.model_dump()
    user_id = request.state.token.id
    employee['created_by_id'] = user_id
    hashed_password = auth_gen.hash_password(employee['password'])
    employee['hashed_password'] = hashed_password
    del employee['password']
    del employee['confirm_password']
    async with session.begin():
        employee_data_access = dal_employees.Employees(session)
        new_employee = await employee_data_access.add(employee)
    employee_id = new_employee.id
    response.headers["Location"] = f"/employees/{employee_id}"
    return new_employee


@router.get("/employees", status_code=status.HTTP_200_OK, response_model=list[mod_emp.EmployeeLocation])
async def get_employees(session: AsyncSessionDep, pagination: mod_gen.pagination_dependency, response: Response)\
                        -> Sequence[db_mod.Employees]:
    async with session.begin():
        data_access = dal_employees.Employees(session)
        employees, employees_number = await data_access.get_many(pagination)
    if not employees:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    for employee in employees:
        employee.location = f'/employees/{employee.id}'
    link = ''
    page_size = pagination['page_size']
    offset = pagination['offset']
    if offset != 0:
        link += f"<employees?page-number=1&page-size={page_size}>; rel=\"first\""
    prev_page_number = int(offset/page_size)
    if prev_page_number != 1:
        link += f" <employees?page-number={prev_page_number}&page-size={page_size}>; rel=\"prev\""
    page_number = offset/page_size + 1
    next_page_number = page_number + 1
    last_page_number = ceil(employees_number/page_size)
    if next_page_number < last_page_number:
        link += f" <employees?page-number={next_page_number}&page-size={page_size}>; rel=\"next\""
    if page_number < last_page_number:
        link += f" <employees?page-number={last_page_number}&page-size={page_size}>; rel=\"last\""
    response.headers["Link"] = link
    return employees


@router.patch("/employees/{employee_id}", status_code=status.HTTP_200_OK,
              response_model=mod_emp.EmployeeUpdate)
async def update_employee(employee_id: UUID, employee_data: mod_emp.EmployeeUpdate, session: AsyncSessionDep,
                          request: Request) -> db_mod.Employees:
    employee_data: dict[str, Any] = employee_data.model_dump(exclude_none=True)
    user_id = request.state.token.id
    employee_data['last_modified_by_id'] = user_id
    employee_data['last_modified_date'] = datetime.now()
    async with session.begin():
        data_access = dal_employees.Employees(session)
        employee = await data_access.update(employee_id, employee_data)
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
