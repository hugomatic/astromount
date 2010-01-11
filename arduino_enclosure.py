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
#from astro import *
import math

      
def take_a_break():
    """This function is called when the debug line is printed (if a debug number is specified in the GUI). 
    Use it to print debug information or add a breakpoint in your IDE.
    sys.stdout redirection is temporarily suspended during this call.  
    """
    import sys, traceback
    traceback.print_stack( file = sys.stdout)
    
    
# Create the Parameters object. It is used to create the GUI and set values in global variables
params = hugomatic.toolkit.Parameters('Astromount', 'Part name: %s' %  os.path.basename(__file__), 
                                      picture_file="arduino.gif", # picture on the left
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
tool_dia = 0.250
params.addArgument(tool_dia, 'Tool diameter in Inches', group='setup')  

show_stock_contour = True
params.addArgument(show_stock_contour, 'Show stock contour in EMC', group='stock')

dx_stock = 5.92 #inches
params.addArgument(dx_stock, 'Stock length along x', group='stock')

dy_stock = 3.04
params.addArgument(dy_stock, 'Stock height along y', group='stock')

z_stock = -0.45
params.addArgument(z_stock, 'Stock thickness along z', group='stock')

operation_drill_mount_holes = True
params.addArgument(operation_drill_mount_holes , 'Drill mounting holes', group='Drilling')

drill_dia = 0.125
params.addArgument(drill_dia, 'Screw drill diameter', group='Drilling')

mount_holes_depth = -0.3
params.addArgument(mount_holes_depth, 'Mounting holes depth along Z', group='Drilling')

operation_arduino_carve = True
params.addArgument(operation_arduino_carve, 'Mill Arduino recess', group='Milling')


operation_connector_carve = True
params.addArgument(operation_connector_carve, 'Mill Arduino connectors recess', group='Milling')

margin = 0.3
params.addArgument(margin, 'Left wall thickness', group='Milling')

base_z = -0.3
params.addArgument(base_z, 'Board carving final Z', group='Milling')

operation_box_carve = True
params.addArgument(operation_box_carve, 'Cut box walls', group='Box')

bottom_z = -0.35
params.addArgument(bottom_z, 'Wall final Z', group='Box')

def clear_corners(x0, y0, x1, y1, z_safe, z_rapid, tool_dia, cuts):
    
    tool_rad = tool_dia * 0.5
    delta = tool_rad * (1- math.cos(math.pi * 0.25))
    
    # top left
    xstart = x0 + tool_rad
    ystart = y1 - tool_rad
    xend = xstart - delta
    yend = ystart + delta
    hugomatic.code.line(xstart, ystart, xend, yend, z_safe, z_rapid, cuts)
    
    # top right
    xstart = x1 - tool_rad
    ystart = y1 - tool_rad
    xend = xstart + delta
    yend = ystart + delta
    hugomatic.code.line(xstart, ystart, xend, yend, z_safe, z_rapid, cuts)
    
    # bottom right
    xstart = x1 - tool_rad
    ystart = y0 + tool_rad
    xend = xstart + delta
    yend = ystart - delta
    hugomatic.code.line(xstart, ystart, xend, yend, z_safe, z_rapid, cuts)
    
    # bottom left
    xstart = x0 + tool_rad
    ystart = y0 + tool_rad
    xend = xstart - delta
    yend = ystart - delta
    hugomatic.code.line(xstart, ystart, xend, yend, z_safe, z_rapid, cuts)
    
    

start_x = 1.5
start_y = 0.5

circuit_board_dx = 2.75
circuit_board_dy = 2.125
        
        
# Show the GUI, wait for the user to press the OK button
if params.loadParams():  # returns False if the window is closed without pressing OK
    
    # generate GCODE here!
    hugomatic.code.header(units, feed)   

    tool_changer = hugomatic.code.ToolChanger(1., 0.5, 0.007,  z_safe)
    if operation_drill_mount_holes:   
        tool_changer.change_tool(drill_dia, 'drill', 'drill')
        print "(Drilling mount holes)"
        z = mount_holes_depth
        peck =  drill_dia * 3
        
        x = start_x+2.6
        y = start_y+0.3
        hugomatic.code.peck_drill(x, y, z_safe, z_rapid, peck, z)
#        x = start_x+2.6
#        y = start_y+1.4
#        hugomatic.code.peck_drill(x, y, z_safe, z_rapid, peck, z)
        x = start_x+0.6
        y = start_y+2.
        hugomatic.code.peck_drill(x, y, z_safe, z_rapid, peck, z)
        
    if operation_arduino_carve:      
        tool_changer.change_tool(tool_dia, 'flat end mill', 'mill')        
        cuts = hugomatic.code.z_cut_compiler(base_z, cut); # an array of depths
        x0 = start_x
        y0 = start_y
        x1 = start_x + circuit_board_dx
        y1 = start_y + circuit_board_dy
        hugomatic.code.pocket_rectangle(x0, y0, x1, y1, z_safe, z_rapid, tool_dia, cuts)
        clear_corners(x0, y0, x1, y1, z_safe, z_rapid, tool_dia, cuts)
        
    if operation_connector_carve:      
        tool_changer.change_tool(tool_dia, 'flat end mill', 'mill')        
        cuts = hugomatic.code.z_cut_compiler(base_z + 0.125, cut); # an array of depths
        
        x0 = start_x - margin
        x1 = start_x + tool_dia * 0.5
        
        #USB
        y0 = start_y + 1.26        
        y1 = y0 + 0.5
        hugomatic.code.pocket_rectangle(x0, y0, x1, y1, z_safe, z_rapid, tool_dia, cuts)
        
        #POWER
        y0 = start_y + 0.17
        y1 = y0 + 0.37
        hugomatic.code.pocket_rectangle(x0, y0, x1, y1, z_safe, z_rapid, tool_dia, cuts)
   
    if operation_box_carve:
        x0 = start_x - margin
        y0 = start_y - margin
        x1 = start_x + circuit_board_dx + margin
        y1 = start_y + circuit_board_dy + margin
        cuts = hugomatic.code.z_cut_compiler(bottom_z, cut, z_rapid)
        radius = 0.125
        hugomatic.code.round_rectangle_tool_outside(x0, y0, x1, y1, radius, z_safe, z_rapid, tool_dia, cuts)
        
        
           
    if show_stock_contour:
        hugomatic.code.stock(0, 0, dx_stock, dy_stock, 0,z_stock)#dy_stock * 0.5,  dx_stock, dy_stock, 0., z_stock)

        
    hugomatic.code.footer()
