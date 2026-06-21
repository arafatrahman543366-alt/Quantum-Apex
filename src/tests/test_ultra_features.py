import pandas as pd
import numpy as np
import pytest
from src.indicators.smc import SMCIndicators
from src.tracking.risk_manager import RiskManager

@pytest.fixture
def sample_data():
    data = {
        'timestamp': pd.date_range(start='2023-01-01', periods=50, freq='15min'),
        'open': np.random.uniform(100, 110, 50),
        'high': np.random.uniform(110, 120, 50),
        'low': np.random.uniform(90, 100, 50),
        'close': np.random.uniform(100, 110, 50),
        'volume': np.random.uniform(1000, 5000, 50)
    }
    return pd.DataFrame(data)

def test_smc_ob_detection(sample_data):
    smc = SMCIndicators()
    obs = smc.detect_order_blocks(sample_data)
    assert isinstance(obs, list)
    if obs:
        assert 'type' in obs[0]
        assert 'price_high' in obs[0]

def test_smc_fvg_detection(sample_data):
    smc = SMCIndicators()
    fvgs = smc.detect_fvg(sample_data)
    assert isinstance(fvgs, list)

def test_atr_calculation(sample_data):
    smc = SMCIndicators()
    atr = smc.calculate_atr(sample_data, period=14)
    assert len(atr) == 50
    assert not atr.iloc[-1] == np.nan

def test_position_sizing():
    rm = RiskManager({})
    size = rm.calculate_position_size(10000, 100, 95, 0.01)
    # 1% of 10000 = 100. Price risk = 5. 100/5 = 20 units.
    assert size == 20.0

def test_trailing_sl_buy():
    rm = RiskManager({})
    # Direction: BUY, Price: 115, Current SL: 95, Entry: 100, TP1: 110
    # Should move to entry at least
    new_sl = rm.calculate_trailing_sl("BUY", 115, 95, 100, 110)
    assert new_sl >= 100
    
def test_trailing_sl_sell():
    rm = RiskManager({})
    # Direction: SELL, Price: 85, Current SL: 105, Entry: 100, TP1: 90
    new_sl = rm.calculate_trailing_sl("SELL", 85, 105, 100, 90)
    assert new_sl <= 100
