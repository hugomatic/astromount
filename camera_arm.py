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
                                      picture_file="camera_arm.gif", # picture on the left
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

operation_drill_camera = False
params.addArgument(operation_drill_camera, 'Drill camera mount screw hole on side', group='Camera')
drill_dia_camera = 0.1509
params.addArgument(drill_dia_camera, 'Screw drill diameter for camera mount', group='Camera')      

operation_mirror = False
params.addArgument(operation_mirror, 'Flip operations for second side', group='side')

z_center_drill = -0.15
center_drill = True
params.addArgument(center_drill, 'Center drill before drilling to depth', group='drill')
params.addArgument(z_center_drill, 'Center drill z depth', group='drill')


drill_dia = 0.1509
params.addArgument(drill_dia, 'Screw drill diameter #21 for 10-32', group='drill')
operation_drill_nut = True
params.addArgument(operation_drill_nut , 'Drill nut joint screw hole', group='drill')
operation_drill_arm = True
params.addArgument(operation_drill_arm , 'Drill arm joint screw hole', group='drill')

shoulder = SHOULDER_SIZE
params.addArgument(shoulder, 'Size of the coupling shoulder', group='couplings')
dx_recess = RECESS_LENGTH
params.addArgument(dx_recess, 'Length of the coupling recess', group='couplings')
z_recess = z_RECESS
params.addArgument(z_recess, 'Depth of the coupling recess', group='couplings')
        
operation_recess_nut = True
params.addArgument(operation_recess_nut, 'Mill the nut joint recess', group='nut joint')


operation_recess_arm = True
params.addArgument(operation_recess_arm, 'Mill the arm joint recess', group='arm joint')

operation_weight = True
params.addArgument(operation_weight, 'Remove the extra weight', group='Weight')

operation_cut_stock_left = True
params.addArgument(operation_cut_stock_left, 'Cut the left end of stock to 0', group='stock')

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
    
    if operation_drill_camera:
        x = 0.75
        y = 0.
        if center_drill:
            peck = 0.1
            z = z_center_drill
            hugomatic.code.peck_drill(x_drill_arm, 0., z_safe, z_rapid, peck, z, feed)
        # this operation requires flipping the stock
        print "(Drilling camera mount hole)"
        
        z = -dy_stock
        peck =  drill_dia_camera * 2
        hugomatic.code.peck_drill(x, y, z_safe, z_rapid, peck, z, feed)
        if show_stock_contour:
            x0 = 0.
            y0 = z_stock * 0.5
            dy = -z_stock
            z1 = z
            hugomatic.code.stock(x0, y0,  dx_stock, dy, 0., z1)
        hugomatic.code.footer()
        exit(0)  
    
        
    tool_changer = hugomatic.code.ToolChanger(0., 0., 0.,  z_safe)
    x_drill_arm = dx_recess * 0.5
    x_drill_nut = dx_stock - dx_recess * 0.5
    
    if center_drill:
        peck = 0.1
        if operation_drill_arm: 
            tool_changer.change_tool(0.1, 'Center drill', 'center drill')
            hugomatic.code.peck_drill(x_drill_arm, 0., z_safe, z_rapid, peck, z_center_drill)
        if operation_drill_nut:
            tool_changer.change_tool(0.1, 'Center drill', 'center drill') 
            hugomatic.code.peck_drill(x_drill_nut, 0., z_safe, z_rapid, peck, z_center_drill)
            
    peck =  drill_dia * 2            
    if operation_drill_arm:   
        tool_changer.change_tool(drill_dia, '#21 drill', 'drill')
        print "(Drilling arm joint mount screw hole)"
        hugomatic.code.peck_drill(x_drill_arm, 0., z_safe, z_rapid, peck, z_stock)
        
    if operation_drill_nut:
        tool_changer.change_tool(drill_dia, '#21 drill', 'drill')
        print "(Drilling nut joint mount screw hole)"
        hugomatic.code.peck_drill(x_drill_nut, 0., z_safe, z_rapid, peck, z_stock)
    
    if operation_recess_arm:
        tool_changer.change_tool(tool_dia, 'flat end mill', 'mill')
        cuts = hugomatic.code.z_cut_compiler(z_recess, cut)  # an array of depths
        x0 = 0.
        x1 = dx_recess 
        y0 = -dy_stock * 0.5 
        y1 = dy_stock * 0.5
        bottom_left_recess(x0, y0, x1, y1, shoulder, z_safe, z_rapid, tool_changer.diameter, operation_mirror, cuts)
            
    if operation_recess_nut:
        tool_changer.change_tool(tool_dia, 'flat end mill', 'mill')
        cuts = hugomatic.code.z_cut_compiler(z_recess, cut); # an array of depths
        x0 = dx_stock - dx_recess 
        x1 = dx_stock 
        y0 = -dy_stock * 0.5 
        y1 = dy_stock * 0.5
        top_right_recess(x0, y0, x1, y1, shoulder, z_safe, z_rapid, tool_changer.diameter, operation_mirror, cuts)
   
    
    if operation_weight: # remove extra weight
        margin = 0.1
        tool_rad = tool_dia * 0.5
        x0 = dx_recess + + margin + tool_rad
        x1 = dx_stock - dx_recess- margin - tool_rad
        y0 = - dy_stock * 0.5 + margin
        y1 = -y0
        z1 = -0.25
        z2 = z_stock * 0.55
        remove_weight(x0, x1, y0, y1, tool_dia, cut, z_safe, z_rapid, z1, z2)
    

    if operation_cut_stock_left:
        tool_changer.change_tool(tool_dia, 'flat end mill', 'mill')
        cuts = hugomatic.code.z_cut_compiler(z_stock, cut) # z_surf = 0 first_cut = cut, last_cut = cut
        x0 = 0. - tool_dia * 0.5
        x1 = x0
        y0 = dy_stock * 0.5 + tool_dia
        y1 = -y0
        hugomatic.code.line(x0, y0, x1, y1, z_safe, z_rapid, cuts)

    if operation_cut_stock_right:
        tool_changer.change_tool(tool_dia, 'flat end mill', 'mill')
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
