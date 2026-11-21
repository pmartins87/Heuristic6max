from pathlib import Path
import csv, hashlib, sys, unittest
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import build_multilimp as b
import ml_interpreter as p

class MultiLimpBB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.model=p.parse_file()
    def act(self,street='flop',**kw):return p.evaluate(self.model,street,p.observe(street,**kw))
    def test_seven_unique_preflop_options_not_calls_or_raises(self):
        src=b.CAPTURE.read_text()
        lines=[x for x in src.splitlines() if x.startswith('WHEN ')]
        self.assertEqual(len(lines),14)
        self.assertEqual(sum(' Check FORCE' in x for x in lines),7)
        self.assertEqual(sum(' Set user_H6_ML' in x for x in lines),7)
        self.assertTrue(all('Calls = ' in x and 'Raises = 0' in x and
                            'InBigBlind' in x and 'StillToAct = 0' in x for x in lines))
        self.assertEqual({x[0:2] for x in ((str(n),typ) for n,typ,_ in b.INTENTS)},
                         {(str(n),typ) for n in (2,3,4) for typ in ('SB','Other')}|{('5','SB')})
        self.assertEqual({(n,typ,b.pot_for(n,typ)) for n,typ,_ in b.INTENTS},
                         {(2,'SB',3),(2,'Other',3.5),(3,'SB',4),(3,'Other',4.5),
                          (4,'SB',5),(4,'Other',5.5),(5,'SB',6)})

    def test_39_actions_and_consistent_parser(self):
        self.assertEqual([len(self.model.rules[s]) for s in p.STREETS],[14,13,12])
        self.assertEqual(len(self.model.helpers),32)
        self.assertEqual(b.build(),(7,39,117))

    def test_valid_street_topology_all_seven_intents(self):
        for street,n,t,r,left in b.topologies():
            for nn,typ,tag in b.INTENTS:
                if nn!=n:continue
                ov={'OpponentsOnFlop':n,'OpponentsLeft':left,
                    'OpponentsOnTurn':t if t is not None else n,
                    'OpponentsOnRiver':r if r is not None else n,
                    'user_H6_ML2SB':False,tag:True}
                with self.subTest(street=street,n=n,t=t,r=r,left=left,typ=typ):
                    self.assertEqual(self.act(street,**ov),'Check')
                    self.assertEqual(self.act(street,AmountToCall=500,**ov),'Fold')
                    self.assertEqual(self.act(street,HaveNuts=True,AmountToCall=500,**ov),'Call')

    def test_invalid_monotone_history_not_accepted(self):
        for street,extra in (
            ('flop',{'OpponentsLeft':3}),
            ('turn',{'OpponentsOnTurn':3,'OpponentsLeft':2}),
            ('river',{'OpponentsOnTurn':2,'OpponentsOnRiver':3,'OpponentsLeft':2}),
            ('river',{'OpponentsOnTurn':1,'OpponentsOnRiver':1,'OpponentsLeft':2}),
        ):
            self.assertIsNone(self.act(street,**extra))

    def test_old_intents_and_3bet_never_enter_limped_family(self):
        for k,v in (('user_H6_LimpSBIntent',True),('user_H6_LimpOtherIntent',True),
                    ('user_H6_3betIntent',True),('user_H6_RFIIntent',True),
                    ('BotRaisedBeforeFlop',True),('BotCalledBeforeFlop',True),
                    ('BotCheckedPreflop',False),('StackUnknown',True),
                    ('NumberOfRaisesBeforeFlop',1),('NumberOfOpponentsAllin',1)):
            with self.subTest(k=k):self.assertIsNone(self.act(**{k:v}))

    def test_competing_intents_never_both_admitted(self):
        self.assertIsNone(self.act(user_H6_ML2Other=True))
        self.assertIsNone(self.act(user_H6_ML3SB=True))
        self.assertIsNone(self.act(user_H6_ML2SB=False))

    def test_betting_tightens_as_more_opponents_remain(self):
        for left,cap in ((1,8.),(2,6.5),(3,4.8)):
            ctx={'OpponentsOnFlop':3,'OpponentsLeft':left,
                 'OpponentsOnTurn':3,'OpponentsOnRiver':3,'HaveSet':True,
                 'user_H6_ML2SB':False,'user_H6_ML3SB':True}
            self.assertEqual(self.act(AmountToCall=cap,**ctx),'Call')
            self.assertEqual(self.act(AmountToCall=cap+.01,**ctx),'Fold')

    def test_no_automatic_air_bluffs_with_many_limpers(self):
        for street in p.STREETS:
            self.assertEqual(self.act(street,randomhand=0),'Check')
            self.assertEqual(self.act(street,HaveNuts=True,AmountToCall=360),'Call')
            self.assertEqual(self.act(street,HaveNuts=True,AmountToCall=1),'RaiseHalfPot')

    def test_preflop_parent_action_text_identical_and_source_unique(self):
        old=b.PARENT.read_text();new=b.COMBINED.read_text()
        o=[x for x in old.splitlines() if x.startswith('WHEN ')]
        n=[x for x in new.splitlines() if x.startswith('WHEN ')]
        i=0
        for x in o:
            while i<len(n) and n[i]!=x:i+=1
            self.assertLess(i,len(n));i+=1
        for street in ('preflop','flop','turn','river'):
            self.assertEqual(new.count(f'##f${street}##'),1)

    def test_parser_rejects_unguarded_bad_moves(self):
        source=b.STRATEGY.read_text();top=b.HELPERS.read_text()
        for bad in (source+'\nWHEN Others Fold FORCE',
                    source.replace('f$H6MLValid AND AmountToCall > 0) Fold FORCE',
                                   'AmountToCall > 0) Fold FORCE'),
                    source.replace('HaveNuts','UnknownHandSymbol',1)):
            with self.assertRaises(p.SourceError):p.parse(top,bad)

    def test_unknown_symbols_finite_and_types_checked(self):
        for kwargs in ({'randomhand':1},{'AmountToCall':-2},{'PotSize':0},
                       {'BotCheckedPreflop':1},{'Position':'Bottom'},
                       {'IsRiver':True}):
            with self.subTest(kwargs=kwargs),self.assertRaises(p.SourceError):self.act(**kwargs)

    def test_csv_topology_map_and_regeneration_deterministic(self):
        with b.MATRIX.open(encoding='utf-8',newline='') as fp:rows=list(csv.DictReader(fp))
        self.assertEqual(len(rows),179) # 117 toplogies, with seven SB-other cases
        self.assertEqual(set(r['StaticRoute'] for r in rows),{'MULTILIMP_BB_POLICY'})
        before=[hashlib.sha256(p.read_bytes()).digest() for p in (b.PARENT,b.COMBINED,b.CAPTURE,b.HELPERS,b.MATRIX)]
        self.assertEqual(b.build(),(7,39,117))
        self.assertEqual(before,[hashlib.sha256(p.read_bytes()).digest() for p in (b.PARENT,b.COMBINED,b.CAPTURE,b.HELPERS,b.MATRIX)])

if __name__=='__main__':unittest.main()
