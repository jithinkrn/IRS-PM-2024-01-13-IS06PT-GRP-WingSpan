import pandas as pd
import os
from random import sample
import matplotlib.pyplot as plt
from apriori_python import apriori
import numpy as np
import pickle

# define a function to return the unique set of all items (as a freq dictionary)
def itemcounts(itemsets):
    allitems = dict()
    for its in itemsets:
        for i in its:
            if i in allitems.keys():
                allitems[i] = allitems[i] + 1
            else:
                allitems[i] = 1
    return allitems


# a nicer rules display, that shows the highest confidence rules first
def showrules(rules, N=20):
    for L, R, C in reversed(rules):
        print("cf={:.4f}".format(C), " ", L, "=>\t", R)
        N = N - 1
        if N <= 0:
            break


# show each unique item (rule RHS) that can be recommended by the ruleset and the number of rules that recommend that item


def RHSitems(rules):
    allitems = dict()
    for LHS, RHS, conf in rules:
        for item in RHS:
            if item in allitems.keys():
                allitems[item] = allitems[item] + 1
            else:
                allitems[item] = 1
    return allitems


# Define a function to input a lication list and a ruleset and then execute those rules
# in the ruleset where any subset of the lication list matches the rule LHS.
# Output a list of tuples: (item, confidence) for the topN items output by the rules with highest confidence
# Ignore rules if the rule RHS is also within the LHS (eg ignore "if A and B then A").
# If many rules output the same item then return the highest confidence for that item.
def execrules_anymatch(itemset, rules, topN=10):
    preds = dict()
    for LHS, RHS, conf in rules:
        if LHS.issubset(itemset):
            for pitem in RHS:
                # ignore rules like A => A
                if not pitem in itemset:
                    if pitem in preds.keys():
                        preds[pitem] = max(preds[pitem], conf)
                    else:
                        preds[pitem] = conf
    recs = sorted(preds.items(), key=lambda kv: kv[1], reverse=True)
    return recs[0 : min(len(recs), topN)]


# Define a Holdout test for a set of association rules on a testset, also compute rule lift over random.
# For each basket: do tpb (testsperbasket) tests by holding out in turn the first, second, third etc items in the testitems.
# Compute a random recommendation only when a rule-based recommendation is also made (for accurate comparison with the ruleset).
# We assume virtual items (if any) occur at the start of the basket:
# usually virtual items (eg age, gender) are not items that we wish to recommend hence itemstart indicates
# the start of the items that are to be tested (ie can be recommended).


def rulehits_holdout_lift(testbaskets, rules, allitems, topN=10, tpb=5, itemstart=0):
    tothits = tottests = totrecs = totrhits = totrrecs = 0
    for testbasket in testbaskets:
        virtualitems = testbasket[:itemstart]
        testitems = testbasket[itemstart:]
        numtests = min(len(testitems), tpb)
        for i in range(0, numtests):
            recs = execrules_anymatch(
                virtualitems + testitems[:i] + testitems[i + 1 :], rules, topN
            )  # omit (holdout) the ith testitem
            nrecs = len(recs)
            if nrecs > 0:
                recitems = set()
                for item, conf in recs:
                    recitems.add(item)  # strip out the confidences
                tothits = tothits + int(
                    testitems[i] in recitems
                )  # increment if testitem is in the recommended items
                totrecs = totrecs + nrecs
                tottests = tottests + 1
                # now do the random recommendations
                unseenitems = set(allitems) - set(
                    testitems[:i] + testitems[i + 1 :]
                )  # remove the testbasket items (except the holdout)
                recitems = sample(list(unseenitems), min(topN, len(unseenitems), nrecs))
                nrecs = len(recitems)
                totrhits = totrhits + int(
                    testitems[i] in recitems
                )  # increment if testitem is in the recommended items
                totrrecs = totrrecs + nrecs
    if totrecs == 0 or totrrecs == 0 or totrhits == 0:
        print("no recommendations made, please check your inputs")
        return np.nan
    print(
        "number of holdbacks=",
        tottests,
        "recommendeditems=",
        totrecs,
        "hits=",
        tothits,
        "({:.2f}%)".format(tothits * 100 / totrecs),
        "randomrecommendeditems=",
        totrrecs,
        "randomhits=",
        totrhits,
        "({:.2f}%)".format(totrhits * 100 / totrrecs),
        "rulelift={:.2f}".format((tothits / totrecs) / (totrhits / totrrecs)),
    )
    return tothits, totrecs, tottests, totrhits, totrrecs


# Main code
# Get the current working directory
current_directory_path = os.getcwd()
print(f"Current directory: {current_directory_path}")

# Construct the full path to the CSV file
data_path = os.path.join(current_directory_path, "Data", "Park_Recommendation_Data.csv")
print(f"Data path: {data_path}")

# Read the CSV file into a DataFrame

sighting_data = pd.read_csv(data_path, encoding="latin1")
sighting_data.columns = ["bird", "datetime", "location"]

allitems = np.unique(sighting_data.location)
print("data items=", len(allitems))

# group transactions into baskets (a series of lists)
locationList_list = sighting_data.groupby("bird")["location"].apply(list)


# User input for bird type
#user_bird = input("Please enter the bird type you're interested in: ")

# Check if the entered bird type is in the DataFrame
#if user_bird in locationList_list.index:
    #user_bird_locations = locationList_list[user_bird]
    #print(f"Locations for {user_bird}: {user_bird_locations}")

    #ruleset_loaded = []  # This should be loaded from your saved rules if available
    #recommendations = execrules_anymatch(set(user_bird_locations), ruleset_loaded, topN=5)
    #print("Recommendations:", recommendations)


# to test the rules we first divide the baskets into training and test sets and then rebuild the ruleset
testsize = int(len(locationList_list) * 0.3)
testsize  # set the size of the test set
testids = sample(list(locationList_list.index), testsize)
trainids = list(set(locationList_list.index) - set(testids))
train_loc_list = locationList_list[trainids]
test_loc_list = locationList_list[testids]

# for correct testing we rebuild the ruleset using the training baskets only
freqItemSet, rules = apriori(train_loc_list, minSup=0.05, minConf=0.1)
print("number of rules generated=", len(rules))

# display the rules
showrules(rules)

# show each unique item (rule RHS) that can be recommended by the ruleset and the number of rules that recommend that item
ruleRHSitems = RHSitems(rules)

print("number of recommendable items=", len(ruleRHSitems))

all_items = {item for sublist in train_loc_list for item in sublist}

_ = rulehits_holdout_lift(test_loc_list, rules, allitems, topN=5, tpb=5)


# Save freqItemSet and rules

# Save freqItemSet and rules
with open("Park_Recomendation_freqItemSet.pkl", "wb") as f:
    pickle.dump(freqItemSet, f)

with open("Park_Recomendation_rules.pkl", "wb") as f:
    pickle.dump(rules, f)