import pytest
import io
import sys
from yat.model import Number, Function, FunctionDefinition, Conditional, Print, Read, FunctionCall, Reference, BinaryOperation, UnaryOperation

@pytest.fixture
def pcv():
    from yat.static_analyzer import PureCheckVisitor
    return PureCheckVisitor().visit

class TestPureCheckVisitor:
    def test_smoke1(self, pcv):
        prog1 = Conditional(BinaryOperation(Number(4), "=", Number(5)), [
            Number(123),
        ], [
            Number(456),
        ])
        assert pcv(prog1) == True

    def test_smoke2(self, pcv):
        prog2 = Conditional(BinaryOperation(Number(4), "=", Number(5)), [
            Print(Number(123)),
        ], [
            Number(456),
        ])
        assert pcv(prog2) == False

    def test_numver(self, pcv):
        assert pcv(Number(10)) == True

    def test_function_empty(self, pcv):
        assert pcv(Function([], [])) == True

    def test_function_pure_non_empty(self, pcv):
        assert pcv(Function([], [Number(10), Number(20)])) == True

    def test_function_unpure(self, pcv):
        assert pcv(Function([], [Number(10), Print(Number(5)), Number(20)])) == False

    def test_function_definition(self, pcv):
        assert pcv(FunctionDefinition("name", Function([], [Number(5)]))) == True

    def test_conditional_empty(self, pcv):
        assert pcv(Conditional(Number(0), [], [])) == True

    def test_conditional_none(self, pcv):
        assert pcv(Conditional(Number(0), None, None)) == True

    def test_conditional_non_empty(self, pcv):
        assert pcv(Conditional(Number(0), [Number(10), Number(20)], [Number(30), Number(40)])) == True

    def test_conditional_unpure_true_non_empty(self, pcv):
        assert pcv(Conditional(Number(0), [Number(10), Print(Number(0)), Number(20)], [Number(30), Number(40)])) == False

    def test_conditional_unpure_true_empty(self, pcv):
        assert pcv(Conditional(Number(0), [Number(10), Print(Number(0)), Number(20)], [])) == False

    def test_conditional_unpure_false_non_empty(self, pcv):
        assert pcv(Conditional(Number(0), [Number(10), Number(20)], [Number(30), Print(Number(0)), Number(40)])) == False

    def test_conditional_unpure_false_empty(self, pcv):
        assert pcv(Conditional(Number(0), [], [Number(30), Print(Number(0)), Number(40)])) == False

    def test_conditional_unpure_cond_non_empty(self, pcv):
        assert pcv(Conditional(Print(Number(0)), [Number(10), Number(20)], [Number(30), Number(0), Number(40)])) == False

    def test_conditional_unpure_cond_empty(self, pcv):
        assert pcv(Conditional(Print(Number(0)), [], [])) == False

    def test_print(self, pcv):
        assert pcv(Print(Number(10))) == False

    def test_read(self, pcv):
        assert pcv(Read("foo")) == False

    def test_function_call_no_args(self, pcv):
        assert pcv(FunctionCall(Reference("foo"), [])) == True

    def test_function_call_pure_args(self, pcv):
        assert pcv(FunctionCall(Reference("foo"), [Number(10), Number(20)])) == True

    def test_function_call_unpure_args(self, pcv):
        assert pcv(FunctionCall(Reference("foo"), [Number(10), Print(Number(0)), Number(20)])) == False

    def test_function_call_unpure_expr(self, pcv):
        cond = Conditional(Number(1), [Print(Number(1)), Reference("foo")])
        assert pcv(FunctionCall(cond, [])) == False

    def test_reference(self, pcv):
        return pcv(Reference("foo")) == True

    def test_binary_operation_pure(self, pcv):
        return pcv(BinaryOperation(Number(10), "+", Number(20))) == True

    def test_binary_operation_unpure_lhs(self, pcv):
        return pcv(BinaryOperation(Print(Number(10)), "+", Number(20))) == False

    def test_binary_operation_unpure_rhs(self, pcv):
        return pcv(BinaryOperation(Number(10), "+", Print(Number(20)))) == False

    def test_unary_operation_pure(self, pcv):
        return pcv(UnaryOperation("-", Number(10))) == True

    def test_unary_operation_unpure(self, pcv):
        return pcv(UnaryOperation("-", Print(Number(10)))) == True

@pytest.fixture
def nrcv():
    from yat.static_analyzer import NoReturnCheckVisitor
    visit = NoReturnCheckVisitor().visit
    def visit_wrapped(tree):
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        visit(tree)
        result = set(sys.stdout.getvalue().splitlines())
        sys.stdout = old_stdout
        return result
    return visit_wrapped

class TestNoReturnCheckVisitor:
    def test_smoke(self, monkeypatch, nrcv):
        prog = (
            Conditional(Number(1), [
                FunctionDefinition("foo", Function([], [
                    Number(123),
                    Conditional(Number(1), [
                        Number(2),
                    ])
                ])),
                FunctionDefinition("bar", Function([], [
                    Number(123)
                ])),
                FunctionDefinition("baz", Function([], [
                ])),
                FunctionDefinition("foobar", Function([], [
                    Conditional(Number(1), [
                        Number(2),
                    ]),
                    Number(123)
                ])),
            ])
        )
        assert nrcv(prog) == set(["foo", "baz"])

if __name__ == "__main__":
    pytest.main([sys.argv[0]])
