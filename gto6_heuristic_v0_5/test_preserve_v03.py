"""Regression gate: baseline v0.3 files must not silently change in v0.4.

This intentionally locks byte hashes. Future justified edits must explicitly
update this gate and the cumulative README/changelog, never replace the baseline.
"""
import hashlib
from pathlib import Path
import unittest

EXPECTED={
 'rfi_reference.py':'2de98eff7b1fa9b650f31d142d3a94cca01221269c918af5c211c15a661e5ab2',
 'vs_open_reference.py':'4c2801bf4d1ba19cfe6be11e68ca34d07f7bec9721fbb206e3e88e5aff1efa15',
 'action_ledger.py':'e98b0b60bdcde517db11ea10e2c43c50b40ee03dee4814fac96e9e3d90bcde38',
 'scenario_contract.py':'cad33818d7559b0322029f0b2a02c2643b9fd2c9b609f05e4236d76944fa2e51',
 'strict_observation.py':'3ab851b18ff78f2a720107b8fccba60f96ca09c26b9b4b2f73689ccae17e6e6f',
 'vs_open_bridge.py':'9982d34dfb61779df5ffba21f39822af430b07988d47225bb1dea0f1e88566a0',
 'RFI_100BB_169x5_DRAFT.csv':'b06d1e675a9b84adecab15c4f657908d889e7563f2a7ed99388e676b74ceba8b',
 'VS_OPEN_100BB_15x169_DRAFT.csv':'1f259ad51f6ab56dd8d53fc8add28f32120e8fadb23d59e497c2bc4755fd676c',
}
class BaselinePreservation(unittest.TestCase):
    def test_v03_files_byte_identical(self):
        root=Path(__file__).parent
        for name,digest in EXPECTED.items():
            with self.subTest(file=name):
                self.assertEqual(hashlib.sha256((root/name).read_bytes()).hexdigest(),digest)
