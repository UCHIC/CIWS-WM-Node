# Import Packages


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mode
import sklearn.cluster as cluster
sns.set()
from sklearn.preprocessing import StandardScaler
from mpl_toolkits.mplot3d import Axes3D

#################################################################################
#DATA#

# Parse the string representation as dates
dateparse = lambda x: pd.datetime.strptime(x, '%y-%m-%d %H:%M:%S')

# Read csv data file as a dataframe where the index column is the date/time column
data = pd.read_csv('/home/pi/019_0003.csv',index_col ='Time',parse_dates = ['Time'], date_parser=dateparse, skiprows = 3)
data = data.drop(columns=['Record'])



#################################################################################
#DATA FILTERING#

# Copy the pulses attribute into a new array
signal = np.copy(data.Pulses.values)

# Remove noise (undesired extra pulses) in the trace

def removal(signal, repeat):
    copy_signal = np.copy(signal)
    for j in range(repeat):
        for i in range(1, len(signal)):
            copy_signal[i - 1] = (copy_signal[i - 2] + copy_signal[i]) // 2
    return copy_signal

# Generate the new series

def get(original_signal, removed_signal):
    buffer = []
    for i in range(len(removed_signal)):
        buffer.append(original_signal[i] - removed_signal[i])
    return np.array(buffer)

removed_signal = removal(signal, 1)
noise = get(signal, removed_signal)

Time = np.copy(data.index)
Signal = np.copy(data.Pulses.values)
Removed_signal = removal(Signal, 1)
Noise = get(Signal, Removed_signal)

WaterData = pd.DataFrame({'Time':Time, 'FilteredData':Removed_signal, 'OriginalData':Signal })

for i in range(len(WaterData)) :
    if (WaterData.loc[i , "OriginalData"] >= 1 and WaterData.loc[i, "FilteredData"] == 0):
        WaterData.loc[i, 'FilteredData'] = WaterData.loc[i , "OriginalData"]

    if (WaterData.loc[i , "OriginalData"] == 0 and WaterData.loc[i, "FilteredData"] >= 1):
        WaterData.loc[i, 'FilteredData'] = 0


#################################################################################
#FEATURE EXTRACTION#

# Create a blank dataframe to store events features in it
EventsDF = pd.DataFrame(columns = ['ID','StartTime', 'EndTime', 'FilteredVolume','FilteredDuration','FilteredFlowRate', 'OriginalVolume', 'OriginalDuration', 'OriginalFlowRate', 'RMS', 'Number_of_peaks', 'Peak_Value' ,'Mode_Value', 'Event_Type'])

# Create a blank dataframe to store overlapping non aggregated events in it
OL_Events = pd.DataFrame(columns = ['Time', 'FilteredData', 'OriginalData' , 'Type'])

pulse = 0 # number of pulses in the filtered trace
pulse2 = 0 # number of pulses in the original trace
i = 0 # Array index
j = 0 # Array index
duration = 0 # the duration of an event/s
k = 0 # Array index
st = '' # starting time
et = '' # end time
Dominant_Flow = 0
LList = [] # list of water use pulses of same event/s
V = 0 # number of different vertices of event/s
VV = 0
Peak = 0 # peak water use value of event/s
Dom_Test = [] # a list of flows used to evaluate the dominancy of the dominant flow
DT = 0 # Array index
counter3 = 0 # dominancy count of different flow rate values
OL = 3 # Binary variable, if 1: the event is overlapping, if 0 the event is single
Pulse = 0 # single pulse value in the filtered trace
Pulse2 = 0 # single pulse value in the original trace
Time = '' # time increments in the disaggregated set
I = 0 # Array index
J = 0 # Array index
S = 3
counter = 0
Index = 0

# Loop thru water use data (filtered)
while (i < len(WaterData) - 1):
    if(WaterData.loc[i, "FilteredData"] == 0):
        i = i + 1
        k = k + 1
        I = I + 1
    elif(WaterData.loc[i, "FilteredData"] != 0):
        k = i
        st = WaterData.loc[k - 1, "Time"] # initialize the starting time of an event ZZZZZZZ updated original bd filtered####
        while(WaterData.loc[i, "FilteredData"] != 0):
            pulse = pulse + WaterData.loc[i, "FilteredData"] # accumulate the number of pulses of and event from filtered data
            pulse2 = pulse2 + WaterData.loc[i, "OriginalData"] # accumulate the number of pulses of an event from original data
            duration = duration + 4 # calculate the duration of an event
            et = WaterData.loc[i , "Time"] # the end time of an event ############
            LList.append(WaterData.loc[i, "FilteredData"].tolist()) # List of pulse values of an event
            i = i + 1
        Dominant_Flow = mode(LList) # the dominant flow of an event
        Dominant_Flow = int(Dominant_Flow[0])
        Peak = max(LList) # the peak value of an event
        peak = max(LList)
        X = np.array(LList)


        for z in range(len(LList) - 2): # Number of different vertices in an event
            if((LList[z+1] == LList[z] and LList[z+1] != LList[z+2]) or (LList[z+1] != LList[z] and LList[z+1] != LList[z+2])):
                V = V + 1


        for z in range(len(LList) - 2): # Number of different vertices in an event
            if(LList[z+1] != LList[z] and LList[z+1] == LList[z+2]):
                VV = VV + 1



        NDF = sum(1 for x in LList if x == Dominant_Flow)


        RMS = np.sqrt(np.mean(X**2))



        # Test 1: check the value of dominant flow - RMS. Multiple events are more likely to have -ve values for this test
        Test1 = Dominant_Flow - RMS

        # Test 2 : check the number of vertices. if more than 2, it is more likely to be multiple event given that test 1 value is -ve
        Test2 = VV

        # Test 3 : check the frequency of the dominant flow vs the frequency of the peak flow
        Test3 = NDF - LList.count(Peak)

        # Test 4: check weahter the peak flow equals the dominant flow
        Test4 = Peak - Dominant_Flow


        ###############################################
        # Uploading features in the EventsDF dataframe
        ###############################################

        EventsDF.loc[j,'ID'] = Index + 1
        Index = Index + 1
        EventsDF.loc[j,'StartTime'] = st # starting time of event
        EventsDF.loc[j,'EndTime'] = et # end time of event
        EventsDF.loc[j,'FilteredVolume'] = (pulse * 0.041619) # Volume in gals
        EventsDF.loc[j,'FilteredDuration'] = duration/60
        EventsDF.loc[j,'FilteredFlowRate'] =  ((pulse * 0.041619)/((duration/60)))  #0.041619
        EventsDF.loc[j,'OriginalVolume'] = pulse2 * 0.041619
        EventsDF.loc[j,'OriginalDuration'] = duration/60
        EventsDF.loc[j,'OriginalFlowRate'] =  ((pulse2 * 0.041619)/((duration/60)))
        EventsDF.loc[j,'RMS'] = RMS
        EventsDF.loc[j,'Number_of_peaks'] = VV  #np.sqrt(np.mean(X**2))
        EventsDF.loc[j,'Peak_Value'] = (Peak )#* 0.041619) # Value in gals
        EventsDF.loc[j,'Mode_Value'] = Dominant_Flow
        if (Test1 < 0 and Test2 > 3 and Test3 > 1 and Test4 > 1):
            EventsDF.loc[j, 'Event_Type'] = "Multiple"
        else:
            EventsDF.loc[j, 'Event_Type'] = "Single"

        if (pulse2 <=2 or duration == 4):
            EventsDF.loc[j, 'Event_Type'] = "Unclassified"


        ###############################################
        # Events as increments
        ###############################################

        while(WaterData.loc[I, "FilteredData"] != 0 ):  #### Updated
            Pulse = WaterData.loc[I,"FilteredData"]
            Pulse2 = WaterData.loc[I, "OriginalData"]
            Time = WaterData.loc[I,"Time"]
            OL_Events.loc[J, 'Time'] = Time
            OL_Events.loc[J, 'FilteredData'] = Pulse
            OL_Events.loc[J, 'OriginalData'] = Pulse2
            if(Test1 < 0 and Test2 > 3 and Test3 > 1 and Test4 > 1):
                OL_Events.loc[J,'Type'] = "Multiple"
            else:
                OL_Events.loc[J,'Type'] = "Single"

            if (pulse2 <=2):
                EventsDF.loc[j, 'Event_Type'] = "Unclassified"


            I = I + 1
            J = J + 1

        ##############################################

        pulse = 0
        pulse2 = 0
        duration = 0
        Peak = 0
        peak = 0
        j = j + 1
        st = ''
        et = ''
        Dominant_Flow = 0
        LList.clear()
        V = 0
        VV = 0
        num_DF = 0
        NDF = 0
        DT = 0
        counter3 = 0 # ADDED
        Dom_Test.clear()
        OL = 3
        ST = 0
        S = 3
        Pulse = 0
        Pulse2 = 0
        Time = ''
        J = J + 1
        RMS = 0


# Single Events
SingleEvents = EventsDF[EventsDF['Event_Type'] == "Single"].reset_index(drop=True)

# Multiple Events
MultipleEvents = EventsDF[EventsDF['Event_Type'] == "Multiple"].reset_index(drop=True)

# Unclassified Events
UnclassifiedEvents = EventsDF[EventsDF['Event_Type'] == "Unclassified"].reset_index(drop=True)

# Multiple Events As Increments
MultipleEventsIncrements = OL_Events[OL_Events['Type'] == "Multiple"].reset_index(drop=True)


#################################################################################
#OVERLAPPING EVENTS#

Pulse = 0 # number of pulses of an event in filtered data
Pulse2 = 0 # number of pulses of an event in original data
i = 0 # Array index
j = 0 # Array index
st = '' # starting time of an event
et = '' # end time of an event
cutoff = 0 # cutoff value for overlapping events
counter = 0 #Array index
LList = [] # list of pulses of an event from filtered data
SG = 0 # a copy of list of pulses of an event from filtered data
peak = 0 # peak value of an event
LList2 = [] # list of pulses of an event from original data
SG2 = 0 # a copy of list of pulses of an event from original data
counter2 = 0 # Array index
SI = 0 # Index of first element greater than 0 in an array
V = 0 # number of vertices
num_DF = 0 # number of pulses of dominant flow
NDF = 0 # dominant flow presistance index
DT = 0 # Array index
counter3 = 0 #Array index
Dom_Test.clear() # a list of flows used to evaluate the dominancy of the dominant flow
OL = 0 # Binary variable, if 1: cutoff = 2nd dominant flow, if 0: cutoff = dominant flow
ST = 0 # Array of pulses sorted in decending order
STT = 0 # Array of pulses sorted in ascending order

# Initilize a dataframe and store seperated overlapping events features into it (simplified overlapping events)
SOLE = pd.DataFrame(columns = ['StartTime', 'EndTime', 'FilteredVolume','FilteredDuration', 'FilteredFlowRate', 'OriginalVolume', 'OriginalDuration', 'OriginalFlowRate', 'RMS', 'Number_of_peaks', 'Peak_Value' ,'Mode_Value'])
MEI = MultipleEventsIncrements.copy()

# Multiple events Disaggregation

while (i < (len(MEI) - 1)):
    while (((MEI.loc[i + 1, 'Time'] - MEI.loc[i, 'Time']).seconds == 4)):
        LList.append(MEI.loc[i, 'FilteredData'].tolist()) ##
        LList2.append(MEI.loc[i, 'OriginalData'].tolist()) ##ADDDED
        i = i + 1
        if (i + 1 == len(MEI)):
            break


    SG = LList.copy()
    SG2 = LList2.copy()
    peak = max(LList)
    cutoff = mode(LList)
    CO = int(cutoff[0])
    X = np.array(LList)

    #######################################################################
    # Disaggregation Part: one overlapping event = multiple single events
    #######################################################################

    # Inspect some features first to determine the cutoff value of the first event

    while(max(SG)>0):


        for z in range(len(LList) - 2): # Number of different vertices in an event
            if(LList[z+1] != LList[z] and LList[z+1] == LList[z+2]):
                V = V + 1


        NDF = sum(1 for x in LList if x == Dominant_Flow) #Dominancy Test


        RMS = np.sqrt(np.mean(X**2))


        while((max(SG) - DT) > 0):
            counter3 = SG.count((max(SG)) - DT)
            Dom_Test.append(counter3)
            DT = DT + 1

        Dom_Test.sort(reverse = True)



        # Sort values in an array to select the cutoff value
        ST = list(set(SG))
        ST.sort(reverse = True)

        STT = list(set(SG))
        STT.sort()


        res = []
        for val in STT:
            if val != 0 :
                res.append(val)
        res.sort(reverse = True)



        SI = next(x for x, val in enumerate(SG)   #Get the Index of first element greater than 0 and set it as the starting time
                 if val > 0)


        while (j <= (len(SG) - 1) and SG[j] > 0 ):
            counter = counter +1
            if(SG[j] >= CO):
                Pulse = Pulse + CO
                Pulse2 = Pulse2 + CO
                SG[j] = SG[j] - CO
                SG2[j] = SG2[j] - CO

            elif(SG[j] < CO):
                Pulse = Pulse + SG[j]
                if (SG2[j] > 0):
                    Pulse2 = Pulse2 + SG2[j]
                SG[j] = SG[j] - SG[j]
                SG2[j] = SG2[j] - SG2[j]


            if (SG2[j] > 0 and SG[j] ==0):
                counter2 = counter2 + SG2[j]
                SG2[j] = 0

            j = j + 1
            if (j == len(SG)):
                break

        if (counter !=0):
            SOLE.loc[k,'FilteredVolume'] = Pulse * 0.041619
            SOLE.loc[k,'FilteredDuration'] = ((counter) *4)/60
            SOLE.loc[k,'FilteredFlowRate'] = (Pulse * 0.041619)/(((counter ) * 4)/60)
            SOLE.loc[k,'OriginalVolume'] = (Pulse2 + counter2) * 0.04169
            SOLE.loc[k,'OriginalDuration'] = ((counter) *4)/60
            SOLE.loc[k,'OriginalFlowRate'] = (Pulse2 * 0.041619)/(((counter ) * 4)/60)
            SOLE.loc[k,'StartTime'] = MEI.loc[i - len(SG) + SI + 1, 'Time'] ######
            SOLE.loc[k,'EndTime'] = MEI.loc[i - len(SG) + j, 'Time']  ########
            SOLE.loc[k, 'Number_of_peaks'] = V
            SOLE.loc[k, 'RMS'] = RMS
            SOLE.loc[k, 'Peak_Value'] = peak
            SOLE.loc[k, 'Mode_Value'] = CO



            k = k + 1
            j = 0



        # Cutoff check

        cutoff = int(mode(SG)[0])
        CO = cutoff



        if(counter == 0):
            j = j + 1
        else:
            j = 0


        counter = 0
        counter2 = 0
        Pulse = 0
        Pulse2 = 0
        t1 = 0
        t2 = 0

        if ((j > len(SG) - 1)):
            j = 0

        if (max(SG) == 0):
            break

        if (CO ==0):
            res = []
            for val in SG:
                if val != 0:
                    res.append(val)
            cutoff = int(mode(res)[0])
            CO = cutoff

        V = 0
        num_DF = 0
        NDF = 0
        counter3  = 0
        Dom_Test.clear()
        DT = 0
        OL = 0
        ST = 0
        STT = 0


        for z in range (len(SG) - 2):
            if(SG[z+1] == SG[z] and SG[z+1] != SG[z+2] and SG[z+1] != 0 and SG[z+2] != 0 and SG[z] != 0):
                V = V + 1

        DF = np.array(SG)
        num_DF = (DF == max(SG)).sum
        NDF = num_DF

        while((max(SG) - DT) > 0):
            counter3 = SG.count((max(SG)) - DT)
            Dom_Test.append(counter3)
            DT = DT + 1

        Dom_Test.sort(reverse = True)

        for z in range (len(Dom_Test) - 1):
            if ((Dom_Test[0] - Dom_Test[1]) <= 3):
                OL = 1
            else:
                OL = 0

        ST = list(set(SG))
        ST.sort(reverse = True)

        STT = list(set(SG))
        STT.sort()


        res = []
        for val in STT:
            if val != 0:
                res.append(val)
        res.sort(reverse = True)


        if (CO == max(SG) or V < 2 or NDF == 2 or NDF == 1 or NDF == 0):
            CO = max(SG)


        else:
            CO = int(res[1])


        V = 0
        num_DF = 0
        NDF = 0
        DT = 0
        counter3 = 0
        Dom_Test.clear()
        OL = 0
        ST = 0
        STT = 0
        res = []





    i = i + 1
    LList.clear()
    SG.clear()
    LList2.clear()
    SG2.clear()

SOLE = SOLE.reset_index(drop=True)


#################################################################################
#VOLUME CHECK#
Original_Volume = WaterData['OriginalData'].sum() * 0.041619
print("Water use volume from the original dataset is", Original_Volume, "Gal")

SingleEvents_Volume = SingleEvents['OriginalVolume'].sum()
MultipleEvents_Volume = SOLE['OriginalVolume'].sum()
UnclassifiedEvents_Volume = UnclassifiedEvents['OriginalVolume'].sum()
Total_Volume = SingleEvents_Volume + MultipleEvents_Volume + UnclassifiedEvents_Volume

print("Water use volume from the disaggregated dataset is", Total_Volume, "Gal")

print("Water use volume difference is", abs(Total_Volume - Original_Volume) , "Gal")


#################################################################################
#CLUSTERING#

SingleEvents_Copy = SingleEvents.drop(columns=['Event_Type', 'ID'])
SOLE_Copy = SOLE.copy()

Events = pd.concat([SingleEvents_Copy, SOLE_Copy], ignore_index = True)

features = [ 'OriginalVolume','OriginalDuration', 'Mode_Value']
featureLabels = [ 'Volume(gal)','Duration (min)',  'Mode_Value (gal)']

# Get a new data frame (df_sub) with just the "Features" of the events we are interested in for clustering
Events_sub = Events[features].copy()

# Scale the data as before using the SciKit StandardScaler object
scaler = StandardScaler()
scaler.fit(Events_sub)
scaledData = scaler.transform(Events_sub)
df_sub_scaled = pd.DataFrame.from_records(scaledData, columns=features)

def generate_3d_plot(plot_df, plot_features, plot_labels, cluster_labels):
    """Generate a 3D scatter plot for 3 variables

    :param plot_df: The data frame that contains the data for the features to plot
    :param plot_features: A list of 3 variables/features to plot
    :param plot_labels: A list of 3 axes labels to correspond to the plotted variables
    :param cluster_labels: An ndarray that contains the labels for how to color the points
    :return: Nothing
    """
    # Plot the data for the 3 Features of the events in 3 dimensions to have a quick look
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Create the scatter plot - first 3 parameters are x, y, and z values
    ax.scatter(plot_df[plot_features[0]], plot_df[plot_features[1]], plot_df[plot_features[2]],
               c=cluster_labels, marker='o', edgecolor='black')
    # Set the labels on the 3 axes
    ax.set_xlabel(plot_labels[0])
    ax.set_ylabel(plot_labels[1])
    ax.set_zlabel(plot_labels[2])
    plt.show()

    # open file or show dialog asking for the number of clusters/ number of end uses inside a household. Elbow method might underestimate the numbers since faucets and showers are expected to have similar flow rates but with different durations


clusterModel = cluster.AffinityPropagation(preference = -17.0)
# Fit the model to the scaled data
clusterModel.fit(df_sub_scaled)


# Use the K-means predict() function to use the model we just created to
# predict which cluster each of the events falls into. The labels object
# contains a label for for each event indicating which cluster it belongs to
labels = clusterModel.predict(df_sub_scaled)


# Create a 3-dimensional plot of the scaled event data and color each event
# based on the cluster labels - Call the function to generate the 3D plot
generate_3d_plot(Events_sub, features, featureLabels, labels)

# Add the cluster labels as a new series to the data frame of events
# that doesn't include the outlier events
Events['Cluster'] = labels

# Write the event data with cluster numbers out to a CSV file
Events.to_csv('/home/pi/ClusterEventsData.csv', index = None, header=True)

print('Done!')







