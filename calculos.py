from sympy import symbols, sympify, S, solveset, Eq, N, lambdify
from sympy.calculus.util import continuous_domain, function_range
from sympy import Interval, Union, FiniteSet, Pow, log

class FunctionAnalyzer:
    def __init__(self, expr_str, var_symbol='x'):
        expr_str = expr_str.replace('^', '**')
        self.var = symbols(var_symbol)
        self.expr = sympify(expr_str)

    def _find_denominator_roots(self):
        num, den = self.expr.as_numer_denom()
        if den == 1:
            return None, "No hay denominador."
        zeros = solveset(den, self.var, domain=S.Reals)
        return zeros, f"Denominador: {den}; raíces (excluir): {zeros}"

    def analyze(self):
        steps = []
        den_roots, den_desc = self._find_denominator_roots()
        steps.append(den_desc)

        domain = continuous_domain(self.expr, self.var, S.Reals)
        rnge = function_range(self.expr, self.var, domain)
        x_roots = solveset(Eq(self.expr, 0), self.var, domain)

        y0 = None
        if 0 in domain:
            y0 = N(self.expr.subs(self.var, 0))

        return {
            'domain': domain,
            'range': rnge,
            'x_intercepts': x_roots,
            'y_intercept': y0,
            'steps': "\n".join(steps)
        }

    def evaluate_at(self, x_value):
        x_expr = sympify(str(x_value))
        subs_expr = self.expr.subs(self.var, x_expr)
        numeric = N(subs_expr)
        ordered = (float(N(x_expr)), float(numeric))
        return {
            'x': x_expr,
            'subs_expr': subs_expr,
            'numeric': numeric,
            'ordered_pair': ordered
        }
