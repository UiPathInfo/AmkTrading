"""
ML-based Conviction Scoring Engine for High-Probability Setups

Implements:
- Feature engineering from OHLCV data
- XGBoost/Random Forest model for directional prediction
- Conviction score generation (0.0 to 1.0)
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    logger.warning("XGBoost not available, will use RandomForest as fallback")

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import TimeSeriesSplit
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logger.warning("scikit-learn not available, ML features disabled")


class FeatureEngineer:
    """Generate predictive features from OHLCV data."""
    
    @staticmethod
    def engineer_features(data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """
        Create feature matrix for ML model.
        
        Features:
        1. Price-Based: daily returns, distance from 200 EMA, volatility (ATR)
        2. Volume-Based: OBV, Chaikin Money Flow, delivery ratio
        3. Volatility State: TTM Squeeze status, Bollinger Band width percentile
        4. Market Structure: Distance from POC, Value Area location
        5. Momentum: MACD histogram slope, RSI, RSI divergence
        """
        df = data.copy()
        
        # 1. Price-Based Features
        df['Daily_Return'] = df['Close'].pct_change() * 100
        df['Return_Momentum'] = df['Daily_Return'].rolling(window=5).mean()
        
        if 'EMA_200' in df.columns:
            df['Distance_from_200EMA'] = ((df['Close'] - df['EMA_200']) / df['EMA_200']) * 100
            df['Above_200EMA'] = (df['Close'] > df['EMA_200']).astype(int)
        
        if 'ATR' in df.columns:
            df['ATR_Pct'] = (df['ATR'] / df['Close']) * 100
        else:
            df['ATR_Pct'] = df['Close'].pct_change().rolling(window=14).std() * np.sqrt(14) * 100
        
        # 2. Volume-Based Features
        df['Volume_MA_Ratio'] = df['Volume'] / df['Volume'].rolling(window=20).mean()
        df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
        df['OBV_EMA'] = df['OBV'].ewm(span=20).mean()
        
        # CMF (Chaikin Money Flow)
        hlc_avg = (df['High'] + df['Low']) + df['Close']
        mfm = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / hlc_avg.replace(0, 1)
        df['CMF'] = (mfm * df['Volume']).rolling(window=21).sum() / df['Volume'].rolling(window=21).sum()
        
        # 3. Volatility State Features
        if 'squeeze_level' in df.columns:
            squeeze_map = {'red': 3, 'orange': 2, 'gray': 1}
            df['Squeeze_Level_Num'] = df['squeeze_level'].map(squeeze_map).fillna(0)
        else:
            df['Squeeze_Level_Num'] = 0
        
        if 'compression_pct' in df.columns:
            df['Compression_Intensity'] = df['compression_pct']
        
        # Bollinger Band Width percentile
        bb = pd.DataFrame()
        bb['std'] = df['Close'].rolling(window=20).std()
        bb['mean'] = df['Close'].rolling(window=20).mean()
        df['BB_Width_Pct'] = ((bb['std'] * 2) / bb['mean'] * 100).fillna(0)
        
        # 4. Market Structure Features
        if 'poc' in df.columns or 'POC' in df.columns:
            poc_col = 'poc' if 'poc' in df.columns else 'POC'
            df['Distance_from_POC'] = abs(df['Close'] - df[poc_col])
        
        # 5. Momentum Features
        if 'MACD_Hist' in df.columns:
            df['MACD_Hist_Slope'] = df['MACD_Hist'].diff()
            df['MACD_Positive'] = (df['MACD_Hist'] > 0).astype(int)
        
        if 'RSI' in df.columns:
            df['RSI'] = df['RSI'].fillna(50)
            df['RSI_Overbought'] = (df['RSI'] > 70).astype(int)
            df['RSI_Oversold'] = (df['RSI'] < 30).astype(int)
            df['RSI_Divergence'] = (df['RSI_Div'] == 'Bullish').astype(int) if 'RSI_Div' in df.columns else 0
        
        # 6. Delivery & Institutional Features
        if 'Delivery_Pct' in df.columns:
            df['High_Delivery'] = (df['Delivery_Pct'] > 50).astype(int)
            df['Delivery_Trend_Up'] = (df['Delivery_Trend'] == 'Rising').astype(int) if 'Delivery_Trend' in df.columns else 0
        
        return df
    
    @staticmethod
    def get_feature_list() -> list:
        """Get list of feature column names for model training."""
        return [
            'Daily_Return', 'Return_Momentum', 'Distance_from_200EMA', 'Above_200EMA',
            'ATR_Pct', 'Volume_MA_Ratio', 'OBV', 'OBV_EMA', 'CMF',
            'Squeeze_Level_Num', 'Compression_Intensity', 'BB_Width_Pct',
            'Distance_from_POC', 'MACD_Hist_Slope', 'MACD_Positive',
            'RSI', 'RSI_Overbought', 'RSI_Oversold', 'RSI_Divergence',
            'High_Delivery', 'Delivery_Trend_Up'
        ]


class ConvictionScorer:
    """Calculate ML-based conviction score for trading setups."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = None
        self.scaler = StandardScaler() if HAS_SKLEARN else None
        self.feature_engineer = FeatureEngineer()
    
    def train_model(self, historical_data: pd.DataFrame) -> bool:
        """
        Train ML model on historical data.
        
        Args:
            historical_data: DataFrame with OHLCV data and targets
            
        Returns:
            True if training successful, False otherwise
        """
        if not HAS_SKLEARN:
            logger.warning("scikit-learn not available, skipping model training")
            return False
        
        try:
            # Engineer features
            df = self.feature_engineer.engineer_features(historical_data, self.config)
            feature_cols = self.feature_engineer.get_feature_list()
            
            # Remove NaN values
            df = df.dropna(subset=feature_cols)
            
            if len(df) < 100:
                logger.warning(f"Insufficient data for training: {len(df)} rows")
                return False
            
            X = df[feature_cols].values
            
            # Create target: 5% appreciation within 10 days
            target_return = self.config['ml']['target_return']
            prediction_window = self.config['ml']['prediction_window']
            y = []
            
            for i in range(len(df) - prediction_window):
                future_price = df.iloc[i + prediction_window]['Close']
                current_price = df.iloc[i]['Close']
                return_pct = (future_price - current_price) / current_price
                y.append(1 if return_pct >= target_return else 0)
            
            # Trim X to match y length
            X = X[:len(y)]
            y = np.array(y)
            
            if len(y) < 50:
                logger.warning(f"Insufficient target samples: {len(y)}")
                return False
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            if HAS_XGBOOST and self.config['ml']['model_type'] == 'xgboost':
                self.model = xgb.XGBClassifier(
                    n_estimators=100,
                    max_depth=5,
                    learning_rate=0.1,
                    random_state=self.config['ml']['random_state']
                )
            elif HAS_SKLEARN:
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=self.config['ml']['random_state'],
                    n_jobs=-1
                )
            
            if self.model:
                self.model.fit(X_scaled, y)
                logger.info(f"ML model trained with {len(y)} samples")
                return True
            
        except Exception as e:
            logger.error(f"Model training error: {e}")
        
        return False
    
    def calculate_score(self, current_data: pd.DataFrame, 
                       technical_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate conviction score for current setup.
        
        Args:
            current_data: Latest OHLCV data
            technical_analysis: Output from indicators.py analysis
            
        Returns:
            Conviction score dictionary with components
        """
        if not HAS_SKLEARN or self.model is None:
            # Fallback to rule-based conviction
            return self._rule_based_conviction(technical_analysis)
        
        try:
            # Engineer features for latest data
            df = self.feature_engineer.engineer_features(current_data, self.config)
            feature_cols = self.feature_engineer.get_feature_list()
            
            latest_features = df[feature_cols].iloc[-1:].values
            
            # Handle NaN
            latest_features = np.nan_to_num(latest_features, 0.0)
            
            # Scale and predict
            latest_features_scaled = self.scaler.transform(latest_features)
            
            if HAS_XGBOOST and isinstance(self.model, xgb.XGBClassifier):
                probabilities = self.model.predict_proba(latest_features_scaled)
                ml_score = float(probabilities[0][1])
            else:
                probabilities = self.model.predict_proba(latest_features_scaled)
                ml_score = float(probabilities[0][1])
            
        except Exception as e:
            logger.error(f"Conviction scoring error: {e}")
            ml_score = 0.5
        
        # Combine ML score with technical confluence
        technical_score = self._calculate_technical_confluence(technical_analysis)
        
        # Weighted average: 60% ML, 40% Technical
        final_score = (ml_score * 0.6) + (technical_score * 0.4)
        
        return {
            "ml_score": ml_score,
            "technical_score": technical_score,
            "conviction_score": min(1.0, max(0.0, final_score)),
            "recommendation": self._score_to_recommendation(final_score),
            "confidence_level": self._score_to_confidence(final_score),
        }
    
    def _rule_based_conviction(self, technical_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback rule-based conviction score."""
        confluence = technical_analysis.get('confluence', {})
        confluence_factors = confluence.get('total_confluent_factors', 0)
        
        score = confluence_factors * 0.3
        
        # Add RSI signal
        momentum = technical_analysis.get('momentum', {})
        rsi = momentum.get('rsi', 50)
        if 40 < rsi < 70:
            score += 0.1
        
        # Add trend signal
        trend = technical_analysis.get('trend', {})
        if trend.get('above_200_ema'):
            score += 0.15
        
        final_score = min(1.0, max(0.0, score / 1.0))
        
        return {
            "ml_score": 0.5,
            "technical_score": final_score,
            "conviction_score": final_score,
            "recommendation": self._score_to_recommendation(final_score),
            "confidence_level": self._score_to_confidence(final_score),
        }
    
    @staticmethod
    def _calculate_technical_confluence(technical_analysis: Dict[str, Any]) -> float:
        """Calculate technical confluence score (0.0 to 1.0)."""
        confluence = technical_analysis.get('confluence', {})
        total_factors = confluence.get('total_confluent_factors', 0)
        
        # 0 factors = 0.3, 1 factor = 0.5, 2 factors = 0.7, 3 factors = 0.95
        scores = {0: 0.3, 1: 0.5, 2: 0.7, 3: 0.95}
        return scores.get(total_factors, 0.3)
    
    @staticmethod
    def _score_to_recommendation(score: float) -> str:
        """Convert score to recommendation."""
        if score >= 0.85:
            return "Strong Buy"
        elif score >= 0.75:
            return "Buy"
        elif score >= 0.60:
            return "Weak Buy"
        elif score >= 0.40:
            return "Hold"
        elif score >= 0.25:
            return "Weak Sell"
        elif score >= 0.15:
            return "Sell"
        else:
            return "Strong Sell"
    
    @staticmethod
    def _score_to_confidence(score: float) -> str:
        """Convert score to confidence level."""
        if score >= 0.80:
            return "Very High"
        elif score >= 0.65:
            return "High"
        elif score >= 0.50:
            return "Medium"
        elif score >= 0.35:
            return "Low"
        else:
            return "Very Low"
