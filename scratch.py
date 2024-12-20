import golf_ballstics
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.animation as animation

# Initialize the ballistics model
gb = golf_ballstics.golf_ballstics()
# Read in the ball stats data from CSV
clubs = pd.read_csv('C:\\Users\\Caroline\\Documents\\Ian\\OneDrive\\Documents\\OCG404\\Final\\Swing_Stats.csv')
# Convert ball speed from mph to mps
clubs['AvgBallSpeed'] = clubs['AvgBallSpeed']*0.44704
# Get shot distance and wind data from user
shotDist = float(input("How long is the shot you want to hit in yards? "))
windSpd = input("\nHow fast is the wind blowing in miles per hour? ")
windDir = input("\nWhat direction is the wind blowing (0 degrees is a perfect tailwind, 90 degrees is exactly off the left) ")

# Run the ball model and predict which club is best... essentially closest without going over
clubDist = np.zeros(len(clubs['Club']))
clubHorz = np.zeros_like(clubDist)
for i in range(len(clubs['Club'])):
    [x, y] = gb.get_landingpos(velocity=clubs['AvgBallSpeed'][i], launch_angle_deg=clubs['AvgLaunchAngle'][i],
                               off_center_angle_deg=clubs['AvgFaceToPath'][i], spin_rpm = clubs['AvgSpinRate'][i],
                               spin_angle_deg=clubs['AvgSpinAxis'][i], windspeed=float(windSpd)**0.44704, windheading_deg=float(windDir))
    clubDist[i] = y*1.09361
    clubHorz[i] = x*1.09361

distDiff = shotDist - clubDist
distDiff[distDiff > 3] = np.NAN
clubIdx = np.argmin(np.abs(distDiff)) - 1

# Get shot power
if distDiff[clubIdx] > 0:
    shotType = "hard"
elif (distDiff[clubIdx] < 0) & (distDiff[clubIdx] >= -3):
    shotType = "full"
elif distDiff[clubIdx] < -3:
    shotType = "light"

# Get aim point
if clubHorz[clubIdx] > 0:
    aimDir = "left"
elif clubHorz[clubIdx] < 0:
    aimDir = "right"
else:
    aimDir = "straight"
print("Use club: " + shotType + " " + clubs['Club'][clubIdx] + ". Aim " + str(abs(clubHorz[clubIdx])) + " yards " + aimDir)

# Run the flight model again, but this time only for the club selected. Get the output and plot the ball path
gb.initiate_hit(velocity=clubs['AvgBallSpeed'][clubIdx], launch_angle_deg=clubs['AvgLaunchAngle'][clubIdx],
                               off_center_angle_deg=clubs['AvgFaceToPath'][clubIdx], spin_rpm = clubs['AvgSpinRate'][clubIdx],
                               spin_angle_deg=clubs['AvgSpinAxis'][clubIdx], windspeed=float(windSpd), windheading_deg=float(windDir))
shotDF = gb.df_simres

# Eliminate Z values less than 0
dt = shotDF['t'][1] - shotDF['t'][0]
x=[shotDF[shotDF['z']>=0]['x']]
y=[shotDF[shotDF['z']>=0]['y']]
z=[shotDF[shotDF['z']>=0]['z']]

fig = plt.figure()
axs = plt.subplot(1,2,1, projection='3d')
axs.azim = 270
axs.dist = 2
axs.elev = 0
axs2 = plt.subplot(1,2,2, projection='3d')

sct1 = axs.scatter([],[],[])
axs.set_xlim(-7, 7)
axs.set_zlim(0, 50)
axs2.scatter([],[],[])
axs2.set_xlim(-7, 7)
axs2.set_zlim(0, 50)


def update(frame):
    axs.scatter(x[0][:frame+1], y[0][:frame+1], z[0][:frame+1], color='b')
    axs2.scatter(x[0][:frame+1], y[0][:frame+1], z[0][:frame+1], color='b')

ani = animation.FuncAnimation(fig, update, frames=len(x[0]), interval=dt*1000, repeat=True, blit=False)
#ani.save(str(shotDist) + "_ani.gif", writer="pillow")
plt.show()

