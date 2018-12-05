import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from operator import itemgetter
from scipy.stats import zscore
import random
 
def remove_bad_data(df): 
   return df[df.Duplicate != 'x']

def find_average_points_per_contestant(df):
   points_given = {}
   for row in df.itertuples():
      contestant = row[6] + "-" + str(row[3])
      if contestant not in points_given:
         points_given[contestant] = [row[7]]
      else:
         points_given[contestant].append(row[7])

   average_points = {}
   for contestant in points_given:
      average_points[contestant] = sum(points_given[contestant])/(len(points_given[contestant]))
   return average_points

def above_average_given(to_country, contest, points, averages):
   if averages[to_country + "-" + str(contest)] < points:
      return True
   else:
      return False

def find_when_countries_gave_above_average_points(df, average_points):
   above_average_dict = {}
   for row in df.itertuples():
      relationship = row[5] + "-" + row[6]
      above_average = above_average_given(row[6], row[3], row[7], average_points)
      if relationship not in above_average_dict:
         above_average_dict[relationship] = [above_average]
      else:
         above_average_dict[relationship].append(above_average)
   return above_average_dict

def remove_new_relationships(above_average_dict):
   dict_without_new_relationships = {}
   for relationship in above_average_dict:
      if len(above_average_dict[relationship]) > 4:
          dict_without_new_relationships[relationship] = above_average_dict[relationship]
   return dict_without_new_relationships

def classify_relationship(above_average_dict):
   relationship_dict = {}
   for relationship in above_average_dict:
      from_country = relationship.split('-')[0]
      to_country = relationship.split('-')[1]
      friend_percentage = sum(above_average_dict[relationship])/len(above_average_dict[relationship])
      if to_country not in relationship_dict:
         relationship_dict[to_country] = {"best_friends" : [], "close_friends" : [], "acquaintances" : []}
      if friend_percentage >= 0.90:
         relationship_dict[to_country]["best_friends"].append(from_country)
      elif friend_percentage >= 0.75:
         relationship_dict[to_country]["close_friends"].append(from_country)
      elif friend_percentage >= 0.60:
         relationship_dict[to_country]["acquaintances"].append(from_country)
   return relationship_dict
      
def create_performance_database(df, average, relationship):
   performances = {}
   for vote in df.itertuples():
      contestant = vote[6] + "-" + vote[3]
      if contestant not in performances:
         performances[contestant] = [0,0,0,average[contestant]]
      if vote[6] in relationship: #only not truwe when we didn't have enough data to define their relationships
         if vote[5] in relationship[vote[6]]["best_friends"]:
            performances[contestant][0] += 1
         if vote[5] in relationship[vote[6]]["close_friends"]:
            performances[contestant][1] += 1
         if vote[5] in relationship[vote[6]]["acquaintances"]:
            performances[contestant][2] += 1
   return performances

def performances_with_position(performances):
   rankings = {}
   for performance in performances:
      context = performance.split('-')
      country = context[0]
      stage = context[1]
      if stage not in rankings:
         rankings[stage] = []
      rankings[stage].append([country, performances[performance][3]])
   for year in rankings:
      rankings[year] = sorted(rankings[year], key=lambda x: x[1], reverse=True)
      final_rankings = []
      for country in rankings[year]:
         final_rankings.append(country[0])
      rankings[year] = final_rankings
   for performance in performances:
      context = performance.split('-')
      country = context[0]
      stage = context[1]
      performances[performance].append(round(performances[performance][0]*100/len(rankings[stage]),2))
      performances[performance].append(round(performances[performance][1]*100/len(rankings[stage]),2))
      performances[performance].append(round(performances[performance][2]*100/len(rankings[stage]),2))
      if rankings[stage].index(country) == 0:
         performances[performance].append(True)
      else:
         performances[performance].append(False)
      if rankings[stage].index(country) < 6:
         performances[performance].append(True)
      else:
         performances[performance].append(False)
      if rankings[stage].index(country) < 11:
         performances[performance].append(True)
      else:
         performances[performance].append(False)
   return performances
   
def transform_to_df(performances):
   stages = []
   df_list = []
   column_list = ["Stage", "Country", "Best friends", "Close Friends", "Acquaintance", "BF%", "CF%", "A%", "Winner", "Top 5", "Top 10"]
   i = -1
   for performance in performances:
      context = performance.split('-')
      country = context[0]
      stage = context[1]
      if stage not in stages:
         stages.append(stage)
         df = pd.DataFrame(columns = column_list)
         df_list.append(df)
         i += 1
      performances[performance].insert(0, country)
      performances[performance].insert(0, stage)
      del performances[performance][5]
      df2 = pd.DataFrame(data =[performances[performance]], columns = column_list)
      df_list[i] = df_list[i].append(df2)
   for df in df_list:
      df[["Best friends","Close Friends", "Acquaintance"]] = df[["Best friends","Close Friends", "Acquaintance"]].apply(zscore)
      #print(df)
   #print (df_list[0:len(df_list)-3])
   final_2017 = (df_list[-3])
   finalsf1_2017 = (df_list[-2])
   finalsf2_2017 = (df_list[-1])
   return df_list

def GetScores(table, original_z_diff, original_percent_diff):
   evaluation = []
   training = []
   #random_years = random.sample(range(67), 20)
   random_years = [26, 8, 22, 57, 53, 40, 66, 17, 25, 11, 60, 42, 29, 16, 61, 65, 37, 62, 55, 2]
   for i in range(len(table)):
      if (i in random_years):
         evaluation.append(table[i])
      else:
         training.append(table[i])
  # print(training)
   results = []
   #test = (table[-3:])
   #data = (table[0:len(table)-3])
   for df in evaluation:
      for country in df.itertuples():
         z_diff = original_z_diff
         percent_diff = original_percent_diff
         contestant = country[2] + "-" + country[1]
         print(contestant + " Predicted result:")
         while (len(results)<7):
            results = country_result(training, country[3], country[4], country[5], country[6], country[7], country[8], z_diff, percent_diff)
            z_diff += .1
            percent_diff += 2
         predict_result(results)
         results = []

def country_result(training, BF, CF, A, BFP, CFP, AP, z_diff, percent_diff):
   results_country = []
   win_count = 0
   top5_count = 0
   top10_count = 0
   for df in training:
      for country in df.itertuples():
         if ((BF-z_diff <= country[3] <= BF+z_diff)&
            (CF-z_diff <= country[4] <= CF+z_diff)&
            (A-z_diff <= country[5] <= A+z_diff)&
            (BFP - percent_diff <= country[6] <= BFP + percent_diff)&
            (CFP - percent_diff <= country[7] <= CFP + percent_diff)&
            (AP - percent_diff <= country[8] <= AP + percent_diff)):
               if country[9] == True:
                  win_count +=1
                  results_country.append("Winner")
               if country[10] == True:
                  results_country.append("Top 5")
               if country[11] == True:
                  top10_count +=1
                  results_country.append("Top 10")
               else:
                  results_country.append("Loser")
         else:
            pass
        # if ((BF-z_diff <= data[a][["Best friends"]].iloc[m]["Best friends"] <= BF+z_diff)& 
         #   (CF -z_diff <= data[a][["Close Friends"]].iloc[m]["Close Friends"] <= CF+z_diff) &
          #  (A -z_diff <= data[a][["Acquaintance"]].iloc[m]["Acquaintance"] <= A+z_diff) &
           # (BFP-percent_diff <= data[a][["BF%"]].iloc[m]["BF%"] <= BFP+percent_diff) &
          #  (CFP-percent_diff <= data[a][["CF%"]].iloc[m]["CF%"] <= CFP+percent_diff) &
          #  (AP-percent_diff <= data[a][["A%"]].iloc[m]["A%"] <= AP+percent_diff)):
               #print((data[a][["Stage"]].iloc[m]["Stage"])+" "+(data[a][["Country"]].iloc[m]["Country"]))
           #    if str((data[a][["Winner"]].iloc[m]["Winner"])) == "True":
            #      win_count +=1
             #     results_country.append("Winner")
              # if str((data[a][["Top 5"]].iloc[m]["Top 5"])) == "True":
               #   results_country.append("Top 5")
            #   if str((data[a][["Top 10"]].iloc[m]["Top 10"])) == "True":
            #      top10_count +=1
           #       results_country.append("Top 10")
          #     else:
          #        results_country.append("Loser")
        # else:
         #      pass
   return results_country

def predict_result(results):
   score = 0
   #print(results)
   length = len(results)
   winner_count = results.count("Winner")
   five_count = results.count("Top 5")
   ten_count = results.count("Top 10")
   score += winner_count * 3
   score += five_count * 2
   score += ten_count
   print(score/len(results))
   if winner_count > length/2:
      print("Winner!!!!!")
   elif (winner_count + five_count) > length/2:
      print("Top 5 - Well done!")
   elif (winner_count + five_count + ten_count) > length/2:
      print("Top 10 - meh")
   else:
      print("Loser!!!!! - haha")

original_df = pd.read_excel(r"C:\Users\User\Desktop\Data Mining\eurovision\eurovision_song_contest_1975_2017v4.xlsx")
df = remove_bad_data(original_df)
average_points = find_average_points_per_contestant(df)
above_average_dict = find_when_countries_gave_above_average_points(df, average_points)
above_average_dict = remove_new_relationships(above_average_dict)
relationship_dict = classify_relationship(above_average_dict)
performances = create_performance_database(original_df, average_points, relationship_dict)
performances = performances_with_position(performances)
performance_df = transform_to_df(performances)
results = GetScores(performance_df, .2, 5)
