from pathlib import Path
import csv,hashlib,sys,unittest
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import build_3bet_multiway as b
import mw3b_interpreter as p

class ThreeBetMultiway(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.m=p.parse_file()
    def act(self,street='flop',**kwargs):return p.evaluate(self.m,street,p.observe(street,**kwargs))
    def test_source_and_action_count(self):
        self.assertEqual([len(self.m.streets[s]) for s in p.STREETS],[17,14,12])
        self.assertEqual(b.build(),(117,43))

    def test_every_legal_action_topology_has_explicit_policy(self):
        for street,n,t,r,left in b.legal():
            args={'OpponentsOnFlop':n,'OpponentsLeft':left,
                  'OpponentsOnTurn':n if t is None else t,
                  'OpponentsOnRiver':n if r is None else r}
            with self.subTest(street=street,n=n,t=t,r=r,left=left):
                self.assertEqual(self.act(street,**args),'Check')
                self.assertEqual(self.act(street,AmountToCall=100,**args),'Fold')
                self.assertEqual(self.act(street,HaveNuts=True,AmountToCall=100,**args),'Call')

    def test_caller_origin_not_discarded(self):
        caller={'user_H6_3betIntent':False,'user_H6_RFIIntent':True,
                'BotRaisedBeforeFlop':True,'BotCalledBeforeFlop':True}
        for street in p.STREETS:self.assertEqual(self.act(street,**caller),'Check')
        self.assertIsNone(self.act(user_H6_RFIIntent=True))

    def test_not_srp_not_limp_not_4bet_not_3bet_hu(self):
        for name,val in [('user_H6_3betIntent',False),('BotRaisedBeforeFlop',False),
                         ('NumberOfRaisesBeforeFlop',0),('NumberOfRaisesBeforeFlop',2),
                         ('BotCalledBeforeFlop',True),('user_H6_RFIIntent',True),
                         ('user_H6_LimpSBIntent',True),('user_H6_ML2SB',True),
                         ('user_H6_VSOpenCallIntent',True),('StackUnknown',True),
                         ('NumberOfOpponentsAllin',1),('OpponentsOnFlop',1)]:
            with self.subTest(name=name):self.assertIsNone(self.act(**{name:val}))

    def test_invalid_monotone_street_counts(self):
        for street,kw in (
            ('flop',{'OpponentsOnFlop':2,'OpponentsLeft':3}),
            ('turn',{'OpponentsOnFlop':3,'OpponentsOnTurn':4,'OpponentsLeft':2}),
            ('turn',{'OpponentsOnFlop':4,'OpponentsOnTurn':2,'OpponentsLeft':3}),
            ('river',{'OpponentsOnFlop':5,'OpponentsOnTurn':3,'OpponentsOnRiver':4,'OpponentsLeft':2}),
            ('river',{'OpponentsOnFlop':3,'OpponentsOnTurn':2,'OpponentsOnRiver':1,'OpponentsLeft':2})):
            self.assertIsNone(self.act(street,**kw))

    def test_nut_cannot_fold_overbet(self):
        for street in p.STREETS:
            self.assertEqual(self.act(street,HaveNuts=True,AmountToCall=399),'Call')
            self.assertEqual(self.act(street,HaveNuts=True,AmountToCall=1),'RaiseHalfPot')

    def test_multiway_strong_call_tighter_with_more_villains(self):
        for left,cap in ((1,9.5),(2,7.2),(3,5.)):
            d={'OpponentsOnFlop':3,'OpponentsLeft':left,
               'OpponentsOnTurn':3,'OpponentsOnRiver':3,'HaveSet':True}
            self.assertEqual(self.act(AmountToCall=cap,**d),'Call')
            self.assertEqual(self.act(AmountToCall=cap+.01,**d),'Fold')

    def test_source_never_air_cbet_into_3bet_multiway(self):
        for street in p.STREETS:
            self.assertEqual(self.act(street,AmountToCall=0,randomhand=0),'Check')

    def test_existing_all_WHEN_preserved_and_streets_unique(self):
        old=b.PARENT.read_text();new=b.COMBINED.read_text()
        before=[x for x in old.splitlines() if x.startswith('WHEN ')]
        after=[x for x in new.splitlines() if x.startswith('WHEN ')]
        i=0
        for x in before:
            while i<len(after) and after[i]!=x:i+=1
            self.assertLess(i,len(after));i+=1
        for street in ('preflop','flop','turn','river'):
            self.assertEqual(new.count(f'##f${street}##'),1)
        self.assertTrue(new.split('##f$flop##')[0].startswith(old.split('##f$flop##')[0]))

    def test_parser_rejects_unsafe_fallback(self):
        top=b.HELPERS.read_text();pol=b.POLICY.read_text()
        for bad in (pol+'\nWHEN Others Fold FORCE',
                    pol.replace('f$H6ThreeBetMWValid AND AmountToCall > 0) Fold FORCE',
                                'AmountToCall > 0) Fold FORCE'),
                    pol.replace('HaveNuts','HaveUnrecognizedCard',1)):
            with self.assertRaises(p.SourceError):p.parse(top,bad)

    def test_bad_input_rejected(self):
        for args in ({'randomhand':1},{'AmountToCall':float('nan')},
                     {'BotRaisedBeforeFlop':1},{'IsRiver':True},{'Position':'Late'}):
            with self.assertRaises(p.SourceError):self.act(**args)

    def test_generator_idempotent_and_topology_matrix(self):
        with b.MATRIX.open(newline='',encoding='utf-8') as f:rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),234)
        self.assertEqual({row['PreflopRole'] for row in rows},
                         {'THREEBET_AGGRESSOR','RFI_CALLER_VS_THREEBET'})
        files=(b.PARENT,b.COMBINED,b.HELPERS,b.MATRIX)
        hashes=[hashlib.sha256(path.read_bytes()).digest() for path in files]
        self.assertEqual(b.build(),(117,43))
        self.assertEqual(hashes,[hashlib.sha256(path.read_bytes()).digest() for path in files])

if __name__=='__main__':unittest.main()
