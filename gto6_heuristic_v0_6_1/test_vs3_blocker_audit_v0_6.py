"""Validação combinatória independente da camada de auditoria v0.6."""
import unittest
from itertools import combinations
from scenario_contract import combo_count
from vs_open_reference import RANGES as VILLAIN
from vs_3bet_reference import SPECS
from vs3_blocker_audit_v0_6 import (
    COMBOS,BY_CLASS,hand_class,villain_mass_by_hero_combo,
    adjusted_action_percentages,audit_pair)

class BlockerAuditContracts(unittest.TestCase):
    def test_1326_combos_all_classes(self):
        self.assertEqual(len(COMBOS),1326)
        self.assertEqual(len(BY_CLASS),169)
        self.assertEqual(sum(map(len,BY_CLASS.values())),1326)
        for hand,combos in BY_CLASS.items():
            self.assertEqual(len(combos),combo_count(hand))

    def test_disjoint_mass_matches_independent_bruteforce(self):
        for pair in [('LJ','HJ'),('BTN','SB'),('SB','BB')]:
            by_hero,total=villain_mass_by_hero_combo(*pair)
            villain=VILLAIN[pair]
            self.assertGreater(total,0)
            for hero in [(0,1),(0,48),(25,26),(39,50)]:
                brute=sum(villain[hand_class(v)].threebet for v in COMBOS if not set(hero)&set(v))
                self.assertAlmostEqual(by_hero[hero],brute,places=8)

    def test_probabilities_conserve_mass_15_nodes(self):
        for s in SPECS:
            n=audit_pair(s.opener,s.threebettor)
            self.assertAlmostEqual(n.new_4bet+n.new_call+n.new_fold,100,places=8)
            self.assertGreater(n.model_3bet_unconditional,0)
            self.assertLessEqual(n.model_3bet_unconditional,100)
            self.assertEqual(n.reachable,sum(1 for h,cs in BY_CLASS.items()
                       if cs and __import__('vs_3bet_reference').RANGES[(s.opener,s.threebettor)][h].open_probability>0))

    def test_adjusted_bluff_share_valid(self):
        for s in SPECS:
            n=audit_pair(s.opener,s.threebettor)
            self.assertGreaterEqual(n.new_bluff_share,0)
            self.assertLessEqual(n.new_bluff_share,100)

    def test_blocker_changes_not_identity_transform(self):
        nodes=[audit_pair(s.opener,s.threebettor) for s in SPECS]
        self.assertTrue(any(abs(n.delta4)>1e-4 for n in nodes))

if __name__=='__main__': unittest.main()
