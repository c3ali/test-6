from sqlalchemy import Table, Column, ForeignKey
from database import Base
board_members = Table(
    'board_members',
    Base.metadata,
    Column('board_id', ForeignKey('boards.id'), primary_key=True),
    Column('user_id', ForeignKey('users.id'), primary_key=True)
)
cards_labels = Table(
    'cards_labels',
    Base.metadata,
    Column('card_id', ForeignKey('cards.id'), primary_key=True),
    Column('label_id', ForeignKey('labels.id'), primary_key=True)
)