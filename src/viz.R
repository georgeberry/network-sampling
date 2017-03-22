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
    a,
    b,
    aa,
    ab,
    ba,
    bb) %>%
  mutate(
    n_tot = a + b,
    e_tot = aa + ab + ba + bb, #sum
    cg = ab + ba, # cg = crossgroup
    wg = aa + bb) %>% # wg = within_group
  mutate(
    h_a = (aa / (aa + ab + ba) - a/n_tot) / (1 - a/n_tot),
    h_b = (bb / (bb + ab + ba) - b/n_tot) / (1 - b/n_tot),
    # normalize
    a = a / n_tot,
    b = b / n_tot,
    aa = aa / e_tot,
    ab = ab / e_tot,
    ba = ba / e_tot,
    bb = bb / e_tot,
    cg = cg / e_tot,
    wg = wg / e_tot)

# Select non-filtered runs
samp_df = df %>%
  filter(filter_fn == "filter_none", samp_fn != "population") %>%
  group_by(samp_fn, g_idx, homophily_a, maj_size)

# True vals
pop_df = df %>%
  filter(filter_fn == "filter_none", samp_fn == "population") %>%
  group_by(g_idx, homophily_a, maj_size) %>%
  summarize(
    a_mu = mean(a),
    b_mu = mean(b),
    aa_mu = mean(aa),
    ab_mu = mean(ab),
    ba_mu = mean(ba),
    bb_mu = mean(bb),
    cg_mu = mean(cg),
    wg_mu = mean(wg),
    h_a_mu = mean(h_a),
    h_b_mu = mean(h_b))

base_df = samp_df %>%
  left_join(pop_df, c("g_idx" = "g_idx",
                      "homophily_a" = "homophily_a",
                      "maj_size" = "maj_size")) %>%
  mutate(
    a_err = a - a_mu,
    b_err = b - b_mu,
    aa_err = aa - aa_mu,
    ab_err = ab - ab_mu,
    ba_err = ba - ba_mu,
    bb_err = bb - bb_mu,
    cg_err = cg - cg_mu,
    wg_err = wg - wg_mu,
    h_a_err = h_a - h_a_mu,
    h_b_err = h_b - h_b_mu)

#### Cross-group MSE plots ######################################################

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

# Join true vals to samples
# Need to group in 2 steps: group w/in graphs then b/t graphs
cg_plot_df = base_df %>%
  # group w/in graph runs
  group_by(g_idx, samp_fn, homophily_a, maj_size) %>%
  summarize(
    cg_rmse = sqrt(mean(cg_err^2)),
    cg_diff = mean(cg_err),
    cg_mu = mean(cg_mu)) %>%
  # aggregate across graph runs
  group_by(samp_fn, homophily_a, maj_size) %>%
  summarize(
    cg_m_rmse = mean(cg_rmse),
    cg_sd_mse = sd(cg_rmse),
    cg_m_diff = mean(cg_diff),
    cg_mu = mean(cg_mu)) %>%
  mutate(hom_majsz=paste0(homophily_a, '|', maj_size))

# TODO: change this plot to be relative to the baseline nubmer of cg ties
# Even group sizes, by homophily
p1 = cg_plot_df %>%
  filter(maj_size == 0.5) %>%
  ggplot(.) +
  geom_point(aes(x = factor(homophily_a), y = cg_m_rmse, color=samp_fn),
             position=position_dodge(width=0.5)) +
  geom_errorbar(aes(x = factor(homophily_a), ymin = cg_m_rmse - 1.96 * cg_sd_mse, ymax = cg_m_rmse + 1.96 * cg_sd_mse, color=samp_fn), position=position_dodge(width=0.5)) +
  geom_hline(aes(yintercept=0), linetype='dashed') +
  labs(title="RMSE for fraction of cross-group ties, equal sized groups",
       x=element_blank(),
       y="Cross-group fraction RMSE") +
  theme_bw()

ggsave("~/Desktop/p1.png", plot=p1, height=5, width=8)

p2 = cg_plot_df %>%
  filter(maj_size == 0.8) %>%
  ggplot(.) +
  geom_point(aes(x = factor(homophily_a), y = cg_m_rmse, color=samp_fn),
             position=position_dodge(width=0.5)) +
  geom_errorbar(aes(x = factor(homophily_a), ymin = cg_m_rmse - 1.96 * cg_sd_mse, ymax = cg_m_rmse + 1.96 * cg_sd_mse, color=samp_fn), position=position_dodge(width=0.5)) +
  geom_hline(aes(yintercept=0), linetype='dashed') +
  labs(title="RMSE for fraction of cross-group ties, maj group = 0.8",
       x="",
       y="Cross-group fraction RMSE") +
  theme_bw()

ggsave("~/Desktop/p2.png", plot=p2, height=5, width=8)



# Method on x axis
p3 = cg_plot_df %>%
  ggplot(.) +
  geom_point(aes(x = factor(samp_fn), y = cg_m_rmse, color=factor(hom_majsz)),
               position=position_dodge(width=0.5)) +
  geom_errorbar(aes(x = factor(samp_fn), ymin = cg_m_rmse - 1.96 * cg_sd_mse, ymax = cg_m_rmse + 1.96 * cg_sd_mse, color=factor(hom_majsz)), position=position_dodge(width=0.5)) +
  geom_hline(aes(yintercept=0), linetype='dashed') +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  xlab("") +
  ylab("Cross-group fraction RMSE") +
  ggtitle("RMSE for fraction of cross-group ties by sampling method")

ggsave("~/Desktop/p3.png", plot=p3, height=5, width=8)


#### Disaggregated plots to assess bias vs variance #############################

cg_disagg_plot_df = base_df %>%
  filter(g_idx == 0) %>%
  mutate(hom_majsz = paste(homophily_a, maj_size, sep="|"))

p4 = cg_disagg_plot_df %>%
  ggplot(.) +
  geom_hline(aes(yintercept=0), linetype='dashed') +
  geom_point(aes(x = factor(samp_fn), y = cg_err, color=hom_majsz),
                 position=position_dodge(width=0.5)) +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  xlab("") +
  ylab("Cross-group fraction RMSE") +
  ggtitle("Error for fraction of cross group ties (one run)")

ggsave("~/Desktop/p4.png", plot=p4, height=5, width=8)

#### Group size plots ###########################################################

grp_plot_df = base_df %>%
  # group w/in graph runs
  group_by(g_idx, samp_fn, homophily_a, maj_size) %>%
  summarize(
    a_rmse = sqrt(mean(a_err^2)),
    a_diff = mean(a_err),
    a_mu = mean(a_mu)) %>%
  # aggregate across graph runs
  group_by(samp_fn, homophily_a, maj_size) %>%
  summarize(
    a_m_rmse = mean(a_rmse),
    a_sd_mse = sd(a_rmse),
    a_m_diff = mean(a_diff),
    a_mu = mean(a_mu)) %>%
    mutate(hom_majsz=paste0(homophily_a, '|', maj_size))

p5 = grp_plot_df %>%
  ggplot(.) +
  geom_point(aes(x = factor(samp_fn), y = a_m_rmse, color=factor(hom_majsz)),
               position=position_dodge(width=0.5)) +
  geom_errorbar(aes(x = factor(samp_fn), ymin = a_m_rmse - 1.96 * a_sd_mse, ymax = a_m_rmse + 1.96 * a_sd_mse, color=factor(hom_majsz)), position=position_dodge(width=0.5)) +
  geom_hline(aes(yintercept=0), linetype='dashed') +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  xlab("") +
  ylab("Majority group size RMSE") +
  ggtitle("RMSE for majority group size by sampling method")


ggsave("~/Desktop/p5.png", plot=p5, height=5, width=8)

grp_disagg_plot_df = base_df %>%
  filter(g_idx == 0) %>%
  mutate(hom_majsz = paste(homophily_a, maj_size, sep="|"))

p6 = grp_disagg_plot_df %>%
  ggplot(.) +
  geom_hline(aes(yintercept=0), linetype='dashed') +
  geom_point(aes(x = factor(samp_fn), y = a_err, color=hom_majsz),
                 position=position_dodge(width=0.5)) +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  xlab("") +
  ylab("Majority group fraction RMSE") +
  ggtitle("Error for size of majority group (one run)")


ggsave("~/Desktop/p6.png", plot=p6, height=5, width=8)


#### MSE vs group size accuracy #################################################

tradeoff_df = base_df %>%
  # group w/in graph runs
  group_by(g_idx, samp_fn, homophily_a, maj_size) %>%
  summarize(
    a_rmse = sqrt(mean(a_err^2)),
    a_diff = mean(a_err),
    a_mu = mean(a_mu),
    cg_rmse = sqrt(mean(cg_err^2)),
    cg_diff = mean(cg_err),
    cg_mu = mean(cg_mu)) %>%
  # aggregate across graph runs
  group_by(samp_fn, homophily_a, maj_size) %>%
  summarize(
    a_m_rmse = mean(a_rmse),
    a_sd_mse = sd(a_rmse),
    a_m_diff = mean(a_diff),
    a_mu = mean(a_mu),
    cg_m_rmse = mean(cg_rmse),
    cg_sd_mse = sd(cg_rmse),
    cg_m_diff = mean(cg_diff),
    cg_mu = mean(cg_mu)) %>%
  group_by(samp_fn) %>%
  summarize(a_m_rmse = mean(a_m_rmse),
            cg_m_rmse = mean(cg_m_rmse))

# clowny af
id_e = 1-tradeoff_df[which(tradeoff_df$samp_fn=="sample_random_edges"),"cg_m_rmse"]$cg_m_rmse[[1]]
id_n = 1-tradeoff_df[which(tradeoff_df$samp_fn=="sample_random_nodes"),"a_m_rmse"]$a_m_rmse[[1]]

p7 = tradeoff_df %>%
  ggplot(.) +
  geom_segment(aes(x=1.0, y=1.0, xend=1.0, yend=-Inf)) +
  geom_segment(aes(x=1.0, y=1.0, xend=-Inf, yend=1.0)) +
  geom_segment(aes(x=id_n, y=id_e, xend=-Inf, yend=id_e), linetype="dashed") +
  geom_segment(aes(x=id_n, y=id_e, xend=id_n, yend=-Inf), linetype="dashed") +
  # geom_segment(aes(xintercept=1.0), linetype="twodash") +
  # geom_segment(aes(xend=id_e_val), linetype="dashed") +
  # geom_segment(aes(xintercept=ideal_node_samp_val), linetype="dashed") +
  geom_point(aes(x = 1-a_m_rmse, y = 1-cg_m_rmse, color = samp_fn), size=8) +
  lims(x = c(.9,1), y = c(.9,1)) +
  theme_bw() +
  xlab("1 - RMSE for majority group size") +
  ylab("1 - RMSE for fraction of cross-group ties") +
  ggtitle("Comparison of sampling methods to ideal")


ggsave("~/Desktop/p7.png", plot=p7, height=5, width=8)

#### Actual homophily numbers ###################################################

h_plot_df = base_df %>%
  # group w/in graph runs
  group_by(g_idx, samp_fn, homophily_a, maj_size) %>%
  summarize(
    h_b_rmse = sqrt(mean(h_b_err^2)),
    h_b_diff = mean(h_b_err),
    h_b_mu = mean(h_b_mu)) %>%
  # aggregate across graph runs
  group_by(samp_fn, homophily_a, maj_size) %>%
  summarize(
    h_b_m_rmse = mean(h_b_rmse),
    h_b_sd_mse = sd(h_b_rmse),
    h_b_m_diff = mean(h_b_diff),
    h_b_mu = mean(h_b_mu)) %>%
  mutate(hom_majsz=paste0(homophily_a, '|', maj_size))


p8 = h_plot_df %>%
  ggplot(.) +
  geom_point(aes(x = factor(samp_fn), y = h_b_m_rmse, color=factor(hom_majsz)),
               position=position_dodge(width=0.5)) +
  geom_errorbar(aes(x = factor(samp_fn), ymin = h_b_m_rmse - 1.96 * h_b_sd_mse, ymax = h_b_m_rmse + 1.96 * h_b_sd_mse, color=factor(hom_majsz)), position=position_dodge(width=0.5)) +
  geom_hline(aes(yintercept=0), linetype='dashed') +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  xlab("") +
  ylab("RMSE") +
  ggtitle("Coleman's homophily index: minority group")


ggsave("~/Desktop/p8.png", plot=p8, height=5, width=8)

# TODO: this part
# Plot: correct h val
h_disagg_plot_df = base_df %>%
  filter(g_idx == 0) %>%
  mutate(hom_majsz = paste(homophily_a, maj_size, sep="|"))

p9 = h_disagg_plot_df %>%
  ggplot(.) +
  geom_hline(aes(yintercept=0), linetype='dashed') +
  geom_point(aes(x = factor(samp_fn), y = h_b_err, color=hom_majsz),
                 position=position_dodge(width=0.5)) +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  xlab("") +
  ylab("RMSE") +
  ggtitle("Coleman's homophily index: minority group (one run)")

ggsave("~/Desktop/p9.png", plot=p9, height=5, width=8)

####

h_summary_df = base_df %>%
  # group w/in graph runs
  group_by(g_idx, samp_fn, homophily_a, maj_size) %>%
  summarize(
    h_b_rmse = sqrt(mean(h_b_err^2))) %>%
  # aggregate across graph runs
  group_by(samp_fn, homophily_a, maj_size) %>%
  summarize(
    h_b_m_rmse = mean(h_b_rmse),
    h_b_sd_rmse = sd(h_b_rmse)) %>%
  group_by(samp_fn) %>%
  summarize(h_b_rmse = mean(h_b_m_rmse),
            h_b_sd = mean(h_b_sd_rmse))

p10 = h_summary_df %>%
  ggplot(.) +
  geom_bar(
    aes(y=h_b_rmse, x=factor(samp_fn), fill=factor(samp_fn)),
    position="dodge",
    stat="identity") +
  geom_errorbar(
    aes(x=factor(samp_fn),
    ymin=h_b_rmse - 1.96 * h_b_sd,
    ymax=h_b_rmse + 1.96 * h_b_sd),
    width=.5) +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  xlab("") +
  ylab("RMSE") +
  ggtitle("Aggregated homophily RMSE by sampling method")

ggsave("~/Desktop/p10.png", plot=p10, height=6, width=7)


#### Future to-dos ##############################################################

# TODO: plot normality of error w/in runs
# TODO: convergence speed (in terms of # nodes visited)
# TODO: throw in filters to this
# TODO: better frame question: what useful thing are we trying to give the world?
# TODO: is filter function wrong?
# TODO: make sampling methods generators
