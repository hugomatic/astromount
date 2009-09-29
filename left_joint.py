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
                                      picture_file="arm_joint.gif", # picture on the left
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

operation_drill_shaft_hole = True
params.addArgument(operation_drill_shaft_hole , 'Drill shaft hole', group='shaft')
x_center_shaft = 0.375
params.addArgument(x_center_shaft , 'Center x', group='shaft')
y_center_shaft = 0.
params.addArgument(y_center_shaft , 'Center y', group='shaft')


z_center_drill = -0.15
center_drill = True
params.addArgument(center_drill, 'Center drill before drilling to depth', group='drill')
params.addArgument(z_center_drill, 'Center drill z depth', group='drill')
drill_shaft_dia = 0.25
params.addArgument(drill_shaft_dia, 'Shaft drill diameter', group='drill')
x_cam_mount_hole = x_center_shaft + 0.75
params.addArgument(x_cam_mount_hole, 'Screw drill hole position along x', group='drill')

operation_screw_cap = False
#params.addArgument(operation_screw_cap, 'Screw cap hole', group='arm joint')
operation_recess = True
params.addArgument(operation_recess, 'Left side recess', group='arm joint')
z_recess = -0.25
params.addArgument(z_recess, 'Left side recess final Z (negatif)', group='arm joint')

operation_left_side = True
params.addArgument(operation_left_side, 'Left side rounded', group='arm joint')
x_shoulder = 0.5 
params.addArgument(x_shoulder , 'shoulder length along x measured from shaft center', group='shaft')

operation_cut_stock_right = True
params.addArgument(operation_cut_stock_right, 'Cut the right end of stock to length', group='stock')

show_stock_contour = True
params.addArgument(show_stock_contour, 'Stock stock contour in EMC', group='stock')
dx_stock = 1.3
params.addArgument(dx_stock, 'Stock length along x', group='stock')
dy_stock = STOCK_HEIGHT
params.addArgument(dy_stock, 'Stock height along y', group='stock')
z_stock = -STOCK_HEIGHT
params.addArgument(z_stock, 'Stock thickness along z', group='stock')
        
        
# Show the GUI, wait for the user to press the OK button
if params.loadParams():  # returns False if the window is closed without pressing OK
    
    # generate GCODE here!
    hugomatic.code.header(units, feed)   
    
    tool_changer = hugomatic.code.ToolChanger(0., 0., 0.,  z_safe)
    
    if operation_drill_shaft_hole:

        print "(Drilling shaft hole)"
        x = x_center_shaft
        y = 0.
        if center_drill:
            peck = 0.1
            tool_changer.change_tool(0.1, 'Center drill', 'center drill')
            hugomatic.code.peck_drill(x, y, z_safe, z_rapid, peck, z_center_drill)
        tool_changer.change_tool(drill_shaft_dia, 'Shaft drill', 'drill')
        z = z_stock - drill_shaft_dia
        peck =  drill_shaft_dia * 2
        hugomatic.code.peck_drill(x, y, z_safe, z_rapid, peck, z)
   
    if operation_screw_cap:
        tool_changer.change_tool(tool_dia, 'flat end mill', 'mill')
        x = x_cam_mount_hole
        y = 0.
        screwCap1032(x, y, cut, z_safe, z_rapid, -0.20, tool_changer.diameter)
    
    if operation_recess:
        tool_changer.change_tool(tool_dia, 'flat end mill', 'mill')
        x0 = -tool_dia
        x1 = x_center_shaft + x_shoulder
        y0 = -dy_stock / 2 - tool_dia
        y1 = -y0
        z = z_recess
        cuts = hugomatic.code.z_cut_compiler(z, cut)
        hugomatic.code.pocket_rectangle(x0, y0, x1, y1, z_safe, z_rapid, tool_dia, cuts)
                 
    if operation_left_side:
        tool_changer.change_tool(tool_dia, 'flat end mill', 'mill')
        x0 =  x_shoulder + x_center_shaft
        y_step = 0.05
        surface = 0.
        if operation_recess:
            surface = z_recess
        cuts = hugomatic.code.z_cut_compiler(z_stock, z_surf = surface, cut = cut)
       
        contour = TripodLeftSide(x0, dy_stock, y_step, x_center_shaft, y_center_shaft, tool_dia, z_safe, z_rapid)
        contour.cut(cuts) 

    if operation_cut_stock_right:
        z = z_stock
        cuts = hugomatic.code.z_cut_compiler(z, cut)
        x0 = dx_stock + tool_dia * 0.5
        x1 = x0
        y0 = dy_stock * 0.5 + tool_dia
        y1 = -y0
        hugomatic.code.line(x0, y0, x1, y1, z_safe, z_rapid, cuts)
    
    if show_stock_contour:
        hugomatic.code.stock(0, -dy_stock * 0.5,  dx_stock, dy_stock, 0., z_stock)

        
    hugomatic.code.footer()
