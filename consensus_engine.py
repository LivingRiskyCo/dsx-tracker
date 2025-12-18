"""
Consensus engine for aggregating crowd-sourced tags
"""

from collections import Counter
from statistics import mean
from typing import Dict, List, Optional
from tagging_database import TaggingDatabase

class ConsensusEngine:
    def __init__(self, db: TaggingDatabase):
        self.db = db
        self.min_votes = 2  # Minimum votes for consensus
        self.agreement_threshold = 0.6  # 60% agreement required
        self.expert_weight = 1.5  # Expert votes count more
    
    def calculate_consensus(self, video_id: str, frame_num: int, track_id: int) -> Optional[Dict]:
        """
        Calculate consensus from multiple user tags
        
        Returns:
            Consensus result with player_name, confidence_score, vote_count, etc.
        """
        tags = self.db.get_tags(video_id, frame_num, track_id)
        
        if not tags:
            return None
        
        if len(tags) < self.min_votes:
            # Not enough votes yet
            most_common = Counter([t['player_name'] for t in tags]).most_common(1)[0]
            return {
                'player_name': most_common[0],
                'confidence_score': 0.4,  # Low confidence
                'vote_count': len(tags),
                'agreement_rate': 1.0,
                'status': 'pending'
            }
        
        # Group by player name with weighted votes
        name_votes = Counter()
        name_confidences = {}
        user_weights = {}
        
        # Calculate user weights (based on reputation)
        for tag in tags:
            user_id = tag['user_id']
            user_rep = self.db.get_user_reputation(user_id)
            user_weights[user_id] = self._calculate_weight(user_rep)
        
        # Weighted vote counting
        for tag in tags:
            player_name = tag['player_name']
            weight = user_weights.get(tag['user_id'], 1.0)
            name_votes[player_name] += weight
            
            if player_name not in name_confidences:
                name_confidences[player_name] = []
            name_confidences[player_name].append(tag['confidence'] * weight)
        
        # Find most voted name
        total_weighted_votes = sum(name_votes.values())
        if total_weighted_votes == 0:
            return None
        
        most_voted = name_votes.most_common(1)[0]
        player_name, vote_count = most_voted
        
        # Calculate agreement rate
        agreement_rate = vote_count / total_weighted_votes if total_weighted_votes > 0 else 0
        
        # Calculate confidence score
        confidences = name_confidences.get(player_name, [])
        avg_confidence = mean(confidences) if confidences else 0.5
        
        # Combine agreement rate and user confidence
        confidence_score = (agreement_rate * 0.7) + (avg_confidence * 0.3)
        
        # Determine status
        if agreement_rate >= self.agreement_threshold and len(tags) >= self.min_votes:
            status = 'confirmed'
        elif len(tags) >= self.min_votes:
            status = 'disputed'
        else:
            status = 'pending'
        
        # Get alternatives
        alternatives = [
            {'name': name, 'votes': int(count), 'rate': count/total_weighted_votes}
            for name, count in name_votes.most_common(3)
            if name != player_name
        ]
        
        consensus = {
            'player_name': player_name,
            'confidence_score': confidence_score,
            'vote_count': len([t for t in tags if t['player_name'] == player_name]),
            'agreement_rate': agreement_rate,
            'status': status,
            'alternatives': alternatives
        }
        
        # Update database
        self.db.update_consensus(video_id, frame_num, track_id, consensus)
        
        return consensus
    
    def _calculate_weight(self, reputation: Optional[Dict]) -> float:
        """Calculate vote weight based on user reputation"""
        if reputation is None:
            return 1.0
        
        rep_score = reputation.get('reputation_score', 0.5)
        expertise = reputation.get('expertise_level', 'beginner')
        
        # Base weight from reputation (0.5 to 1.0)
        weight = 0.5 + (rep_score * 0.5)
        
        # Expertise multiplier
        expertise_multiplier = {
            'beginner': 1.0,
            'intermediate': 1.2,
            'expert': self.expert_weight
        }
        
        weight *= expertise_multiplier.get(expertise, 1.0)
        return weight
    
    def update_all_consensus(self, video_id: str, frame_num: int):
        """Update consensus for all players in a frame"""
        # Get all unique track_ids with tags in this frame
        tags = self.db.get_tags(video_id, frame_num, None)  # Get all tags for frame
        track_ids = set([t['track_id'] for t in tags])
        
        for track_id in track_ids:
            self.calculate_consensus(video_id, frame_num, track_id)

