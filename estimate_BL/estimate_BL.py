import numpy as np
import os, shutil

## inputs
folder_inputs   = 'C:/Material/Projects/Aeroacoustics/verifyAA/OpenFAST_IEA_LB_RWT/Airfoils'
path2xfoil      = 'C:/Material/Programs/xfoil/'
folder_outputs  = folder_inputs
n_stations      = 30
aoa             = np.linspace(-5., 25., 30)             # List of angles of attack
Re              = np.array([0.5e+06, 1.e+06, 5.e+06, 10.e+06])  # List of Reynolds numbers
TEoffset        = 1 # Number of nodes away from the TE where the BL properties are extracted, TEoffset = 0 is prone to convergence issues 
trip            = 0 # Flag to set free (0) or force (1)

## code

inputs_list  = []
outputs_list = []
for i in range(n_stations):
        if i < 10: 
            inputs_list.append(folder_inputs   + '/RotorSE_FAST_IEA_landBased_RWT_AeroDyn15_coords_0' + str(i) + '.txt')    # List of files containing the airfoil coordinates
        else:
            inputs_list.append(folder_inputs   + '/RotorSE_FAST_IEA_landBased_RWT_AeroDyn15_coords_' + str(i) + '.txt')    # List of files containing the airfoil coordinates
        outputs_list.append(folder_outputs + '/AF' + str(i + 1) + 'BL_TripMod' + str(trip) + '.txt')      # List of files containing the boundary layer characteristics


for id in range(5,len(inputs_list)):
    
    filename    = inputs_list[id]
    coord       = np.loadtxt(filename, skiprows = 9)
    np.savetxt('airfoil.dat', coord)
    Ue_Vinf_SS  = np.zeros((len(aoa),len(Re)))
    Ue_Vinf_PS  = np.zeros((len(aoa),len(Re)))
    Dstar_SS    = np.zeros((len(aoa),len(Re)))
    Dstar_PS    = np.zeros((len(aoa),len(Re)))
    Cf_SS       = np.zeros((len(aoa),len(Re)))
    Cf_PS       = np.zeros((len(aoa),len(Re)))
    Theta_SS    = np.zeros((len(aoa),len(Re)))
    Theta_PS    = np.zeros((len(aoa),len(Re)))
    
    
    for k in range(len(Re)):
        fid = open('inputxfoil.vbs','w')
        fid.write('\n')
        fid.write('load airfoil.dat\n')
        fid.write('airfoil\n')
        fid.write('pane\n')
        fid.write('plop\n')
        fid.write('w\n')
        fid.write('%f\n'    % 0.8)
        fid.write('\n')
        fid.write('oper\n')
        fid.write('visc %1.3e\n' % (Re[k]))
        fid.write('iter\n')
        fid.write('%u\n'    % 200)

        if trip == 1:
            fid.write('vpar\n')
            fid.write('xtr 0.05 0.1\n')
            fid.write('\n')
        
        for j in range(len(aoa)):
            fid.write('alfa %3.2f\n'        % aoa[j])
            fid.write('dump airfoil.bl%u\n' % j)
        fid.write('\n')
        fid.write('quit\n')
        fid.close()
        
        os.system(path2xfoil + 'xfoilP4.exe < inputxfoil.vbs')
        
        os.remove('inputxfoil.vbs')

        for j in range(len(aoa)):
            bl = np.loadtxt('airfoil.bl' + str(j))
            Ue_Vinf_SS[j,k] = bl[0  + TEoffset , 3]
            Ue_Vinf_PS[j,k] = bl[-1 + TEoffset , 3]
            Dstar_SS[j,k]   = bl[0  + TEoffset , 4]
            Dstar_PS[j,k]   = bl[-1 + TEoffset , 4]
            Theta_SS[j,k]   = bl[0  + TEoffset , 5]
            Theta_PS[j,k]   = bl[-1 + TEoffset , 5]
            Cf_SS[j,k]      = bl[0  + TEoffset , 6]
            Cf_PS[j,k]      = bl[-1 + TEoffset , 6]
            
            os.remove('airfoil.bl' + str(j))
    
    os.remove('airfoil.dat')
    
    fid=open(outputs_list[id],'w')
    fid.write('! Boundary layer characteristics at the trailing edge for the airfoil coordinates of %s\n' % filename)
    fid.write('! Legend: aoa - angle of attack (deg), Re - Reynolds number (-, millions), PS - pressure side, SS - suction side,  Ue_Vinf - edge velocity (-), Dstar - displacement thickness (-), Theta - momentum thickness (-) Cf  - friction coefficient (-)\n')
    fid.write('%u \t ReListBL   -  Number of Reynolds numbers (it corresponds to the number of tables)\n' % len(Re))
    fid.write('%u \t aoaListBL  -  Number of angles of attack (it corresponds to the number of rows in each table)\n' % len(aoa))
    for k in range(len(Re)):
        fid.write('%1.2f \t   -  Re\n' % (Re[k]*1.e-6))
        fid.write('aoa \t \t Ue_Vinf_SS \t Ue_Vinf_PS \t  Dstar_SS \t \t  Dstar_PS \t \t  Theta_SS \t \t  Theta_PS \t \t    Cf_SS \t \t    Cf_PS\n')
        fid.write('(deg) \t \t \t (-) \t \t \t (-) \t \t \t (-) \t \t \t (-) \t \t \t (-) \t \t \t (-) \t \t \t (-) \t \t \t (-)\n')
        for j in range(len(aoa)):
            fid.write('%1.5f \t %1.5e \t %1.5e \t %1.5e \t %1.5e \t %1.5e \t %1.5e \t %1.5e \t %1.5e \n' % (aoa[j], Ue_Vinf_SS[j,k], Ue_Vinf_PS[j,k], Dstar_SS[j,k], Dstar_PS[j,k], Theta_SS[j,k], Theta_PS[j,k], Cf_SS[j,k], Cf_PS[j,k]))
        
    fid.close()
    
    