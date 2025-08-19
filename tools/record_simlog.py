from __future__ import annotations
import json
from typing import TextIO


class SimLogRecorder:
    """
    Subscribe to your SimRunner log stream (pull-based) and write JSONL.
    Usage:
        rec = SimLogRecorder(open("artifacts/run.jsonl","w"))
        ... after your session:
        rec.dump(gs.sim_runner.get_log())
    """
    def __init__(self, fp: TextIO):
        self.fp = fp

    def dump(self, log: list[dict]) -> None:
        for entry in log:
            self.fp.write(json.dumps(entry) + "\n")
        self.fp.flush()


def dump_simlog(gs, fp: TextIO) -> None:
    """
    Writes your SimRunner log to JSONL using gs.sim_runner.get_log() -> List[Dict].
    """
    sim = getattr(gs, "sim_runner", None)
    if not sim or not hasattr(sim, "get_log"):
        return
    for entry in sim.get_log():  # List[Dict]
        fp.write(json.dumps(entry) + "\n")
    fp.flush()
