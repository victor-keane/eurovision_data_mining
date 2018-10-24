import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from operator import itemgetter
from scipy.stats import zscore
 
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
      print(df)

original_df = pd.read_excel('H:/eurovision/eurovision_song_contest_1975_2017v4.xlsx')
df = remove_bad_data(original_df)
average_points = find_average_points_per_contestant(df)
above_average_dict = find_when_countries_gave_above_average_points(df, average_points)
above_average_dict = remove_new_relationships(above_average_dict)
relationship_dict = classify_relationship(above_average_dict)
performances = create_performance_database(original_df, average_points, relationship_dict)
performances = performances_with_position(performances)
performance_df = transform_to_df(performances)
