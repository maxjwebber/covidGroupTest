# One-Pass Group Testing Algorithm and Probabilistic Prediction Algorithm
## Practical Code
Download and run userDefTest.py, which combines simulation file functions. Provide a csv of groups testing positive and a csv of groups testing negative, receive remaining groups and (optionally) probability of infection for all subjects. 

## Simulation Files
generateTestData.py – generates csv containing binary strings with n 0s (uninfected subjects) and k 1s (infected people). user can also specify how many runs
generateGroupTests_range.py—similar but the output csv contains strings of numbers in base-g where g is the number of groups. Therefore an index of testdata (a subject) can be assigned to a group by looking at the same index. The program will generate a csv for each value of s (group size) in a range of provided group sizes.
convertbincsv.py – converts the testdata and grouptest files to binary (to reduce loa## covidGroupTestd times)
1PgeneratePlot.py – runs 1PIA for the provided binary testdata and grouptests, creates plot of identified positives/negatives versus the number of tests.
1PgenerateRemaining.py - runs 1PIA for the provided testdata and grouptests, creates file containing leftover individuals at each partition (for probability testing)
calcProb_bruteForce.py – calculates probability of infection for remaining individuals (using output of previous program).
