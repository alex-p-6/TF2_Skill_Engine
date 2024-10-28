import csv
from openskill.models import PlackettLuce

model = PlackettLuce()
match_list = list()

with open('master_data.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in spamreader:
        match_list.append(row)

#list is player_name, current rating, peak rating, games played
player_current_skill_list = dict()
player_peak_skill_list = dict()
player_count_matches = dict()
player_region = dict()

# Calculate model accuracy
total_matches = 0
total_correct = 0
role_power = {"cs":0,"fs":0, "r":0, "p":0, "d":0, "m":0}

role_power_by_year = [[0]*7 for i in range(20)]




for x in match_list[1:]:
#     print("status: match " + str(match_list.index(x)) + " out of " + str(len(match_list)))
#     print(x[0])
    
    #initialise values
    team_1_players = list()
    team_1_ratings = list()
    
    team_2_players = list()
    team_2_ratings = list()
    
    team_1_players = [x[9].lower()+"_scout",
                      x[10].lower()+"_scout",
                      x[11].lower()+"_soldier",
                      x[12].lower()+"_soldier",
                      x[13].lower()+"_demo",
                      x[14].lower()+"_medic"]
    
    for a in team_1_players:
        if player_current_skill_list.get(a) == None:
            player_current_skill_list.update({a:model.rating()})
        if player_peak_skill_list.get(a) == None:
            player_peak_skill_list.update({a:float(0)})
        if player_count_matches.get(a) == None:
            player_count_matches.update({a:0})
        player_count_matches.update({a:int(player_count_matches.get(a))+1})
        if x[1].startswith("ESEA") or x[1].startswith("RGL"):
            player_region.update({a:"NA"})
        elif x[1].startswith("ETF2L"):
            player_region.update({a:"EU"})
        elif x[1].startswith("Ozfortress"):
            player_region.update({a:"AU/NZ"})

    for a in team_1_players:
        if a.startswith("n/a"):
            team_1_ratings.append(model.rating())
        else:
            team_1_ratings.append(player_current_skill_list.get(a))
            
    team_2_players = [x[15].lower()+"_scout",
                  x[16].lower()+"_scout",
                  x[17].lower()+"_soldier",
                  x[18].lower()+"_soldier",
                  x[19].lower()+"_demo",
                  x[20].lower()+"_medic"]

    for a in team_2_players:
        if player_current_skill_list.get(a) == None:
            player_current_skill_list.update({a:model.rating()})
        if player_peak_skill_list.get(a) == None:
            player_peak_skill_list.update({a:float(0)})
        if player_count_matches.get(a) == None:
            player_count_matches.update({a:0})
        player_count_matches.update({a:int(player_count_matches.get(a))+1})
        if x[1].startswith("ESEA") or x[1].startswith("RGL"):
            player_region.update({a:"NA"})
        elif x[1].startswith("ETF2L"):
            player_region.update({a:"EU"})
        elif x[1].startswith("Ozfortress"):
            player_region.update({a:"AU/NZ"})


    for a in team_2_players:
        if a.startswith("n/a"):
            team_2_ratings.append(model.rating())
        else:
            team_2_ratings.append(player_current_skill_list.get(a))
    
    
    bb = model.predict_win([team_1_ratings, team_2_ratings])
    if bb[0] > 0.5 and x[6] == '1':
        total_matches += 1
        total_correct += 1
    elif bb[0] < 0.5 and x[6] == '2':
        total_matches += 1
        total_correct += 1
    elif bb[0] > 0.5 and x[6] == '2':
        total_matches += 1
    elif bb[0] < 0.5 and x[6] == '1':
        total_matches += 1

    for c, a in enumerate(role_power):
        if model.predict_win([[team_1_ratings[c]], [team_2_ratings[c]]])[0]>0.5 and x[6] == '1':
            role_power.update({a:role_power.get(a)+1})
        elif model.predict_win([[team_1_ratings[c]], [team_2_ratings[c]]])[0]<0.5 and x[6] == '2':
            role_power.update({a:role_power.get(a)+1})

    match_year_ref = int(x[0].split(",")[0].replace("(",""))-2008
    for b in range(0,6):
        if model.predict_win([[team_1_ratings[b]], [team_2_ratings[b]]])[0] > 0.5 and x[6] == '1':
            role_power_by_year[match_year_ref][b] += 1
        elif model.predict_win([[team_1_ratings[c]], [team_2_ratings[c]]])[0] < 0.5 and x[6] == '2':
            role_power_by_year[match_year_ref][b] += 1
    if x[6] == '1' or x[6] == '2':
        role_power_by_year[match_year_ref][6] += 1

            
    if x[6] == '1':
        model.rate([team_1_ratings, team_2_ratings], ranks = [1,2])
    elif x[6] == '2':
        model.rate([team_1_ratings, team_2_ratings], ranks = [2,1])
    elif x[6] == 'draw':
        model.rate([team_1_ratings, team_2_ratings], ranks = [1,1])

    for c, a in enumerate(team_1_players):
        if player_peak_skill_list.get(a) < float(player_current_skill_list.get(a).ordinal()):
            player_peak_skill_list.update({a: float(player_current_skill_list.get(a).ordinal())})

    for c, a in enumerate(team_2_players):
        if player_peak_skill_list.get(a) < float(player_current_skill_list.get(a).ordinal()):
            player_peak_skill_list.update({a: float(player_current_skill_list.get(a).ordinal())})

print("Open Skill model correctly predicts " + str(total_correct/total_matches*100)+"% of matches")
for a in role_power:
   print(a+" predicted " + str(round(role_power.get(a)/total_matches*100,4)) + "% of matches")

with open('player_open_skill.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(["player","current_open_skill","peak_rating", "count_matches", "player_region"])
    for a in player_current_skill_list:
        spamwriter.writerow([a, round(player_current_skill_list.get(a).ordinal(),4), round(player_peak_skill_list.get(a),4),player_count_matches.get(a), player_region.get(a)])

with open('role_power_by_year.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(["cs", "fs", "r", "p","d", "m","tot"])
    for a in role_power_by_year:
        spamwriter.writerow(a)