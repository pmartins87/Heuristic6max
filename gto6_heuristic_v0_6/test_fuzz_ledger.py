"""Testes por propriedades com sequências variadas legais (sem dependências)."""
import random
import unittest
from action_ledger import HandLedger, Move, Round

class FuzzLedgerTests(unittest.TestCase):
    def test_randomized_valid_actions_no_negative_chips(self):
        rng=random.Random(20261120)
        roles={2:('SB','BB'),3:('BTN','SB','BB'),4:('CO','BTN','SB','BB'),
               5:('HJ','CO','BTN','SB','BB'),6:('LJ','HJ','CO','BTN','SB','BB')}
        completed=0
        for n in roles:
            for repeat in range(100):
                stacks={p:rng.choice((12.,35.,100.,160.)) for p in roles[n]}
                l=HandLedger(f'{n}-{repeat}',stacks)
                steps=0
                while l.next_actor and steps<100:
                    steps+=1
                    p=l.next_actor
                    opts=sorted(l.allowed(p),key=lambda x:x.value)
                    move=rng.choice(opts)
                    if move in (Move.BET,Move.RAISE):
                        min_raise=l.min_raise_to()
                        max_raise=l.seats[p].contrib+l.seats[p].balance
                        # pode haver menos fichas que minimum raise: SHOVE legal substitui RAISE
                        if max_raise+1e-8 < min_raise:
                            move=Move.SHOVE
                            l.act(p,move)
                        else:
                            bet=min(max_raise,min_raise+rng.randint(0,5))
                            l.act(p,move,bet)
                    else:
                        l.act(p,move)
                    self.assertTrue(all(-1e-7<=s.balance for s in l.seats.values()))
                    self.assertTrue(all(abs(s.original_stack-s.balance-s.paid)<1e-6
                                        for s in l.seats.values()))
                    self.assertAlmostEqual(l.pot_bb,sum(s.paid for s in l.seats.values()))
                    self.assertTrue(all(p in l.seats for p in l.pending))
                self.assertLess(steps,100)
                if not l.finished:
                    for street in (Round.FLOP,Round.TURN,Round.RIVER):
                        l.next_street(street)
                        steps=0
                        while l.next_actor and steps<100:
                            steps+=1
                            p=l.next_actor
                            move=rng.choice(sorted(l.allowed(p),key=lambda x:x.value))
                            if move in (Move.BET,Move.RAISE):
                                top=l.seats[p].contrib+l.seats[p].balance
                                if top+1e-8<l.min_raise_to():
                                    move=Move.SHOVE
                                    l.act(p,move)
                                else:l.act(p,move,l.min_raise_to())
                            else:l.act(p,move)
                            self.assertTrue(all(s.balance>=-1e-7 for s in l.seats.values()))
                        self.assertLess(steps,100)
                        if l.finished: break
                completed+=1
        self.assertEqual(completed,500)

if __name__=='__main__':unittest.main()
