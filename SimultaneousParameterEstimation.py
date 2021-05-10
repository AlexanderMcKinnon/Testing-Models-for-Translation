from FullAnalysis_functions import *
from parameter_and_initial_values import *
from CreateReactionFunctions import *
from scipy.optimize import *
import scipy
from scipy.integrate import *
import numpy as np

def SimultaneousParameterEstimation(information_lists, information_lists_labels):
    Models_tempdict = {}
    Reaction_functions_tempdict = {}
    Initial_values_tempdict = {}
    Rates_values_tempdict = {}
    Rates_indexes_tempdict = {}
    Protein_Indexes_tempdict = {}
    for i in range(len(information_lists)):
        temp_dict = CreateReactionFunction(information_lists[i])
        Models_tempdict[information_lists_labels[i]] = temp_dict["Model"]
        Reaction_functions_tempdict[information_lists_labels[i]] = temp_dict["Reaction_functions"]
        Initial_values_tempdict[information_lists_labels[i]] = temp_dict["Initial_values"]
        Rates_values_tempdict[information_lists_labels[i]] = temp_dict["Rates_values"]
        Rates_indexes_tempdict[information_lists_labels[i]] = temp_dict["Rates_indexes"]
        Protein_Indexes_tempdict[information_lists_labels[i]] = temp_dict["Protien_indexes"]
    
    experimental_data_indecies = ["P_G", "P_R"]
    experimental_estimation_data = []
    for i in range(len(information_lists_labels)):
        for j in range(len(experimental_data_indecies)):
            experimental_estimation_data = np.concatenate((experimental_estimation_data, experimental_data[information_lists_labels[i]][experimental_data_indecies[j]]))

    rates_string = ""
    for i in range(len(list(Rates_values_dict.keys()))):
        rates_string = rates_string + list(Rates_values_dict.keys())[i]+","
        
    exec('''def model_predict(t,'''+rates_string+'''):\n
        \t import scipy.integrate \n
        \t import numpy as np \n
        \t from parameter_and_initial_values import time_points\n
        \t output_data = []\n
        \t rate_list = ['''+rates_string+''']\n
        \t for i in range(len(information_lists_labels)): \n
        \t\t    simulation_results_parameter_estimation = scipy.integrate.odeint(Models_tempdict[information_lists_labels[i]], Initial_values_tempdict[information_lists_labels[i]], t, args=(Reaction_functions_tempdict[information_lists_labels[i]], tuple([rate_list[int(j)] for j in Rates_indexes_tempdict[information_lists_labels[i]]])))\n
        \t\t    for j in range(len(Protein_Indexes_tempdict[information_lists_labels[i]])):\n
        \t\t\t      output_data = np.concatenate((output_data, simulation_results_parameter_estimation[time_points][:, Protein_Indexes_tempdict[information_lists_labels[i]][j]]))\n
        \t return output_data\n''', locals(), globals())


    bounds = np.zeros([2,len(list(Rates_values_dict.keys()))])
    for i in range(len(list(Rates_values_dict.keys()))):
        bounds[:,i] = Rates_bounds_dict[list(Rates_values_dict.keys())[i]]



    t = np.linspace(0, t_max, n) 
    import scipy
    import scipy.integrate
    popt, pcov = scipy.optimize.curve_fit(model_predict, t, experimental_estimation_data, bounds=bounds)
    
    print("-----------------------------------------------------------------")
    print("|      Rates\t|     Initial Values\t|   Estimated Values\t|")
    print("-----------------------------------------------------------------")
    for i in range(len(popt)):
        initial_rate_value = round(list(Rates_values_dict.keys())[i], 3 - int(math.floor(math.log10(abs(list(Rates_values_dict.keys())[i])))) - 1)
        final_rate_value = round(popt[i], 3 - int(math.floor(math.log10(abs(popt[i])))) - 1)
        print("|",list(Rates_values_dict.keys())[i],"\t\t|" if len(list(Rates_values_dict.keys())[i])<=4 else "\t|" , initial_rate_value,"\t\t\t|" if len(str(initial_rate_value))<=4 else "\t\t|" , final_rate_value,"\t\t\t|" if len(str(final_rate_value))<=4 else "\t\t|")
    print("-----------------------------------------------------------------")
    
    
    
    return