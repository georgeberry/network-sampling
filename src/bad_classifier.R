library(tidyverse)

DATA_PATH = '/Users/g/Desktop/output.tsv'
df = read.csv(DATA_PATH, sep='\t')

df %>%
  group_by(p_misclassify) %>%
  mutate(deviations = d_aa - true_d_aa) %>%
  ggplot(.) +
    geom_boxplot(aes(x=factor(p_misclassify), y=deviations, color=factor(p_misclassify))) +
    labs(title='ingroup links, equal group sizes, .8 ingroup link generation')

df %>%
  group_by(p_misclassify) %>%
  mutate(deviations = d_ab - true_d_ab) %>%
  ggplot(.) +
  geom_boxplot(aes(x=factor(p_misclassify), y=deviations, color=factor(p_misclassify))) +
  labs(title='outgroup links, equal group sizes, .8 ingroup link generation')
