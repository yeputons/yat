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
    from yat.static_analyzer import NoReturnValueCheckVisitor
    visit = NoReturnValueCheckVisitor().visit
    def visit_wrapped(tree):
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        visit(tree)
        result = set(sys.stdout.getvalue().splitlines())
        sys.stdout = old_stdout
        return result
    return visit_wrapped


@pytest.fixture
def nrcv_good(nrcv):
    def visit_wrapped(tree):
        res = nrcv(FunctionDefinition("foo", Function([], [tree])))
        assert res == set() or res == set(["foo"])
        return "foo" not in res
    return visit_wrapped


class TestNoReturnValueCheckVisitor:
    def test_smoke(self, nrcv):
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

    class TestNumber:
        def test_good(self, nrcv_good):
            assert nrcv_good(Number(1))

    class TestFunction:
        def test_good(self, nrcv):
            prog = FunctionDefinition("foo", Function([], [Number(10)]))
            assert nrcv(prog) == set()

        def test_good_with_args(self, nrcv):
            prog = FunctionDefinition("foo", Function(["arg"], [Number(10)]))
            assert nrcv(prog) == set()

        def test_bad_empty(self, nrcv):
            prog = FunctionDefinition("foo", Function([], []))
            assert nrcv(prog) == set(["foo"])

        def test_bad_with_args(self, nrcv):
            prog = FunctionDefinition("foo", Function(["arg"], []))
            assert nrcv(prog) == set(["foo"])

        def test_bad_not_last(self, nrcv):
            prog = FunctionDefinition("foo", Function(["arg"], [
                Conditional(Number(0), [], []),
                Number(1)
            ]))
            assert nrcv(prog) == set()

        def test_definition_containing_good(self, nrcv_good):
            assert nrcv_good(FunctionDefinition("foo", Function([], [Number(10)])))

        def test_definition_containing_bad(self, nrcv_good):
            assert not nrcv_good(FunctionDefinition("foo", Function([], [])))

        def test_embedded(self, nrcv):
            prog = FunctionDefinition("foo1", Function([], [
                FunctionDefinition("foo2", Function([], [
                    FunctionDefinition("foo3", Function([], [])),
                ])),
                FunctionDefinition("foo4", Function([], [
                    FunctionDefinition("foo5", Function([], [])),
                    Conditional(Number(0), [], [])
                ])),
                FunctionDefinition("foo6", Function([], []))
            ]))
            assert nrcv(prog) == set(["foo3", "foo4", "foo5", "foo6"])

    class TestConditional:
        def test_none(self, nrcv_good):
            assert not nrcv_good(Conditional(Number(0), None, None))

        def test_empty(self, nrcv_good):
            assert not nrcv_good(Conditional(Number(0), [], []))

        def test_empty_false(self, nrcv_good):
            assert not nrcv_good(Conditional(Number(0), [Number(1)], []))

        def test_none_false(self, nrcv_good):
            assert not nrcv_good(Conditional(Number(0), [Number(1)], None))

        def test_empty_true(self, nrcv_good):
            assert not nrcv_good(Conditional(Number(0), [], [Number(1)]))

        def test_none_true(self, nrcv_good):
            assert not nrcv_good(Conditional(Number(0), None, [Number(1)]))

        def test_non_empty(self, nrcv_good):
            assert nrcv_good(Conditional(Number(0), [Number(1)], [Number(2)]))

        def test_bad_true(self, nrcv_good):
            bad = Conditional(Number(0), [], [])
            assert not nrcv_good(Conditional(Number(0), [bad], [Number(2)]))

        def test_bad_false(self, nrcv_good):
            bad = Conditional(Number(0), [], [])
            assert not nrcv_good(Conditional(Number(0), [Number(1)], [bad]))

        def test_bad_not_last(self, nrcv_good):
            bad = Conditional(Number(0), [], [])
            assert nrcv_good(Conditional(Number(0), [bad, Number(1)], [bad, Number(2)]))

        def test_embedded(self, nrcv):
            prog = Conditional(Number(0), [
                Conditional(Number(0), [], []),
                FunctionDefinition("foo1", Function([], [])),
                FunctionDefinition("foo2", Function([], [Number(1)])),
                Number(2),
            ], [
                Conditional(Number(0), [], []),
                FunctionDefinition("foo3", Function([], [])),
                FunctionDefinition("foo4", Function([], [Number(3)])),
                Number(4),
            ])
            assert nrcv(prog) == set(["foo1", "foo3"])

        def test_embedded_in_bad_if(self, nrcv):
            prog = Conditional(Number(0), [
                FunctionDefinition("foo1", Function([], [])),
                FunctionDefinition("foo2", Function([], [Number(1)])),
                Conditional(Number(0), [], [])
            ], [
                FunctionDefinition("foo3", Function([], [])),
                FunctionDefinition("foo4", Function([], [Number(3)])),
                Conditional(Number(0), [], [])
            ])
            assert nrcv(prog) == set(["foo1", "foo3"])

    class TestPrint:
        def test_good(self, nrcv_good):
            assert nrcv_good(Print(Number(10)))

        def test_bad_with_cond(self, nrcv_good):
            assert not nrcv_good(Print(Conditional(Number(0), [], [])))

    class TestRead:
        def test_good(self, nrcv_good):
            assert nrcv_good(Read("foo"))

    class TestFunctionCall:
        def test_good(self, nrcv_good):
            assert nrcv_good(FunctionCall(Reference("hello"), [Number(1), Number(2), Number(3)]))

        def test_bad_with_cond(self, nrcv_good):
            assert not nrcv_good(FunctionCall(Reference("hello"), [Number(1), Conditional(Number(0), [], []), Number(3)]))

        def test_embed(self, nrcv):
            bad = Conditional(Number(0), [], [])
            def func_def(name):
                return FunctionDefinition(name, Function([], []))
            prog = FunctionCall(bad, [Number(1), func_def("foo1"), Number(2), func_def("foo2"), Number(3)])
            assert nrcv(prog) == set(["foo1", "foo2"])

    class TestReference:
        def test_good(self, nrcv_good):
            assert nrcv_good(Reference("foo"))

    class TestBinaryOperation:
        def test_good(self, nrcv_good):
            assert nrcv_good(BinaryOperation(Number(1), "+", Number(2)))

        def test_bad_lhs_with_cond(self, nrcv_good):
            assert not nrcv_good(BinaryOperation(Conditional(Number(0), [], []), "+", Number(2)))

        def test_bad_rhs_with_cond(self, nrcv_good):
            assert not nrcv_good(BinaryOperation(Number(1), "+", Conditional(Number(0), [], [])))

        def test_bad_both_with_cond(self, nrcv_good):
            assert not nrcv_good(BinaryOperation(Conditional(Number(0), [], []), "+", Conditional(Number(0), [], [])))

        def test_embedded(self, nrcv):
            def func_def(name):
                return FunctionDefinition(name, Function([], []))
            prog = BinaryOperation(func_def("foo1"), "+", func_def("foo2"))
            assert nrcv(prog) == set(["foo1", "foo2"])

        def test_embedded_and_bad_lhs(self, nrcv):
            bad = Conditional(Number(0), [], [])
            def func_def(name):
                return FunctionDefinition(name, Function([], []))
            prog = BinaryOperation(bad, "+", func_def("foo2"))
            assert nrcv(prog) == set(["foo2"])

        def test_embedded_and_bad_rhs(self, nrcv):
            bad = Conditional(Number(0), [], [])
            def func_def(name):
                return FunctionDefinition(name, Function([], []))
            prog = BinaryOperation(func_def("foo1"), "+", bad)
            assert nrcv(prog) == set(["foo1"])

    class TestUnaryOperation:
        def test_good(self, nrcv_good):
            assert nrcv_good(UnaryOperation("-", Number(1)))

        def test_bad_expr_with_cond(self, nrcv_good):
            assert not nrcv_good(UnaryOperation("-", Conditional(Number(0), [], [])))

if __name__ == "__main__":
    pytest.main([sys.argv[0]])
