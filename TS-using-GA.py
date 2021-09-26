import numpy as np
import random 
import matplotlib.pyplot as plt
import copy


###################################################################################
def get_preferences(nNurses): #Function to get the preferences of the Nurses
    preferences = np.zeros((nNurses,3)) #Initial preferences array
    for i in range(nNurses):
        preferencesi = preferences[i]
        for j in range(3):
            #preferencesi[j] = input("Enter Nurse " + str(i+1) + " preference day to off day " +str(j+1)+": ")
            preferencesi[j] = np.random.randint(1,7)
    return preferences
#################################################################################################################
def init_pop(nNurses,npop): #Function to initialize the pop of schedules
    total_shifts = (nNurses*npop) * 7  #Calculate Total shifts  = Number of nurses * number of schedules * 7 days
    print("total shifts: ",total_shifts)
    total_day_off = (nNurses*npop)*3 # Calculate Total day offs  = Number of nurses * number of schedules * 3 day off per week for each nurse
    print("total total day offs: ",total_day_off)
    remaining_shifts = total_shifts - total_day_off # Calculate remaining shifts = Total shifts - total day offs
    print("total remaining_shifts: ",remaining_shifts)
    total_night_shifts = int(remaining_shifts/3) # Calculate Total night shifts = (1/3) * remaining shifts 
    print("total_night_shifts: ",total_night_shifts)
    total_day_shifts = remaining_shifts - total_night_shifts  # Calculate Total day shifts = remaining shifts - total night shifts 
    print("total_day_shifts: ",total_day_shifts)
    pop = np.zeros((nNurses*npop,7),dtype='<U5') #initialize the pop(schedules) 
    shifts = ['D','A','N'] #shifts --> D("Day shift") - A("Afternoon shift") - N("Night shift")
    for i in range(nNurses*npop):
        days = [0,1,2,3,4,5,6] #Array to handle the days 
        si = pop[i]
        for i in range(3):   #hard constraint : every nurse can take 3 off days per week
            offday = random.choice(days) #random day 
            si[offday] = 'O' #Set the off day in random day 
            days.remove(offday)
        while(len(days) >= 1):
            shift = random.choice(days)
            si[shift] = random.choice(shifts)
            days.remove(shift)
    for i in range(nNurses*npop):
        si = pop[i]
        for j in range(7):
            if(j == 6):
                break
            else:
                if(si[j]=='N' and si[j+1] == 'D'): #handling hard constraint that no Night shift follwed by a day shift
                    si[j+1] = random.choice(['N','A'])
    return pop
#######################################################################################################################3

############################################################################################################################
def calc_fitness_individual(individual,nNurses,preferences): #Function to calculate the fitness of the Schedule by penalty method
    fitness_individual = 0
    w1 = 0.5 # Weight of Constraint 1
    w2 = 0.24 # Weight of Constraint 2
    w3 = 0.24 # Weight of Constraint 3
    w4 = 0.1 # Weight of Constraint 4
    w5 = 0.1 # Weight of Constraint 5
    v1 = 0 # Number of violations of constraint 1
    v2 = 0 # Number of violations of constraint 2
    v3 = 0 # Number of violations of constraint 3
    v4 = 0 # Number of violations of constraint 4
    v5 = 0 # Number of violations of constraint 5
    # Soft Constraint 1 : |Number of day shifts - Number of afternoon shifts - Number of night shifts| should be > 1 
    count_Day_shifts =  np.count_nonzero(individual == 'D', axis = 0) # Count The day shifts per day
    count_Afternon_shifts =  np.count_nonzero(individual == 'A', axis = 0) # Count The afternoon shifts per day
    count_Night_shifts =  np.count_nonzero(individual == 'N', axis = 0) # Count The night shifts per day
    for i in range(7):
        if (abs(count_Day_shifts[i] - count_Afternon_shifts[i] - count_Night_shifts[i]) > 1 ):
            v1 += 1
    #......................................................................................................
    #Soft Constraint 2 : two Day shifts follwed by an off day
    for i in range(nNurses):
        individuali = individual[i]
        for j in range(7):
            if(j == 5):
                break
            if(individuali[j]=='D' and individuali[j+1] == 'D' and individuali[j+2] =='N'):
                v2 += 1
            elif(individuali[j]=='D' and individuali[j+1] == 'D' and individuali[j+2] =='A'):
                v2 += 1
            elif(individuali[j]=='D' and individuali[j+1] == 'D' and individuali[j+2] =='D'):
                v2 += 1
    #................................................................................................
    #Soft Constraint 3 : Night shift +  off days follwed by a night or an off day
    for i in range(nNurses):
        individuali = individual[i]
        for j in range(7):
            if(j == 5):
                break
            if(individuali[j]=='N' and individuali[j+1] == 'O' and individuali[j+2] =='D'):
                v3 += 1
            elif(individuali[j]=='N' and individuali[j+1] == 'O' and individuali[j+2] =='A'):
                v3 += 1
    #..................................................................................................
    #Soft Constraint 4 : each nurse can't take a three consecutive off days
    for i in range(nNurses):
        individuali = individual[i]
        for j in range(7):
            if(j == 5):
                break
            if(individuali[j]=='O' and individuali[j+1] == 'O' and individuali[j+2] =='O'):
                v4 += 1
    #.................................................................................................
    #Soft Constraint 5 : trying to matching the preferences of off days of each nurse
    for i in range(nNurses):
        individuali = individual[i]
        preferencesi = preferences[i]
        for j in range(7):
            if(individuali[int(preferencesi[0])-1] != 'O' and individuali[int(preferencesi[1])-1] != 'O' and individuali[int(preferencesi[2])-1] != 'O'):
                v5 += 1
    #.........................................................................................................
    fitness_individual  = (w1*v1)+((w2*v2)+(w3*v3)+(w4*v4)+(w5*v5)) #Calcultae the fitness
    return fitness_individual
########################################################################################################################
def calc_pop_fit(pop,npop,nNurses,preferences): #Function to calculate the fitness of all schedules
    fit = []
    for i in range(npop):
        fit.append(calc_fitness_individual(pop[i],nNurses,preferences))
    return fit
#########################################################################################################################3
def tournament(pop,tour_size,fit,nNurses): #Function to do Tournament selection
    two_winners= [0.0,0.0]
    two_parents = np.zeros((nNurses*2,7),dtype='<U5')
    two_parents = np.split(two_parents, 2)
    for i in range(2):
        two_fitness = np.random.choice(fit, tour_size)
        two_winners[i] = np.amin(two_fitness)
        two_parents[i] = pop[fit.index(two_winners[i])]
    return two_parents
################################################################################################################################
def crossover(two_parents,nNurses): # Crossover function
    two_childs = two_parents
    parent1 = two_parents[0]
    parent2 = two_parents[1]
    n = np.random.randint(1,(nNurses/2)+1)
    child1 = two_childs[0]
    child2 = two_childs[1]
    nurses = np.zeros(n)
    for i in range(n):
        nurses[i] = int(i)
    for i in range(n):
        nurse  = int(random.choice(nurses))
        x = copy.copy(child1[nurse])
        y = copy.copy(child2[nurse])
        child1[nurse] = y
        child2[nurse] = x
        nurses = np.delete(nurses, np.where(nurses == nurse))
        
        
    return two_childs
###################################################
def mutation(two_childs,pmute,nNurses): #Mutation Function
    child1 = two_childs[0]
    child2 = two_childs[1]
    #......Child 1 mutation................
    for i in range(nNurses):
        child1i = child1[i]
        for j in range(7):
            if(j == 5):
                break
            if(child1i[j] == 'D' and child1i[j+1] == 'D' and child1i[j+2] == 'N'):
                p = np.random.random()
                if(p < pmute):
                    child1i[j+2] = 'O'
            elif(child1i[j] == 'D' and child1i[j+1] == 'D' and child1i[j+2] == 'D'):
                p = np.random.random()
                if(p < pmute):
                    child1i[j+2] = 'O'
            elif(child1i[j] == 'D' and child1i[j+1] == 'D' and child1i[j+2] == 'A'):
                p = np.random.random()
                if(p < pmute):
                    child1i[j+2] = 'O'
            else:
                child1i = child1i
        for j in range(7):
            if(j == 5):
                break
            if(child1i[j] == 'N' and child1i[j+1] == 'O' and child1i[j+2] == 'D'):
                p = np.random.random()
                if(p < pmute):
                    child1i[j+2] = 'N'
            elif(child1i[j] == 'N' and child1i[j+1] == 'O' and child1i[j+2] == 'A'):
                p = np.random.random()
                if(p < pmute):
                    child1i[j+2] = 'N'
            else:
                child1i = child1i
    #......Child 2 mutation.................
    for i in range(nNurses):
        child2i = child2[i]
        for j in range(7):
            if(j == 5):
                break
            if(child2i[j] == 'D' and child2i[j+1] == 'D' and child2i[j+2] == 'N'):
                p = np.random.random()
                if(p < pmute):
                    child2i[j+2] = 'O'
            elif(child2i[j] == 'D' and child2i[j+1] == 'D' and child2i[j+2] == 'D'):
                p = np.random.random()
                if(p < pmute):
                    child2i[j+2] = 'O'
            elif(child2i[j] == 'D' and child2i[j+1] == 'D' and child2i[j+2] == 'A'):
                p = np.random.random()
                if(p < pmute):
                    child2i[j+2] = 'O'
            else:
                child2i = child2i
        for j in range(7):
            if(j == 5):
                break
            if(child2i[j] == 'N' and child2i[j+1] == 'O' and child2i[j+2] == 'D'):
                p = np.random.random()
                if(p < pmute):
                    child2i[j+2] = 'N'
            elif(child2i[j] == 'N' and child2i[j+1] == 'O' and child2i[j+2] == 'A'):
                p = np.random.random()
                if(p < pmute):
                    child2i[j+2] = 'N'
            else:
                child2i = child2i
    return two_childs
#############################################################################################################
def NRP(npop,nNurses,ngen,pcross,pmute,tour_size): #Main function
    all = []
    print("Nurses Rostering  Problem")
    print("--------------------")
    pop = init_pop(nNurses,npop) 
    print(pop)
    pop = np.split(pop, npop)
    preferences = get_preferences(nNurses)
   
    fit = calc_pop_fit(pop,npop,nNurses,preferences)
    new_pop = pop
    c=0
    while(c <ngen):
        
        r = 0

        for i in range(0,int(npop/2)):
            ppcross = np.random.random()
            while True:
                two_parents = tournament(pop,tour_size,fit,nNurses)
                comparison = two_parents[0] == two_parents[1]
                equal_parents = comparison.all()
                if(equal_parents == True):
                    two_parents = tournament(pop,tour_size,fit,nNurses)
                else:
                    break

            Day_shifts_p1 =  np.count_nonzero(two_parents[0] == 'D')
            Night_shifts_p1 =  np.count_nonzero(two_parents[0] == 'N')
            Afternon_shifts_p1 =  np.count_nonzero(two_parents[0] == 'A')
            Day_shifts_p2 =  np.count_nonzero(two_parents[1] == 'D')
            Night_shifts_p2 =  np.count_nonzero(two_parents[1] == 'N')
            Afternon_shifts_p2 =  np.count_nonzero(two_parents[1] == 'A')
            
            if(Day_shifts_p1 == Day_shifts_p2 and Night_shifts_p1 == Night_shifts_p2 and Afternon_shifts_p1 == Afternon_shifts_p2 and ppcross < pcross):
                two_childs = crossover(two_parents,nNurses)

            else:
                two_childs = two_parents

            two_childs = mutation(two_childs,pmute,nNurses)
            new_pop[r] = two_childs[0] 
            new_pop[r+1] = two_childs[1] 
            r = r+2
        pop = new_pop #Replace the old pop with the new one
        fit = calc_pop_fit(pop,npop,nNurses,preferences)
        if(c==0):
            first_fit = fit
            print(first_fit)
        elif(c==(ngen-1)):
            last_fit = fit
            print(last_fit)
        c += 1
    plt.plot(np.arange(npop), first_fit, label='FirstGeneration')
    plt.plot(np.arange(npop), last_fit, label='LastGeneration')
    plt.legend()
    plt.xlabel("Schedules")
    plt.ylabel("Schedule fitness")
    plt.show()
##########################################################################################
npop = 100
nNurses = int(input("Enter Number of Nurses in the hospital: "))
ngen = 5
pcross = 0.8
pmute = 0.001
tour_size = 5
NRP(npop,nNurses,ngen,pcross,pmute,tour_size)
