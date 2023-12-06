from typing import Any
from uuid import UUID
from math import ceil
from datetime import datetime

from src.services.security import hash_password


def prepare_new_user(user: dict[str, Any], user_id: UUID) -> dict[str, Any]:
    user['created_by_id'] = user_id
    hashed_password = hash_password(user['password'])
    user['hashed_password'] = hashed_password
    del user['password']
    del user['confirm_password']
    return user


def prepare_pagination_link(link_base: str, pagination, employees_number: int)-> str:
    links = ''
    page_size = pagination['page_size']
    offset = pagination['offset']
    if offset != 0:
        page_number = 1
        relation = 'rel=\"first\"'
        links += link_base.format(page_number, page_size, relation)
    prev_page_number = int(offset / page_size)
    if prev_page_number != 1:
        page_number = prev_page_number
        relation = 'rel=\"prev\"'
        links += link_base.format(page_number, page_size, relation)
    page_number = offset / page_size + 1
    next_page_number = page_number + 1
    last_page_number = ceil(employees_number / page_size)
    if next_page_number < last_page_number:
        page_number = next_page_number
        relation = 'rel=\"next\"'
        links += link_base.format(page_number, page_size, relation)
    if page_number < last_page_number:
        page_number = last_page_number
        relation = 'rel=\"last\"'
        links += link_base.format(page_number, page_size, relation)
    return links


def add_modification_info(data: [str, Any], user_id: UUID):
    data['last_modified_by_id'] = user_id
    data['last_modified_date'] = datetime.now()
    return data


def prepare_value_object(value_object: dict[str, Any], created_by_id: UUID, id_: Any = None) -> dict[str, Any]:
    value_object['created_by_id'] = created_by_id
    if id_:
        value_object['id'] = id_
    return value_object
