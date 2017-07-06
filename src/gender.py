'''
Contains utility methods for categorizing a sample of the
twitter graph by gender.

To do this, we use the Baby Names from Social Security Card
Applications-National Level Data dataset from from the US
Social Security Administration. The dataset can be found at
https://catalog.data.gov/dataset/baby-names-from-social-security-card-applications-national-level-data

The actual metric computed is the percentage of instances of a
name beteen 1967 and 2017 for which the name was registered
as belonging to a male. This way, we have a measure of confidence
as well as expected gender.
'''
from pymongo import MongoClient

def gender_counts():
	gender_counts = dict()
	for year in range(1967, 2017):
		with open('names/yob' + str(year) + '.txt', 'r') as namefile:
			for line in namefile:
				stripline = line.strip()
				if stripline == '':
					continue
				name, gender, count = stripline.split(',')
				if name not in gender_counts:
					gender_counts[name] = {
						'M': 0,
						'F': 0
					}
				gender_counts[name][gender] += int(count)
	return gender_counts

def pick_gender(node, gender_counts):
	first_name = node["full_name"].strip().split()[0]

	if first_name in gender_counts:
		name_counts = gender_counts[first_name]
		total = name_counts['M'] + name_counts['F']
		return (name_counts['M']/total)
	else:
		return -1

def categorize(gender_counts):
	uname = input("Username: ")
	pwd = input("Password: ")
	client = MongoClient('mongodb://' + uname + ':' + pwd + '@127.0.0.1')

	coll = client['fake_news']['TW_sample']

	i = 0
	for node in coll.find():
		percent_male = pick_gender(node, gender_counts)
		coll.update({"_id":node["_id"]},
			{"$set":{"percent_male":percent_male}})
		i += 1

		if (i % 1000) == 0:
			print(i)

if __name__ == "__main__":
	categorize(gender_counts())