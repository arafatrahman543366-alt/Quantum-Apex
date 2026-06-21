from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Signal(Base):
    __tablename__ = 'signals'
    
    id = Column(Integer, primary_key=True)
    coin = Column(String, nullable=False)
    direction = Column(String, nullable=False)
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    tp1 = Column(Float, nullable=False)
    tp2 = Column(Float)
    tp3 = Column(Float)
    confidence = Column(Integer, nullable=False)
    risk_reward = Column(Float, nullable=False)
    reasons = Column(String)
    trade_id = Column(String, unique=True)
    status = Column(String, default='PENDING') # PENDING, ACTIVE, TP1 HIT, SL HIT, EXPIRED
    telegram_msg_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trades = relationship("Trade", back_populates="signal")

class Trade(Base):
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    signal_id = Column(Integer, ForeignKey('signals.id'))
    coin = Column(String, nullable=False)
    direction = Column(String, nullable=False)
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    tp1 = Column(Float, nullable=False)
    tp2 = Column(Float)
    tp3 = Column(Float)
    status = Column(String, default='PENDING')
    entry_time = Column(DateTime)
    exit_time = Column(DateTime)
    profit_loss = Column(Float)
    duration = Column(Integer) # in minutes
    telegram_msg_id = Column(String)

    signal = relationship("Signal", back_populates="trades")

class Performance(Base):
    __tablename__ = 'performance'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, unique=True, nullable=False)
    total_signals = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    avg_rr = Column(Float, default=0.0)
    top_coins = Column(String) # JSON string
    monthly_profit = Column(Float, default=0.0)

class Setting(Base):
    __tablename__ = 'settings'
    
    key = Column(String, primary_key=True)
    value = Column(String)
    description = Column(String)

def init_db(db_url):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
