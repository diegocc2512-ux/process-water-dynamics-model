# Validation and calibration strategy

The public repository is designed as a model-development example. In an industrial project, the simulation should be converted from a screening model into validation support through measured data.

## 1. Hydraulic characterisation

Measure or verify:

- usable water volume
- retained volume after drainage
- make-up flow
- discharge flow
- recirculation flow
- turnover time
- dead legs and poorly mixed regions
- drain, refill and flushing sequences

## 2. Disinfectant characterisation

Collect time-series residual measurements under:

- freshly prepared water
- normal production load
- high organic load
- idle / standstill
- restart
- end-of-run conditions

Record pH and temperature with each measurement.

## 3. Microbiological characterisation

Collect baseline and time-series samples at locations relevant to the process question. The sampling design should distinguish incoming water, process water, worst hydraulic points and restart conditions.

## 4. Parameter fitting

Estimate:

- first-order residual decay coefficient
- empirical demand term
- contamination input
- relevant microbial kinetic parameters

Retain raw data, fitting method, confidence intervals and goodness-of-fit statistics.

## 5. Model challenge

Compare predictions against independent commissioning or challenge-test datasets that were not used for parameter fitting.

## 6. Uncertainty and sensitivity

Quantify the effect of uncertainty in at least:

- water volume
- flow
- temperature
- contamination input
- disinfectant decay
- microbial kinetic parameters
- sensor measurement error

## 7. Decision criteria

Only after validation should the organisation consider defining operating rules such as maximum water age, minimum disinfectant residual, maximum idle time, flush requirements or restart conditions.

The final limits should remain subject to HACCP review, regulatory requirements, supplier instructions and QA approval.
