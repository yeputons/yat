#!/usr/bin/env python3

import io
import os
import sys
from yat.parser import Parser, Scanner
from yat.printer import PrettyPrinter
from yat.folder import ConstantFolder


def program_to_str(program):
    stdout_ = sys.stdout
    capture = io.StringIO()
    sys.stdout = capture
    try:
        PrettyPrinter().visit(program)
    finally:
        sys.stdout = stdout_
    return capture.getvalue()


def do_test(inp_filename):
    ans_filename = os.path.splitext(filename)[0] + ".ans"
    inputs = Parser().parse(Scanner(inp_filename), wrap=False)
    answers = Parser().parse(Scanner(ans_filename), wrap=False)
    assert len(inputs) == len(answers)
    for inp, ans in zip(inputs, answers):
        out_str = program_to_str(ConstantFolder().visit(inp))
        ans_str = program_to_str(ans)
        out_str_stripped = out_str.replace("(", "").replace(")", "")
        ans_str_stripped = ans_str.replace("(", "").replace(")", "")
        assert out_str_stripped == ans_str_stripped
        if out_str != ans_str:
            print("Expected:\n" + ans_str)
            print("Found:\n" + out_str)
            assert input("Is it ok (y/n)?") == "y"


if __name__ == "__main__":
    import glob
    import traceback
    for filename in sorted(glob.glob("tests/fold/*.y")):
        try:
            do_test(filename)
        except Exception as err:
            print("test {} failed with error:".format(filename))
            traceback.print_exc()
