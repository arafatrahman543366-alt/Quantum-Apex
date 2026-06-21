import pandas as pd
import numpy as np
from src.indicators.technical import TechnicalIndicators

def test_ema_calculation():
    data = {'close': [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}
    df = pd.DataFrame(data)
    ti = TechnicalIndicators()
    ema = ti.calculate_ema(df, 5)
    assert len(ema) == 10
    assert not ema.isnull().all()

def test_rsi_calculation():
    data = {'close': [10, 12, 11, 13, 12, 14, 13, 15, 14, 16, 15, 17, 16, 18]}
    df = pd.DataFrame(data)
    ti = TechnicalIndicators()
    rsi = ti.calculate_rsi(df, 14)
    assert len(rsi) == 14
