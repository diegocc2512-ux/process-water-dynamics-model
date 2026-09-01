# Model equations and implementation notes

## 1. Temperature response

The public example uses the sub-optimal Ratkowsky square-root relationship:

\[
\sqrt{\mu}=b(T-T_{min})
\]

therefore

\[
\mu=[b(T-T_{min})]^2
\]

The implementation returns zero outside the configured temperature bounds. This is a modelling convenience, not a complete full-temperature cardinal model.

## 2. Environmental modifiers

A simple piecewise pH factor is used:

\[
\gamma_{pH}=
\frac{pH-pH_{min}}{pH_{opt}-pH_{min}}
\]

between the configured minimum and optimum, with values clamped to 0–1.

Water activity is treated similarly:

\[
\gamma_{aw}=
\frac{a_w-a_{w,min}}{1-a_{w,min}}
\]

The effective growth rate is:

\[
\mu_{eff}
=
\mu\gamma_{pH}\gamma_{aw}M_{growth}-d
\]

## 3. Logistic population growth

\[
N_{t+\Delta t}
=
\frac{K N_t e^{\mu_{eff}\Delta t}}
{K+N_t(e^{\mu_{eff}\Delta t}-1)}
\]

where `K` is the carrying capacity.

## 4. Disinfectant inactivation

A simplified CT-style relationship is implemented:

\[
LR=k_{CT}C\Delta t f_{pH}f_Tf_O
\]

with:

\[
f_{pH}=e^{-s(pH-pH_{ref})}
\]

\[
f_T=Q_{10}^{(T-T_{ref})/10}
\]

\[
f_O=\frac{1}{1+O\alpha}
\]

Microbial concentration after this step is:

\[
N_{after}=N_{before}10^{-LR}
\]

This is a screening abstraction. Real disinfectant efficacy may be non-linear and organism/matrix dependent.

## 5. Contamination loading

A configured microbial load per cycle is added and converted to concentration using the system water volume:

\[
\Delta N=\frac{L}{1000V}
\]

for `L` CFU added per cycle and `V` litres.

## 6. CSTR-style water replacement

For balanced inlet and outlet flow in a well-mixed constant-volume system:

\[
f=1-e^{-(Q/V)\Delta t}
\]

and:

\[
N_{new}=(1-f)N+fN_{replacement}
\]

## 7. Residual decay

\[
C_{t+\Delta t}=C_te^{-k\Delta t}-D\Delta t
\]

where:

- `k` = first-order decay coefficient
- `D` = empirical demand-loss term

The model records the **pre-redose residual** before applying control logic.

## 8. Redosing

If:

\[
C_{pre-redose}\le C_{trigger}
\]

the model sets the post-control residual to the configured target.

This deliberately records both values so a low transient residual cannot be hidden by the redose action.

## Modelling boundaries

The current public model does not include spatial gradients, biofilms, explicit chemical mass dosing, sensor dynamics, dosing delays, unequal-flow volume changes, stochastic microbial variation or parameter-estimation routines.
