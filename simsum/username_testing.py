import numpy
import matcher

fb_names = ['SachinTendulkar', 'katyperry', 'justinbieber', 'TaylorSwift', 'barackobama', 'rihanna', 'youtube', 'ladygaga', 'twitterinc', 'justintimberlake', 'KimKardashian', 'britneyspears', 'cnn', 'narendramodi', 'iamsrk']
t_names = ['sachin_rt', 'katyperry', 'justinbieber', 'taylorswift13', 'BarackObama', 'rihanna', 'YouTube', 'ladygaga', 'twitter', 'jtimberlake', 'KimKardashian', 'britneyspears', 'cnnbrk', 'narendramodi', 'iamsrk']

mat = numpy.matrix([[matcher.similarity(fb, t) for t in t_names] for fb in fb_names])

print mat