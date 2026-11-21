"""ISODEF-1 contract tests parse the authored OpenPPL, never separate Python ranges.

Not a substitute for OpenHoldem action confirmation, pot-history capture or EV.
"""
from pathlib import Path
import hashlib
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import build_defense as build
import defense_interpreter as d

TAG3=('user_H6_DEF_BTN3','user_H6_DEF_BB3')
TAGC=('user_H6_DEF_BTNC','user_H6_DEF_BBC')
TAGS=TAG3+TAGC


class ISODefenseV1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.post=d.parse_file()
        cls.pre=d.preflop_file()

    def pf(self,hand='AKs',**kw):
        return d.preflop_evaluate(self.pre,d.preflop_state(hand,**kw))

    @staticmethod
    def origin(tag):
        return {**{x:False for x in TAGS},tag:True,
                'BotRaisedBeforeFlop':tag in TAG3,
                'BotCalledBeforeFlop':tag in TAGC}

    def act(self,street='flop',**kw):
        return d.evaluate(self.post,street,d.observe(street,**kw))

    def test_01_source_only_build_reproduces_integrated(self):
        self.assertEqual(build.render(),build.COMBINED.read_text())

    def test_02_all_1920_ancestral_when_preserved_in_order(self):
        old=[s for s in build.PARENT.read_text().splitlines() if s.startswith('WHEN ')]
        new=[s for s in build.COMBINED.read_text().splitlines() if s.startswith('WHEN ')]
        self.assertEqual(len(old),1920)
        pos=0
        for original in old:
            while pos<len(new) and new[pos]!=original:pos+=1
            self.assertLess(pos,len(new))
            pos+=1
        self.assertEqual(len(new),2007)

    def test_03_unchanged_frozen_range_namespace(self):
        old=build.PARENT.read_text()
        new=build.COMBINED.read_text()
        self.assertNotIn('##listH6DEF3BET##',old)
        for tag in ('##f$preflop##','##f$flop##','##f$turn##','##f$river##'):
            self.assertEqual(new.count(tag),1)
        self.assertEqual(len(self.post.helpers)-len(d.prev.parse_file().helpers),7)

    def test_04_disjoint_source_handclasses(self):
        sets=self.pre.lists
        self.assertEqual(len(sets),3)
        self.assertEqual(sets['listH6DEF3BET'],{'AA','KK','QQ','AKs','AKo'})
        self.assertFalse(sets['listH6DEF3BET'] & sets['listH6DEFCALLBTN'])
        self.assertFalse(sets['listH6DEF3BET'] & sets['listH6DEFCALLBB'])

    def test_05_btn_isolation_has_three_actions_with_tags(self):
        for hand,action,tag in (
            ('AA','RaiseTo 13.5 FORCE','user_H6_DEF_BTN3'),
            ('AKo','RaiseTo 13.5 FORCE','user_H6_DEF_BTN3'),
            ('KQs','Call FORCE','user_H6_DEF_BTNC'),
            ('99','Call FORCE','user_H6_DEF_BTNC'),
            ('A2o','Fold FORCE',None)):
            with self.subTest(hand=hand):
                observed,tags=self.pf(hand)
                self.assertEqual(observed,action)
                self.assertEqual(tags,(tag,) if tag else ())

    def test_06_bb_isolation_action_and_bb_investment(self):
        kw={'InButton':False,'InBigBlind':True,
            'StillToAct':0,'FirstRaiserPosition':2,'LastRaiserPosition':2,
            'AmountToCall':3.5}
        for hand,action,tag in (
            ('AA','RaiseTo 15.75 FORCE','user_H6_DEF_BB3'),
            ('AKs','RaiseTo 15.75 FORCE','user_H6_DEF_BB3'),
            ('JJ','Call FORCE','user_H6_DEF_BBC'),
            ('99','Fold FORCE',None),
            ('72o','Fold FORCE',None)):
            self.assertEqual(self.pf(hand,**kw),(action,(tag,) if tag else ()))

    def test_07_preflop_guard_requires_earlier_limper(self):
        for key,val in [('Raises',0),('Raises',2),('Calls',0),
                        ('Calls',2),('PotSize',4),('PotSize',7.5),
                        ('AmountToCall',2.5),('StillToAct',1),
                        ('FirstRaiserPosition',4),('LastRaiserPosition',2),
                        ('nplayersdealt',5),('StackUnknown',True),
                        ('IsPreflop',False),('StackSize',50),
                        ('MinOpponentStackSize',40),('MaxOpponentStackSize',130)]:
            with self.subTest(key=key):
                self.assertEqual(self.pf('AA',**{key:val}),(None,()))

    def test_08_preflop_guard_requires_correct_hero_seat(self):
        self.assertEqual(self.pf('AA',InButton=False),(None,()))
        self.assertEqual(self.pf('AA',InBigBlind=True),(None,()))
        self.assertEqual(self.pf('AA',InButton=False,InBigBlind=True),
                         (None,()))

    def test_09_all_169_hands_have_one_btn_decision(self):
        ranks='AKQJT98765432'
        allhands=[r+r for r in ranks]
        for i,a in enumerate(ranks):
            for b in ranks[i+1:]:
                allhands.extend([a+b+'s',a+b+'o'])
        self.assertEqual(len(allhands),169)
        for h in allhands:
            with self.subTest(hand=h):
                action,tags=self.pf(h)
                self.assertIn(action,('RaiseTo 13.5 FORCE','Call FORCE','Fold FORCE'))
                self.assertLessEqual(len(tags),1)

    def test_10_exact_guarded_preflop_fallback_not_global(self):
        self.assertEqual(len(self.pre.rules),10)
        self.assertEqual(sum(x.action=='Fold FORCE' for x in self.pre.rules),2)
        self.assertNotIn('WHEN Others Fold FORCE',build.PREFLOP.read_text())
        self.assertNotIn('WHEN Others Fold FORCE',build.POLICY.read_text())

    def test_11_four_distinct_postflop_origins_are_reachable(self):
        for tag in TAGS:
            args=self.origin(tag)
            args.update(OpponentsOnFlop=1,OpponentsOnTurn=1,
                        OpponentsOnRiver=1,OpponentsLeft=1)
            for street in build.STREETS:
                with self.subTest(tag=tag,street=street):
                    self.assertEqual(self.act(street,**args),'Check')
                    self.assertEqual(self.act(street,AmountToCall=100,**args),'Fold')

    def test_12_invalid_history_or_origin_is_no_match(self):
        for key,val in [
            ('user_H6_DEF_BB3',True),('user_H6_BISOBB2Other',True),
            ('user_H6_ISOBTN1',True),('user_H6_RFIIntent',True),
            ('user_H6_3betIntent',True),('user_H6_ML2SB',True),
            ('BotCheckedPreflop',True),('BotRaisedBeforeFlop',True),
            ('BotCalledBeforeFlop',False),('NumberOfRaisesBeforeFlop',0),
            ('NumberOfRaisesBeforeFlop',2),('NumberOfOpponentsAllin',1),
            ('StackUnknown',True),('nplayersdealt',5)]:
            with self.subTest(key=key,val=val):
                self.assertIsNone(self.act(**{key:val}))

    def test_13_provenance_3bettor_and_caller_not_interchangeable(self):
        hand3=self.origin('user_H6_DEF_BTN3')
        call=self.origin('user_H6_DEF_BTNC')
        for hand in (hand3,call):
            hand.update(OpponentsOnFlop=1,OpponentsOnTurn=1,
                        OpponentsOnRiver=1,OpponentsLeft=1)
        self.assertEqual(self.act('flop',HaveSet=True,**hand3),'BetHalfPot')
        self.assertEqual(self.act('flop',HaveSet=True,**call),'BetThirdPot')
        self.assertEqual(self.act('flop',HaveNuts=True,**hand3),'BetTwoThirdPot')
        self.assertEqual(self.act('flop',HaveNuts=True,**call),'BetTwoThirdPot')

    def test_14_transitions_3way_to_hu_are_allowed(self):
        for tag in TAGS:
            args=self.origin(tag)
            for street,counts in [
                ('flop',{'OpponentsOnFlop':2,'OpponentsLeft':1}),
                ('turn',{'OpponentsOnFlop':2,'OpponentsOnTurn':1,'OpponentsLeft':1}),
                ('turn',{'OpponentsOnFlop':2,'OpponentsOnTurn':2,'OpponentsLeft':1}),
                ('river',{'OpponentsOnFlop':2,'OpponentsOnTurn':2,'OpponentsOnRiver':1,'OpponentsLeft':1}),
                ('river',{'OpponentsOnFlop':2,'OpponentsOnTurn':2,'OpponentsOnRiver':2,'OpponentsLeft':1})]:
                self.assertEqual(self.act(street,**args,**counts),'Check')

    def test_15_outside_topology_never_claim_new_policy(self):
        for st,counts in [
            ('flop',{'OpponentsOnFlop':3,'OpponentsLeft':2}),
            ('flop',{'OpponentsOnFlop':1,'OpponentsLeft':2}),
            ('turn',{'OpponentsOnFlop':1,'OpponentsOnTurn':2,'OpponentsLeft':1}),
            ('turn',{'OpponentsOnFlop':2,'OpponentsOnTurn':1,'OpponentsLeft':2}),
            ('river',{'OpponentsOnFlop':2,'OpponentsOnTurn':1,'OpponentsOnRiver':2,'OpponentsLeft':1})]:
            with self.subTest(street=st):
                self.assertIsNone(self.act(st,**counts))

    def test_16_nuts_never_folds_to_large_overbet(self):
        for tag in TAGS:
            args=self.origin(tag)
            for street in build.STREETS:
                self.assertEqual(self.act(street,HaveNuts=True,AmountToCall=2,**args),'RaiseHalfPot')
                self.assertEqual(self.act(street,HaveNuts=True,AmountToCall=400,**args),'Call')

    def test_17_differentiated_hu_vs_threeway_price_caps(self):
        caps={'flop':(8,7,4.8),'turn':(6.5,5.5,3.5),'river':(5,4.3,2.6)}
        for street,(three,caller,two) in caps.items():
            for tag,opp,cap in [('user_H6_DEF_BTN3',1,three),
                                ('user_H6_DEF_BTNC',1,caller),
                                ('user_H6_DEF_BTN3',2,two),
                                ('user_H6_DEF_BTNC',2,two)]:
                args={**self.origin(tag),'OpponentsLeft':opp,
                      'HaveSet':True,'PotSize':10}
                with self.subTest(street=street,tag=tag,opp=opp):
                    self.assertEqual(self.act(street,AmountToCall=cap,**args),'Call')
                    self.assertEqual(self.act(street,AmountToCall=cap+.1,**args),'Fold')

    def test_18_actual_source_parser_rejects_broad_fallback(self):
        policy=build.POLICY.read_text()
        topology=build.TOPOLOGY.read_text()
        for broken in [
            policy.replace('HaveNuts','HaveQuantumNuts',1),
            policy.replace('f$H6DEFValid AND AmountToCall > 0) Fold FORCE',
                           'AmountToCall > 0) Fold FORCE'),
            policy+'\nWHEN Others Fold FORCE']:
            with self.assertRaises(d.SourceError):
                d.parse(topology,broken)

    def test_19_preflop_source_rejects_mutations(self):
        source=build.PREFLOP.read_text()
        hands=build.HAND.read_text()
        for broken in [source.replace('Calls = 1','Calls = 2',1),
                       source.replace('listH6DEF3BET','listH6DEFUNKNOWN',1),
                       source.replace('RaiseTo 13.5 FORCE','Check FORCE',1)]:
            with self.assertRaises(d.SourceError):
                d.parse_preflop(hands,broken)
        with self.assertRaises(d.SourceError):
            d.parse_preflop(hands.replace('AA KK QQ AKs AKo','AA KK QQ JJ AKs AKo'),source)

    def test_20_bad_inputs_are_rejected(self):
        with self.assertRaises(d.SourceError):self.pf('AA',Calls=float('nan'))
        with self.assertRaises(d.SourceError):self.pf('AA',IsPreflop=1)
        with self.assertRaises(d.SourceError):self.act(AmountToCall=float('nan'))
        with self.assertRaises(d.SourceError):self.act(Position='Unknown')

    def test_21_build_repeatable_from_source_bytes(self):
        files=(build.PARENT,build.HAND,build.PREFLOP,build.TOPOLOGY,
               build.POLICY,build.COMBINED)
        originals=[hashlib.sha256(p.read_bytes()).hexdigest() for p in files]
        self.assertEqual(build.build()[0],42)
        self.assertEqual(originals,[hashlib.sha256(p.read_bytes()).hexdigest() for p in files])


if __name__=='__main__':
    unittest.main()
