"""
Balances the results to ensure a mix of Cognitive/Knowledge (K) and Personality/Behavior (P) tests.
Rule: If a query hints at both skills and personality, return a balanced mix.
"""

class Balancer:
    def balance(self, results: list[dict], query: str, limit: int = 10) -> list[dict]:
        if not results:
            return []

        # Check if query needs balance (e.g., mentions both tech skills and culture/behavior)
        # For internship/standard task, we'll try to ensure at least some diversity in top 10
        
        # Test types categorized:
        # P-Type: 'Personality & Behaviour', 'Motivation', 'Competencies', 'Biodata & Situational Judgement', 'Video Interview'
        # K-Type: 'Knowledge & Skills', 'Ability & Aptitude', 'Simulations', 'Coding', 'Technology'
        
        p_types = {'Personality & Behaviour', 'Motivation', 'Competencies', 'Biodata & Situational Judgement', 'Video Interview'}
        k_types = {'Knowledge & Skills', 'Ability & Aptitude', 'Simulations', 'Coding', 'Technology'}
        
        p_results = []
        k_results = []
        other_results = []
        
        for item in results:
            item_types = set(item.get("test_type", []))
            if item_types.intersection(p_types):
                p_results.append(item)
            elif item_types.intersection(k_types):
                k_results.append(item)
            else:
                other_results.append(item)

        # Basic balancing: 60/40 or 50/50 mix for top results
        balanced = []
        p_idx = 0
        k_idx = 0
        other_idx = 0
        
        # Interleave if both exist
        while len(balanced) < limit:
            added = False
            
            # Add one from K if available
            if k_idx < len(k_results):
                balanced.append(k_results[k_idx])
                k_idx += 1
                added = True
            
            if len(balanced) >= limit: break
            
            # Add one from P if available
            if p_idx < len(p_results):
                balanced.append(p_results[p_idx])
                p_idx += 1
                added = True
                
            if not added:
                # Add one from 'others' if available
                if other_idx < len(other_results):
                    balanced.append(other_results[other_idx])
                    other_idx += 1
                else:
                    break
                    
        return balanced[:limit]
