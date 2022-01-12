from typing import Iterable, Mapping
import numpy as np
import importlib

from cocotb.triggers import RisingEdge as RE, FallingEdge as FE, Timer
from cocotb.handle import SimHandleBase

cocotb_coverage = importlib.import_module('cocotb-coverage.cocotb_coverage.coverage')
coverage_db = cocotb_coverage.coverage_db

from cocotb_util.cocotb_util import assign_probe_str, assign_probe_int
from cocotb_util.cocotb_driver import BusDriver
from cocotb_util.cocotb_monitor import BusMonitor
from cocotb_util.cocotb_agent import BusAgent
from cocotb_util.cocotb_scoreboard import Scoreboard
from cocotb_util.cocotb_transaction import Transaction
from cocotb_util.cocotb_coverage import CoverPoint, CoverCross
from cocotb_util.cocotb_coverage_processor import CoverProcessor
from cocotb_util.cocotb_testbench import TestBench


class TemplateDriver(BusDriver):
    def __init__(
        self,
        entity: SimHandleBase,
        signals: Iterable[str] = [],
        probes: Mapping[str, SimHandleBase] = None,
    ):

        signals = {sig: f'{sig.upper()}' for sig in signals}
        super().__init__(
            entity,
            signals=signals,
            probes=probes)

    def check_trx(self, trx: Transaction):
        """Check applied trx consistency. Will be called before Trx sending"""
        error_msg = f'Wrong trx: {trx}!!!'
        assert isinstance(trx, Transaction), error_msg

    async def driver_send(self, trx: Transaction):
        """Send Trx"""
        await Timer(20, units='ns')
        self.log.info(f"Sending {repr(trx)}")

class TemplateMonitor(BusMonitor):

    def __init__(
        self,
        entity: SimHandleBase,
        signals: Iterable[str],
        probes: Mapping[str, SimHandleBase] = None,
    ):
        signals = {sig: f'{sig.upper()}' for sig in signals}
        super().__init__(
            entity,
            signals=signals,
            probes=probes)

    async def receive(self):
        """Receive Trx"""
        await Timer(200, units='ns')
        foo = None
        self.log.info(f"Monitor received: {foo}")
        return foo


class TemplateAgent(BusAgent):

    def __init__(
        self,
        entity: SimHandleBase = None,
        name: str = None,
        driver: str = 'on',
        monitor: str = 'on',
    ):
        super().__init__()

        self.signals = ['i_reset_n']

        self.add_driver(
            TemplateDriver(
                entity,
                signals=self.signals) if driver.lower() == 'on' else None
        )

        self.add_monitor(
            TemplateMonitor(
                entity,
                signals=self.signals) if monitor.lower() == 'on' else None
        )

class TemplateTrx(Transaction):

    def __init__(self, *args):
        items = ['foo', 'bar_range', 'bar']
        super().__init__(items)

        self.foo = 0
        self.bar_range = 'min'
        self.add_rand('foo', [0, 1])

        self.bar_range_weights = {'min': 1, 'mid': 2, 'max': 1}
        self.add_rand('bar_range', list(self.bar_range_weights.keys()))

        # hard constr
        def foo_cstr(foo):
            return foo in [0, 1]

        # soft constr
        def bar_cstr(bar_range):
            return self.bar_range_weights[bar_range]

        self.add_constraint(foo_cstr)
        self.add_constraint(bar_cstr)
        self.solve_order('foo', 'bar_range')

    def post_randomize(self):
        """"""
        self.bar = {'min': np.random.randint(0, 10), 'mid': np.random.randint(40, 60), 'max': np.random.randint(90, 100)}[self.bar_range]
        self.log.debug(repr(self))


class TemplateCoverProcessor(CoverProcessor):
    def __init__(self, **kwargs):

        coverage_report_cfg = {
            'status': {
                'top.foo': ['new_hits'],
                'top.bar': ['cover_percentage', 'new_hits']
            },
            'final': {'bins': True}
        }

        super().__init__(report_cfg=coverage_report_cfg)

    def define(self):
        self.log.info('Define coverage')

        def rel_qux(trx, bin):
            if bin == 'min':
                return trx.bar in [0, 10]
            elif bin == 'mid':
                return trx.bar in [40, 60]
            elif bin == 'max':
                return trx.bar in [90, 100]
            else:
                return False

        self.add_cover_items(
            CoverPoint(
                "top.foo",
                xf=lambda trx: trx.foo,
                bins=[0, 1]
            ),

            CoverPoint(
                "top.bar",
                xf=lambda trx: trx,
                bins=['min', 'max', 'mid'],
                rel=rel_qux,
                inj=False
            ),

            CoverCross(
                name="top.foo_bar_cross",
                items=["top.foo", "top.bar"],
                ign_bins=[],
            )
        )

class TemplateTestBench(TestBench):

    def __init__(
        self,
        dut: SimHandleBase
    ):

        super().__init__()
        self.dut = dut

        self.agent = TemplateAgent(
            dut.template_dut,
            driver='on',
            monitor='on'
        )
        self.agent.driver.probes = {'fooo': dut.probes.fooo}
        self.agent.monitor.probes = {'barr': dut.probes.barr}
        self.agent.monitor.add_callback(self.do_smth)

        self.scoreboard = Scoreboard(dut.template_dut, fail_immediately=True)
        self.scoreboard.add_interface(
            self.agent.monitor,
            self.agent.monitor.expected,
            compare_fn=None,
            x_fn=lambda trx: None,
            strict_type=True)

        self.coverage = TemplateCoverProcessor()

        self.max_runs = 2

    def do_smth(self, got):
        """Do smth"""
        self.log.debug('Do smth')

    def init(self):
        """ Init smth"""
        self.log.debug('Init smth')

    def stop(self):
        """Stop testing when test goal achieved."""
        return (self.runs >= self.max_runs
            or coverage_db['top.foo_bar_cross'].cover_percentage == 100)

    async def run(self):
        """Send transactions. Store expected responses."""
        for trx in self.sequencer(TemplateTrx, self.stop):
            self.log.info(trx)
            self.agent.monitor.add_expected(trx)

            await self.agent.driver.send(trx)
            self.coverage.collect(trx)

        await Timer(400, units='ns')


if __name__ == "__main__":
    cfg = {}
    foo = TemplateTrx(cfg)

    for _ in range(100):
        foo.randomize()
