#!/usr/bin/python

#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# You will find the latest version of this code at the following address:
# http://github.com/hugomatic
#
# You can contact me at the following email address:
# ugomatik@gmail.com
#
import os
import hugomatic.toolkit    # the GUI stuff
import hugomatic.code       # the GCODE routines
from astro import *

      
def take_a_break():
    """This function is called when the debug line is printed (if a debug number is specified in the GUI). 
    Use it to print debug information or add a breakpoint in your IDE.
    sys.stdout redirection is temporarily suspended during this call.  
    """
    import sys, traceback
    traceback.print_stack( file = sys.stdout)
    
    
# Create the Parameters object. It is used to create the GUI and set values in global variables
params = hugomatic.toolkit.Parameters('Astromount', 'Part name: %s' %  os.path.basename(__file__), 
                                      picture_file="blank.gif", # picture on the left
                                      debug_callback=take_a_break)

units = "Inches"
#params.addArgument(units,  'Units', choices=("mm","Inches"), group='setup' )
feed = 2.0 
params.addArgument(feed,  'Feed rate in Inches per minute', group='setup' )
cut = 0.05
params.addArgument(cut, 'Cut per pass in Inches', group='setup')
z_safe = 0.25
params.addArgument(z_safe , 'Safe Z above surface and clamps in Inches', group='setup')                
z_rapid = 0.05
params.addArgument(z_rapid , 'Rapid Z plane above surface where rapid movements stop', group='setup')                

tool_dia = 0.25
params.addArgument(tool_dia, 'Tool diameter in Inches', group='setup')    


show_stock_contour = True
params.addArgument(show_stock_contour, 'Show stock contour in EMC', group='stock')
dx_stock = 4.5
params.addArgument(dx_stock, 'Stock length along x', group='stock')
dy_stock = STOCK_HEIGHT
params.addArgument(dy_stock, 'Stock height along y', group='stock')
z_stock = -STOCK_THICK
params.addArgument(z_stock, 'Stock thickness along z', group='stock')

operation_A = True
params.addArgument(operation_A , 'Operation A: drilling?', group='A')
drill_dia = 0.1509
params.addArgument(drill_dia, 'Screw drill diameter', group='A')

operation_B = True
params.addArgument(operation_B, 'Operation B', group='B')



        
        
# Show the GUI, wait for the user to press the OK button
if params.loadParams():  # returns False if the window is closed without pressing OK
    
    # generate GCODE here!
    hugomatic.code.header(units, feed)   
    

    tool_changer = hugomatic.code.ToolChanger(0., 0., 0.,  z_safe)
    if operation_A:   
        tool_changer.change_tool(drill_dia, '#21 drill', 'drill')
        print "(Drilling mount holes)"
        x = 0.5
        y = 0.5
        z = z_stock
        peck =  drill_dia * 3
        hugomatic.code.peck_drill(x, y, z_safe, z_rapid, peck, z)
        
    if operation_B:      
        tool_changer.change_tool(tool_dia, 'flat end mill', 'mill')
        
        cuts = hugomatic.code.z_cut_compiler(z_stock, cut); # an array of depths
        x0 = 0.
        y0 = 0.
        diameter = 1.0
        hugomatic.code.circle_heli(x0, y0, diameter,  z_safe, z_rapid, cuts )
        
        x0 = 1.
        y0 = 1.
        form =  Contour(x0, y0, tool_dia, z_safe, z_rapid)
        form.cut(cuts)
    
    if show_stock_contour:
        hugomatic.code.stock(0, -dy_stock * 0.5,  dx_stock, dy_stock, 0., z_stock)

        
    hugomatic.code.footer()
