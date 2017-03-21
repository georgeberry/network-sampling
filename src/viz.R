library(ggplot2)
library(dplyr)
library(data.table)

df = fread("~/Drive/project-RA/network-sampling/sim_output/output.csv") %>%
  select(
    g_idx,
    samp_idx,
    homophily_a,
    maj_size,
    filter_fn,
    filter_fn_args,
    samp_fn,
    aa,
    ab,
    ba,
    bb) %>%
  mutate(
    tot = aa + ab + ba + bb, #sum
    cg = ab + ba, # cg = crossgroup
    wg = aa + bb) %>% # wg = within_group
  mutate( # normalize
    aa = aa / tot,
    ab = ab / tot,
    ba = ba / tot,
    bb = bb / tot,
    cg = cg / tot,
    wg = wg / tot
  )

#### Homophily by variance plots ###############################################

# Analysis plan: compare each sim run (100) with the true mean for the run
# Plot MSE and the variance of MSE
# Aggregate within each run
# Idea is that a "sample" is one graph with 100 runs from it
# These are normal & iid, combine straightforwardly

# Notes:
# - There are two indexes: g_idx and samp_idx
#   samp_idx are nested within g_idx
# - homophily_a == homophily_b, .2, .5, .8
# - maj_size = .5 or .8
# - filter_fn = filter_none for no filter
# - samp_fn one of: sample_random_nodes, sample_ego_networks,
#   sample_random_edges, sample_random_walk, sample_snowball, population

# Select non-filtered runs
samp_df = df %>%
  filter(filter_fn == "filter_none", samp_fn != "population") %>%
  group_by(samp_fn, g_idx, homophily_a, maj_size) %>%
  top_n(100)

# True vals
pop_df = df %>%
  filter(filter_fn == "filter_none", samp_fn == "population") %>%
  group_by(g_idx, homophily_a, maj_size) %>%
  top_n(100) %>%
  summarize(
    aa_mu = mean(aa),
    ab_mu = mean(ab),
    ba_mu = mean(ba),
    bb_mu = mean(bb),
    cg_mu = mean(cg),
    wg_mu = mean(wg))

# Join true vals to samples
# Need to group in 2 steps: group w/in graphs then b/t graphs
plot_df = samp_df %>%
  left_join(pop_df, c("g_idx" = "g_idx",
                      "homophily_a" = "homophily_a",
                      "maj_size" = "maj_size")) %>%
  # create error statistics for each run
  mutate(
    aa_err = aa - aa_mu,
    ab_err = ab - ab_mu,
    ba_err = ba - ba_mu,
    bb_err = bb - bb_mu,
    cg_err = cg - cg_mu,
    wg_err = wg - wg_mu) %>%
  # group w/in graph runs
  group_by(g_idx, samp_fn, homophily_a, maj_size) %>%
  summarize(
    aa_rmse = sqrt(mean(aa_err^2)),
    ab_rmse = sqrt(mean(ab_err^2)),
    ba_rmse = sqrt(mean(ba_err^2)),
    bb_rmse = sqrt(mean(bb_err^2)),
    cg_rmse = sqrt(mean(cg_err^2)),
    wg_rmse = sqrt(mean(wg_err^2))) %>%
    # aa_sd_err = sd(aa_err^2),
    # ab_sd_err = sd(ab_err^2),
    # ba_sd_err = sd(ba_err^2),
    # bb_sd_err = sd(bb_err^2),
    # cg_sd_err = sd(cg_err^2),
    #wg_sd_err = sd(wg_err^2)) %>%
  # aggregate across graph runs
  group_by(samp_fn, homophily_a, maj_size) %>%
  summarize(
    aa_mmse = mean(aa_rmse),
    ab_mmse = mean(ab_rmse),
    ba_mmse = mean(ba_rmse),
    bb_mmse = mean(bb_rmse),
    cg_mmse = mean(cg_rmse),
    wg_mmse = mean(wg_rmse),
    aa_sd_mse = sd(aa_rmse),
    ab_sd_mse = sd(ab_rmse),
    ba_sd_mse = sd(ba_rmse),
    bb_sd_mse = sd(bb_rmse),
    cg_sd_mse = sd(cg_rmse),
    wg_sd_mse = sd(wg_rmse))


# TODO: change this plot to be relative to the baseline nubmer of cg ties
# Even group sizes, by homophily
p1 = plot_df %>%
  filter(maj_size == 0.5) %>%
  ggplot(.) +
  geom_point(aes(x = factor(homophily_a), y = cg_mmse, color=samp_fn),
             position=position_dodge(width=0.5)) +
  geom_errorbar(aes(x = factor(homophily_a), ymin = cg_mmse - 1.96 * cg_sd_mse, ymax = cg_mmse + 1.96 * cg_sd_mse, color=samp_fn), position=position_dodge(width=0.5)) +
  geom_hline(aes(yintercept=0), linetype='dashed') +
  theme_bw()

p2 = plot_df %>%
  filter(maj_size == 0.8) %>%
  ggplot(.) +
  geom_point(aes(x = factor(homophily_a), y = cg_mmse, color=samp_fn),
             position=position_dodge(width=0.5)) +
  geom_errorbar(aes(x = factor(homophily_a), ymin = cg_mmse - 1.96 * cg_sd_mse, ymax = cg_mmse + 1.96 * cg_sd_mse, color=samp_fn), position=position_dodge(width=0.5)) +
  geom_hline(aes(yintercept=0), linetype='dashed') +
  theme_bw()



# Method on x axis
p3 = plot_df %>%
  ggplot(.) +
  geom_point(aes(x = factor(samp_fn), y = cg_mmse, color=factor(paste0(homophily_a, '|', maj_size))),
             position=position_dodge(width=0.5)) +
  geom_errorbar(aes(x = factor(samp_fn), ymin = cg_mmse - 1.96 * cg_sd_mse, ymax = cg_mmse + 1.96 * cg_sd_mse, color=factor(paste0(homophily_a, '|', maj_size))), position=position_dodge(width=0.5)) +
  geom_hline(aes(yintercept=0), linetype='dashed') +
  theme_bw()


# TODO: plot normality of error w/in runs
# TODO: group sizes
# TODO: convergence speed (in terms of # nodes visited)
# TODO: throw in filters to this
# TODO: change snowball to be more reasonable (sampling almost half the edges right now)
# TODO: better align sizes of edge samples
# TODO: better frame question: what useful thing are we trying to give the world?
# TODO: is filter function wrong?
