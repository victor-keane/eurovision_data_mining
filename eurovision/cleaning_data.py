import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
 
def remove_bad_data(df): 
   return df[df.Duplicate != 'x']

def find_average_points_per_contestant(df):
   points_given = {}
   for row in df.itertuples():
      contestant = row[6] + str(row[1]) + str(row[2])
      if contestant not in points_given:
         points_given[contestant] = [row[7]]
      else:
         points_given[contestant].append(row[7])

   average_points = {}
   for contestant in points_given:
      average_points[contestant] = sum(points_given[contestant])/(len(points_given[contestant]))
   return average_points

def above_average_given(to_country, stage, year, points, averages):
   if averages[to_country + str(year) + str(stage)] < points:
      return True
   else:
      return False

def find_when_countries_gave_above_average_points(df, average_points):
   above_average_dict = {}
   for row in df.itertuples():
      relationship = row[5] + "-" + row[6]
      above_average = above_average_given(row[6], row[2], row[1], row[7], average_points)
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
      
df = pd.read_excel('H:/eurovision/eurovision_song_contest_1975_2017v4.xlsx')
df = remove_bad_data(df)
average_points = find_average_points_per_contestant(df)
above_average_dict = find_when_countries_gave_above_average_points(df, average_points)
above_average_dict = remove_new_relationships(above_average_dict)
relationship_dict = classify_relationship(above_average_dict)
for i in relationship_dict:
   print(i)
   print(relationship_dict[i])
   print()

