import unittest
from dataclasses import replace
from action_ledger import HandLedger, Move, Round, LedgerError
from strict_observation import Observation, SeenSeat, validate_observation

SIX={p:100.0 for p in ('LJ','HJ','CO','BTN','SB','BB')}

def make_obs(l, **overrides):
    d=dict(hand_id=l.hand_id, street=l.street, hero_position=l.next_actor,
           hero_turn=True, pot_bb=l.pot_bb,
           hero_to_call_bb=l.to_call(l.next_actor),
           seats={p:SeenSeat(s.balance,s.contrib,s.folded,s.allin)
                  for p,s in l.seats.items()},
           complete_history=True, stable_scrape=True)
    d.update(overrides)
    return Observation(**d)

class StrictObservationTests(unittest.TestCase):
    def test_valid_exact_snapshot(self):
        l=HandLedger('001',SIX)
        l.act('LJ', Move.RAISE,2.5)
        validate_observation(l,make_obs(l))

    def test_reject_nonstable(self):
        l=HandLedger('002',SIX)
        for o in (make_obs(l,stable_scrape=False),make_obs(l,complete_history=False)):
            with self.assertRaises(LedgerError):validate_observation(l,o)

    def test_reject_wrong_hand(self):
        l=HandLedger('002',SIX)
        with self.assertRaises(LedgerError):validate_observation(l,make_obs(l,hand_id='003'))

    def test_reject_hero_turn_off(self):
        l=HandLedger('002',SIX)
        with self.assertRaises(LedgerError):validate_observation(l,make_obs(l,hero_turn=False))

    def test_reject_pot_corrupted(self):
        l=HandLedger('002',SIX)
        with self.assertRaises(LedgerError):validate_observation(l,make_obs(l,pot_bb=90))

    def test_reject_to_call_corrupted(self):
        l=HandLedger('002',SIX)
        with self.assertRaises(LedgerError):validate_observation(l,make_obs(l,hero_to_call_bb=0))

    def test_reject_missing_seat(self):
        l=HandLedger('002',SIX)
        obs=make_obs(l)
        seats=dict(obs.seats); seats.pop('BB')
        with self.assertRaises(LedgerError):validate_observation(l,replace(obs,seats=seats))

    def test_reject_balance_corrupted(self):
        l=HandLedger('002',SIX)
        obs=make_obs(l)
        seats=dict(obs.seats); seats['SB']=replace(seats['SB'],stack_remaining_bb=42)
        with self.assertRaises(LedgerError):validate_observation(l,replace(obs,seats=seats))

    def test_reject_fold_bit_corrupted(self):
        l=HandLedger('002',SIX)
        obs=make_obs(l)
        seats=dict(obs.seats); seats['LJ']=replace(seats['LJ'],folded=True)
        with self.assertRaises(LedgerError):validate_observation(l,replace(obs,seats=seats))

if __name__=='__main__': unittest.main()
