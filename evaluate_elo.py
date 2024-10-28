import csv

match_list = list()

with open('master_data.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in spamreader:
        match_list.append(row)

#Create player_match_list??


#set constants
k_value = 20

##setup_Elo_list##
player_current_elos = dict()
player_peak_elos = dict()
initial_elo = 1200

# Calculate model accuracy
total_matches = 0
total_correct = 0



for x in match_list[1:]:
#    print("status: match " + str(match_list.index(x)) + " out of " + str(len(match_list)))
    #initialise values
    team_1_elo = int()
    team_2_elo = int()
    team_1_players = list()
    team_2_players = list()
    
    #evaluate team_1 elo
    team_1_players = [x[9].lower()+"_scout",
                      x[10].lower()+"_scout",
                      x[11].lower()+"_soldier",
                      x[12].lower()+"_soldier",
                      x[13].lower()+"_demo",
                      x[14].lower()+"_medic"]

    for a in team_1_players:
        if player_current_elos.get(a) == None:
            player_current_elos.update({a:initial_elo})
        if player_peak_elos.get(a) == None:
            player_peak_elos.update({a:initial_elo})
        team_1_elo += player_current_elos.get(a)
    
    team_2_players = [x[15].lower()+"_scout",
                      x[16].lower()+"_scout",
                      x[17].lower()+"_soldier",
                      x[18].lower()+"_soldier",
                      x[19].lower()+"_demo",
                      x[20].lower()+"_medic"]

    for a in team_2_players:
        if player_current_elos.get(a) == None:
            player_current_elos.update({a:initial_elo})
        if player_peak_elos.get(a) == None:
            player_peak_elos.update({a:initial_elo})
        team_2_elo += player_current_elos.get(a)

    prob_team_1_win = 1/(1+pow(10,(team_2_elo - team_1_elo)/400))
    rating_change = int() 
    if x[6] == '1':
        rating_change = k_value*(1-prob_team_1_win)
    elif x[6] == '2':
        rating_change = k_value*(0-prob_team_1_win)
    
    if team_1_elo > team_2_elo and x[6] == '1':
        total_matches += 1
        total_correct += 1
    elif team_2_elo > team_1_elo and x[6] == '2':
        total_matches += 1
        total_correct += 1
    elif team_1_elo > team_2_elo and x[6] == '2':
        total_matches += 1
    elif team_2_elo > team_1_elo and x[6] == '1':
        total_matches += 1

    for a in team_1_players:
        if not a.startswith("n/a"):
            new_elo = 0
            new_elo = player_current_elos.get(a)+rating_change
            player_current_elos.update({a:new_elo})
            if new_elo > player_peak_elos.get(a):
                player_peak_elos.update({a:new_elo})

    for a in team_2_players:
        if not a.startswith("n/a"):
            new_elo = 0
            new_elo = player_current_elos.get(a)-rating_change
            player_current_elos.update({a:new_elo})
            if new_elo > player_peak_elos.get(a):
                player_peak_elos.update({a:new_elo})



print("elo model correctly predicts " + str(total_correct/total_matches*100)+"% of matches correctly")


# 
with open('player_elos.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(["player","current_elo","peak_elo"])
    for a in player_current_elos:
        spamwriter.writerow([a, player_current_elos.get(a), player_peak_elos.get(a)])
# print(dict(sorted(players_elo_peak.items(), key=lambda item: item[1])))
        

