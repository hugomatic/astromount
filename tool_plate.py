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
                                      picture_file="tool_plate.gif", # picture on the left
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
center_drill = True
params.addArgument(center_drill, 'Center drill holes before drilling', group='setup')

operation_back_groove = True
params.addArgument(operation_back_groove , 'Back groove', group='back')
operation_back_rect = True
params.addArgument(operation_back_rect , 'Back rectangle', group='back')
z_groove = -0.075
params.addArgument(z_groove, 'Depth of groove and rectangle along z', group='back')
operation_back_drill = True
params.addArgument(operation_back_drill, 'Drill holes for clamps', group='back')

drill21_dia = 0.1509
params.addArgument(drill21_dia, 'Screw drill diameter #21', group='screws')

operation_screws = True
params.addArgument(operation_screws, 'Screws mount holes', group='mount')
tool2_dia = 0.125
params.addArgument(tool2_dia, 'Mill end dia for mount holes', group='mount')

z_center_drill = -0.10
drill2_dia = 0.2
params.addArgument(drill2_dia, 'Drill dia for mount holes', group='mount')
x1_hole = 0.3
params.addArgument(x1_hole, 'M hole 1 x position', group='mount')
x2_hole = 4.7
params.addArgument(x2_hole, 'M hole 1 x position', group='mount')

operation_cut_stock_left = True
params.addArgument(operation_cut_stock_left, 'Cut the left end of stock to 0', group='stock')

operation_cut_stock_right = True
params.addArgument(operation_cut_stock_right, 'Cut the right end of stock to length', group='stock')

operation_recess = True
params.addArgument(operation_recess, 'Mill recess', group='recess')

show_stock_contour = True
params.addArgument(show_stock_contour, 'Show stock contour in EMC', group='stock')
dx_stock = 5
params.addArgument(dx_stock, 'Stock length along x', group='stock')
dy_stock = 1.5
params.addArgument(dy_stock, 'Stock height along y', group='stock')
z_stock = -0.377
params.addArgument(z_stock, 'Stock thickness along z', group='stock')

          
        
# Show the GUI, wait for the user to press the OK button
if params.loadParams():  # returns False if the window is closed without pressing OK
    
    # generate GCODE here!
    hugomatic.code.header(units, feed)   
    

    tool_changer = hugomatic.code.ToolChanger(0., 0., 0.,  z_safe)
    if operation_back_groove:   
        
        tool_changer.change_tool(tool_dia, 'flat end mill' , 'mill')
        print "(back slot)"
        
        x0 = 0.
        y0 = 0.
        x1 = dx_stock
        y1 = 0.
        z = z_groove
        cuts = hugomatic.code.z_cut_compiler(z, cut)
        hugomatic.code.line(x0, y0, x1, y1, z_safe, z_rapid, cuts)
   
    if operation_back_rect:   
        tool_changer.change_tool(tool_dia, 'flat end mill' , 'mill')
        x0 = 0.
        y0 = dy_stock * -0.5 
        x1 = dx_stock
        y1 = -y0
        z = z_groove
        cuts = hugomatic.code.z_cut_compiler(z, cut)
        hugomatic.code.rectangle(x0, y0, x1, y1, z_safe, z_rapid, tool_dia, cuts)
        
    if operation_screws:
        
        if center_drill:
            peck = 0.1
            tool_changer.change_tool(0.1, 'Center drill', 'center drill')
            hugomatic.code.peck_drill(x1_hole, 0., z_safe, z_rapid, peck, z_center_drill)
            hugomatic.code.peck_drill(x2_hole, 0., z_safe, z_rapid, peck, z_center_drill)
            
        peck =  drill2_dia * 2            
        tool_changer.change_tool(drill2_dia, 'drill', 'drill')
        print "(Drilling mount screw hole)"
        hugomatic.code.peck_drill(x1_hole, 0., z_safe, z_rapid, peck, z_stock - 0.05)
        hugomatic.code.peck_drill(x2_hole, 0., z_safe, z_rapid, peck, z_stock - 0.05)
    
        tool_changer.change_tool(tool2_dia, 'Screw cap hole mill', 'mill')
        y = 0.
        screwCap1032(x1_hole, y, cut, z_safe, z_rapid, -0.22, tool2_dia)
        screwCap1032(x2_hole, y, cut, z_safe, z_rapid, -0.22, tool2_dia)
    
    if operation_back_drill:
        x = 0.25
        y = dy_stock * -0.5 + 0.3
        positions = [x]
        while x < dx_stock:
            positions.append(x)
            x+= 0.25
            
        if center_drill:
            peck = 0.1
            tool_changer.change_tool(0.1, 'Center drill', 'center drill')
            for xi in positions:
                hugomatic.code.peck_drill(xi, y, z_safe, z_rapid, peck, z_center_drill)
        
        tool_changer.change_tool(drill21_dia, 'drill #21', 'drill')
        peck =  tool_changer.diameter * 2.
        for xi in positions:
                hugomatic.code.peck_drill(xi, y, z_safe, z_rapid, peck, z_stock - 0.05)  
                 
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
        
        cuts = hugomatic.code.z_cut_compiler(z, cut)
        x0 = dx_stock + tool_dia * 0.5
        x1 = x0
        y0 = dy_stock * 0.5 + tool_dia
        y1 = -y0
        hugomatic.code.line(x0, y0, x1, y1, z_safe, z_rapid, cuts)
    
    if operation_recess:
        tool_changer.change_tool(tool_dia, 'flat end mill', 'mill')
        x0 = 0 - tool_dia
        x1 = dx_stock + tool_dia
        y0 = dy_stock*-0.5 - tool_dia
        y1 = dy_stock*0.5 - 0.2
        z_recess = -0.162
        cuts = hugomatic.code.z_cut_compiler(z_recess, cut)
        hugomatic.code.pocket_rectangle(x0, y0, x1, y1, z_safe, z_rapid, tool_dia, cuts)
    
    if show_stock_contour:
        hugomatic.code.stock(0, -dy_stock * 0.5,  dx_stock, dy_stock, 0., z_stock)

        
    hugomatic.code.footer()
