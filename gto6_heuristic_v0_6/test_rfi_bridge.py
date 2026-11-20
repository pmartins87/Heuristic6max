import unittest
from action_ledger import HandLedger, Move, LedgerError
from strict_observation import Observation, SeenSeat
from rfi_bridge import prepare_rfi

SIX={p:100.0 for p in ('LJ','HJ','CO','BTN','SB','BB')}

def snapshot(l,stable=True):
    h=l.next_actor
    return Observation(hand_id=l.hand_id, street=l.street,
            hero_position=h,hero_turn=True,pot_bb=l.pot_bb,
            hero_to_call_bb=l.to_call(h),
            seats={p:SeenSeat(s.balance,s.contrib,s.folded,s.allin) for p,s in l.seats.items()},
            complete_history=True,stable_scrape=stable)

class BridgeTests(unittest.TestCase):
    def test_hero_lj_rfi(self):
        l=HandLedger('abc',SIX)
        p=prepare_rfi(l,snapshot(l),'AA')
        self.assertIsNotNone(p)
        self.assertEqual(p.status,'DRAFT')
        self.assertEqual(p.actions[0].raise_to_bb,2.5)

    def test_hero_btn_after_folds(self):
        l=HandLedger('abc',SIX)
        for p in ('LJ','HJ','CO'):l.act(p,Move.FOLD)
        self.assertIsNotNone(prepare_rfi(l,snapshot(l),'Q9o'))

    def test_hero_sb_open_size(self):
        l=HandLedger('abc',SIX)
        for p in ('LJ','HJ','CO','BTN'):l.act(p,Move.FOLD)
        p=prepare_rfi(l,snapshot(l),'AA')
        self.assertEqual(p.actions[0].raise_to_bb,3.0)

    def test_no_rfi_after_limps(self):
        l=HandLedger('abc',SIX)
        l.act('LJ',Move.CALL)
        self.assertIsNone(prepare_rfi(l,snapshot(l),'AA'))

    def test_no_rfi_after_open(self):
        l=HandLedger('abc',SIX)
        l.act('LJ',Move.RAISE,2.5)
        self.assertIsNone(prepare_rfi(l,snapshot(l),'AA'))

    def test_snapshot_inconsistent_blocks(self):
        l=HandLedger('abc',SIX)
        with self.assertRaises(LedgerError):prepare_rfi(l,snapshot(l,False),'AA')

if __name__=='__main__':unittest.main()
