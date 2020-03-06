# -*- coding: utf-8 -*-
from __future__ import division

from pylab import *
from numpy import *
import scipy.integrate as integrate
from scipy import constants as k
#import bigfloat


class MagneT(object):
    """
    Set of function to calculate the magnetisation in QHE with and without spin splitting.
    """
    def __init__(self,**kwarg):
#        self._type = kwargs['type'] if 'type' in kwargs else 'kitten'
        self._Xi = kwarg['Xi'] if 'Xi' in kwarg else 0.2
#        Xi_default = .2
        m_default = 0.067*k.m_e
        self._m = kwarg['mass'] if 'mass' in kwarg else 0.067*k.m_e
        self._T = kwarg['Temp'] if 'Temp' in kwarg else 15e-3
        self._p = kwarg['power'] if 'power' in kwarg else 0
        self._N = kwarg['N-LL'] if 'N-LL' in kwarg else 50
        self._ns = kwarg['density'] if 'density' in kwarg else 2.75e15*0.99
#        T_default = 15e-3
#        p_default = 0
#        Nmax_default = 50
#        ns = 2.75e15*0.99
        self._mu = self._ns*pi*k.hbar**2/self._m
        self._EF = self._ns*pi*k.hbar**2/self._m
        self._E = linspace(0,2*self._mu,1002)
        self._Gamm = kwarg['Gamma'] if 'Gamma' in kwarg else self._EF/15
        self._s_default = 0
        self._B = kwarg['Bfield'] if 'Bfield' in kwarg else linspace(0.25,8,5000)

    def fd(self,E = None ,T = None, mu = None):
        """
        Parameters:
            E = energy range over wich to compute fd
            T = electron temperature
            mu = chemical potential (can be an np.array)
        return: the Fermi-Dirac distrubution
        """
        if E: self._E = E
        if T: self.T = T
        if mu: self.mu = mu
        bet = (self._E-self._mu)/(k.k*self._T)
        if shape(self._mu) == ():
            for n in range(shape(self._E)[0]):
                if abs(bet[n]) < 100:
                    bet[n] = 1/(1+exp(bet[n]))
                elif bet[n] < -100:
                    bet[n] = 1
                else:
                    bet[n] = 0               
        else:
            for p in range(shape(self._mu)[0]):
                for n in range(shape(E)[0]):
                    if abs(bet[n,p]) < 100:
                        bet[n,p] = 1/(1+exp(bet[n,p]))
                    elif bet[n,p] < -100:
                        bet[n,p] = 1
                    else:
                        bet[n,p] = 0           
        return bet
#    return 1/(1+bigfloat.exp((E-mu)/(k.k*T)),bigfloat.precision(100))

    def gEgaussian(self,B, E, Gam, Nmax):
        """       
        B is a vector of M elements
        E is a vector of L elements
        Return: the density of state for LL with Gaussian Broadening without spin splitting
        """
        if B: self._B = B
        if Gam: self._Gam = Gam
        if m: self._m = m
        if Nmax: self._N = Nmax
        wc = k.e*B/self._m     # M elements
        l = sqrt(k.hbar/(k.e*B))  # M elements
        n = arange(self._N+1)[:, newaxis, newaxis] # N,1 elements (N=Nmax+1)
        En = k.hbar*wc*(n+1./2) # NxM elements)
        return 1./(pi*l**2) * 1/(sqrt(2*pi)*self._Gam) * sum(exp(-(E-En)**2/(2*self._Gam**2)), axis=0)

    def gElorentzian(self,B, E, Gam, m, Nmax):
        """
        return: the density of state for LL with Lorenzian Broadening without spin splitting
        B is a vector of M elements
        E is a vector of L elements
        """
#        if E: self._E = E
        if B: self._B = B
        if Gam: self._Gam = Gam
        if m: self._m = m
        if Nmax: self._N = Nmax
        wc = k.e*B/self._m     # M elements
        l = sqrt(k.hbar/(k.e*B))  # M elements
        n = arange(self._N+1)[:, newaxis] # N,1 elements (N=Nmax+1)
        En = k.hbar*wc*(n+1./2) # NxM elements)
        return 1./(pi*l**2) * sum(self._Gam/((self._E-En)**2 + self._Gam**2), axis=0)
    
    def gESS(self,B, E,  Gam , Xi, Nmax, Bs = 2, alpha = 0, GL = 0):     
        """
        return: the density of state for LL with spin splitted with Gaussian or Lorentzian Broadening
        B is a vector of M elements
        E is a vector of L elements
        """
        if B: self._B = B
        if Gam: self._Gam = Gam
        if m: self._m = m
        if Nmax: self._N = Nmax
        if Xi: self._Xi = Xi
        Bp = B*cos(alpha)
        Bt = B
        gp = 0.44+0.9*(1-1/(1+exp((B-Bs)/1)))
        gn = 0.44+0.5*(1-1/(1+exp((B-Bs)/0.6)))
        mub = k.e*k.hbar/(2*self._m)
        wc = k.e*Bp/self._m     # M elements
        ws = k.e*Bt/self._m     # M elements
        Dn = gn*mub*Bt/2
        Dp = gp*mub*Bt/2
        p=0
        self._Gam = self._Gam*B**self._p
        #    ep = 0.05e-23*B**3
        ep = 0
        l = sqrt(k.hbar/(k.e*Bp))  # M elements
        #    n = arange(Nmax+1)[:, newaxis, newaxis, newaxis] # N,1 elements (N=Nmax+1)
        n = arange(self._Nmax+1)[:, newaxis, newaxis] 
        #    nS = arange((Nmax+1)*2)[:, newaxis] # N,1 elements (N=Nmax+1)
        En = k.hbar*wc*(n+1./2)
        EnP = k.hbar*wc*(n+1./2)+Dp+ep
        EnN = k.hbar*wc*(n+1./2)-Dn
        if GL == 1:
            dos = Xi*m/(pi*k.hbar**2)+(1-Xi)/2* ((1./(pi*l**2) * 1/(sqrt(2*pi)*self._Gam) * sum(exp(-(E-EnP)**2/(2*self._Gam**2)), axis=0))+ (1./(pi*l**2) * 1/(sqrt(2*pi)*self._Gam) *sum(exp(-(E-EnN)**2/(2*self._Gam**2)), axis=0)))
#            print(Xi)
        else:
            dos = Xi*m/(pi*k.hbar**2)+(1-Xi)*1./(pi*l**2)/2 * (sum(self._Gam/((E-EnP)**2 + self._Gam**2), axis=0) +sum(Gam/((E-EnN)**2 + Gam**2), axis=0))
#            print('L')   
        return dos
    
    

    def Dbe(self,B, E, Gam, Xi, m, Nmax, gE=gEgaussian):
        """
        B is a vector on M elements
        E can also be a vector of L elements
        """
        if B: self._B = B
        if Gam: self._Gam = Gam
        if m: self._m = m
        if Nmax: self._N = Nmax
        if Xi: self._Xi = Xi
        single = False
        if not isinstance(B, (list, ndarray)) and not isinstance(E, (list, ndarray)):
            single = True
            Ggi = gE(B, E, Gam, Nmax)
            ret = Xi*m/(pi*k.hbar**2)+(1-Xi)*2*k.e*B/(pi*k.h)*Ggi
            if single:
                return ret[0]
            return ret

    def fermi_weight(self,E, EF, T):
        """
        Fermi-Dirac function
        """
        if EF: self._EF = EF
        a = (E-EF)/(k.k*T)
        ret = log( 1. - 1./(1+exp(a)) )
        #return where(ret==-inf, a, ret) # fix for -inf
        return ret

    def Omega(self,B, EF, T, Gam, Xi, m, Nmax, gE=gEgaussian):
        """
        return: calculation of the grand potential calculation 
        B is a vector
        T is the temperature (single value)
        """
        if B: self._B = B
        if EF: self._EF = EF
        if Gam: self._Gam = Gam
        if m: self._m = m
        if T: self._T = T
        if Nmax: self._N = Nmax
        if Xi: self._Xi = Xi
        integ_result = empty_like(B)
        integrand = lambda E: Dbe(B, E, Gam, Xi, m, Nmax, gE)*fermi_weight(E, EF, T)
        for i,b in enumerate(B):
            integ_result[i], error = integrate.quad(integrand, 0, EF*10)
        return k.k*T * integ_result 

    def OmegaC(self, B, T, mu, Gam, Xi, Nmax, Bs = 2, GL = 1, alpha = 0):
        """
        Numeric function for calculating the grand potential, 
        Bs is the field for spin splitting (if Bs = 0 no spin splitting )
        """
        if B: self._B = B
        if mu: self._mu = mu
        if Gam: self._Gam = Gam
        if m: self._m = m
        if T: self._T = T
        if Nmax: self._N = Nmax
        if Xi: self._Xi = Xi
        if shape(mu) == ():
            E = linspace(0,2*mu,1002)[:, newaxis]
        else:
            E = linspace(0,2*mu[0],1002)[:, newaxis]
        bet = (mu-E)/(k.k*T)
        if shape(mu) == ():
            for n in range(shape(E)[0]):
                if abs(bet[n]) < 50:
                    bet[n] = log(1+exp(bet[n]))
                elif (bet[n]) < -50:
                    bet[n] = 0
            else:
                for p in range(shape(mu)[0]):
                    for n in range(shape(E)[0]):
                        if abs(bet[n,p]) < 50:
                            bet[n,p] = log(1+exp(bet[n,p]))
                        elif (bet[n,p]) < -50:
                            bet[n,p] = 0
                    
        if Bs == 0:
            Z = gEgaussian(B,E,Gam)*bet
        else:
            Z = gESS(B,E,Bs,Gam,Xi, alpha , Nmax, GL)*bet
        S = sum(Z, axis = 0)
        self._Om = -S*(max(E)-min(E))/shape(E)[0]*k.k*T
        return self._Om 

    def OmegaCS(self, B, T ,mu , Gam , Nmax , Xi, Bs = 2):
        if B: self._B = B
        if mu: self._mu = mu
        if Gam: self._Gam = Gam
        if m: self._m = m
        if T: self._T = T
        if Nmax: self._N = Nmax
        if Xi: self._Xi = Xi
        E = linspace(0,2*mu,1002)[:, newaxis]
        #    Z = gEgaussianS(B,E,Gam)[0]*(mu[newaxis]-E)/(k.k*T)
        Z = gESS(B,E,Gam, Xi)*(mu-E)/(k.k*T)
        S = np.zeros((shape(B)[0]))
        for p in range(shape(B)[0]):
            for n in range(shape(E)[0]):
                if Z[n,p] < 0:
                    Z[n,p] = 0
            S[p] = sum(Z[:,p])
        return -S*(max(E)-min(E))/shape(E)[0]*k.k*T
    # B = np.linspace(1,20,1000)
    # iB = linspace(1./20, 1./1, 1000)
    # ee=linspace(0, EF_default*10,1000)
    # plot(B, gEgaussian(B, EF_default*10, Gam_default)
    # plot(1/B, gEgaussian(B, EF_default*10, Gam_default, Nmax=100))
    # plot(iB, gEgaussian(1/iB, EF_default*10, Gam_default, Nmax=100))
    # plot(iB, Dbe(1/iB, EF_default*1.1, Gam_default/1, Nmax=100, gE=gEgaussian))

    def Om2(self, B, mu, T, Gam, Xi, m, Nmax):
        if mu: self._mu = mu
        if Gam: self._Gam = Gam
        if m: self._m = m
        if T: self._T = T
        if Nmax: self._N = Nmax
        if Xi: self._Xi = Xi
        wc = k.e*B/m
        hwc = k.hbar*wc
        n = arange(1,Nmax+1)[:, newaxis] # N,1 elements (N=Nmax+1)
        I3 = -(mu**2/(2*k.k*T)+pi**2*k.k*T/6)
        I4 = -(hwc)**2/(4*pi**2*n**2*k.k*T) + hwc/(2*n)*cos(2*pi*n*mu/hwc)/sinh(2*pi**2*n*k.k*T/hwc)
        return m*k.k*T/(pi*k.hbar**2)*(I3+2*(1-Xi)*sum((-1)**n*exp(-2*(n*pi*Gam)**2/(hwc)**2)*I4, axis=0))

    def Mag( self, B, ns , mu, T, Gam, Xi, m, p, Nmax, s , phi = 0):
        """
        Return: the Magnetisation in QHE with Gaussian broadening without spin splitting
        calculated by the analytical expression based on the Fourier decomposition
        """
        if B: self._B = B
        if mu: self._mu = mu
        if Gam: self._Gam = Gam
        if m: self._m = m
        if T: self._T = T
        if Nmax: self._N = Nmax
        if Xi: self._Xi = Xi
        if ns: self._ns = ns
        if p: self._p = p
        if self._s_default: self._s_default = s
        wc = k.e*B/m
        n = arange(1,Nmax+1)[:, newaxis] # N,1 elements (N=Nmax+1)
        hwc = k.hbar*wc    
        smu = 2*pi*n*mu/(hwc) + phi*2*pi*n #2nd term is a Berry phase 
        skt = 2*pi**2*n*k.k*T/(hwc)
        Gam = Gam*B**p
        I4 =  -(hwc)**2/(4*pi**2*n**2*k.k*T) + hwc/(2*n)*cos(smu)/sinh(2*pi**2*n*k.k*T/hwc)
        DI4 =  1/B*(-hwc**2/(2*pi**2*n**2*k.k*T)+pi*mu*sin(smu)/sinh(skt)+cos(smu)/sinh(skt)*(hwc/(2*n)+pi**2*k.k*T*1/tanh(skt)))   
        return -2*m*k.k*T/(pi*k.hbar**2)*(1-Xi)*sum((-1)**n*exp(-2*(n*pi*Gam)**2/(hwc)**2)*(DI4+(1-p)*(2*pi*n*Gam/hwc)**2*I4/B), axis=0)

    def MagL(self, B, ns, mu, T, Gam, Xi, m, p , Nmax, s, phi = 0):
        """
        Return: the Magnetisation in QHE with Lorentzian broadening without spin splitting
        calculated by the analytical expression based on the Fourier decomposition
        """
        if B: self._B = B
        if mu: self._mu = mu
        if Gam: self._Gam = Gam
        if m: self._m = m
        if T: self._T = T
        if Nmax: self._N = Nmax
        if ns: self._ns = ns
        if p: self._p = p
        if self._s_default: self._s_default = s
        wc = k.e*B/m
        n = arange(1,Nmax+1)[:, newaxis] # N,1 elements (N=Nmax+1)
        hwc = k.hbar*wc    
        smu = 2*pi*n*mu/(hwc) + phi*2*pi*n #2nd term is a Berry phase 
        skt = 2*pi**2*n*k.k*T/(hwc)
        Gam = Gam*B**p
        I4 =  -(hwc)**2/(4*pi**2*n**2*k.k*T) + hwc/(2*n)*cos(smu)/sinh(2*pi**2*n*k.k*T/hwc)
        DI4 =  1/B*(-hwc**2/(2*pi**2*n**2*k.k*T)+pi*mu*sin(smu)/sinh(skt)+cos(smu)/sinh(skt)*(hwc/(2*n)+pi**2*k.k*T*1/tanh(skt)))   
        return -2*m*k.k*T/(pi*k.hbar**2)*(1-Xi)*sum((-1)**n*exp(-2*(n*pi*Gam)/(hwc))*(DI4+(1-p)*(2*pi*n*Gam/hwc)*I4/B), axis=0)

    def MagC( self, B, Om):
        """
        Calculate Magnetization from Grand Potential Omega
        """
        if not self_Om : self._Om = Om
        OmC = savgol_filter(self.Om,21,3)
        self._MagC = -diff(OmC)/diff(B)
        return  self._MagC

    def MagCmu( self, B, Om, mu, ns):
        if not self_Om : self._Om = Om
        OmC = savgol_filter(Om,21,3)
        self._MagCmu = -diff(OmC+mu*ns)/diff(B)
        return self._MagCmu
    
    def nsb(self, B, mu, T, Gam, Xi, m, p , Nmax, s, phi = 0):
        """
        Calculates the density of state analytically (for Gaussian LL )
        """
        if mu: self._mu = mu
        if Gam: self._Gam = Gam
        if m: self._m = m
        if T: self._T = T
        if Nmax: self._N = Nmax
        if p: self._p = p
        if self._s_default: self._s_default = s
        wc = k.e*B/m
        n = arange(1,Nmax+1)[:, newaxis, newaxis] # N,1 elements (N=Nmax+1)
        hwc = k.hbar*wc    
        smu = 2*pi*n*mu/(hwc) + phi*2*pi*n #2nd term is a Berry phase 
        skt = 2*pi**2*n*k.k*T/(hwc)
        Gam = Gam*B**p
        I1 = mu+k.k*T*log(1+exp(-mu/(k.k*T)))
        I2 = pi*k.k*T*sin(smu)/sinh(2*pi**2*n*k.k*T/hwc)
        return m/(pi*k.hbar**2)*(I1+2*(1-Xi)*sum((-1)**n*exp(-2*(n*pi*Gam)**2/(hwc)**2)*I2, axis=0))

    def nsbL( self, B, mu, T, Gam, Xi, m, p, Nmax, s, phi = 0):
        """
        Calculates the density of state analytically (for Lorenzian LL )
        """
        if mu: self._mu = mu
        if Gam: self._Gam = Gam
        if m: self._m = m
        if T: self._T = T
        if Nmax: self._N = Nmax
        if self._s_default: self._s_default = s
        wc = k.e*B/self._m
        n = arange(1,self._Nmax+1)[:, newaxis, newaxis] # N,1 elements (N=Nmax+1)
        hwc = k.hbar*wc    
        smu = 2*pi*n*self._mu/(hwc) + phi*2*pi*n #2nd term is a Berry phase 
        skt = 2*pi**2*n*k.k*T/(hwc)
        Gam = self._Gam*B**p
        I1 = mu+k.k*T*log(1+exp(-mu/(k.k*T)))
        I2 = pi*k.k*T*sin(smu)/sinh(2*pi**2*n*k.k*T/hwc)
        return m/(pi*k.hbar**2)*(I1+2*(1-Xi)*sum((-1)**n*exp(-2*(n*pi*Gam)/(hwc))*I2, axis=0))

    def nsbC(self, B, mu, T, Gam, Xi, p, Nmax, alpha = 0, GL = 1, Bs = 2):
        """
        Calculates the density of state numerically
        """
        if mu: self._mu = mu
        if Gam: self._Gam = Gam
        if m: self._m = m
        if T: self._T = T
        if Nmax: self._N = Nmax
        E = linspace(0,1.1*mu,500)[:, newaxis]
        a = fd(E,T,mu)*gESS(B, E,Bs, Gam, Xi, alpha, Nmax, GL)
        return sum(a, axis = 0)*(max(E)-min(E))/shape(E)[0]

    def find_nearest(self,array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return (idx,array[idx])
    

    def update_progress(self,progress):
        barLength = 10 
        status = ""
        if isinstance(progress, int):
            progress = float(progress)
        if not isinstance(progress, float):
            progress = 0
            status = "error: progress var must be float\r\n"
        if progress < 0:
            progress = 0
            status = "Halt...\r\n"
        if progress >= 1:
            progress = 1
            status = "Done...\r\n"
        block = int(round(barLength*progress))
        text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
        sys.stdout.write(text)
        sys.stdout.flush()

#mul = linspace(1.5e-21,3e-21,1100)[:,newaxis]
#N = nsb(B, mu = mul)

#Mat = np.zeros((1000,2))
#for i in range(1000):
#    Mat[i] = find_nearest(N[:,i],ns)
#    
#for i in range(1000):
#    mub[i] = mul[int(Mat[i,0])]
#    
#M2 = Mag(B, mu = mub)



#def MagS(B,ns = ns, phi = 0, T=T_default, Gam=Gam_default, Xi=Xi_default, m=m_default, p = p_default, Nmax=Nmax_default ):
#    wc = k.e*B/m
#    n = arange(1,Nmax+1)[:, newaxis] # N,1 elements (N=Nmax+1)
#    hwc = k.hbar*wc
#    mu = ns*pi*k.hbar**2/m_default    
#    smu = 2*pi*n*mu/(hwc) + phi*2*pi*n #2nd term is a Berry phase 
#    skt = 2*pi**2*n*k.k*T/(hwc)
#    Gam = Gam*B**p
#    I4 =  -(hwc)**2/(4*pi**2*n**2*k.k*T) + hwc/(2*n)*cos(smu)/sinh(2*pi**2*n*k.k*T/hwc)
#    DI4 =  1/B*(-hwc**2/(2*pi**2*n**2*k.k*T)+pi*mu*sin(smu)/sinh(skt)+cos(smu)/sinh(skt)*(hwc/(2*n)+pi**2*k.k*T*1/tanh(skt)))   
#    return -2*m*k.k*T/(pi*k.hbar**2)*(1-Xi)*sum((-1)**n*exp(-2*(n*pi*Gam)**2/(hwc)**2)*(DI4+(1-p)*(2*pi*n*Gam/hwc)**2*I4/B), axis=0)

def main():
        
    if __name__ == '__main__': main()        