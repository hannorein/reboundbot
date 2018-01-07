import tweepy
from secrets import *
import rebound 
import numpy as np
import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt
import io

        
auth = tweepy.OAuthHandler(consumer_key, consumer_secret) 

auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth) 
class BotStreamer(tweepy.StreamListener):

    def on_status(self, status):
        username = status.user.screen_name 
        try:
            new_status = api.update_status(status='@{0} Starting your REBOUND simulation... results will come shortly...  '.format(username), in_reply_to_status_id=status.id)
            text = status.text
            text = text.replace("@reboundbot","",100)
            sim = rebound.Simulation()
            for line in text.splitlines():
                args = line.strip().split(" ")
                argsdict = {}
                for arg in args:
                    name, param = arg.split("=")
                    if name in ["x","y","z","a","p","e","inc","omega","Omega","pomega","f","M","l","theta","T","h","k","ix","iy","vx","vy","vz","m"]:
                        argsdict[name] = float(param)
                    else:
                        print("unknown parameter")

                sim.add(**argsdict)
            sim.move_to_com()
            
            orbits = sim.calculate_orbits()
            min_timescale = 1.0e300
            for o in orbits:
                if o.P<min_timescale:
                    min_timescale = o.P
            sim.min_dt = min_timescale*1e-4
            steps = 100000
            dots = np.zeros((steps,sim.N,2))
            for i in range(steps):
                for j in range(sim.N):
                    dots[i,j,0] = sim.particles[j].x
                    dots[i,j,1] = sim.particles[j].y
                sim.step()
        
            for j in range(sim.N):
                plt.plot(dots[:,j,0],dots[:,j,1])
            plt.axis('equal')
            fig = plt.gcf()

            buf = io.BytesIO(); 
            plt.gcf().savefig(buf, format='png'); 
            buf.seek(0);
            #b = buf.read()
            api.update_with_media("image.png",status='@{0} Here is the outcome of your REBOUND simulation:'.format(username), in_reply_to_status_id=new_status.id,file=buf)
        except:
            api.update_status(status='@{0} Hm... something wrent wrong. Please try again.'.format(username), in_reply_to_status_id=status.id)

myStreamListener = BotStreamer()

stream = tweepy.Stream(auth, myStreamListener)
stream.filter(track=['@reboundbot'])


