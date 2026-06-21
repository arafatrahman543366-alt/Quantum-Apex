class SignalScorer:
    def __init__(self, config):
        self.weights = config['scoring']['weights']

    def calculate_score(self, analysis_results):
        score = 0
        
        # Trend Analysis (25 points)
        if analysis_results.get('trend_aligned', False):
            score += self.weights['trend']
            
        # Market Structure (25 points)
        structure = analysis_results.get('structure', {})
        if structure.get('hh') and structure.get('hl'):
            score += self.weights['structure']
        elif structure.get('bos'):
            score += self.weights['structure'] * 0.8
            
        # Volume Analysis (20 points)
        if analysis_results.get('volume_increasing', False):
            score += self.weights['volume']
            
        # Momentum (15 points)
        if analysis_results.get('momentum_positive', False):
            score += self.weights['momentum']
            
        # Market Health (15 points)
        if analysis_results.get('market_healthy', False):
            score += self.weights['market_health']
            
        return score
