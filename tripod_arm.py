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
    hugomatic.toolkit.print_debug_info()
    
    
# Create the Parameters object. It is used to create the GUI and set values in global variables
params = hugomatic.toolkit.Parameters('Astromount', 'Part name: %s' %  os.path.basename(__file__), 
                                      picture_file="tripod_arm.gif", # picture on the left
                                      debug_callback=take_a_break)

units = "Inches"
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


z_center_drill = -0.15
center_drill = True
params.addArgument(center_drill, 'Center drill before drilling to depth', group='drill')


operation_drill_tripod = False
params.addArgument(operation_drill_tripod, 'Drill tripod mount screw hole on side', group='top side')
drill_dia_tripod = 0.1509
params.addArgument(drill_dia_tripod, 'Screw drill diameter for tripod mount', group='top side')      

operation_drill_shaft_setscrew = False
params.addArgument(operation_drill_shaft_setscrew, 'Drill shaft set screw hole on side', group='top side')
drill_dia_setscrew = 1.106
params.addArgument(drill_dia_setscrew, 'Screw drill setscrew #36 for #6-32 thread', group='top side')      
x_set_screw = 0.5


params.addArgument(z_center_drill, 'Center drill z depth', group='drill')
drill21_dia = 0.1509
params.addArgument(drill21_dia, 'Screw drill #21 diameter', group='drill')        
operation_drill_motor = True
params.addArgument(operation_drill_motor , 'Drill motor joint screw hole', group='drill')
operation_drill_shaft = True
params.addArgument(operation_drill_shaft , 'Drill arm joint shaft', group='drill')
drill_dia_shaft = 0.25
params.addArgument(drill_dia_shaft, 'Screw drill diameter for shaft', group='drill')
x_center_shaft = 0.5
params.addArgument(x_center_shaft , 'Center x', group='drill')
y_center_shaft = 0.
params.addArgument(y_center_shaft , 'Center y', group='drill')       

operation_mirror = False
params.addArgument(operation_mirror, 'Flip operations for second side', group='side')

shoulder = SHOULDER_SIZE
params.addArgument(shoulder, 'Height of the coupling shoulder', group='motor joint')
dx_recess_motor = RECESS_LENGTH
params.addArgument(dx_recess_motor, 'Length of the motor coupling recess', group='motor joint')
z_recess_motor = z_RECESS
params.addArgument(z_recess_motor, 'Depth of the coupling recess', group='motor joint')

operation_recess_motor = True
params.addArgument(operation_recess_motor, 'Mill the motor joint recess', group='motor joint')

operation_recess_arm = True
params.addArgument(operation_recess_arm, 'Mill the arm joint recess', group='arm joint')
dx_recess_arm = 1.
params.addArgument(dx_recess_arm, 'Length of the motor coupling recess', group='arm joint')
z_recess_arm = -0.15
params.addArgument(z_recess_arm, 'Depth of the coupling recess', group='arm joint')

operation_left_side = True
params.addArgument(operation_left_side, 'Left side rounded', group='arm joint')

        
operation_weight = True
params.addArgument(operation_weight, 'Remove the extra weight', group='Weight')

operation_cut_stock_right = True
params.addArgument(operation_cut_stock_right, 'Cut the right end of stock to length', group='stock')

sixty_pc_cut = True
params.addArgument(sixty_pc_cut, 'Cut stock right to only 60% of stock depth', group='stock')

show_stock_contour = True
params.addArgument(show_stock_contour, 'Show stock contour in EMC', group='stock')
dx_stock = 5.5
params.addArgument(dx_stock, 'Stock length along x', group='stock')
dy_stock = STOCK_HEIGHT
params.addArgument(dy_stock, 'Stock height along y', group='stock')
z_stock = -STOCK_THICK
params.addArgument(z_stock, 'Stock thickness along z', group='stock')


       
# Show the GUI, wait for the user to press the OK button
if params.loadParams():  # returns False if the window is closed without pressing OK
    
    # generate GCODE here!
    hugomatic.code.header(units, feed)   
    tool_changer = hugomatic.code.ToolChanger(0., 0., 0.,  z_safe)
    
         
    if operation_drill_shaft_setscrew:
        tool_changer.change_tool(drill_dia_setscrew, 'drill setscrew #36 for #6-32', 'drill')
        x = 0.5
        y = 0.
        z = -dy_stock * 0.5
        peck =  tool_changer.diameter * 2
        hugomatic.code.peck_drill(x, y, z_safe, z_rapid, peck, z)
        
    if operation_drill_tripod:
        tool_changer.change_tool(drill_dia_tripod, '#21 drill', 'drill')
        # this operation requires flipping the stock
        print "(Drilling camera mount hole)"
        x_tripod_hole = 0.75
        y = 0.
        z = -dy_stock
        peck =  tool_changer.diameter * 2
        hugomatic.code.peck_drill(x, y, z_safe, z_rapid, peck, z)
        
        
        if operation_drill_shaft_setscrew or operation_drill_tripod:
            if center_drill:
                tool_changer.change_tool(0.1, 'Center drill', 'center drill')
                peck = tool_changer.diameter * 2.
                z = z_center_drill
                if operation_drill_shaft_setscrew:
                        hugomatic.code.peck_drill(x_set_screw, 0., z_safe, z_rapid, peck, z)
                if operation_drill_tripod:   
                    hugomatic.code.peck_drill(x_tripod_hole, 0., z_safe, z_rapid, peck, z)
            
            tool_changer.change_tool(drill21_dia, '#21 drill', 'drill')
            peck = tool_changer.diameter * 2.
            z = z_stock
            if operation_drill_shaft_setscrew:
                hugomatic.code.peck_drill(x_set_screw, 0., z_safe, z_rapid, peck, z)
            if operation_drill_tripod:   
                hugomatic.code.peck_drill(x_tripod_hole, 0., z_safe, z_rapid, peck, z)
                

            if show_stock_contour:
                x0 = 0.
                y0 = z_stock * 0.5
                dy = -z_stock
                z1 = z
                hugomatic.code.stock(x0, y0,  dx_stock, dy, 0., z1)
            hugomatic.code.footer()
            exit(0)    
                
    x_motor_hole = dx_stock - dx_recess_motor * 0.5
    y_motor_hole = 0.
    
    if center_drill:
        
        z = z_center_drill
        if operation_drill_shaft:
            tool_changer.change_tool(0.1, 'Center drill', 'center drill')
            peck = tool_changer.diameter * 2.
            x = x_center_shaft
            y = y_center_shaft
            hugomatic.code.peck_drill(x, y, z_safe, z_rapid, peck, z)
        if operation_drill_motor:
            tool_changer.change_tool(0.1, 'Center drill', 'center drill')
            peck = tool_changer.diameter * 2.
            x = x_motor_hole
            y = y_motor_hole
            hugomatic.code.peck_drill(x, y, z_safe, z_rapid, peck, z)
    
        
    if operation_drill_shaft:
        x = x_center_shaft
        y = y_center_shaft    
        tool_changer.change_tool(drill_dia_shaft, 'Shaft drill', 'drill')
        peck = tool_changer.diameter * 2.
        z = z_stock
        print "F %.4f (reduce feed for this large hole)" % (feed * 0.5)
        hugomatic.code.peck_drill(x, y, z_safe, z_rapid, peck, z)
        print "F %.4f (restore feed)" % feed
        
           
    if operation_drill_motor:
        tool_changer.change_tool(drill21_dia, '#21 drill', 'drill')
        print "(Drilling nut joint mount screw hole)"
        x = x_motor_hole
        y = y_motor_hole
        z = z_stock
        peck = tool_changer.diameter * 2.
        hugomatic.code.peck_drill(x, y, z_safe, z_rapid, peck, z)
    
    if operation_recess_arm:
        tool_changer.change_tool(tool_dia, 'flat end mill', 'mill')
        cuts = hugomatic.code.z_cut_compiler(z_recess_arm, cut); # an array of depths
        x0 = 0.
        x1 = dx_recess_arm
        y0 = -dy_stock * 0.5  - tool_dia # bottom of stock, and extra to avoid round corners
        y1 = -y0
        hugomatic.code.pocket_rectangle(x0, y0, x1, y1, z_safe, z_rapid, tool_changer.diameter, cuts)
            
    if operation_recess_motor:
        tool_changer.change_tool(tool_dia, 'flat end mill', 'mill')
        cuts = hugomatic.code.z_cut_compiler(z_recess_motor, cut) # an array of depths
        x0 = dx_stock - dx_recess_motor
        x1 = dx_stock
        y0 = -dy_stock * 0.5 
        y1 = dy_stock * 0.5 # bottom of stock
        bottom_right_recess(x0, y0, x1, y1, shoulder,z_safe, z_rapid, tool_changer.diameter, operation_mirror, cuts)

    
    if operation_left_side:
        tool_changer.change_tool(tool_dia, 'flat end mill', 'mill')
        x0 = 0.75
        y_step = 0.1
        cuts = hugomatic.code.z_cut_compiler(z_stock - z_recess_arm - 0.05, cut, z_surf = z_recess_arm )
        z_rapid_left = z_recess_arm + z_rapid
        contour = TripodLeftSide(x0, dy_stock, y_step, x_center_shaft, y_center_shaft, tool_dia, z_safe, z_rapid_left)
        contour.cut(cuts) 
    
 
    if operation_weight: # remove extra weightz_rapid
        margin = 0.1
        tool_rad = tool_dia * 0.5
        x0 = dx_recess_arm + + margin + tool_rad
        x1 = dx_stock - dx_recess_motor- margin - tool_rad
        y0 = - dy_stock * 0.5 + margin
        y1 = -y0
        z1 = -0.25
        z2 = z_stock * 0.55
        remove_weight(x0, x1, y0, y1, tool_dia, cut, z_safe, z_rapid, z1, z2)
    
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
