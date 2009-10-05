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
tool_z_max = -0.5
params.addArgument(tool_z_max, 'End mill maximum plunge depth', group='setup')


z_center_drill = -0.15
center_drill = True
params.addArgument(center_drill, 'Center drill before drilling to depth', group='drill')

operation_drill_tripod = False
params.addArgument(operation_drill_tripod, 'Drill tripod mount screw hole on side', group='top side')
drill_dia_tripod = 0.1509
params.addArgument(drill_dia_tripod, 'Screw drill diameter for tripod mount', group='top side')      
x_tripod_hole = 1.
params.addArgument(x_tripod_hole, 'Tripod mount hole x position', group='top side')

operation_recess_left_joint = False
params.addArgument(operation_recess_left_joint, 'Mill the left joint joint recess', group='top side')
dx_recess_arm = 0.75
params.addArgument(dx_recess_arm, 'Length of the left joint recess', group='top side')
z_recess_arm = -0.55
params.addArgument(z_recess_arm, 'Depth of the coupling recess', group='top side')
operation_joint_hole = False
params.addArgument(operation_joint_hole, 'Drill joint hole', group='top side')
x_joint_hole = 0.5 * dx_recess_arm

operation_mill_motor_slot_right = False
params.addArgument(operation_mill_motor_slot_right, 'Mill right motor slot', group='Top')
motor_slot_dx = 0.75
params.addArgument(motor_slot_dx, 'Motor slot dx', group='Top')
mill_shaft_dy = 0.5
params.addArgument(mill_shaft_dy, 'Motor slot dy', group='Top')


params.addArgument(z_center_drill, 'Center drill z depth', group='drill')
drill21_dia = 0.1509
params.addArgument(drill21_dia, 'Screw drill #21 diameter', group='drill')        

operation_bearing = True
params.addArgument(operation_bearing , 'Cut ball bearing hole', group='ball bearings')
x_bb_left = 11.43 /2 + dx_recess_arm*0.5
params.addArgument(x_bb_left , 'Ball bearing center x', group='ball bearings')
y_bb = 0.
params.addArgument(y_bb , 'Ball bearing y', group='ball bearings')
bearing_large_dia = 0.5
params.addArgument(bearing_large_dia , 'ball bearing large diameter', group='ball bearings')
bearing_small_dia = 0.35
params.addArgument(bearing_small_dia , 'ball bearing small diameter', group='ball bearings')
z_bearing_step = -0.20
params.addArgument(z_bearing_step , 'ball bearing z step', group='ball bearings')
       
operation_weight = True
params.addArgument(operation_weight, 'Remove the extra weight', group='Weight')

operation_cut_stock_left = True
params.addArgument(operation_cut_stock_left, 'Cut the left end of stock to 0', group='stock')

operation_cut_stock_right = True
params.addArgument(operation_cut_stock_right, 'Cut the right end of stock to length', group='stock')

show_stock_contour = True
params.addArgument(show_stock_contour, 'Show stock contour in EMC', group='stock')
dx_stock = 6.5
params.addArgument(dx_stock, 'Stock length along x', group='stock')
dy_stock = STOCK_HEIGHT
params.addArgument(dy_stock, 'Stock height along y', group='stock')
z_stock = -STOCK_THICK
params.addArgument(z_stock, 'Stock thickness along z', group='stock')

def bearing(x,y):
    z_depth = z_stock
    if z_depth < tool_z_max:
         z_depth = tool_z_max
    bearing_heli(x,y, bearing_large_dia, bearing_small_dia, tool_dia, z_bearing_step, z_depth, z_safe, z_rapid, cut )

       
# Show the GUI, wait for the user to press the OK button
if params.loadParams():  # returns False if the window is closed without pressing OK
    
    # generate GCODE here!
    hugomatic.code.header(units, feed)   
    tool_changer = hugomatic.code.ToolChanger(0., 0., 0.,  z_safe)
    
#    if operation_joint_hole:
#        tool_changer.change_tool(drill_dia_tripod, '#21 drill', 'drill')
#        # this operation requires flipping the stock
#        print "(Drilling camera mount hole)"
#        x_joint_hole = 0.5 * dx_recess_arm
#        y = 0.
#        z = -dy_stock
#        peck =  tool_changer.diameter * 2
#        hugomatic.code.peck_drill(x, y, z_safe, z_rapid, peck, z)
#        
#        
#    if operation_drill_tripod:
#        tool_changer.change_tool(drill_dia_tripod, '#21 drill', 'drill')
#        # this operation requires flipping the stock
#        print "(Drilling camera mount hole)"
#        x = x_tripod_hole
#        y = 0.
#        z = -dy_stock
#        peck =  tool_changer.diameter * 2
#        hugomatic.code.peck_drill(x, y, z_safe, z_rapid, peck, z)
#        
#        
    if operation_joint_hole  or operation_drill_tripod:
        x_joint_hole = 0.5 * dx_recess_arm
        if center_drill:
            tool_changer.change_tool(0.1, 'Center drill', 'center drill')
            peck = tool_changer.diameter * 2.
            z = z_center_drill
            if operation_joint_hole:
                    hugomatic.code.peck_drill(x_joint_hole, 0., z_safe, z_rapid, peck, z)
            if operation_drill_tripod:   
                hugomatic.code.peck_drill(x_tripod_hole, 0., z_safe, z_rapid, peck, z)
        
        tool_changer.change_tool(drill21_dia, '#21 drill', 'drill')
        peck = tool_changer.diameter * 2.
        z = z_stock
        if operation_joint_hole:
            hugomatic.code.peck_drill(x_joint_hole, 0., z_safe, z_rapid, peck, z)
        if operation_drill_tripod:   
            hugomatic.code.peck_drill(x_tripod_hole, 0., z_safe, z_rapid, peck, z)
    
        if operation_mill_motor_slot_right:
            tool_changer.change_tool(tool_dia, 'flat end mill', 'mill')
            x0 = dx_stock - motor_slot_dx
            x1 = dx_stock + tool_dia 
            y0 = mill_shaft_dy * -0.5
            y1 = -y0
            z = z_stock
            if z < tool_z_max:
                z = tool_z_max
            cuts = hugomatic.code.z_cut_compiler(z, cut)
            hugomatic.code.pocket_rectangle(x0, y0, x1, y1, z_safe, z_rapid, tool_dia, cuts)

        if operation_recess_left_joint:
            tool_changer.change_tool(tool_dia, 'flat end mill', 'mill')
            cuts = hugomatic.code.z_cut_compiler(z_recess_arm, cut); # an array of depths
            x0 = 0. - tool_dia *0.5
            x1 = dx_recess_arm
            y0 = -dy_stock * 0.5  - tool_dia # bottom of stock, and extra to avoid round corners
            y1 = -y0
            hugomatic.code.pocket_rectangle(x0, y0, x1, y1, z_safe, z_rapid, tool_changer.diameter, cuts)


        if operation_mill_motor_slot_right or operation_recess_left_joint or operation_joint_hole or operation_drill_tripod or operation_recess_left_joint:
            if show_stock_contour:
                x0 = 0.
                y0 = z_stock * 0.5
                dy = -z_stock
                z1 = -dy_stock
                hugomatic.code.stock(x0, y0,  dx_stock, dy, 0., z1)
            #hugomatic.code.footer()
            #exit(0)    
                
    
   

            
    if operation_bearing:      
        tool_changer.change_tool(tool_dia, 'flat end mill', 'mill')
        bearing(x_bb_left, y_bb);
 
    
    if operation_cut_stock_left:
        z = z_stock
        if z< tool_z_max:
            z = tool_z_max
        tool_changer.change_tool(tool_dia, 'flat end mill', 'mill')
        cuts = hugomatic.code.z_cut_compiler(z, cut) # z_surf = 0 first_cut = cut, last_cut = cut
        x0 = 0. - tool_dia * 0.5
        x1 = x0
        y0 = dy_stock * 0.5 + tool_dia
        y1 = -y0
        hugomatic.code.line(x0, y0, x1, y1, z_safe, z_rapid, cuts)
    
 
    if operation_weight: # remove extra weightz_rapid
        margin = 0.1
        tool_rad = tool_dia * 0.5
        x0 = dx_recess_arm + + margin + tool_rad
        x1 = dx_stock -motor_slot_dx- margin - tool_rad
        y0 = - dy_stock * 0.5 + margin
        y1 = -y0
        z1 = -0.25
        z2 = z_stock * 0.55
        remove_weight(x0, x1, y0, y1, tool_dia, cut, z_safe, z_rapid, z1, z2)
    
    if operation_cut_stock_right:
        z = z_stock
        if z< tool_z_max:
            z = tool_z_max
        cuts = hugomatic.code.z_cut_compiler(z, cut)
        x0 = dx_stock + tool_dia * 0.5
        x1 = x0
        y0 = dy_stock * 0.5 + tool_dia
        y1 = -y0
        hugomatic.code.line(x0, y0, x1, y1, z_safe, z_rapid, cuts)

        
    if show_stock_contour:
        hugomatic.code.stock(0, -dy_stock * 0.5,  dx_stock, dy_stock, 0., z_stock)

        
    hugomatic.code.footer()
