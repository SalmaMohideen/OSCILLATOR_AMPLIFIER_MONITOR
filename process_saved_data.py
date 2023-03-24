from scipy import integrate
import numpy as np
import matplotlib.pyplot as plt
from timeit import default_timer as timer




def find_elapsed_minutes(start_time, time):
    times = time.split('_')[1].split('-')
    start_times = start_time.split('_')[1].split('-')
    
    hours_diff = int(times[0]) - int(start_times[0])
    mins_diff = int(times[1]) - int(start_times[1])
    secs_diff = int(times[2]) - int(start_times[2])


    print(times)
    print(start_times)
    print  (hours_diff*60 + mins_diff + secs_diff/60)
    return (hours_diff*60 + mins_diff + secs_diff/60)



def main():
    filename = "C:\\Users\\247HP2\\Documents\\GitHub\\Oscillator_Amplifier_Monitor\\Data\\2023-03-23_21-40-44.txt"

    fig, axes = plt.subplots(1,2,figsize= (12,5.5) )
    fig1, axes1 = plt.subplots(1,2,figsize= (12,5.5) )

    file = open(filename, 'r')
    count = 0
    wavelengths = np.empty(0)
    intensities = np.empty(0)

    all_times = np.empty(0)
    all_intensities = np.empty(0)
    intensities_empty = True 
    start_time = None

    for line in file:
        
        line = line.replace('[','')
        line = line.replace(']','')
        line = line.strip().split(':')        
    
        if 'wavelength' in line[0]:
            print(line[0][0:10])
            wavelengths = np.fromstring(line[1], dtype=float, sep=' ')
            print(wavelengths)
            
        if 'time' in line[0]:
            if start_time == None: 
                all_times = 0
                start_time = line[1]

            print(line[0][0:5])
            time = line[1]
            elapsed_time = find_elapsed_minutes(start_time, time)
            all_times = np.append(all_times,elapsed_time)
            print("elapsed: ", elapsed_time)
            print(start_time)
            print(all_times)

        if 'intensities' in line[0]:
            
            print(line[0][0:11])
            intensities = np.fromstring(line[1], dtype=float, sep=' ')
            axes[0].plot(wavelengths, intensities, '-', label = time)
            axes[0].legend(loc='best')
            intensities_new_formatted = np.delete(intensities, len(intensities)-1)
            if intensities_empty: 
                all_intensities = intensities_new_formatted
                intensities_empty = False 
                

            else:
                all_intensities = np.append(all_intensities, intensities_new_formatted, axis=0)  
            # plt.show()
            print(np.size(all_intensities))

        if 'power integrated' in line[0]:
            print(line[0][0:16]) 
            power_integrated = float(line[1])
            print(power_integrated)
            axes1[0].plot(elapsed_time, power_integrated, "o")




        if not line:
            break
        if line == ['']:
            break
    
          



    
   
    intensities_2D =  np.reshape(all_intensities,(len(all_times)-1,len(intensities)-1))
    print('times', all_times)
    im = axes[1].pcolormesh(all_times, wavelengths, np.transpose(intensities_2D))
    fig.colorbar(im, label = 'light intensities')
    axes[1].set_xlabel("time(minutes)")
    axes[1].set_ylabel("wavelengths(nm)")
    axes[1].set_title("Color Plot: Intensities vs Time")
    axes[0].set_xlabel("Wavelengths (nm)")
    axes[0].set_ylabel("Intensities (watts/nm)")
    axes[0].set_title("Wavelengths vs Intensities")
    axes1[0].set_xlabel("Time(minutes)")
    axes1[0].set_ylabel("Integrated Intensities (watts)")
    axes1[0].set_title("Integrated Intensities vs Time")

    plt.show()
        



if __name__ == "__main__":
    main()
