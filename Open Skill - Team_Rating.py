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

#create lists to store team skill
team_skill_list = dict()


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
    
    #populate team skill list
    team_skill = list()    
    for b in team_1_ratings:
        team_skill.append(model.rating(mu=b.mu, sigma=b.sigma))
    team_skill_list.update({x[7].lower():team_skill})
    team_skill = list()    
    for b in team_2_ratings:
        team_skill.append(model.rating(mu=b.mu, sigma=b.sigma))
    team_skill_list.update({x[8].lower():team_skill})



print("Open Skill model correctly predicts " + str(total_correct/total_matches*100)+"% of matches")

with open('team_skill_list.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(["Tournament_Team_ID","Total_Ordinal_Skill"])
    for a in team_skill_list:
        team_skill = 0
        spamwriter.writerow([a, team_skill_list.get(a)[0].ordinal() +
                             team_skill_list.get(a)[1].ordinal() +
                             team_skill_list.get(a)[2].ordinal() +
                             team_skill_list.get(a)[3].ordinal() +
                             team_skill_list.get(a)[4].ordinal() +
                             team_skill_list.get(a)[5].ordinal() ])
