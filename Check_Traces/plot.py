#----------------------------------libraries-----------------------------------

# for plotting
import matplotlib.pyplot as plt

# for background map
from mpl_toolkits.basemap import Basemap

#---------------------Interpolation (LS without constraints)-------------------

# model for fit

def fitfunc(x,p): #f(x)= a x^2 + b x+ c
    a,b,c=p
    return c + b*x + a*x**2

# array of residuals

def residuals(p): 
    return abs(dataLatTest-fitfunc(dataLongTest,p))

 # function we want to minimize

def sum_residuals_custom(p):
    return sum(residuals(p)**2)

# interpolation

def interpolation(n, epsilon, x, y):
    
    global dataLongTest # dataset for interpolation
    global dataLatTest
    dataLongTest = x[0:3]
    dataLatTest = y[0:3]
    
    p0=[1,0,0] # initial parameters guess
    p,cov,infodict,mesg,ier = scimin.leastsq(residuals, p0,full_output=True) #interpolation
    
    curve_interpolation = [p] # add model to result
    curve_points = [x[0]]
    i = 0
    
    while i < n :
        
        if abs(fitfunc(x[i],p) - y[i]) > epsilon:
            
            dataLongTest = x[(i-2):(i+2)]
            dataLatTest = y[(i-2):(i+2)]
            dataLatTest[0] = fitfunc(x[i-2],p)
            
            p,cov,infodict,mesg,ier=scimin.leastsq(residuals, p0,full_output=True)
            pwith=scimin.fmin_slsqp(sum_residuals_custom,p)
            
            curve_interpolation.append(pwith)
            curve_points.append(x[i-2])
            i += 1
            
        i+=1
    
    curve_points.append(x[n-1]) # add last point 
    
    return curve_interpolation, curve_points

#----------------------------------plotting------------------------------------

#METTRE LES COORDONNEES D'UN VEHICULE ICI
dataLong =
dataLat = 

# adding background map
latMin = 48.774618 - 0.0005 # background map size
latMax = 48.952002 + 0.0005
longMin = 2.092213 - (latMax - latMin)/2
longMax = 2.582987 + (latMax - latMin)/2

m = Basemap(llcrnrlon=longMin, llcrnrlat= latMin, urcrnrlon=longMax, urcrnrlat=latMax, epsg = 4326,resolution='i',projection='merc')
m.arcgisimage(service='ESRI_StreetMap_World_2D', xpixels = 12000, verbose= True)

# adding GPS coordinates

m.plot(dataLong,dataLat,ls="",marker="x",color="red",mew=2.0,label="Datas")

#adding path

curve_interpolation, curve_points = interpolation(len(dataLong),0.0001, dataLong, dataLat)

for e in range(len(dataLong)-1):
    morex=numpy.linspace(dataLong[e],dataLong[e+1], num = 500, endpoint = True)
    morey = numpy.linspace(dataLat[e],dataLat[e+1], num = 500, endpoint = True)
    m.plot(morex,morey,color="blue")

plt.show()