# Manyterm
![PyPI - Version](https://img.shields.io/pypi/v/manyterm) ![PyPI - Downloads](https://img.shields.io/pypi/dm/manyterm) [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/donate/?business=8VDFKHMBFSC2Q&no_recurring=0&currency_code=USD)  
Spawn multiple terminals to print to.  
Compatible with Windows, Linux, and MacOS.    
### Installation
`pip install manyterm` or `pip3 install manyterm`
### Usage
```py
import manyterm 

t1 = manyterm.Terminal() # init a new window

t1.print("Hello World") # print to the window

t1.print("supercalifragilisticexpialidocious", end="") # default end="\n"

t1.close() # close the window
```
### Description
This program creates multiple terminals in python. New terminals can only be printed to (no input). `tests/test.py` contains an example of how to use this program. A server is used to print to client windows based on a uuid. When a new window object is made `manyterm.Terminal()` the program checks to make sure that the server is running, then assigns itself a uuid, and then the program calls itself from a new terminal using the uuid as an argument. The new program contacts the server with its' uuid and the connection is made.
## Windows 11
![Picture showing windows example](docs/screenshots/screenshot-win.png)
## Linux (Ubuntu 23.10)
![Picture showing windows example](docs/screenshots/screenshot-linux.png)
## MacOS Sonoma
![Picture showing windows example](docs/screenshots/screenshot-macos.jpg)
