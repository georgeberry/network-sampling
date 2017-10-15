# network-sampling

## Some coding conventions

* Use python 3
* Write lots of little functions
* Use NetworkX for graph
* Use numpy tools where available
* Update this README regularly

## Analyses
1. Visibility accuracy
1. Majority group size accuracy
1. Cross link proportion accuracy
1. Homophily accuracy

## Paremeters
1. Without classifier error
1. With classifier error
1. As the sample gets bigger

## Networks
1. Simulated parameter space
1. Pokec
1. Sexual

## Sampling methods
1. Edge
1. Node
1. Snowball
1. RDS

## Summary

This gives 3 parmeters, 3 network types, and 4 sampling methods for a total of 45 analyses

This is too many

We are going to do the full gamut for the 4 sampling methods on the simulated parameter space.

What will these plots look like?

## Types of plots to make
1. Accuracy at sampling fraction for simulated graphs, 4 sampling methods, with and without correction for classifier error
1. Bias for a fixed sampling size (1000 nodes)
1. Compare RDS to ideal variance given by node or edge sampling for the given task
1. Comparison with and without correction for classifier error
1. Ratio between error & variance for no-clf-error with the corrected version
1. f(err) for homophily as we increase misclassification probability
1. do an actual two-sample where use a node and edge sample within to get an ideal lower bound of variance
