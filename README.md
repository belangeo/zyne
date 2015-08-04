# Zyne #

Zyne is a Python modular synthesizer using pyo as its audio engine.

Zyne comes with more than 10 builtin modules implementing different kind of 
synthesis engines and provides a simple API to create your own custom modules.

Tutorial on how to create a custom Zyne module:
[Tutorial](https://github.com/belangeo/zyne/blob/wiki/CustomModule.md)

A little sampler, written in pyo, that can be used to play exported soundfiles:
[SimpleSampler.py](https://github.com/belangeo/zyne/blob/master/scripts/SimpleSampler.py)

If you want to share your own modules with other users, send it by email to 
belangeo(at)gmail.com and it will be added to the download repository.

## Updates ##

### Zyne 0.1.2 ###

Bug fixes release:

  * Fixed an important memory leak
  * Disable Midi controllers interpolation to provide a more natural mapping 
  of values to the graphical sliders.

### Zyne 0.1.1 ###

Bug fixes release:

  * Fixed bug with Built-in Output not opening device on OS X 10.5
  * Fixed Jack support on linux
  * Midi notes and controllers can come from any channel instead of only 
  channel 1
  * Fixed "Midi interface" popup initialization

## Contact ##

For questions and comments please mail belangeo(at)gmail.com


## Donation ##

This project is developed by Olivier Bélanger on his free time to help 
creation of original soundfiles and sound exploration. If you feel this 
project is useful to you and want to support it and it's future development 
please consider donating money. I only ask for a small donation, but of 
course I appreciate any amount.

[![](https://www.paypal.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=9CA99DH6ES3HA)