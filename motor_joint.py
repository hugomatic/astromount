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



operation_drill_tripod_arm = True
params.addArgument(operation_drill_tripod_arm, 'Drill the tripod arm mount hole', group='camera arm')
drill_dia = 0.175
params.addArgument(drill_dia, 'Screw drill diameter', group='drill')
x_cam_mount_hole = 1.25
params.addArgument(x_cam_mount_hole, 'Screw drill hole position along x', group='drill')

operation_shaft = True
params.addArgument(operation_shaft , 'Drill shaft hole', group='shaft')
drill_dia_shaft = 0.175
params.addArgument(drill_dia_shaft, 'Screw drill diameter', group='shaft')
x_center_shaft = 0.5
params.addArgument(x_center_shaft , 'Center x', group='shaft')
y_center_shaft = 0.
params.addArgument(y_center_shaft , 'Center y', group='shaft')

operation_mirror = False
params.addArgument(operation_mirror, 'Flip operations for second side', group='side')

operation_shoulder = True
params.addArgument(operation_shoulder , 'Mill shoulder space', group='Shoulder')
shoulder = SHOULDER_SIZE
params.addArgument(shoulder, 'Height of the coupling shoulder', group='Shoulder')


operation_left_side = True
params.addArgument(operation_left_side, 'Left side rounded', group='arm joint')

operation_cut_stock_right = True
params.addArgument(operation_cut_stock_right, 'Cut the right end of stock to length', group='stock')
sixty_pc_cut = True
params.addArgument(sixty_pc_cut, 'Cut stock right to only 60% of stock depth', group='stock')

show_stock_contour = True
params.addArgument(show_stock_contour, 'Stock stock contour in EMC', group='stock')
dx_stock = 1.7
params.addArgument(dx_stock, 'Stock length along x', group='stock')
dy_stock = STOCK_HEIGHT
params.addArgument(dy_stock, 'Stock height along y', group='stock')
z_stock = -STOCK_THICK_JOINT
params.addArgument(z_stock, 'Stock thickness along z', group='stock')
        
        
# Show the GUI, wait for the user to press the OK button
if params.loadParams():  # returns False if the window is closed without pressing OK
    
    # generate GCODE here!
    hugomatic.code.header(units, feed)   
    
    tool_changer = hugomatic.code.ToolChanger(0., 0., 0.,  z_safe)
    
    if operation_drill_tripod_arm:
        tool_changer.change_tool(drill_dia, '#21 drill', 'drill')
        print "(Drilling camera arm mount screw hole)"
        x = x_cam_mount_hole
        y = 0.
        z = z_stock
        peck =  drill_dia * 2
        hugomatic.code.peck_drill(x, y, z_safe, z_rapid, peck, z)
        
    if operation_shaft:      
        tool_changer.change_tool(drill_dia_shaft, 'shaft drill', 'drill')
        x = x_center_shaft
        y = y_center_shaft
        z = z_stock - 0.05
        peck =  drill_dia_shaft * 2
        hugomatic.code.peck_drill(x, y, z_safe, z_rapid, peck, z)

    if operation_left_side:
        tool_changer.change_tool(tool_dia, 'flat end mill', 'mill')
        x0 = 0.75
        y_step = 0.1
        cuts = hugomatic.code.z_cut_compiler(z_stock, cut)
        contour = TripodLeftSide(x0, dy_stock, y_step, x_center_shaft, y_center_shaft, tool_dia, z_safe, z_rapid)
        contour.cut(cuts) 

    if operation_shoulder:
        x0 = dx_stock - dy_stock
        x1 = dx_stock
        y0 = dy_stock *-0.5
        y1 = -y0
        anti_shoulder = dy_stock - shoulder
        cuts = hugomatic.code.z_cut_compiler(z_stock, cut)
        bottom_right_recess(x0, y0, x1, y1, anti_shoulder, z_safe, z_rapid, tool_dia, operation_mirror, cuts)

    if operation_cut_stock_right:
        z = z_stock
        if sixty_pc_cut:
            z = z * 0.6
        cuts = hugomatic.code.z_cut_compiler(z, cut)
        x0 = dx_stock + tool_dia * 0.5
        x1 = x0
        y0 = dy_stock * 0.5 + tool_dia
        y1 = -y0
        hugomatic.code.line(x0, y0, x1, y1, z_safe, z_rapid, cuts)
    
    if show_stock_contour:
        hugomatic.code.stock(0, -dy_stock * 0.5,  dx_stock, dy_stock, 0., z_stock)

        
    hugomatic.code.footer()
