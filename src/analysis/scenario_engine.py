# -*- coding: utf-8 -*-
r"""A counterfactual scenario engine for environmentally extended MRIO.

Scenario results in this study were previously produced by scaling one term of
the deterministic footprint and reporting the difference. That is adequate for a
lever which acts on a single bottom-up item, and wrong for anything that changes
a production recipe: it cannot propagate an effect through the supply chain, it
cannot show burden shifting between impact categories, and levers cannot be
combined except by adding their separate answers, which double counts every
interaction between them.

This module implements the counterfactual formalism that the environmentally
extended input-output literature has converged on, so that scenario results in
this study are comparable with the published ones.

Formalism
---------
Following Aguilar-Hernandez et al. (2018, eqs. 1-3) and Donati et al. (2020,
eqs. 1, 5, 6), a scenario is a triple of edited objects
:math:`(\mathbf{B}^{*}, \mathbf{A}^{*}, \mathbf{y}^{*})` and its result is a
second full solution of the Leontief system:

.. math::

    \mathbf{r}   &= \mathbf{B}\,(\mathbf{I}-\mathbf{A})^{-1}\mathbf{y}
                    + \mathbf{d} + \mathbf{u} \\
    \mathbf{r}^{*} &= \mathbf{B}^{*}(\mathbf{I}-\mathbf{A}^{*})^{-1}\mathbf{y}^{*}
                    + \mathbf{d}^{*} + \mathbf{u}^{*} \\
    \Delta       &= \mathbf{r}^{*} - \mathbf{r}

where :math:`\mathbf{d}` is the direct (operational) vector of the Danish health
industry and :math:`\mathbf{u}` the bottom-up items that sit outside the MRIO.
The counterfactual is solved, never approximated: ``numpy.linalg.solve`` on
:math:`(\mathbf{I}-\mathbf{A}^{*})` takes about three seconds on this model, so
there is no reason to reuse a stale inverse.

Every edit carries an explicit **change coefficient**

.. math:: k_a = k_t \, k_p

after Donati et al. (2020, §2.4), where :math:`k_t` is the *technical* change
coefficient - what the intervention achieves where it is applied - and
:math:`k_p` the *market penetration* coefficient - the share of the affected
market that adopts it. Splitting the two is what makes an ambition level
auditable: a reader can accept the engineering evidence for :math:`k_t` and
still disagree about :math:`k_p`, and can see which is which. An edit is

.. math:: M^{*}_{ij} = M_{ij}\,(1 - k_a)

and a substitution between two entries, where a reduction in one input is taken
up by another, is

.. math:: M^{*}_{ij} = M_{ij} + \alpha\,(M^{*}_{mn} - M_{mn})

with :math:`\alpha` the substitution weighting factor.

Rebound
-------
Money not spent on one product does not vanish. Where a scenario reduces final
demand, the engine can hold total expenditure constant and redistribute the
released budget over the remaining demand in proportion to its existing shares -
the zero-cost counterfactual of Donati et al. (2020), after Takase et al. (2005)
as formalised by Aguilar-Hernandez et al. (2018, eq. 4):

.. math:: \mathbf{y}^{**} = \mathbf{y}^{*}\,
          \frac{\mathbf{i}'\mathbf{y}}{\mathbf{i}'\mathbf{y}^{*}}

This is a crude rebound - it assumes the released budget is spent on the same
basket - but reporting a demand-reduction scenario *without* it silently assumes
the money is destroyed, which is a stronger and less defensible assumption. Both
are reported.

What the engine does not claim
------------------------------
Editing :math:`\mathbf{A}` unbalances the accounts: column sums of the edited
table no longer equal total output, because nothing is assumed about what the
industry does with the money it stops spending on that input (Donati et al.,
2020, §2.3). The engine measures the imbalance and reports it per scenario
rather than hiding it. It is an attributional model throughout, so a scenario is
a *what-if on the recipe*, not a market response: no price effects, no capacity
constraints, no substitution the model was not told about.

References
----------
Aguilar-Hernandez, G. A., Sigüenza-Sanchez, C. P., Donati, F., Rodrigues,
J. F. D., & Tukker, A. (2018). Assessing circularity interventions: A review of
EEIOA-based studies. *Journal of Economic Structures*, 7, 14.
https://doi.org/10.1186/s40008-018-0113-3

Donati, F., Aguilar-Hernandez, G. A., Sigüenza-Sánchez, C. P., de Koning, A.,
Rodrigues, J. F. D., & Tukker, A. (2020). Modeling the circular economy in
environmentally extended input-output tables: Methods, software and case study.
*Resources, Conservation and Recycling*, 152, 104508.
https://doi.org/10.1016/j.resconrec.2019.104508

Wiebe, K. S., Bjelle, E. L., Többen, J., & Wood, R. (2018). Implementing
exogenous scenarios in a global MRIO model for the estimation of future
environmental footprints. *Journal of Economic Structures*, 7, 20.
https://doi.org/10.1186/s40008-018-0118-y
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Sequence

import numpy as np

Target = Literal["A", "B", "y", "bottom_up"]


@dataclass(frozen=True)
class Edit:
    """One change coefficient applied to one block of one model object.

    Parameters
    ----------
    target : {"A", "B", "y", "bottom_up"}
        Which object is edited. ``"A"`` is the technical coefficient matrix,
        ``"B"`` the impact intensity matrix, ``"y"`` the final-demand stimulus
        and ``"bottom_up"`` an item outside the MRIO.
    k_t : float
        Technical change coefficient: the fractional reduction the intervention
        achieves where it is applied. ``0.15`` means "uses 15 % less".
    k_p : float
        Market penetration coefficient: the share of the affected market that
        adopts it. ``k_a = k_t * k_p`` is the change actually applied.
    rows, cols : numpy.ndarray or slice, optional
        Selectors into the target. For ``"A"`` both apply; ``cols`` alone edits
        whole columns (a production recipe), ``rows`` alone whole rows (a
        product's deliveries). For ``"B"`` ``cols`` selects nodes and ``rows``
        selects indicator rows - omit ``rows`` to act on every indicator. For
        ``"y"`` only ``rows`` applies. For ``"bottom_up"`` ``key`` names the
        item.
    key : str, optional
        Bottom-up item name, when ``target="bottom_up"``.
    substitute_rows, substitute_cols : optional
        Where the released quantity reappears, if it does. With ``alpha`` this
        implements the substitution form of Donati et al. (2020, eq. 6).
    alpha : float
        Substitution weighting factor. ``1.0`` moves the whole released
        quantity; ``0.0`` (the default) means the input is simply not bought.
    source : str
        Evidence for ``k_t``. Required: an edit without a source is an opinion.
    penetration_basis : str
        Evidence or stated assumption for ``k_p``.
    """

    target: Target
    k_t: float
    k_p: float
    source: str
    penetration_basis: str
    rows: Any = None
    cols: Any = None
    key: str | None = None
    substitute_rows: Any = None
    substitute_cols: Any = None
    alpha: float = 0.0

    @property
    def k_a(self) -> float:
        """Applied change coefficient, ``k_t * k_p``."""
        return float(self.k_t) * float(self.k_p)

    def __post_init__(self) -> None:
        """Validate the coefficients and evidence fields after construction.

        Raises
        ------
        ValueError
            If ``k_t`` or ``k_p`` is not a fraction in ``[0, 1]``, or if
            ``source`` is empty (an edit without evidence is an opinion).
        """
        if not 0.0 <= self.k_t <= 1.0:
            raise ValueError(f"k_t must be a fraction in [0, 1], got {self.k_t}")
        if not 0.0 <= self.k_p <= 1.0:
            raise ValueError(f"k_p must be a fraction in [0, 1], got {self.k_p}")
        if not self.source:
            raise ValueError("every edit must name the evidence for k_t")


@dataclass
class Scenario:
    """A named counterfactual: a set of edits plus how to report it.

    Parameters
    ----------
    sid : str
        Short stable identifier, e.g. ``"P4"``. Used to group ambition levels of
        the same lever, so a figure can show one row per lever.
    name : str
        Human-readable label, without the identifier.
    kind : str
        ``"intervention"`` (a policy could cause it), ``"background pathway"``
        (it happens regardless of what the health system does),
        ``"counterfactual"`` (a demand trajectory, not a lever) or
        ``"combined"``.
    ambition : str
        The ambition level, as it should appear on a figure.
    edits : sequence of Edit
        What changes.
    rebound : bool
        Whether to hold total final expenditure constant (see module docstring).
    note : str
        What the scenario assumes and what it does not.
    """

    sid: str
    name: str
    kind: str
    ambition: str
    edits: Sequence[Edit] = field(default_factory=tuple)
    rebound: bool = False
    note: str = ""

    @property
    def label(self) -> str:
        """Identifier and name, as used in the output tables."""
        return f"{self.sid} {self.name}"


def _as_index(sel: Any, size: int) -> np.ndarray:
    """Normalise a selector into an integer index array."""
    if sel is None:
        return np.arange(size)
    arr = np.asarray(sel)
    if arr.dtype == bool:
        return np.flatnonzero(arr)
    return arr.reshape(-1)


def apply_edits(A: np.ndarray, B: np.ndarray, y: np.ndarray,
                edits: Sequence[Edit]) -> tuple[np.ndarray, np.ndarray,
                                                np.ndarray, dict[str, float]]:
    """Build the counterfactual objects for one scenario.

    Copies only the objects an edit actually touches - the technical
    coefficient matrix is 510 MB, so copying it for a scenario that only scales
    an intensity would triple the memory footprint for nothing.

    Parameters
    ----------
    A, B, y : numpy.ndarray
        Baseline technical coefficients, impact intensities and final demand.
    edits : sequence of Edit
        The scenario's edits. ``"bottom_up"`` edits are ignored here and handled
        by the caller, which holds those items.

    Returns
    -------
    A_alt, B_alt, y_alt : numpy.ndarray
        The counterfactual objects; the baseline object itself is returned
        where nothing touched it.
    released : dict
        ``{"y": amount}`` where a demand edit released expenditure, for the
        rebound step.
    """
    n = A.shape[0]
    A_alt, B_alt, y_alt = A, B, y
    released = {"y": 0.0}

    for e in edits:
        if e.target == "bottom_up":
            continue
        k = e.k_a
        if e.target == "A":
            if A_alt is A:
                A_alt = A.copy()
            r = _as_index(e.rows, n)
            c = _as_index(e.cols, n)
            block = A_alt[np.ix_(r, c)]
            removed = block * k
            A_alt[np.ix_(r, c)] = block - removed
            if e.alpha and e.substitute_rows is not None:
                sr = _as_index(e.substitute_rows, n)
                sc = _as_index(e.substitute_cols if e.substitute_cols is not None
                               else e.cols, n)
                # Spread the released input over the substitute rows in
                # proportion to their existing size, so a substitution cannot
                # invent a supply relation that does not already exist.
                take = removed.sum(axis=0) * e.alpha
                sub = A_alt[np.ix_(sr, sc)]
                w = sub.sum(axis=0)
                share = np.divide(sub, w, out=np.zeros_like(sub),
                                  where=w > 0)
                A_alt[np.ix_(sr, sc)] = sub + share * take
        elif e.target == "B":
            if B_alt is B:
                B_alt = B.copy()
            r = _as_index(e.rows, B.shape[0])
            c = _as_index(e.cols, n)
            B_alt[np.ix_(r, c)] *= (1.0 - k)
        elif e.target == "y":
            if y_alt is y:
                y_alt = y.copy()
            r = _as_index(e.rows, n)
            cut = y_alt[r] * k
            y_alt[r] -= cut
            released["y"] += float(cut.sum())
            if e.alpha and e.substitute_rows is not None:
                sr = _as_index(e.substitute_rows, n)
                w = y_alt[sr]
                tot = w.sum()
                if tot > 0:
                    y_alt[sr] += (w / tot) * cut.sum() * e.alpha
                    released["y"] -= float(cut.sum() * e.alpha)
        else:
            raise ValueError(f"unknown edit target {e.target!r}")
    return A_alt, B_alt, y_alt, released


def rebound_rescale(y_alt: np.ndarray, y_ref: np.ndarray,
                    edited: np.ndarray | None = None) -> np.ndarray:
    """Hold total final expenditure constant (Aguilar-Hernandez et al., 2018, eq. 4).

    Parameters
    ----------
    y_alt : numpy.ndarray
        Counterfactual final demand, already edited.
    y_ref : numpy.ndarray
        Baseline final demand.
    edited : numpy.ndarray, optional
        Positions the scenario reduced. The released budget is spread over the
        remaining positions only. Aguilar-Hernandez et al. (2018) distribute it
        "proportionally to the rest of goods" and Wood et al. (2017, eq. 9) over
        "all products unaffected by the intervention"; rescaling the reduced
        rows as well would give part of the cut straight back.

    Returns
    -------
    numpy.ndarray
        ``y_alt`` with the released budget redistributed, so its total equals
        the baseline total. Returns the input unchanged when the scenario did
        not reduce spending.
    """
    tot_ref, tot_alt = float(y_ref.sum()), float(y_alt.sum())
    if tot_alt <= 0 or tot_alt >= tot_ref:
        return y_alt

    released = tot_ref - tot_alt
    untouched = np.asarray(y_alt).astype(float).copy()
    if edited is not None:
        mask = np.zeros(untouched.shape, dtype=bool)
        mask[np.asarray(edited, dtype=int)] = True
        untouched[mask] = 0.0
    base = float(untouched.sum())
    if base <= 0:                      # everything was edited; nothing to absorb
        return y_alt
    return np.asarray(y_alt).astype(float) + untouched * (released / base)


def solve(A: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Total output driven by ``y``, solving rather than inverting.

    Parameters
    ----------
    A : numpy.ndarray
        Technical coefficient matrix.
    y : numpy.ndarray
        Final-demand vector.

    Returns
    -------
    numpy.ndarray
        ``x = (I - A)^-1 y``, obtained by LU factorisation. On this model the
        result agrees with the stored Leontief inverse to 1e-11.
    """
    n = A.shape[0]
    M = -A.astype(np.float64, copy=True)
    M.flat[::n + 1] += 1.0
    x = np.linalg.solve(M, y)
    del M
    return x


def column_imbalance(A_alt: np.ndarray, A: np.ndarray,
                     x: np.ndarray) -> float:
    """Value of inputs no longer purchased, as a share of total output.

    Editing ``A`` breaks the accounting identity that column sums plus value
    added equal total output, because the model is not told what the industry
    does with the money it stops spending (Donati et al., 2020, §2.3). This
    quantifies how far the counterfactual departs from balance so that the
    departure is reported rather than assumed away.

    Parameters
    ----------
    A_alt, A : numpy.ndarray
        Counterfactual and baseline coefficient matrices.
    x : numpy.ndarray
        Counterfactual total output.

    Returns
    -------
    float
        Unbalanced value as a percentage of the output driven by health-care
        final demand. Zero when ``A`` was not edited.

    Notes
    -----
    The absolute value is taken **per column**, before summing. Taking it after
    the inner product would let a column that gained inputs cancel one that lost
    them, and report a balanced table where two equal and opposite departures
    sit side by side. Every scenario in the present set edits in one direction,
    so the two forms agree today; a substitution with a negative weighting
    factor, which Donati et al. (2020, §4) use, would separate them.

    ``x`` is the output driven by health-care final demand, not economy-wide
    output, because that is what the counterfactual is solved for. The share is
    labelled accordingly wherever it is reported.
    """
    if A_alt is A:
        return 0.0
    per_column = np.abs((A - A_alt).sum(axis=0) * np.asarray(x).reshape(-1))
    total = float(np.asarray(x).sum())
    return 100.0 * float(per_column.sum()) / total if total else 0.0
