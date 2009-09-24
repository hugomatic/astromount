import hugomatic.code

STOCK_THICK = 0.75 #0.625        #5./8.
STOCK_HEIGHT= 0.75
STOCK_THICK_JOINT = 0.25 #0.375  3/8

RECESS_LENGTH = 0.75
z_RECESS = -0.1
SHOULDER_SIZE = 0.2

def screwCap1032 (x, y, cut, z_safe, z_rapid, z, tool_dia):
    diameter = 0.31 + 0.07     
    z = -0.22 
    print ""
    print "\n(screwCap1032 %.4f %.4f)" % (x, y)
    cuts =  hugomatic.code.z_cut_compiler(z, cut)
    hugomatic.code.circle_heli_tool_inside(x, y, diameter, z_safe, z_rapid, tool_dia, cuts)

def bearing_heli   (x,y, bearing_large_dia, bearing_small_dia, tool_dia, z_bearing_step, z, z_safe, z_rapid, cut ):     
    z1 = z_bearing_step
    z2 = z
    z2_rapid = z1 + 0.05
    cuts_large = hugomatic.code.z_cut_compiler(z1, cut, z_surf = z_rapid)
    hugomatic.code.circle_heli_tool_inside(x, y, bearing_large_dia,  z_safe, z_rapid, tool_dia, cuts_large)
    cuts_small = hugomatic.code.z_cut_compiler(z2 , cut, z_surf = z2_rapid)
    hugomatic.code.circle_heli_tool_inside(x, y, bearing_small_dia, z_safe, z2_rapid, tool_dia, cuts_small)


def remove_weight(x0, x1, y0, y1, tool_dia, cut, z_safe, z_rapid, z1, z2):
    print "(Remove extra weight)"
    cuts = hugomatic.code.z_cut_compiler(z1, cut)
    hugomatic.code.pocket_rectangle(x0, y0, x1, y1, z_safe, z_rapid, tool_dia, cuts)
    
    cuts = hugomatic.code.z_cut_compiler(z2, cut, z_surf = z1)
    spacer_x = (x1 -x0) /13.
    spacer_y = 0.1 #(y1 - y0 )* 0.25
    for i in range(4):
        x_pocket0 = x0 + (i * 3 +1) * spacer_x 
        y_pocket0 = y0 + spacer_y
        x_pocket1 = x_pocket0 + 2 * spacer_x
        y_pocket1 = y1 - spacer_y
        z = z2
        z_safe2 = z_safe + z1 
        z_rapid2 = z_rapid + z1
        hugomatic.code.pocket_rectangle(x_pocket0, y_pocket0, x_pocket1, y_pocket1, z_safe2, z_rapid2, tool_dia, cuts)

def top_right_recess(x0, y0, x1, y1, shoulder, z_safe, z_rapid, tool_dia, mirror, cuts):  
    # enlarge rectangle to avoid round corners
    # on right and top sides
    x1 += tool_dia 
    y1 += tool_dia
    
    #leave shoulder on bottom
    y0 += shoulder
    
    x_line0 = x0 + tool_dia * 0.5
    y_line0 = y0 + tool_dia * 0.5
    x_line1 = x0
    y_line1 = y0
    if mirror:
        swap = y0
        y0 = -y1
        y1 = -swap
        x_line0 = x0 + tool_dia * 0.5
        y_line0 = y1 - tool_dia * 0.5
        x_line1 = x0
        y_line1 = y1
    hugomatic.code.pocket_rectangle(x0, y0, x1, y1, z_safe, z_rapid, tool_dia, cuts)
    # line to remove rounded corner
    hugomatic.code.line(x_line0, y_line0, x_line1, y_line1, z_safe, z_rapid, cuts)
    
def bottom_right_recess(x0, y0, x1, y1, shoulder, z_safe, z_rapid, tool_dia, mirror, cuts): 
    mirror = not mirror
    top_right_recess(x0, y0, x1, y1, shoulder, z_safe, z_rapid, tool_dia, mirror, cuts)
 
def bottom_left_recess(x0, y0, x1, y1, shoulder, z_safe, z_rapid, tool_dia, operation_mirror, cuts):
    # enlarge rectangle to avoid round corners
    # on left and bottom sides
    x0 = x0 -tool_dia
    y0 = y0 -tool_dia
    
    # leave shoulder on top
    y1 += -shoulder
    
    x_line0 = x1 - tool_dia * 0.5
    y_line0 = y1 - tool_dia * 0.5
    x_line1 = x1
    y_line1 = y1
    if operation_mirror:
        swap = y0
        y0 = -y1
        y1 = -swap
        x_line0 = x1 - tool_dia * 0.5
        y_line0 = y0 + tool_dia * 0.5
        x_line1 = x1
        y_line1 = y0
    hugomatic.code.pocket_rectangle(x0, y0, x1, y1, z_safe, z_rapid, tool_dia, cuts)
    # line to remove rounded corner
    hugomatic.code.line(x_line0, y_line0, x_line1, y_line1, z_safe, z_rapid, cuts)

class Contour(object):
    
    def __init__(self, 
                 x0,
                 y0,
                 tool_dia,
                 z_safe, 
                 z_rapid):
                 
        self.x0 = x0
        self.y0 = y0
        self.tool_dia = tool_dia
        
        self.z_safe = z_safe
        self.z_rapid = z_rapid
        
        self.tool_rad = 0.5 * tool_dia
           
    def _approach(self):

        print "g0 z%.4f" % self.z_safe
        print "g0 x%.4f y%.4f" % (self.x0, self.y0)
        print "g0 z%.4f" % self.z_rapid
        
        
    def _retract(self):
        print "G4 p0.1 (0.1 sec Pause)" 
        print "g0 z%.4f" % self.z_safe
        
        
    def _mill(self, z):
        print "(mill z = %.4f)" % z
          
    def cut(self, cuts):
        print "(Cutting %s)" % type(self).__name__
        self._approach()
        for z in cuts:
            self._mill(z)
        self._retract()
        
        
class TripodLeftSide(Contour):
    def __init__(self, x0, stock_dy, y_step, x_center, y_center, tool_dia, z_safe, z_rapid):
        # set x0,y0 to be the right side of the tool
        x = x0 - tool_dia * 0.5
        y = stock_dy * 0.5 + tool_dia * 0.5
        Contour.__init__(self, x, y, tool_dia, z_safe, z_rapid)
        
        self.y_step = y_step
        self.x_center = x_center
        self.y_center = y_center
        
        
    
    def _approach(self):

        print "g0 z%.4f" % self.z_safe
        print "g0 x%.4f y%.4f" % (self.x0, self.y0)
        print "g0 z%.4f" % self.z_rapid
 
    
    def _mill(self, z):
        print "(mill z = %.4f)" % z
        print "g1 z%.4f" % z
        y = self.y0 - self.y_step #+ self.tool_rad
        print "g1 y%.4f (top step)" % y
        x = self.x_center
        print "g1 x%.4f (above center)" % x
        j = -y
        y = -y
        i = 0.
        print "g3 x%.4f y%.4f i%.4f j%.4f" % (x,y,i,j)
        x = self.x0
        print "g1 x%.4f (below center)" % x
        y = - self.y0
        print "g1 y%.4f (bottom step)" % y
        print "g0 z%.4f" % self.z_rapid
        print "g0 y%.4f" % self.y0
