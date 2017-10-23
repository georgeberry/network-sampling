library(tidyverse)

df = read_tsv('/Users/g/Drive/project-RA/network-sampling/data/pokec/soc-pokec-profiles.txt',
              na = 'null',
              col_names = c('user_id',
                            'public',
                            'completion_percentage',
                            'gender',
                            'region',
                            'last_login',
                            'registration',
                            'AGE',
                            'body',
                            'I_am_working_in_field',
                            'spoken_languages',
                            'hobbies',
                            'I_most_enjoy_good_food',
                            'pets',
                            'body_type',
                            'my_eyesight',
                            'eye_color',
                            'hair_color',
                            'hair_type',
                            'completed_level_of_education',
                            'favourite_color',
                            'relation_to_smoking',
                            'relation_to_alcohol',
                            'sign_in_zodiac',
                            'on_pokec_i_am_looking_for',
                            'love_is_for_me',
                            'relation_to_casual_sex',
                            'my_partner_should_be',
                            'marital_status',
                            'children',
                            'relation_to_children',
                            'I_like_movies',
                            'I_like_watching_movie',
                            'I_like_music',
                            'I_mostly_like_listening_to_music',
                            'the_idea_of_good_evening',
                            'I_like_specialties_from_kitchen',
                            'fun',
                            'I_am_going_to_concerts',
                            'my_active_sports',
                            'my_passive_sports',
                            'profession',
                            'I_like_books',
                            'life_style',
                            'music',
                            'cars',
                            'politics',
                            'relationships',
                            'art_culture',
                            'hobbies_interests',
                            'science_technologies',
                            'computers_internet',
                            'education',
                            'sport',
                            'movies',
                            'travelling',
                            'health',
                            'companies_brands',
                            'more'))

non_null_count = function(col) {
  return(sum(!is.na(col)))
}

non_null_counts = df %>%
  summarize_all(funs(non_null_count))

non_null_counts$user_id - non_null_counts$gender
# equals 163 out of 1632803 so it's fine to ignore them

# choose column gender

gender_df = df %>%
  select(user_id, gender) %>%
  filter(!is.na(gender))
  
write_tsv(gender_df, '/Users/g/Drive/project-RA/network-sampling/data/pokec/gender_df.tsv')

age_df = df %>%
  select(user_id, AGE) %>%
  filter(AGE > 0, !is.na(AGE))

write_tsv(age_df, '/Users/g/Drive/project-RA/network-sampling/data/pokec/age_df.tsv')
