# ========================================================================================
# OLD FILE -- USED TO LAY OUT 280GHz LED ARRAY
# preserved here for reference
# https://github.com/Wheeler1711/kicad/blob/main/led_mapper_CCAT_kicad_v6/place_stuff.py
# ========================================================================================


# for pcbnew CCAT led
# execfile("/Users/jdw8/Documents/kicad_projects/led_mapper_CCAT/place_stuff.py")

import pcbnew
import time

pcb = pcbnew.GetBoard()

# delet all tracks to left of diagonal
'''
for t in pcb.GetTracks():
    end = t.GetEnd()
    start = t.GetStart()
    max_x = max(start[0],end[0])
    if max_x == end[0]:
        y_max = end[1]
    else:
        y_max = start[1]
    if max_x<2.8*25400*10**3-y_max/3**0.5:
        pcb.Delete(t)
'''
#delete all tracks
for t in pcb.GetTracks():
    pcb.Delete(t)

#pcbnew.Refresh()
#time.sleep(5)

netcodes = pcb.GetNetsByNetcode()

half_pad = 0.762*10**6
pixel_y = (3**0.5/2*2750)*10**3
pixel_x = 2750*10**3
five_mils = 0.127*10**6
y_offset = 0

#for netcode, net in netcodes.items():
#    print("netcode {}, name {}".format(netcode, net.GetNetname()))

#layertable = {}

#numlayers = pcbnew.LAYER_ID_COUNT
#for i in range(numlayers):
#    layertable[i] = pcb.GetLayerName(i)
#    print("{} {}".format(i, pcb.GetLayerName(i)))

layertable = {}

for i in range(1000):
    name = pcb.GetLayerName(i)
    if name != "BAD INDEX!":
        layertable[name]=i

front_copper_layer = layertable['F.Cu']
back_copper_layer = layertable['B.Cu']
edgecut = layertable['Edge.Cuts']

count = 0
for i in range(0,24):
    
    for j in range(0,12):
        
        mod = pcb.FindFootprintByReference('D'+str(count+1))
        x = 24*pixel_x-(j*pixel_x/2+i*pixel_x)
        y = y_offset+j*pixel_y
        mod.SetPosition(pcbnew.wxPoint(x, y))
        mod.SetOrientation(90*10)
        count = count+1


#connect 24 columns to gether with red tracks
count = 0
for i in range(0,24):   
    for j in range(0,11):
        mod = pcb.FindFootprintByReference('D'+str(count+1))
        for pad in mod.Pads():
            if int(pad.GetPadName()) == 1:
                pad1 = pad
                net1 = pad.GetNetCode()
            else:
                pad2 = pad
                net2 = pad.GetNetCode()
        x = 24*pixel_x-(j*pixel_x/2+i*pixel_x)+five_mils*0.5 #1.5
        y = y_offset+j*pixel_y+half_pad-five_mils#added five_mils
        #track 1
        track = pcbnew.PCB_TRACK(pcb)
        track.SetStart(pcbnew.wxPoint(x, y))
        track.SetEnd(pcbnew.wxPoint(x, y+pixel_y-five_mils))
        track.SetWidth(int(0.127*10**6))
        track.SetLayer(front_copper_layer)
        pcb.Add(track)
        #track.SetNetCode(net2)
        #track 2
        track = pcbnew.PCB_TRACK(pcb)
        track.SetStart(pcbnew.wxPoint(x, y+pixel_y-five_mils))
        track.SetEnd(pcbnew.wxPoint(x-pixel_y/2-five_mils*2,y+pixel_y-five_mils))
        track.SetWidth(int(0.127*10**6))
        track.SetLayer(front_copper_layer)
        pcb.Add(track)
        #track.SetNetCode(net2)
        count = count +1

#connect diagonals with vias and green tracks
count = 0
for i in range(0,24):   
    for j in range(0,12):
        mod = pcb.FindFootprintByReference('D'+str(count+1))
        for pad in mod.Pads():
            if int(pad.GetPadName()) == 1:
                pad1 = pad
                net1 = pad.GetNetCode()
            else:
                pad2 = pad
                net2 = pad.GetNetCode()
        x = 24*pixel_x-(j*pixel_x/2+i*pixel_x)+7*five_mils #8*
        y = y_offset+j*pixel_y-half_pad+five_mils
            
        v = pcbnew.PCB_VIA(pcb)
        pcb.Add(v)
        v.SetPosition(pcbnew.wxPoint(x,y))
        v.SetWidth(int(0.6*10**6))
        v.SetDrill(int(0.3*10**6))
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetLayerPair(front_copper_layer, back_copper_layer)
        v.SetNetCode(net2)

        track = pcbnew.PCB_TRACK(pcb)
        track.SetStart(pcbnew.wxPoint(x, y))
        track.SetEnd(pcbnew.wxPoint(x-half_pad, y))
        track.SetWidth(int(0.127*10**6))
        track.SetLayer(front_copper_layer)
        pcb.Add(track)

        #add green track        track = pcbnew.PCB_TRACK(pcb)
        
        if i == 0:
            if j != 11:
                
                track = pcbnew.PCB_TRACK(pcb)
                track.SetStart(pcbnew.wxPoint(x, y))
                track.SetEnd(pcbnew.wxPoint(x+five_mils*5.5+five_mils*(12-j)*0.7, y))
                track.SetWidth(int(0.127*10**6))
                track.SetLayer(back_copper_layer)
                pcb.Add(track)
                
                #track 2 track to connect to pins
                track = pcbnew.PCB_TRACK(pcb)
                track.SetStart(pcbnew.wxPoint(x+five_mils*5.5+five_mils*(12-j)*0.7, y))
                track.SetEnd(pcbnew.wxPoint(x+five_mils*5.5+five_mils*(12-j)*0.7+five_mils*5+five_mils*j*1.5, y-five_mils*5-five_mils*j*1.5))
                track.SetWidth(int(0.127*10**6))
                track.SetLayer(back_copper_layer)
                pcb.Add(track)
                #track 3 track to connect to pins
                track = pcbnew.PCB_TRACK(pcb)
                track.SetStart(pcbnew.wxPoint(x+five_mils*5.5+five_mils*(12-j)*0.7+five_mils*5+five_mils*j*1.5, y-five_mils*5-five_mils*j*1.5))
                track.SetEnd(pcbnew.wxPoint(x+five_mils*5.5+five_mils*(12-j)*0.7+five_mils*5+five_mils*j*1.5+five_mils*22*3**0.5, y-five_mils*5-five_mils*j*1.5+five_mils*22))
                track.SetWidth(int(0.127*10**6))
                track.SetLayer(back_copper_layer)
                pcb.Add(track)
                #track r track to connect to pins
                track = pcbnew.PCB_TRACK(pcb)
                track.SetStart(pcbnew.wxPoint(x+five_mils*5.5+five_mils*(12-j)*0.7+five_mils*5+five_mils*j*1.5+five_mils*22*3**0.5, y-five_mils*5-five_mils*j*1.5+five_mils*22))
                track.SetEnd(pcbnew.wxPoint(x+five_mils*5.5+five_mils*(12-j)*0.7+five_mils*5+five_mils*j*1.5+five_mils*22*3**0.5, y-five_mils*5-five_mils*j*1.5+five_mils*22+five_mils*35))
                track.SetWidth(int(0.127*10**6))
                track.SetLayer(back_copper_layer)
                pcb.Add(track)
                ''' #here
                v = pcbnew.PCB_VIA(pcb)
                pcb.Add(v)
                v.SetPosition(pcbnew.wxPoint(x+9*five_mils, y))
                v.SetWidth(int(0.6*10**6))
                v.SetDrill(int(0.3*10**6))
                v.SetViaType(pcbnew.VIA_THROUGH)
                v.SetLayerPair(front_copper_layer, back_copper_layer)
                v.SetNetCode(net2)
                
                
                track = pcbnew.PCB_TRACK(pcb)
                track.SetStart(pcbnew.wxPoint(x+9*five_mils, y))
                track.SetEnd(pcbnew.wxPoint(x+16*five_mils, y))
                track.SetWidth(int(0.127*10**6))
                track.SetLayer(front_copper_layer)
                pcb.Add(track)
                '''

        if i != 0:
            if j != 11:
                track = pcbnew.PCB_TRACK(pcb)
                track.SetStart(pcbnew.wxPoint(x, y))
                track.SetEnd(pcbnew.wxPoint(x+pixel_x/2, y+pixel_y))
                track.SetWidth(int(0.127*10**6))
                track.SetLayer(back_copper_layer)
                pcb.Add(track)
        
        count = count+1


#traces to connect the top in red
j = 0
for i in range(1,24):
        x = 24*pixel_x-(j*pixel_x/2+i*pixel_x)+0*five_mils#2 to 0
        y = y_offset+j*pixel_y+half_pad-2.5*five_mils#-3*five_mils
        #track 1
        '''
        track = pcbnew.PCB_TRACK(pcb)
        track.SetStart(pcbnew.wxPoint(x, y))
        track.SetEnd(pcbnew.wxPoint(x, y-half_pad))
        track.SetWidth(int(0.127*10**6))
        track.SetLayer(front_copper_layer)
        pcb.Add(track)
        '''
        #track 2
        track = pcbnew.PCB_TRACK(pcb)
        track.SetStart(pcbnew.wxPoint(x, y))
        track.SetEnd(pcbnew.wxPoint(x+pixel_x/3, y))
        track.SetWidth(int(0.127*10**6))
        track.SetLayer(front_copper_layer)
        pcb.Add(track)
        #track 4
        track = pcbnew.PCB_TRACK(pcb)
        track.SetStart(pcbnew.wxPoint(x+pixel_x/3, y))
        track.SetEnd(pcbnew.wxPoint(x+pixel_x*0.6, y-1.25*half_pad))
        track.SetWidth(int(0.127*10**6))
        track.SetLayer(front_copper_layer)
        pcb.Add(track)
        #track 5
        track = pcbnew.PCB_TRACK(pcb)
        track.SetStart(pcbnew.wxPoint(x+pixel_x*0.6, y-1.25*half_pad))
        track.SetEnd(pcbnew.wxPoint(x+pixel_x*1/2+half_pad*1.5, y-1.25*half_pad))
        track.SetWidth(int(0.127*10**6))
        track.SetLayer(front_copper_layer)
        pcb.Add(track)

#add vias and tracks bottom row green
j = 11
count = 11*24
for i in range(12,24):
    x = 24*pixel_x-(j*pixel_x/2+i*pixel_x)+5.5*five_mils+pixel_x/2+five_mils*12 #13
    y = y_offset+j*pixel_y+five_mils*4
    mod = pcb.FindFootprintByReference('D'+str(count+1))
    for pad in mod.Pads():
        if int(pad.GetPadName()) == 1:
            pad1 = pad
            net1 = pad.GetNetCode()
        else:
            pad2 = pad
            net2 = pad.GetNetCode()
    v = pcbnew.PCB_VIA(pcb)
    pcb.Add(v)
    v.SetPosition(pcbnew.wxPoint(x,y))
    v.SetWidth(int(0.6*10**6))
    v.SetDrill(int(0.3*10**6))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(front_copper_layer, back_copper_layer)
    v.SetNetCode(net2)

    count = count+1
    # the track
    
    x2 = 24*pixel_x-(j*pixel_x/2+i*pixel_x)+8*five_mils
    y2 = y_offset+j*pixel_y-half_pad+five_mils
    track = pcbnew.PCB_TRACK(pcb)
    track.SetStart(pcbnew.wxPoint(x, y))
    track.SetEnd(pcbnew.wxPoint(x2, y2))
    track.SetWidth(int(0.127*10**6))
    track.SetLayer(back_copper_layer)
    pcb.Add(track)
    
    #the red track
    '''
    track = pcbnew.PCB_TRACK(pcb)
    track.SetStart(pcbnew.wxPoint(x, y))
    track.SetEnd(pcbnew.wxPoint(x+half_pad, y+half_pad))
    track.SetWidth(int(0.127*10**6))
    track.SetLayer(front_copper_layer)
    pcb.Add(track)
    '''
# now the backleg red to geen
count = 0
for i in range(1,13):   
    for j in range(1,12):
        mod = pcb.FindFootprintByReference('D'+str(count+1))
        for pad in mod.Pads():
            if int(pad.GetPadName()) == 1:
                pad1 = pad
                net1 = pad.GetNetCode()
            else:
                pad2 = pad
                net2 = pad.GetNetCode()
        x = 24*pixel_x-(j*pixel_x/2+i*pixel_x)+pixel_x+pixel_x/4+five_mils#nothing
        y = y_offset+j*pixel_y+half_pad-pixel_y/2-0*five_mils#used to be times 2*
        #track 1
        track = pcbnew.PCB_TRACK(pcb)
        if j == 11:
            track.SetStart(pcbnew.wxPoint(x, y)) #bottom
        elif j==1:
            track.SetStart(pcbnew.wxPoint(x-five_mils, y-half_pad)) #middle #addin whole line
        else:
            track.SetStart(pcbnew.wxPoint(x, y-half_pad)) #middle
        if j == 1:
            track.SetEnd(pcbnew.wxPoint(x-five_mils, y-pixel_y/2-6*five_mils)) #top #add minus five_mils minus 6* versus 4*
            
        else:
            track.SetEnd(pcbnew.wxPoint(x, y-pixel_y-half_pad))
        track.SetWidth(int(0.127*10**6))
        track.SetLayer(front_copper_layer)
        pcb.Add(track)
        if j == 1: #drop via
            v = pcbnew.PCB_VIA(pcb)
            pcb.Add(v)
            v.SetPosition(pcbnew.wxPoint(x-five_mils, y-pixel_y/2-6*five_mils))#added - five_mils minus 6* versus 4*
            v.SetWidth(int(0.6*10**6))
            v.SetDrill(int(0.3*10**6))
            v.SetViaType(pcbnew.VIATYPE_THROUGH)
            v.SetLayerPair(front_copper_layer, back_copper_layer)
            v.SetNetCode(net2)
                        
        if j>2:
            track = pcbnew.PCB_TRACK(pcb)
            track.SetStart(pcbnew.wxPoint(x, y-pixel_y-half_pad)) # check here
            track.SetEnd(pcbnew.wxPoint(x+pixel_x/2, y-pixel_y-half_pad))
            track.SetWidth(int(0.127*10**6))
            track.SetLayer(front_copper_layer)
            pcb.Add(track)
        elif j>1: #added in whole else statement
            track = pcbnew.PCB_TRACK(pcb)
            track.SetStart(pcbnew.wxPoint(x, y-pixel_y-half_pad)) # check here
            track.SetEnd(pcbnew.wxPoint(x+pixel_x/2-five_mils, y-pixel_y-half_pad))#added minus five_mils
            track.SetWidth(int(0.127*10**6))
            track.SetLayer(front_copper_layer)
            pcb.Add(track)

# now add the green tracks going back down
j = 1
for i in range(1,13):
    x = 24*pixel_x-(j*pixel_x/2+i*pixel_x)+pixel_x+pixel_x/4#-0.254*10**6
    y = y_offset+j*pixel_y+half_pad-pixel_y/2-2*five_mils
    track = pcbnew.PCB_TRACK(pcb)
    track.SetStart(pcbnew.wxPoint(x, y-pixel_y/2-4*five_mils))
    track.SetEnd(pcbnew.wxPoint(x+pixel_x/2*i-pixel_x/2*0.75, y-pixel_y/2-4*five_mils+pixel_y*i-pixel_y*0.75))
    track.SetWidth(int(0.127*10**6))
    track.SetLayer(back_copper_layer)
    pcb.Add(track)
    #track 2 track to connect to pins
    track = pcbnew.PCB_TRACK(pcb)
    track.SetStart(pcbnew.wxPoint(x+pixel_x/2*i-pixel_x/2*0.75, y-pixel_y/2-4*five_mils+pixel_y*i-pixel_y*0.75))
    track.SetEnd(pcbnew.wxPoint(x+pixel_x/2*i-pixel_x/2*0.75+five_mils*10+five_mils*(12-i)*0.7, y-pixel_y/2-4*five_mils+pixel_y*i-pixel_y*0.75))
    track.SetWidth(int(0.127*10**6))
    track.SetLayer(back_copper_layer)
    pcb.Add(track)
    #track 3 final track frun pins
    track = pcbnew.PCB_TRACK(pcb)
    track.SetStart(pcbnew.wxPoint(x+pixel_x/2*i-pixel_x/2*0.75+five_mils*10+five_mils*(12-i)*0.7, y-pixel_y/2-4*five_mils+pixel_y*i-pixel_y*0.75))
    track.SetWidth(int(0.127*10**6))
    track.SetEnd(pcbnew.wxPoint(x+pixel_x/2*i-pixel_x/2*0.75+five_mils*10+five_mils*(12-i)*0.7+five_mils*6+five_mils*i*1.5, y-pixel_y/2-4*five_mils+pixel_y*i-pixel_y*0.75-five_mils*6-five_mils*i*1.5))
    track.SetWidth(int(0.127*10**6))
    track.SetWidth(int(0.127*10**6))
    track.SetLayer(back_copper_layer)
    pcb.Add(track)
    # track 4
    track = pcbnew.PCB_TRACK(pcb)
    track.SetStart(pcbnew.wxPoint(x+pixel_x/2*i-pixel_x/2*0.75+five_mils*10+five_mils*(12-i)*0.7+five_mils*6+five_mils*i*1.5, y-pixel_y/2-4*five_mils+pixel_y*i-pixel_y*0.75-five_mils*6-five_mils*i*1.5))
    track.SetEnd(pcbnew.wxPoint(x+pixel_x/2*i-pixel_x/2*0.75+five_mils*10+five_mils*(12-i)*0.7+five_mils*6+five_mils*i*1.5+five_mils*4, y-pixel_y/2-4*five_mils+pixel_y*i-pixel_y*0.75-five_mils*6-five_mils*i*1.5))
    track.SetWidth(int(0.127*10**6))
    track.SetWidth(int(0.127*10**6))
    track.SetLayer(back_copper_layer)
    pcb.Add(track)
    '''
    v = pcbnew.PCB_VIA(pcb)
    pcb.Add(v)
    v.SetPosition(pcbnew.wxPoint(x+pixel_x/2*i-pixel_x/2*0.75+pixel_x, y-pixel_y/2-4*five_mils+pixel_y*i-pixel_y*0.75))
    v.SetWidth(int(0.6*10**6))
    v.SetDrill(int(0.3*10**6))
    v.SetViaType(pcbnew.VIA_THROUGH)
    v.SetLayerPair(front_copper_layer, back_copper_layer)
    v.SetNetCode(net2)
    #redtrack after via
    track = pcbnew.PCB_TRACK(pcb)
    track.SetStart(pcbnew.wxPoint(x+pixel_x/2*i-pixel_x/2*0.75+pixel_x, y-pixel_y/2-4*five_mils+pixel_y*i-pixel_y*0.75))
    track.SetEnd(pcbnew.wxPoint(x+pixel_x/2*i-pixel_x/2*0.75+2*pixel_x, y-pixel_y/2-4*five_mils+pixel_y*i-pixel_y*0.75))
    track.SetWidth(int(0.127*10**6))
    track.SetLayer(front_copper_layer)
    pcb.Add(track)
    '''
    
    


# place the resistors do not exist any more
'''
i = -1
count = 1
for j in range(0,12):
    if j == 11:
        mod = pcb.FindModuleByReference('R1')
    else:
        mod = pcb.FindModuleByReference('R'+str(count+1))
    x = 24*pixel_x-(j*pixel_x/2+i*pixel_x) +pixel_x/2
    y = y_offset+j*pixel_y-half_pad
    mod.SetPosition(pcbnew.wxPoint(x, y))
    if j == 11:
        mod.SetOrientation(0*10)
    else:
        mod.SetOrientation(180*10)
    count = count+1

i = -2
count = 12
for j in range(0,12):
    mod = pcb.FindModuleByReference('R'+str(count+1))
    x = 24*pixel_x-(j*pixel_x/2+i*pixel_x) #+2750*10**3/4
    y = y_offset+j*pixel_y+half_pad-five_mils
    mod.SetPosition(pcbnew.wxPoint(x, y))
    mod.SetOrientation(180*10)
    count = count+1
'''

################################################################################################
#                           second readout line
################################################################################################


count = 12*24
for i in range(0,24):
    
    for j in range(12,24):
        
        mod = pcb.FindFootprintByReference('D'+str(count+1))
        x = 24*pixel_x-(j*pixel_x/2+i*pixel_x)
        y = y_offset+j*pixel_y
        mod.SetPosition(pcbnew.wxPoint(x, y))
        mod.SetOrientation(90*10)
        count = count+1


#connect 24 columns to gether with red tracks
count = 12*24
for i in range(0,24):   
    for j in range(12,23):
        mod = pcb.FindFootprintByReference('D'+str(count+1))
        for pad in mod.Pads():
            if int(pad.GetPadName()) == 1:
                pad1 = pad
                net1 = pad.GetNetCode()
            else:
                pad2 = pad
                net2 = pad.GetNetCode()
        x = 24*pixel_x-(j*pixel_x/2+i*pixel_x)+five_mils*0.5#1.5
        y = y_offset+j*pixel_y+half_pad-five_mils#add five mils
        #track 1
        track = pcbnew.PCB_TRACK(pcb)
        track.SetStart(pcbnew.wxPoint(x, y))
        track.SetEnd(pcbnew.wxPoint(x, y+pixel_y-five_mils))
        track.SetWidth(int(0.127*10**6))
        track.SetLayer(front_copper_layer)
        pcb.Add(track)
        #track.SetNetCode(net2)
        #track 2
        track = pcbnew.PCB_TRACK(pcb)
        track.SetStart(pcbnew.wxPoint(x, y+pixel_y-five_mils))
        track.SetEnd(pcbnew.wxPoint(x-pixel_y/2-five_mils*2,y+pixel_y-five_mils))
        track.SetWidth(int(0.127*10**6))
        track.SetLayer(front_copper_layer)
        pcb.Add(track)
        #track.SetNetCode(net2)
        count = count +1

#connect diagonals with vias and green tracks
count = 12*24
for i in range(0,24):   
    for j in range(12,24):
        mod = pcb.FindFootprintByReference('D'+str(count+1))
        for pad in mod.Pads():
            if int(pad.GetPadName()) == 1:
                pad1 = pad
                net1 = pad.GetNetCode()
            else:
                pad2 = pad
                net2 = pad.GetNetCode()
        x = 24*pixel_x-(j*pixel_x/2+i*pixel_x)+7*five_mils #8*
        y = y_offset+j*pixel_y-half_pad+five_mils
            
        v = pcbnew.PCB_VIA(pcb)
        pcb.Add(v)
        v.SetPosition(pcbnew.wxPoint(x,y))
        v.SetWidth(int(0.6*10**6))
        v.SetDrill(int(0.3*10**6))
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetLayerPair(front_copper_layer,back_copper_layer)
        v.SetNetCode(net2)

        track = pcbnew.PCB_TRACK(pcb)
        track.SetStart(pcbnew.wxPoint(x, y))
        track.SetEnd(pcbnew.wxPoint(x-half_pad, y))
        track.SetWidth(int(0.127*10**6))
        track.SetLayer(front_copper_layer)
        pcb.Add(track)

        #add green track        track = pcbnew.PCB_TRACK(pcb)
        
        if i == 0:
            if j != 11+12:
                # make connections to connectort
                track = pcbnew.PCB_TRACK(pcb)
                track.SetStart(pcbnew.wxPoint(x, y))
                x_new =x+10*five_mils+0.75*five_mils*(j-12)-9*five_mils
                y_new =y+five_mils*19-1.5*five_mils*(j-12)+11*five_mils
                track.SetEnd(pcbnew.wxPoint(x_new, y_new))
                track.SetWidth(int(0.127*10**6))
                track.SetLayer(back_copper_layer)
                pcb.Add(track)
                #track 2 #second last connector track
                track = pcbnew.PCB_TRACK(pcb)
                track.SetStart(pcbnew.wxPoint(x_new, y_new))
                x_new =x_new+20*five_mils*3**0.5
                y_new =y_new+20*five_mils
                track.SetEnd(pcbnew.wxPoint(x_new, y_new))
                track.SetWidth(int(0.127*10**6))
                track.SetLayer(back_copper_layer)
                pcb.Add(track)
                #track 3 last connector track
                track = pcbnew.PCB_TRACK(pcb)
                track.SetStart(pcbnew.wxPoint(x_new, y_new))
                x_new =x_new
                y_new =y_new+35*five_mils
                track.SetEnd(pcbnew.wxPoint(x_new, y_new))
                track.SetWidth(int(0.127*10**6))
                track.SetLayer(back_copper_layer)
                pcb.Add(track)
                '''#here
                v = pcbnew.PCB_VIA(pcb)
                pcb.Add(v)
                v.SetPosition(pcbnew.wxPoint(x+9*five_mils, y))
                v.SetWidth(int(0.6*10**6))
                v.SetDrill(int(0.3*10**6))
                v.SetViaType(pcbnew.VIATYPE_THROUGH)
                v.SetLayerPair(front_copper_layer, back_copper_layer)
                v.SetNetCode(net2)
                
                track = pcbnew.PCB_TRACK(pcb)
                track.SetStart(pcbnew.wxPoint(x+9*five_mils, y))
                track.SetEnd(pcbnew.wxPoint(x+16*five_mils, y))
                track.SetWidth(int(0.127*10**6))
                track.SetLayer(front_copper_layer)
                pcb.Add(track)
                '''

        if i != 0:
            if j != 11+12:
                track = pcbnew.PCB_TRACK(pcb)
                track.SetStart(pcbnew.wxPoint(x, y))
                track.SetEnd(pcbnew.wxPoint(x+pixel_x/2, y+pixel_y))
                track.SetWidth(int(0.127*10**6))
                track.SetLayer(back_copper_layer)
                pcb.Add(track)
        
        count = count+1


#traces to connect the top in red
j = 0+12
for i in range(1,24):
        x = 24*pixel_x-(j*pixel_x/2+i*pixel_x)+0*five_mils#2 to 0
        y = y_offset+j*pixel_y+half_pad-2.5*five_mils#-3*five_mils
        #track 1
        '''
        track = pcbnew.PCB_TRACK(pcb)
        track.SetStart(pcbnew.wxPoint(x, y))
        track.SetEnd(pcbnew.wxPoint(x, y-half_pad))
        track.SetWidth(int(0.127*10**6))
        track.SetLayer(front_copper_layer)
        pcb.Add(track)
        '''
        #track 2
        track = pcbnew.PCB_TRACK(pcb)
        track.SetStart(pcbnew.wxPoint(x, y))
        track.SetEnd(pcbnew.wxPoint(x+pixel_x/3, y))
        track.SetWidth(int(0.127*10**6))
        track.SetLayer(front_copper_layer)
        pcb.Add(track)
        #track 4
        track = pcbnew.PCB_TRACK(pcb)
        track.SetStart(pcbnew.wxPoint(x+pixel_x/3, y))
        track.SetEnd(pcbnew.wxPoint(x+pixel_x*0.6, y-1.25*half_pad))
        track.SetWidth(int(0.127*10**6))
        track.SetLayer(front_copper_layer)
        pcb.Add(track)
        #track 5
        track = pcbnew.PCB_TRACK(pcb)
        track.SetStart(pcbnew.wxPoint(x+pixel_x*0.6, y-1.25*half_pad))
        track.SetEnd(pcbnew.wxPoint(x+pixel_x*1/2+half_pad*1.5, y-1.25*half_pad))
        track.SetWidth(int(0.127*10**6))
        track.SetLayer(front_copper_layer)
        pcb.Add(track)

#add vias and tracks bottom row green
j = 11+12
count = 11*24
for i in range(12,24):
    x = 24*pixel_x-(j*pixel_x/2+i*pixel_x)+5.5*five_mils+pixel_x/2+12*five_mils#was 13
    y = y_offset+j*pixel_y+4*five_mils
    mod = pcb.FindFootprintByReference('D'+str(count+1))
    for pad in mod.Pads():
        if int(pad.GetPadName()) == 1:
            pad1 = pad
            net1 = pad.GetNetCode()
        else:
            pad2 = pad
            net2 = pad.GetNetCode()
    v = pcbnew.PCB_VIA(pcb)
    pcb.Add(v)
    v.SetPosition(pcbnew.wxPoint(x,y))
    v.SetWidth(int(0.6*10**6))
    v.SetDrill(int(0.3*10**6))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(front_copper_layer, back_copper_layer)
    v.SetNetCode(net2)

    count = count+1
    # the track
    
    x2 = 24*pixel_x-(j*pixel_x/2+i*pixel_x)+8*five_mils
    y2 = y_offset+j*pixel_y-half_pad+five_mils
    track = pcbnew.PCB_TRACK(pcb)
    track.SetStart(pcbnew.wxPoint(x, y))
    track.SetEnd(pcbnew.wxPoint(x2, y2))
    track.SetWidth(int(0.127*10**6))
    track.SetLayer(back_copper_layer)
    pcb.Add(track)
    
    #the red track
    '''
    track = pcbnew.PCB_TRACK(pcb)
    track.SetStart(pcbnew.wxPoint(x, y))
    track.SetEnd(pcbnew.wxPoint(x+half_pad, y+half_pad))
    track.SetWidth(int(0.127*10**6))
    track.SetLayer(front_copper_layer)
    pcb.Add(track)
    '''
# now the backleg red to geen
count = 12*24
for i in range(1,13):   
    for j in range(1+12,12+12):
        mod = pcb.FindFootprintByReference('D'+str(count+1))
        for pad in mod.Pads():
            if int(pad.GetPadName()) == 1:
                pad1 = pad
                net1 = pad.GetNetCode()
            else:
                pad2 = pad
                net2 = pad.GetNetCode()
        x = 24*pixel_x-(j*pixel_x/2+i*pixel_x)+pixel_x+pixel_x/4+five_mils#nothing
        y = y_offset+j*pixel_y+half_pad-pixel_y/2-0*five_mils#used to be *2
        #track 1
        track = pcbnew.PCB_TRACK(pcb)
        if j == 11+12:
            track.SetStart(pcbnew.wxPoint(x, y)) #bottom
        elif j==1+12:
            track.SetStart(pcbnew.wxPoint(x-five_mils, y-half_pad)) #middle #addin whole line
        else:
            track.SetStart(pcbnew.wxPoint(x, y-half_pad)) #middle
        if j == 1+12:
            track.SetEnd(pcbnew.wxPoint(x-five_mils, y-pixel_y/2-6*five_mils)) #top minus five change 4 to 6
            
        else:
            track.SetEnd(pcbnew.wxPoint(x, y-pixel_y-half_pad))
        track.SetWidth(int(0.127*10**6))
        track.SetLayer(front_copper_layer)
        pcb.Add(track)
        if j == 1+12: #drop via
            v = pcbnew.PCB_VIA(pcb)
            pcb.Add(v)
            v.SetPosition(pcbnew.wxPoint(x-five_mils, y-pixel_y/2-6*five_mils)) # minus 5 and 4 to 6
            v.SetWidth(int(0.6*10**6))
            v.SetDrill(int(0.3*10**6))
            v.SetViaType(pcbnew.VIATYPE_THROUGH)
            v.SetLayerPair(front_copper_layer, back_copper_layer)
            v.SetNetCode(net2)
                        
        if j>2+12:
            track = pcbnew.PCB_TRACK(pcb)
            track.SetStart(pcbnew.wxPoint(x, y-pixel_y-half_pad))
            track.SetEnd(pcbnew.wxPoint(x+pixel_x/2, y-pixel_y-half_pad))
            track.SetWidth(int(0.127*10**6))
            track.SetLayer(front_copper_layer)
            pcb.Add(track)
        elif j>1+12: #added in whole else statement
            track = pcbnew.PCB_TRACK(pcb)
            track.SetStart(pcbnew.wxPoint(x, y-pixel_y-half_pad)) # check here
            track.SetEnd(pcbnew.wxPoint(x+pixel_x/2-five_mils, y-pixel_y-half_pad))#added minus five_mils
            track.SetWidth(int(0.127*10**6))
            track.SetLayer(front_copper_layer)
            pcb.Add(track)
            

# now add the green tracks going back down
j = 1+12
for i in range(1,13):
    
    x = 24*pixel_x-(j*pixel_x/2+i*pixel_x)+pixel_x+pixel_x/4#-0.254*10**6
    y = y_offset+j*pixel_y+half_pad-pixel_y/2-2*five_mils
    track = pcbnew.PCB_TRACK(pcb)
    track.SetStart(pcbnew.wxPoint(x, y-pixel_y/2-4*five_mils))
    track.SetEnd(pcbnew.wxPoint(x+pixel_x/2*i-pixel_x/2*0.75, y-pixel_y/2-4*five_mils+pixel_y*i-pixel_y*0.75))
    track.SetWidth(int(0.127*10**6))
    track.SetLayer(back_copper_layer)
    pcb.Add(track)
    
    #track 2
    track = pcbnew.PCB_TRACK(pcb)
    track.SetStart(pcbnew.wxPoint(x+pixel_x/2*i-pixel_x/2*0.75, y-pixel_y/2-4*five_mils+pixel_y*i-pixel_y*0.75))
    track.SetEnd(pcbnew.wxPoint(x+pixel_x/2*i-pixel_x/2*0.75+pixel_x*1.1-10*five_mils,
y-pixel_y/2-4*five_mils+pixel_y*i-pixel_y*0.75+five_mils*(12-i)*2+18*five_mils))
    track.SetWidth(int(0.127*10**6))
    track.SetLayer(back_copper_layer)
    pcb.Add(track)
    '''
    #track 3
    track = pcbnew.PCB_TRACK(pcb)
    track.SetStart(pcbnew.wxPoint(x+pixel_x/2*i-pixel_x/2*0.75+pixel_x+five_mils*3*i, y-pixel_y/2-4*five_mils+pixel_y*i-pixel_y*0.75))
    track.SetEnd(pcbnew.wxPoint(x+pixel_x/2*i-pixel_x/2*0.75+pixel_x+five_mils*3*i+2.5*pixel_x-five_mils*3*i, y-pixel_y/2-4*five_mils+pixel_y*i-pixel_y*0.75+pixel_y*1.75-2*five_mils*i))
    track.SetWidth(int(0.127*10**6))
    track.SetLayer(back_copper_layer)
    pcb.Add(track)
    '''
    '''
    v = pcbnew.PCB_VIA(pcb)
    pcb.Add(v)
    v.SetPosition(pcbnew.wxPoint(x+pixel_x/2*i-pixel_x/2*0.75+pixel_x, y-pixel_y/2-4*five_mils+pixel_y*i-pixel_y*0.75))
    v.SetWidth(int(0.6*10**6))
    v.SetDrill(int(0.3*10**6))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(front_copper_layer, back_copper_layer)
    v.SetNetCode(net2)
    #redtrack after via
    track = pcbnew.PCB_TRACK(pcb)
    track.SetStart(pcbnew.wxPoint(x+pixel_x/2*i-pixel_x/2*0.75+pixel_x, y-pixel_y/2-4*five_mils+pixel_y*i-pixel_y*0.75))
    track.SetEnd(pcbnew.wxPoint(x+pixel_x/2*i-pixel_x/2*0.75+2*pixel_x, y-pixel_y/2-4*five_mils+pixel_y*i-pixel_y*0.75))
    track.SetWidth(int(0.127*10**6))
    track.SetLayer(front_copper_layer)
    pcb.Add(track)
    '''

    
    


# place the resistors
'''
i = -1
count = 1+24
for j in range(0+12,12+12):
    if j == 11+12:
        mod = pcb.FindModuleByReference('R25')
    else:
        mod = pcb.FindModuleByReference('R'+str(count+1))
    x = 24*pixel_x-(j*pixel_x/2+i*pixel_x) +pixel_x/2
    y = y_offset+j*pixel_y-half_pad
    mod.SetPosition(pcbnew.wxPoint(x, y))
    if j == 11+12:
        mod.SetOrientation(0*10)
    else:
        mod.SetOrientation(180*10)
    count = count+1

i = -2
count = 12+24
for j in range(0+12,12+12):
    mod = pcb.FindModuleByReference('R'+str(count+1))
    x = 24*pixel_x-(j*pixel_x/2+i*pixel_x) #+2750*10**3/4
    y = y_offset+j*pixel_y+half_pad-five_mils
    mod.SetPosition(pcbnew.wxPoint(x, y))
    mod.SetOrientation(180*10)
    count = count+1
'''

#####################################################################################
#      place connectors
#####################################################################################
mod = pcb.FindFootprintByReference('J1')
i = -4.5-0.5
j = 2.5+5.3-1.25
x = 24*pixel_x-(j*pixel_x/2+i*pixel_x) -pixel_x*1.25
y = y_offset+j*pixel_y-half_pad
mod.SetPosition(pcbnew.wxPoint(x, y))
mod.SetOrientation(150*10)

mod = pcb.FindFootprintByReference('J2')
i = -4.5-0.5
j = 2.5+12+6
x = 24*pixel_x-(j*pixel_x/2+i*pixel_x) -pixel_x*1.25
y = y_offset+j*pixel_y-half_pad
mod.SetPosition(pcbnew.wxPoint(x, y))
mod.SetOrientation(150*10)

#####################################################################################
#        edgecuts
####################################################################################
#delete boardedges

for d in pcb.GetDrawings():
    if d.GetLayerName() == u'Edge.Cuts':
        pcb.Remove(d)

# starting form top right        
seg1 = pcbnew.PCB_SHAPE(pcb) 
pcb.Add(seg1)
x1 = pixel_x*32-30*five_mils
x2 = -4*five_mils
y1 = -pixel_y+five_mils*6.5
seg1.SetStart(pcbnew.wxPoint(x1, y1))
seg1.SetEnd( pcbnew.wxPoint(x2, y1))
seg1.SetLayer(edgecut)

y2_old = y1+pixel_y*24+5.75*five_mils+50*five_mils
y2 = y1+(x1-x2)/2*3**0.5#y1+pixel_y*30+5.75*five_mils+50*five_mils#quarter inch
x3_old = x2-(2/3**0.5*(y2_old-y1)/2)
x3 = x2-(2/3**0.5*(y2-y1)/2)

seg1 = pcbnew.PCB_SHAPE(pcb)
pcb.Add(seg1)
seg1.SetStart(pcbnew.wxPoint(x2, y1))
seg1.SetEnd( pcbnew.wxPoint(x3, y2))
seg1.SetLayer(edgecut)

x4 = x3-(x2-x1)
seg1 = pcbnew.PCB_SHAPE(pcb)
pcb.Add(seg1)
seg1.SetStart(pcbnew.wxPoint(x3, y2))
seg1.SetEnd( pcbnew.wxPoint(x4, y2))
seg1.SetLayer(edgecut)

seg1 = pcbnew.PCB_SHAPE(pcb)
pcb.Add(seg1)
seg1.SetStart(pcbnew.wxPoint(x4, y2))
seg1.SetEnd( pcbnew.wxPoint(x1, y1))
seg1.SetLayer(edgecut)

#place connectors?
#drop some vias for mounting

#v = pcbnew.PCB_VIA(pcb)
#pcb.Add(v)
#v.SetPosition(pcbnew.wxPoint(x1-50*five_mils,y1+25*five_mils))
#v.SetWidth(int(40*five_mils))
#v.SetDrill(int(25*five_mils))
#v.SetViaType(pcbnew.VIATYPE_THROUGH)
#v.SetLayerPair(front_copper_layer, back_copper_layer)
#v.SetNetCode(25)


v = pcbnew.PCB_VIA(pcb)
pcb.Add(v)
v.SetPosition(pcbnew.wxPoint(x3_old+450*five_mils,y2_old-25*five_mils))
v.SetWidth(int(30*five_mils))
v.SetDrill(int(20*five_mils))
v.SetViaType(pcbnew.VIATYPE_THROUGH)
v.SetLayerPair(front_copper_layer, back_copper_layer)
v.SetNetCode(25)

v = pcbnew.PCB_VIA(pcb)
pcb.Add(v)
v.SetPosition(pcbnew.wxPoint((x3_old+150*five_mils+x3_old+450*five_mils)/2.,y2_old-25*five_mils))
v.SetWidth(int(30*five_mils))
v.SetDrill(int(20*five_mils))
v.SetViaType(pcbnew.VIATYPE_THROUGH)
v.SetLayerPair(front_copper_layer, back_copper_layer)
v.SetNetCode(25)


v = pcbnew.PCB_VIA(pcb)
pcb.Add(v)
v.SetPosition(pcbnew.wxPoint(x3_old+150*five_mils,y2_old-25*five_mils))
v.SetWidth(int(30*five_mils))
v.SetDrill(int(20*five_mils))
v.SetViaType(pcbnew.VIATYPE_THROUGH)
v.SetLayerPair(front_copper_layer, back_copper_layer)
v.SetNetCode(25)


'''
length = 20
# drop some green lines
for i in range(0,24):
    track = pcbnew.PCB_TRACK(pcb)
    track.SetStart(pcbnew.wxPoint(0+pixel_x*29.5+2*2/3**0.5*five_mils*i, pixel_y*3))
    track.SetEnd(pcbnew.wxPoint(0+pixel_x*29.5 -pixel_x/2*length+2*2/3**0.5*five_mils*i,pixel_y*3+ pixel_y*length))
    track.SetWidth(int(0.127*10**6))
    track.SetLayer(31)
    pcb.Add(track)
    #track.SetNetCode(net2)

'''
pcbnew.Refresh()
