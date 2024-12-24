from pydantic import BaseModel


class GroupModel(BaseModel):
    group_name: str
    chat_name: str
