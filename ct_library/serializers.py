import enum
from datetime import datetime

from pydantic import BaseModel, Field
from pydantic.fields import computed_field


class AuthorInSerializer(BaseModel):
    name: str

    class Config:
        from_attributes = True


class AuthorOutSerializer(AuthorInSerializer):
    name: str
    #    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime = Field()
    updated_at: datetime | None = Field()


class BookInSerializer(BaseModel):
    title: str

    class Config:
        from_attributes = True


class BookOutSerializer(BookInSerializer):
    id: int = Field(init=False, frozen=True)
    available: bool
    author_id: int = Field()
    created_at: datetime = Field()

    updated_at: datetime | None = Field()


class BookLeaseLogInSerializer(BaseModel):
    returned_at: datetime | None = Field(default=None)

    class Config:
        from_attributes = True


class LeaseStatus(enum.Enum):
    leased = "leased"
    returned = "returned"


class BookLeaseLogOutSerializer(BookLeaseLogInSerializer):
    id: int = Field()
    book_id: int = Field()
    created_at: datetime = Field()
    returned_at: datetime | None = Field(default=None)

    @computed_field(return_type=enum.Enum)
    @property
    def status(self):
        if self.returned_at:
            return LeaseStatus.returned
        return LeaseStatus.leased


class BookLendSerializer(BaseModel):
    type: str

    class Config:
        from_attributes = True


class BookFilterParams(BaseModel):
    available: bool | None = Field(default=None)
