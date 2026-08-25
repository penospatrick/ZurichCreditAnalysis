# Updated 2023-10-16


from scipy.optimize import minimize_scalar


class LoanUnending(Exception):
    pass

class Loan:
    'Solver for a single missing loan parameter.'
    def __init__(self, principal=None, interest=None, term=None, amort=None):
        if sum(1 for _ in (principal, interest, term, amort) if _ is None) > 1:
            raise ValueError('At most 1 loan parameter should be unspecified.')
        self.principal = principal
        self.interest = interest
        self.term = term
        self.amort = amort
        self.solve()
    
    def __repr__(self):
        rep_str = (
            f'Loan(principal={self.principal}'
            f', interest={self.interest}'
            f', term={self.term}'
            f', amort={self.amort})'
        )
        return rep_str

    def solve(self):
        if self.amort is None:
            self.unknown = 'amort'
            self._solve_amort()
        elif self.interest is None:
            self.unknown = 'interest'
            self._solve_interest()
        elif self.term is None:
            self.unknown = 'term'
            self._solve_term()
        elif self.principal is None:
            self.unknown = 'principal'
            self._solve_principal()

    def _simulate_loan(self):
        balance = self.principal
        term = 0
        # Accounting for rounding errors
        lower_bound = 0.01 * self.principal
        while balance > lower_bound:
            interest_due = self.interest * balance
            principal_due = min(self.amort - interest_due, balance)
            balance -= principal_due
            term += 1
        return term

    def _solve_term(self):
        if self.amort <= self.principal * self.interest:
            raise LoanUnending('Interest exceeds amortization.')
        self.term = self._simulate_loan()

    @staticmethod
    def amort_calculator(principal, interest, term):
        compounded = (1 + interest)**term
        return principal * interest * compounded / (compounded - 1)

    def _solve_amort(self):
        self.amort = self.amort_calculator(
            self.principal, self.interest, self.term
        )

    def _solve_principal(self):
        # Inverse of the amortization calculator
        self.principal = 1 / self.amort_calculator(
            1/self.amort, self.interest, self.term
        )

    def _solve_interest(self):
        if self.principal > self.amort * self.term:
            raise LoanUnending('Interest exceeds amortization.')
        solution = minimize_scalar(
            lambda interest: (
                (
                    self.amort_calculator(self.principal, interest, self.term) 
                    - self.amort
                )
                ** 2
            ),
            bounds=(0, 1), 
            method='bounded'
        )
        assert solution.success, 'No interest rate found.'
        self.interest = solution.x