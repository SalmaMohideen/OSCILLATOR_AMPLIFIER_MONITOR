import sys
import numpy as np 
np.set_printoptions(threshold=sys.maxsize, linewidth = 10000000000000000)
import matplotlib.pyplot as plt 
import scienceplots
import time 
import os
from scipy import integrate
from time import sleep, localtime, strftime
from matplotlib.widgets import Button
from timeit import default_timer as timer
from seabreeze.spectrometers import Spectrometer

spec = Spectrometer.from_first_available()

#sets the livestream status to be True 
livestream_status = True


# the number of seconds in between data being measured (ie: 30 mins = 1800 seconds)
sleep_time = 10
integration_time = 100000
averages= 1

spec.averages = averages
spec.integration_time_micros = integration_time

# when save_name is None files are automatically saved with date and time
save_path = 'C:\\Users\\247HP2\\Documents\\GitHub\\Oscillator_Amplifier_Monitor\\Data'
save_name = None

#creates global varibales which will store the first spectrometer measurements
first_wavelengths = np.empty
first_intensities = np.empty


def find_elapsed_minutes(start_time):
    return  (timer() - start_time)/60


def close_all(val):
  plt.close('all')
  livestream_status = False 
  exit()


def find_noise(intensities, first_wavelengths):
    
    intensities_noise =np.empty(0)
    count = 0

    for i,w in  zip(intensities,first_wavelengths):
        if (530< w) and  (w <700):
            intensities_noise = np.append(intensities_noise, i)

        if (950< w) and  (w <1150):
            intensities_noise = np.append(intensities_noise, i)
    noise = np.average(intensities_noise)
    return noise 


def remove_noise(intensities, first_wavelengths):
    new_intensities = np.empty(0)

    noise = find_noise(intensities, first_wavelengths)

    for i in intensities:
        if i-noise >= 0:
            new_intensities = np.append(new_intensities, i-noise)
        else:
            new_intensities = np.append(new_intensities, 0)

    
    return callibrate_intensities(new_intensities, noise)


def callibrate_intensities(intensities, noise):
    new_intensities = np.empty(0)

    if (noise < 900): 
        # if it falls into the low noise category 
        b = 0.21329962061398458
        m = .0000028008446909143086
        
        
    elif (noise >= 900): 
        #  if it falls into the high noise category 
        b = 0.1399600187043221
        m = .000002924651417341623

    for i in intensities:
        new_intensities = np.append(new_intensities, (b+i*m))
    
    return new_intensities


def find_integrated_power(intensities, wavelengths):
    diffs = np.diff(wavelengths)
    sum = 0 


    for i in range(1,len(wavelengths)-1): 
        # integrating the area under the curve for peak wavelengths
        if(700<wavelengths[i]<900):
            height = 0.5*(intensities[i]+intensities[i-1])
            base  = wavelengths[i]-wavelengths[i-1] 
            sum += (height * base)
    print(sum)
    
    return sum 



def make_file(intensities, wavelength, integrated_power, save_dir,save_name ):
    if save_name is None:
        save_name = strftime('%Y-%m-%d_%H-%M-%S',localtime())

    file = os.path.join(save_dir, save_name) + '.txt'
    time = strftime('%Y-%m-%d_%H-%M-%S',localtime())
    with open(file, 'w') as f:
        f.write('time:'+time + '\n')
        f.write('power integrated:'+str(integrated_power)+ '\n')
        f.write('wavelength:'+str(wavelength)+ '\n')
        f.write('intensities:'+str(intensities)+ '\n')
    return file


def save_data(intensities,integrated_power,file):
    time = strftime('%Y-%m-%d_%H-%M-%S',localtime())
    with open(file, 'a') as f:
        f.write('time:'+time + '\n')
        f.write('power integrated:' + str(integrated_power)+ '\n')
        f.write('intensities:'+ str(intensities)+ '\n')


def main():
    start_time = timer()


    all_times = np.array(find_elapsed_minutes(start_time))
    all_times = np.append(all_times, find_elapsed_minutes(start_time))

    first_wavelengths = spec.wavelengths()[5::]
    first_intensities = remove_noise(spec.intensities()[5::], first_wavelengths)
    print(len (first_intensities))
    print(len(first_wavelengths))


    # power_integrated_array = np.array(find_integrated_power(first_intensities, 10*first_wavelengths))

    integrated_power = find_integrated_power(first_intensities, first_wavelengths)
    power_integrated_array = np.array(integrated_power)
    # print (power_integrated_array)
    # print(all_times)

    ift_first_intensities =  np.fft.ifftshift(first_intensities)
    # np.fft.ifftshift(first_intensities)

    all_intensities = np.delete(first_intensities, len(first_intensities)-1)
    transposed_intensities= np.transpose(all_intensities)
   
    plt.show()

    # plotting multiple axis in one figure; sub-plots in a figure 
    fig, axes = plt.subplots(1,2,figsize= (12,5.5) )
    axes[0].plot(first_wavelengths, first_intensities, '-', color = 'blue')
    axes[0].set_xlabel("wavelengths(nm)")
    axes[0].set_ylabel("intensities")



    axes[1].plot(first_wavelengths, first_intensities, "-",  color = 'purple', lw=1.5, ms = 3, label = 'Data Points')
    axes[1].set_xlabel("wavelengths(nm)")
    axes[1].set_ylabel("intensities")
 
    # defining button and add its functionality
    axes_button = plt.axes([0.43, 0.925, 0.15, 0.075])
    bnext = Button(axes_button, 'Save ALL and Close')
    bnext.on_clicked(close_all)


    filename = make_file(first_intensities, first_wavelengths, integrated_power, save_path, save_name)

    plt.ion()
    plt.show()
    plt.pause(10)
    plt.close('all')

    


    #ech time add new data to contour plot of spectrum over time 

    while livestream_status == True:    

        intensities_new = remove_noise(spec.intensities()[5:],first_wavelengths)

        # power_integrated_array = np.append(find_integrated_power(intensities_new, first_wavelengths))
        integrated_power = find_integrated_power(intensities_new, first_wavelengths)
        if integrated_power >= 10: 
            power_integrated_array = np.append(power_integrated_array,integrated_power)
            intensities_new_formatted = np.delete(intensities_new, len(intensities_new)-1)

            
            all_intensities = np.append(all_intensities, intensities_new_formatted, axis=0)    
            all_times = np.append(all_times,find_elapsed_minutes(start_time))
            
            intensities_2D =  np.reshape(all_intensities,(len(all_times)-1,len(first_intensities)-1))
        
            fig_1, axes_1 = plt.subplots(1,2,figsize= (12,5.5))
            fig_2, axes_2 = plt.subplots(1,2,figsize= (12,5.5))
            
            axes_1[0].plot(first_wavelengths, ift_first_intensities, color = 'orange')
            axes_1[0].plot(first_wavelengths, np.fft.ifftshift(intensities_new), color = 'blue')
            axes_1[0].set_xlabel("Time(s)")
            axes_1[0].set_ylabel("Intensities/nm")
            axes_1[0].set_title("Inverse Fourier Trans: Initial vs Current Intensities")


            axes_1[1].set_xlabel("Time(s)")
            axes_1[1].set_ylabel("Integrated Powers(nm)")
            axes_1[1].set_title("Integrated Powers vs Time")
            axes_1[1].plot(all_times[1::], power_integrated_array,"o")

            axes_2[0].plot(first_wavelengths, intensities_new, color = 'orange')
            axes_2[0].plot(first_wavelengths, first_intensities,color='blue')
            

            axes_2[0].set_xlabel("wavelengths(nm)")
            axes_2[0].set_ylabel("Watts/nm")
            axes_2[0].set_title("Line Plot: Initial vs Current Intensities")


            im = axes_2[1].pcolormesh(all_times, first_wavelengths, np.transpose(intensities_2D))
            fig_2.colorbar(im, label = 'light intensities Watts/nm')
            axes_2[1].set_xlabel("time(s)")
            axes_2[1].set_ylabel("wavelengths(nm)")
            axes_2[1].set_title("Color Plot: Intensities vs Time")
        
            # defining button and add its functionality
            axes_button = plt.axes([0.43, 0.925, 0.15, 0.075])
            bnext = Button(axes_button, 'Save ALL and Close')
            bnext.on_clicked(close_all)


            save_data(intensities_new, integrated_power, filename)

            
            plt.ion()
            plt.show()
            plt.pause(sleep_time)
            plt.close('all')

        else: 
            sleep(sleep_time)



if __name__ == "__main__":
    main()
