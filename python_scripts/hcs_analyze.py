### Use as `python hcs_analyze.py "plt*" <no: of particles>
### It takes the glob pattern of the plot files and the number of particles as argument

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from sys import argv
import glob
​
def get_analytic_soln(npart):
#---------------------------------------------------------------------------------------------------------
#           % Required user input
#---------------------------------------------------------------------------------------------------------
	Np   = npart;
	e    = 0.8;
	T0   = 1000.0;
	diap = 0.01;
	rho_s = 1.0;
	rho_g = 1.0e-3;
	mu_g = 2.0e-4;
	Ld   = 64.0;
#---------------------------------------------------------------------------------------------------------
# Dependent Variables
	phi   = Np*(np.pi/6.0)/Ld**3;
	nu_g  = mu_g/rho_g;
	m     = rho_s*(np.pi/6.0)*diap**3;
	r_rho = 1000.0;
	L     = Ld*diap;
	ReT0  = rho_g*diap*np.sqrt(T0)/mu_g;
#---------------------------------------------------------------------------------------------------------
#           % comment above out if called from dem_data_cruncher
#---------------------------------------------------------------------------------------------------------
#
#
# T-independent variables :
	chi      = (1.0-phi/2.0)/(1-phi)**3;
	mu20     = np.sqrt(2.0*np.pi)*chi*(1-e**2);
	mu40     = (9.0/2.0+e**2)*mu20;
	mu41     = ((3.0/32.0)*(69.0+10.0*e**2)+2.0/(1-e))*mu20;
	xistar   = 0.0;
	a2       = (5.0*mu20 - mu40)/(mu41 - 5.0*((19.0/16.0)*mu20 - (3.0/2.0)*xistar));
#
	zeta0hat = (8.0*phi)/(np.sqrt(np.pi)*diap)*chi*(1.0 - e**2)*(1.0 + 3.0*a2/16.0);
	Rdiss0 = 1.0+3.0*np.sqrt(phi/2.0)+(135.0/64.0)*phi*np.log(phi)+\
	11.26*phi*(1.0-5.1*phi+16.57*phi**2-21.77*phi**3)-phi*chi*np.log(0.01);
	#%Rdrag  = (1+3*np.sqrt(phi/2)+(135/64)*phi*np.log(phi)+17.14*phi)/(1+0.681*phi-8.48*phi**2+8.16*phi**3);
	#%chiMA  = (1+2.5*phi+4.5094*phi**2+4.515439*phi**3)/(1-(phi/0.64356)**3)**0.678021;
	#%Sstar  = Rdrag**2/(chiMA*(1 + 3.5*np.sqrt(phi)+5.9*phi));
	Kofphi = (0.096 + 0.142*phi**0.212)/(1 - phi)**4.454;
#
​
	gammahat = 3.0*np.pi*mu_g*diap;
	gamma    = gammahat*Rdiss0;
	gammaK   = gammahat*(rho_g*diap/mu_g)*Kofphi;
​
#solution consts
	A = zeta0hat + 2.0*gammaK/m;
	B = 2.0*gamma/m;
​
	n = 800;
	xs = np.zeros(n);
	x  = np.zeros(n);
	y  = np.zeros(n);
	minexp=-1.0
	maxexp=2.5
	delexp=(maxexp-minexp)/(n-1)
	for i in range(n):
    		xs[i]=10.0**(minexp+i*delexp)
​
	for i in range(n):
   		x[i] = xs[i]*diap/np.sqrt(T0);
    		y[i] = 1.0/(np.exp(B*x[i]/2.0) + (A/B)*np.sqrt(T0)*(np.exp(B*x[i]/2) - 1))**2;

    #% output: x = t (time), xs = t* = t*np.sqrt(T0)/diap, y = T(t*)/T0 (T0 = T(t* = 0))
    #fprintf(1,'%20.12e\t%20.12e\n',xs,y)
​
	outfile=open("analytic_soln.dat","w")
​
	for i in range(n):
    		outfile.write("%e\t%e\n"%(xs[i],y[i]))
​
	outfile.close()
	return(xs,y,diap/np.sqrt(T0),T0)
​
class AMReXParticleHeader(object):
    '''
​
    This class is designed to parse and store the information
    contained in an AMReX particle header file.
​
    Usage:
​
        header = AMReXParticleHeader("plt00000/particle0/Header")
        print(header.num_particles)
        print(header.version_string)
​
    etc...
​
    '''
​
    def __init__(self, header_filename):
​
        self.real_component_names = []
        self.int_component_names = []
        with open(header_filename, "r") as f:
            self.version_string = f.readline().strip()
​
            particle_real_type = self.version_string.split('_')[-1]
            particle_real_type = self.version_string.split('_')[-1]
            if particle_real_type == 'double':
                self.real_type = np.float64
            elif particle_real_type == 'single':
                self.real_type = np.float32
            else:
                raise RuntimeError("Did not recognize particle real type.")
            self.int_type = np.int32
​
            self.dim = int(f.readline().strip())
            self.num_int_base = 2
            self.num_real_base = self.dim
            self.num_real_extra = int(f.readline().strip())
            for i in range(self.num_real_extra):
                self.real_component_names.append(f.readline().strip())
            self.num_int_extra = int(f.readline().strip())
            for i in range(self.num_int_extra):
                self.int_component_names.append(f.readline().strip())
            self.num_int = self.num_int_base + self.num_int_extra
            self.num_real = self.num_real_base + self.num_real_extra
            self.is_checkpoint = bool(int(f.readline().strip()))
            self.num_particles = int(f.readline().strip())
            self.max_next_id = int(f.readline().strip())
            self.finest_level = int(f.readline().strip())
            self.num_levels = self.finest_level + 1
​
            if not self.is_checkpoint:
                self.num_int_base = 0
                self.num_int_extra = 0
                self.num_int = 0
​
            self.grids_per_level = np.zeros(self.num_levels, dtype='int64')
            for level_num in range(self.num_levels):
                self.grids_per_level[level_num] = int(f.readline().strip())
​
            self.grids = [[] for _ in range(self.num_levels)]
            for level_num in range(self.num_levels):
                for grid_num in range(self.grids_per_level[level_num]):
                    entry = [int(val) for val in f.readline().strip().split()]
                    self.grids[level_num].append(tuple(entry))
​
def get_time_stamp(fldfname):
​
    infile=open(fldfname+"/Header",'r')
​
    infile.readline() #Hyperclaw-v1.1
    nvars=int(infile.readline().split()[0])
​
    for i in range(nvars):
        line=infile.readline()
​
    line=infile.readline() #3 (3 d coords?)
​
    time=float(infile.readline().split()[0])
    return(time)
​
def get_computed_soln(fname_list,tscale,v2scale,ptype="particles"):
​
	outfile=open("vel_computed.dat","w")
​
        m2_to_cm2 = 10000.0
	nondim_temp=np.array([])
	nondim_time=np.array([])
​
    	for fn_i, fn in enumerate(fname_list):
​
		print(fn)
    		time=get_time_stamp(fn)
    		base_fn = fn + "/" + ptype
    		header = AMReXParticleHeader(base_fn + "/Header")
​

    		idtype = "(%d,)i4" % header.num_int
    		if header.real_type == np.float64:
        		fdtype = "(%d,)f8" % header.num_real
    		elif header.real_type == np.float32:
        		fdtype = "(%d,)f4" % header.num_real

    		idata = np.empty((header.num_particles, header.num_int ))
    		rdata = np.empty((header.num_particles, header.num_real))

    		ip = 0
    		for lvl, level_grids in enumerate(header.grids):
        		for (which, count, where) in level_grids:
            			if count == 0: continue
            			fn = base_fn + "/Level_%d/DATA_%05d" % (lvl, which)
​
            			with open(fn, 'rb') as f:
                			f.seek(where)
                			if header.is_checkpoint:
                    				ints   = np.fromfile(f, dtype = idtype, count=count)
                    				idata[ip:ip+count] = ints
​
                			floats = np.fromfile(f, dtype = fdtype, count=count)
                			rdata[ip:ip+count] = floats
            			ip += count
​
    		vx=rdata[:,3]
    		vy=rdata[:,4]
    		vz=rdata[:,5]
​
    		vxm=np.mean(vx)
    		vym=np.mean(vy)
    		vzm=np.mean(vz)
​
    		pecvel_x=vx-vxm
    		pecvel_y=vy-vym
    		pecvel_z=vz-vzm
​
    		pecvel_speed2 = pecvel_x**2+pecvel_y**2+pecvel_z**2

                ndtime=time/tscale
                ndtemp=0.33333*np.mean(pecvel_speed2)/v2scale*m2_to_cm2
​
		nondim_time = np.append(nondim_time,ndtime)
		nondim_temp = np.append(nondim_temp,ndtemp)
		outfile.write("%e\t%e\n"%(ndtime,ndtemp))
​
	return(nondim_time,nondim_temp);
​
#main
font={'family':'Helvetica', 'size':'16'}
mpl.rc('font',**font)
mpl.rc('xtick',labelsize=12)
mpl.rc('ytick',labelsize=12)
plot_data=True
​
part_fn_pattern=argv[1]
npart=int(argv[2])
part_fn_list = glob.glob(part_fn_pattern)
part_fn_list.sort()
​
(a_time,a_temp,tscale,v2scale)=get_analytic_soln(npart)
​
(c_time,c_temp) = get_computed_soln(part_fn_list,tscale,v2scale)
​
if(plot_data):
    plt.yscale('log')
    plt.xscale('log')
    plt.plot(a_time,a_temp,linewidth=2,label="Analytical");
    plt.plot(c_time,c_temp,linewidth=2,label="Computed",marker='o',markersize='3');
    plt.xlabel("Non-dimensional time $(t T_0^{1/2}/d_p)$")
    plt.ylabel("Non-dimensional temperature $(T/T_0)$")
    plt.legend(loc="best")
    plt.tight_layout()
    plt.savefig("haffs_law.png")
    #plt.show()
