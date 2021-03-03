#Author-Harry Felton
#Description-An add-in to automatically create and edit MicroChannel models.

# THE UNIVERSITY OF BRISTOL (UOB) PROVIDES THIS PROGRAM "AS IS" AND WITH ALL FAULTS. UOB SPECIFICALLY  
# DISCLAIMS ANY IMPLIED WARRANTY OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR USE.  
# UOB DOES NOT WARRANT THAT THE OPERATION OF THE PROGRAM WILL BE  
# UNINTERRUPTED OR ERROR FREE.

import adsk.core, adsk.fusion, adsk.cam, traceback
import os, math, time

# Global list to keep all event handlers in scope.

# Command inputs

# File input
_filein = adsk.core.DropDownCommandInput.cast(None)

# Value inputs
_channelwidthin = adsk.core.ValueCommandInput.cast(None)
_depth = adsk.core.ValueCommandInput.cast(None)
_length = adsk.core.ValueCommandInput.cast(None)

# Resistor Inputs
_resistorheight = adsk.core.ValueCommandInput.cast(None)
_resistorcycles = adsk.core.ValueCommandInput.cast(None)

# Droplet Inputs
_inputwidth = adsk.core.ValueCommandInput.cast(None)
_outletwidth = adsk.core.ValueCommandInput.cast(None)
_dropletwidth = adsk.core.ValueCommandInput.cast(None)
_neckwidth = adsk.core.ValueCommandInput.cast(None)
_necklength = adsk.core.ValueCommandInput.cast(None)

# Y Channel Inputs
_angle = adsk.core.ValueCommandInput.cast(None)

# Cross Channel Input
_anglex = adsk.core.ValueCommandInput.cast(None)

# Image inputs
_imgdroplet = adsk.core.ImageCommandInput.cast(None)
_imgresistor = adsk.core.ImageCommandInput.cast(None)
_imgstraight = adsk.core.ImageCommandInput.cast(None)
_imgyjunction = adsk.core.ImageCommandInput.cast(None)
_imgcross = adsk.core.ImageCommandInput.cast(None)

# Joint in inputs
_jointin = adsk.core.DropDownCommandInput.cast(None)
_jointa = adsk.core.DropDownCommandInput.cast(None)
_jointb = adsk.core.DropDownCommandInput.cast(None)
_jointc = adsk.core.DropDownCommandInput.cast(None)
_jointd = adsk.core.DropDownCommandInput.cast(None)

# Error message input
_errMessage = adsk.core.TextBoxCommandInput.cast(None)

# Export to stl input
_stl = adsk.core.DropDownCommandInput.cast(None)

#Get file location for resources
_filelocation = os.path.dirname(os.path.abspath(__file__))

# Set up length switch
_switch = 1

# This is only needed with Python.
handlers = []

def run(context):
    ui = None
    try:

        #global app, ui

        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions
        
        # Create a button command definition.
        button = cmdDefs.addButtonDefinition('MicroButtonid', 
                                                'MicroChannel Generator', 
                                                   'Creates and edits Microfluid Channels',
                                                   './resources/logos')
                                                   
        
        # Connect to the command created event.
        CommandCreated = CommandCreatedEventHandler()
        button.commandCreated.add(CommandCreated)
        handlers.append(CommandCreated)
        
        # Get the ADD-INS panel in the model workspace. 
        addInsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        
        # Add the button to the bottom of the panel.
        buttonControl = addInsPanel.controls.addCommand(button)

        # Get the solid create panel in the model workspace. 
        addInsPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        
        # Add the button to the bottom of the panel.
        buttonControl = addInsPanel.controls.addCommand(button)
        buttonControl.isPromotedByDefault = True

        #Adds a toolbar for the MicroChannels
        workSpace = ui.workspaces.itemById('FusionSolidEnvironment')
        tbPanels = workSpace.toolbarPanels
        

        tbPanel = tbPanels.itemById('MicroPanel')
        if tbPanel:
            tbPanel.deleteMe()
        tbPanel = tbPanels.add('MicroPanel', 'Micro Channels', 'SelectPanel', False)

        # Add the button to the bottom of the panel.
        Microtool = tbPanel.controls.addCommand(button)
        Microtool.isPromotedByDefault = True


    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the commandCreated event.
class CommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        app = adsk.core.Application.get()
        ui  = app.userInterface

        try:

            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)

            handler = 'create'
            
            #Call global variables that are being editted within class
            global _filein, _channelwidthin, _depth, _length
            global _imgdroplet, _imgresistor, _imgstraight,  _imgyjunction, _imgcross
            global _errMessage, _stl, _switch

            _switch = 1

            #Get the command
            cmd = eventArgs.command

            #Get the CommandInputs collection to create new command inputs
            inputs = cmd.commandInputs

            #Image for selected MicroChannel, setting each to full width. Initially showing droplet as default filein
            _imgdroplet = inputs.addImageCommandInput('ImageDroplet', '', '%s/resources/images/droplet.png' %_filelocation)
            _imgdroplet.isFullWidth = True
            _imgdroplet.isVisible = False

            _imgresistor = inputs.addImageCommandInput('Imageresistor', '', '%s/resources/images/resistor.png' %_filelocation)
            _imgresistor.isFullWidth = True
            _imgresistor.isVisible = False

            _imgstraight = inputs.addImageCommandInput('Imagestraight', '', '%s/resources/images/straight.png' %_filelocation)
            _imgstraight.isFullWidth = True
            _imgstraight.isVisible = False

            _imgyjunction = inputs.addImageCommandInput('Imageyjunction', '', '%s/resources/images/y_junction.png' %_filelocation)
            _imgyjunction.isFullWidth = True
            _imgyjunction.isVisible = False

            _imgcross = inputs.addImageCommandInput('Imagecross', '', '%s/resources/images/cross_junction.png' %_filelocation)
            _imgcross.isFullWidth = True
            _imgcross.isVisible = True

            # Create dropdown input to find filename
            _filein = inputs.addDropDownCommandInput('filename', 'Filename', adsk.core.DropDownStyles.TextListDropDownStyle)
            _fileinItems = _filein.listItems
            _fileinItems.add('cross_junction', True, '')
            _fileinItems.add('droplet', False, '')
            _fileinItems.add('resistor', False, '')
            _fileinItems.add('straight',False,'')
            _fileinItems.add('y_junction',False,'')
        
            joints(handler,inputs)

            #define initial length variable depending on file selected
            lengthvar = float(standardlength())

            # Create a value input to get channel width
            _channelwidthin = inputs.addValueInput('channelwidth', 'Channel Width', 'mm', adsk.core.ValueInput.createByReal(0.035))

            # Create a value input to get depth
            _depth = inputs.addValueInput('depth','Depth','mm',adsk.core.ValueInput.createByReal(0.035))
            
            # Create a value input to get length
            _length = inputs.addValueInput('length','Length','mm',adsk.core.ValueInput.createByReal(lengthvar))

            channelfunc(handler, inputs)

            #Create dropdown input to ask whether to export to stl
            _stl = inputs.addDropDownCommandInput('stl', 'Export to stl?', adsk.core.DropDownStyles.TextListDropDownStyle)
            _stlItems = _stl.listItems
            _stlItems.add('Yes', True, '')
            _stlItems.add('No', False, '')

            # Error message input
            _errMessage = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
            _errMessage.isFullWidth = True

            # Connect to the execute event.
            onExecute = CommandExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)

            # Connect to the input changed event.
            onInputChanged = ChannelCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            handlers.append(onInputChanged)

            # Connect to the validate inputs event
            onValidateInputs = ChannelCommandValidateInputsHandler()
            cmd.validateInputs.add(onValidateInputs)
            handlers.append(onValidateInputs)
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the execute event.
class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        # Code to react to the event.
        app = adsk.core.Application.get()
        ui  = app.userInterface

        handler = 'execute'

        #opens the selected file in a new window
        try:
            # Set up importManager
            importManager=app.importManager

            # Get the currently selected file
            fileopen = _filein.selectedItem.name

            # Hides all images except selected image
            imagehide()

            # Sets filename for opening (with path)
            filename = "%s/resources/parts/%s.f3d" %(_filelocation,fileopen)

            # Sets options using file path
            f3dImportOptions = app.importManager.createFusionArchiveImportOptions(filename)

            # Opens file into new document
            app.importManager.importToNewDocument(f3dImportOptions)

            # Pause required for Fusion to work properly
            time.sleep(2)

        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

        #edit user parameters to inputs
        try:
            
            # Gets userParams
            des = adsk.fusion.Design.cast(app.activeProduct)
            userParams = des.userParameters

            #channelwidth
            validcheck = _channelwidthin.isValidExpression
            if  validcheck:
                channelwidth = _channelwidthin.value*10
                userParams.itemByName('channelwidth').expression = '%f' %channelwidth
                
            else:
                ui.messageBox('Value entered for channel width is not a valid expression')
                pass

            #depth
            validcheck = _depth.isValidExpression
            if  validcheck:
                depth = _depth.value*10
                userParams.itemByName('depth').expression = '%f' %depth
                
            else:
                ui.messageBox('Value entered for depth is not a valid expression')
                pass
            
            time.sleep(5)

            #length
            validchecklength = _length.isValidExpression
            if  validchecklength:
                length = _length.value*10
                userParams.itemByName('length').expression = '%f' %length
            else:
                ui.messageBox('Value entered for length is not a valid expression')
                pass

            time.sleep(5)

            # Calls channel specific function
            channelfunc(handler,'')

            # Creates joints
            jointcreate(app, ui, importManager, userParams)

            if _stl.selectedItem.name == 'Yes':
                exportstl(app, ui)
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the inputChanged event.
class ChannelCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        try:

            handler = 'inputchanged'

            # Sets up eventArgs if input changed
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input

            # Switch used depending on how the code works. Stops the value for length changing if the filename is changed after the length has been changed
            global _switch                   
                
            if changedInput.id == 'filename':
                # Changes the length input if the file selected is changed to the default value, only if the length hasn't been manually chnaged already
                if _switch == 1:
                    # Define initial length variable depending on file selected
                    _length.value = standardlength()

                channelfunc(handler,'')
                joints(handler, '')

                # Changes image shown
                imagehide()

            # Sets switch to 0 if length is changed
            if changedInput.id == 'length':
                _switch = 0     
        
            if changedInput.id == 'defaultjoints':
                joints(handler,'')

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        
# Event handler for the validateInputs event.
class ChannelCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:

            app = adsk.core.Application.get()
            ui  = app.userInterface

            eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)
            
            _errMessage.text = ''

            handler = 'error'

            channelfunc(handler, eventArgs)
            

            # Checks that the entered values are greater than 0          
            if _channelwidthin.value <= 0:
                _errMessage.text = 'The channel width must be a positive value.'
                eventArgs.areInputsValid = False
                return
            
            if _depth.value <= 0:
                _errMessage.text = 'The depth must be a positive value.'
                eventArgs.areInputsValid = False
                return

            if _length.value <= 0:
                _errMessage.text = 'The length must be a positive value.'
                eventArgs.areInputsValid = False
                return
                
            
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Function to hide all images and show image for selected file
def imagehide():

    # Hides all images
    _imgcross.isVisible = False
    _imgdroplet.isVisible = False
    _imgresistor.isVisible = False
    _imgstraight.isVisible = False
    _imgyjunction.isVisible = False
    

    # Gets currently selected file
    fname = _filein.selectedItem.name

    # Checks filename and displays respective image
    if fname == 'cross_junction':
        _imgcross.isVisible = True
    elif fname == 'droplet':
        _imgdroplet.isVisible = True
    elif fname == 'resistor':
        _imgresistor.isVisible = True
    elif fname == 'straight':
        _imgstraight.isVisible = True
    elif fname == 'y_junction':
        _imgyjunction.isVisible = True
    else:
        pass

# Function to hold all standard lengths
def standardlength():
    class lengthclass: 
        def __init__(self, name, length): 
            self.name = name 
            self.length = length 

    # creating list	 
    listl = [] 

    # Add data to list
    listl.append(lengthclass('cross_junction', 2))
    listl.append(lengthclass('droplet', 2) ) 
    listl.append(lengthclass('resistor', 3.5) ) 
    listl.append(lengthclass('straight', 1) ) 
    listl.append(lengthclass('y_junction', 1.5) )

    #Set up position list
    pos=[]
    counter = 1

    # Cycle through list
    for obj in listl:
        counter = counter+1  
        pos.append(obj.name)
    
    # Find position
    pos = pos.index('%s' %_filein.selectedItem.name)

    # Find length
    length = listl[pos].length

    # Return length
    return length

def channelfunc(handler, inputs):
    app = adsk.core.Application.get()
    ui  = app.userInterface
    
    try:
        
        # Gets userParams
        des = adsk.fusion.Design.cast(app.activeProduct)
        userParams = des.userParameters

        crossfunc(handler, inputs, ui, userParams)
        dropletfunc(handler, inputs, ui, userParams)
        resistorfunc(handler, inputs, ui, userParams)
        straightfunc(handler, inputs, ui, userParams)
        yfunc(handler, inputs, ui, userParams)


    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def crossfunc(handler, inputs, ui, userParams):
    try:

        global _anglex

        if handler == 'create':
            xang = 45/180 * math.pi
            _anglex = inputs.addValueInput('anglex', 'Angle', 'deg', adsk.core.ValueInput.createByReal(xang))
        
        elif handler == 'execute' and _filein.selectedItem.name == 'cross_junction':
            validcheck = _anglex.isValidExpression
            if validcheck:
                xang = _anglex.value*180/math.pi
                userParams.itemByName('angle').expression = '%f' %xang

        if handler == 'inputchanged' or handler == 'create':
            if _filein.selectedItem.name != 'cross_junction':
                _anglex.isVisible = False
            else:
                _anglex.isVisible = True

        if handler == 'error' and _filein.selectedItem.name == 'cross_junction':
            if _anglex.value < (10*math.pi)/180 or _anglex.value > (150*math.pi)/180:
                _errMessage.text = 'Angle must be between 10 and 150 degrees'
                inputs.areInputsValid = False
                return

    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def dropletfunc(handler, inputs, ui, userParams):
    try:

        global _inputwidth, _neckwidth, _necklength, _outletwidth, _dropletwidth

        if handler == 'create':
            # Create a value input to get input width
            _inputwidth = inputs.addValueInput('inputwidth', 'a', 'mm', adsk.core.ValueInput.createByReal(0.105))

            # Create a value input to get channel width for droplet
            _dropletwidth = inputs.addValueInput('dropletwidth', 'b', 'mm', adsk.core.ValueInput.createByReal(0.035))

            # Create a value input to get neck length
            _necklength = inputs.addValueInput('necklength', 'c', 'mm', adsk.core.ValueInput.createByReal(0.0825))

            # Create a value input to get droplet neck width
            _neckwidth = inputs.addValueInput('neckwidth', 'd', 'mm', adsk.core.ValueInput.createByReal(0.035))

            # Create a value input to get outlet width
            _outletwidth = inputs.addValueInput('outletwidth', 'e', 'mm', adsk.core.ValueInput.createByReal(0.105))


        elif handler == 'execute' and _filein.selectedItem.name == 'droplet':
            inputwidth = _inputwidth.value*10
            userParams.itemByName('inputwidth').expression = '%f' %inputwidth
            dropletwidth = _dropletwidth.value*10
            userParams.itemByName('channelwidth').expression = '%f' %dropletwidth
            neckwidth = _neckwidth.value*10
            userParams.itemByName('neckwidth').expression = '%f' %neckwidth
            necklength = _necklength.value*10
            userParams.itemByName('necklength').expression = '%f' %necklength
            outletwidth = _outletwidth.value*10
            userParams.itemByName('outletwidth').expression = '%f' %outletwidth

        if handler == 'inputchanged' or handler == 'create':
            if _filein.selectedItem.name != 'droplet':
                _inputwidth.isVisible = False
                _dropletwidth.isVisible = False
                _necklength.isVisible = False
                _neckwidth.isVisible = False
                _outletwidth.isVisible = False
            else:
                _inputwidth.isVisible = True
                _dropletwidth.isVisible = True
                _necklength.isVisible = True
                _neckwidth.isVisible = True
                _outletwidth.isVisible = True

        if handler == 'error' and _filein.selectedItem.name == 'droplet':
            if _inputwidth.value <= 0:
                _errMessage.text = 'a must be a positive value.'
                inputs.areInputsValid = False
                return
            elif _dropletwidth.value <= 0:
                _errMessage.text = 'b be a positive value.'
                inputs.areInputsValid = False
                return
            elif _necklength.value <= 0:
                _errMessage.text = 'c be a positive value.'
                inputs.areInputsValid = False
                return
            elif _neckwidth.value <= 0:
                _errMessage.text = 'd be a positive value.'
                inputs.areInputsValid = False
                return
            elif _outletwidth.value <= 0:
                _errMessage.text = 'e be a positive value.'
                inputs.areInputsValid = False
                return

    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def resistorfunc(handler, inputs, ui, userParams):
    try:

        global _resistorheight, _resistorcycles

        if handler == 'create':
            # Create a value input to get resistor height
            _resistorheight = inputs.addValueInput('resistorheight', 'Resistor Height', 'mm', adsk.core.ValueInput.createByReal(1.2))
            _resistorcycles = inputs.addValueInput('numcycles', 'Number of Cycles', '', adsk.core.ValueInput.createByReal(5))

        elif handler == 'execute' and _filein.selectedItem.name == 'resistor':
            validcheck = _resistorheight.isValidExpression
            if validcheck:
                resistorh = _resistorheight.value*10
                userParams.itemByName('resistor_height').expression = '%f' %resistorh

            else:
                ui.messageBox('Error: Value entered for resistor height is not a valid expression')
                pass
            validcheck = _resistorcycles.isValidExpression
            if validcheck:
                resistorcycles = _resistorcycles.value
                userParams.itemByName('numcycles').expression = '%i' %resistorcycles

            app=adsk.core.Application.get()

            ui = app.userInterface
            product = app.activeProduct
            design = adsk.fusion.Design.cast(product)

            features = design.activeComponent.features

            rootComp = design.rootComponent

            numberext = rootComp.features.extrudeFeatures.count

            if numberext != 4:
                ui.messageBox('Unexpected number of extrusions detected. You may need to check the model for warnings.')
            
            else:
                extrudeedit = features.extrudeFeatures.item(3)
                design.timeline.markerPosition = 6

                bodycol = []

                for i in range (0,rootComp.bRepBodies.count):
                    if rootComp.bRepBodies.item(i).isValid == True:
                        bodycol.append(rootComp.bRepBodies.item(i))
                
                extrudeedit.participantBodies = bodycol

                design.timeline.markerPosition = design.timeline.count

            length = _length.value*10
            userParams.itemByName('length').expression = '35'
            userParams.itemByName('length').expression = '%f' %length

        elif handler == 'error' and _filein.selectedItem.name == 'resistor':
            if _resistorheight.value <= 0:
                _errMessage.text = 'The resistor height must be a positive value.'
                inputs.areInputsValid = False
                return

            ans = (_length.value-0.5)/(((_resistorcycles.value-1)*4)+6)
            
            if ans <= _channelwidthin.value*2:
                _errMessage.text = 'The number of cycles must be reduced or the length increased.'
                inputs.areInputsValid = False
                return
                
        
        # Opens if statement if the changed input is filename
        if handler == 'inputchanged' or handler == 'create':
            if _filein.selectedItem.name != 'resistor':
                # Sets the visibility of resistor height depending on whether resistor is selected
                _resistorheight.isVisible = False
                _resistorcycles.isVisible = False
                
            else:
                _resistorheight.isVisible = True
                _resistorcycles.isVisible = True


        

    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def straightfunc(handler, inputs, ui, userParams):
    try:
        # Place holder for a straight channel function
        if _filein.selectedItem.name == 'straight':
            pass
        else:
            pass
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def yfunc(handler, inputs, ui, userParams):
    try:

        global _angle

        if handler == 'create':
            ang = 45/180 * math.pi
            _angle = inputs.addValueInput('yangle', 'Angle', 'deg', adsk.core.ValueInput.createByReal(ang))
        
        elif handler == 'execute' and _filein.selectedItem.name == 'y_junction':
            validcheck = _angle.isValidExpression
            if validcheck:
                yang = _angle.value*180/math.pi
                userParams.itemByName('angle').expression = '%f' %yang

        if handler == 'inputchanged' or handler == 'create':
            if _filein.selectedItem.name != 'y_junction':
                _angle.isVisible = False
            else:
                _angle.isVisible = True

        if handler == 'error' and _filein.selectedItem.name == 'y_junction':
            if _angle.value < (10*math.pi)/180 or _angle.value > (150*math.pi)/180:
                _errMessage.text = 'Angle must be between 10 and 150 degrees'
                inputs.areInputsValid = False
                return

    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def joints(handler, inputs):
    app = adsk.core.Application.get()
    ui  = app.userInterface

    try:

        global _jointin, _jointa, _jointb, _jointc, _jointd

        

        if handler == 'create':
            _jointin = inputs.addDropDownCommandInput('defaultjoints', 'Use Default Joints?', adsk.core.DropDownStyles.TextListDropDownStyle)
            _jointinItems = _jointin.listItems
            _jointinItems.add('Yes', True, '')
            _jointinItems.add('No', False, '')

            _jointa = inputs.addDropDownCommandInput('jointa', 'End 1', adsk.core.DropDownStyles.TextListDropDownStyle)
            _jointaItems = _jointa.listItems
            _jointaItems.add('Ball', True, '')
            _jointaItems.add('Socket', False, '')

            _jointb = inputs.addDropDownCommandInput('jointb', 'End 2', adsk.core.DropDownStyles.TextListDropDownStyle)
            _jointbItems = _jointb.listItems
            _jointbItems.add('Ball', False, '')
            _jointbItems.add('Socket', True, '')

            _jointc = inputs.addDropDownCommandInput('jointc', 'End 3', adsk.core.DropDownStyles.TextListDropDownStyle)
            _jointcItems = _jointc.listItems
            _jointcItems.add('Ball', True, '')
            _jointcItems.add('Socket', False, '')

            _jointd = inputs.addDropDownCommandInput('jointd', 'End 4', adsk.core.DropDownStyles.TextListDropDownStyle)
            _jointdItems = _jointd.listItems
            _jointdItems.add('Ball', True, '')
            _jointdItems.add('Socket', False, '')

        if handler == 'create' or handler == 'inputchanged':
            if _jointin.selectedItem.name == 'Yes':
                             
                _jointa.isVisible = False
                _jointb.isVisible = False
                _jointc.isVisible = False
                _jointd.isVisible = False
                
            elif _filein.selectedItem.name == 'straight':
                _jointa.isVisible = True
                _jointb.isVisible = True
                _jointc.isVisible = False
                _jointd.isVisible = False
            elif _filein.selectedItem.name == 'resistor':
                _jointa.isVisible = True
                _jointb.isVisible = True
                _jointc.isVisible = False
                _jointd.isVisible = False
            elif _filein.selectedItem.name == 'droplet':
                _jointa.isVisible = True
                _jointb.isVisible = True
                _jointc.isVisible = True
                _jointd.isVisible = False
            elif _filein.selectedItem.name == 'y_junction':
                _jointa.isVisible = True
                _jointb.isVisible = True
                _jointc.isVisible = True
                _jointd.isVisible = False
            elif _filein.selectedItem.name == 'cross_junction':
                _jointa.isVisible = True
                _jointb.isVisible = True
                _jointc.isVisible = True
                _jointd.isVisible = True
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def jointcreate(app, ui, importManager, userParams):

        try:

            global _jointa, _jointb, _jointc, _jointd

            # Get active design
            product = app.activeProduct
            design = adsk.fusion.Design.cast(product)

            if _jointin.selectedItem.name == 'Yes':
                _jointa.selectedItem.name = 'Ball'
                _jointb.selectedItem.name = 'Socket'
                _jointc.selectedItem.name = 'Ball'
                _jointd.selectedItem.name = 'Ball'
            else:
                pass

            # Create list of joints used
            jointlist = []
            jointlist.append(_jointa.selectedItem.name)
            jointlist.append(_jointb.selectedItem.name)
            jointlist.append(_jointc.selectedItem.name)
            jointlist.append(_jointd.selectedItem.name)

            # Get root component
            rootComp = design.rootComponent

            # Opens joint a
            # Sets filename for opening (with path)
            filename = "%s/resources/parts/%s.f3d" %(_filelocation,jointlist[0])
            # Sets options using file path
            f3dImportOptions = app.importManager.createFusionArchiveImportOptions(filename)
            # Opens file into current document
            app.importManager.importToTarget(f3dImportOptions, rootComp)

            # Opens joint b
            # Sets filename for opening (with path)
            filename = "%s/resources/parts/%s.f3d" %(_filelocation,jointlist[1])
            # Sets options using file path
            f3dImportOptions = app.importManager.createFusionArchiveImportOptions(filename)
            # Opens file into document
            app.importManager.importToTarget(f3dImportOptions, rootComp)

            # Needed to stop issues with droplet and y junction
            time.sleep(1)

            if _filein.selectedItem.name == 'y_junction':
                # Opens joint c
                # Sets filename for opening (with path)
                filename = "%s/resources/parts/%s.f3d" %(_filelocation,jointlist[2])
                # Sets options using file path
                f3dImportOptions = app.importManager.createFusionArchiveImportOptions(filename)
                # Opens file into current document
                app.importManager.importToTarget(f3dImportOptions, rootComp)

            elif _filein.selectedItem.name == 'droplet':
                # Opens joint c
                # Sets filename for opening (with path)
                filename = "%s/resources/parts/%s.f3d" %(_filelocation,jointlist[2])
                # Sets options using file path
                f3dImportOptions = app.importManager.createFusionArchiveImportOptions(filename)
                # Opens file into document
                app.importManager.importToTarget(f3dImportOptions, rootComp)

            elif _filein.selectedItem.name == 'cross_junction':
                # Opens joint c
                # Sets filename for opening (with path)
                filename = "%s/resources/parts/%s.f3d" %(_filelocation,jointlist[2])
                # Sets options using file path
                f3dImportOptions = app.importManager.createFusionArchiveImportOptions(filename)
                # Opens file into document
                app.importManager.importToTarget(f3dImportOptions, rootComp)
                # Opens joint d
                # Sets filename for opening (with path)
                filename = "%s/resources/parts/%s.f3d" %(_filelocation,jointlist[3])
                # Sets options using file path
                f3dImportOptions = app.importManager.createFusionArchiveImportOptions(filename)
                # Opens file into document
                app.importManager.importToTarget(f3dImportOptions, rootComp)

            # Move joints

            allParams = design.allParameters

            if _filein.selectedItem.name == 'y_junction':
                # Joint 1
                allParams.itemByName('ypos').expression = '(length/2)*sin(angle)'
                allParams.itemByName('jointangle').expression = '(180-angle)'
                allParams.itemByName('xpos').expression = '0'
                allParams.itemByName('jointdepth').expression = 'depth'
                allParams.itemByName('ypos').expression = '-(length/2)*sin(angle)'
                # Joint 2
                allParams.itemByName('ypos_1').expression = '0'
                allParams.itemByName('xpos_1').expression = 'length'
                allParams.itemByName('jointangle_1').expression = '0'
                allParams.itemByName('jointdepth_1').expression = 'depth'
                # Joint 3
                allParams.itemByName('jointangle_2').expression = '(angle+180)'
                allParams.itemByName('ypos_2').expression = '(length/2)*sin(angle)'
                allParams.itemByName('xpos_2').expression = '0'
                allParams.itemByName('jointdepth_2').expression = 'depth'

            if _filein.selectedItem.name == 'straight':
                # Joint 1
                allParams.itemByName('ypos').expression = '0'
                allParams.itemByName('jointangle').expression = '180'
                allParams.itemByName('xpos').expression = '0'
                allParams.itemByName('jointdepth').expression = 'depth'
                # Joint 2
                allParams.itemByName('ypos_1').expression = '0'
                allParams.itemByName('xpos_1').expression = 'length'
                allParams.itemByName('jointangle_1').expression = '0'
                allParams.itemByName('jointdepth_1').expression = 'depth'

            if _filein.selectedItem.name == 'droplet':
                # Joint 1
                allParams.itemByName('ypos').expression = '0'
                allParams.itemByName('jointangle').expression = '(180)'
                allParams.itemByName('xpos').expression = '0'
                allParams.itemByName('jointdepth').expression = 'depth'
                # Joint 2
                allParams.itemByName('ypos_1').expression = '0'
                allParams.itemByName('xpos_1').expression = 'length+necklength+spacer*2'
                allParams.itemByName('jointangle_1').expression = '0'
                allParams.itemByName('jointdepth_1').expression = 'depth'
                # Joint 3
                allParams.itemByName('jointangle_2').expression = '(180)'
                allParams.itemByName('ypos_2').expression = '0'
                allParams.itemByName('xpos_2').expression = 'length+spacer-inputlength'
                allParams.itemByName('jointdepth_2').expression = 'depth'

            if _filein.selectedItem.name == 'resistor':
                # Joint 1
                allParams.itemByName('ypos').expression = '0'
                allParams.itemByName('jointangle').expression = '180'
                allParams.itemByName('xpos').expression = '0'
                allParams.itemByName('jointdepth').expression = 'depth'
                # Joint 2
                allParams.itemByName('ypos_1').expression = '0'
                allParams.itemByName('xpos_1').expression = 'length'
                allParams.itemByName('jointangle_1').expression = '0'
                allParams.itemByName('jointdepth_1').expression = 'depth'

            if _filein.selectedItem.name == 'cross_junction':
                # Joint 1
                allParams.itemByName('ypos').expression = '0'
                allParams.itemByName('jointangle').expression = '180'
                allParams.itemByName('xpos').expression = '0'
                allParams.itemByName('jointdepth').expression = 'depth'
                allParams.itemByName('ypos').expression = '0'
                # Joint 2
                allParams.itemByName('ypos_1').expression = '0'
                allParams.itemByName('xpos_1').expression = 'length'
                allParams.itemByName('jointangle_1').expression = '0'
                allParams.itemByName('jointdepth_1').expression = 'depth'

                point = design.rootComponent.constructionPoints.itemByName('Point1')

                pointgeom = point.geometry

                # Joint 3
                allParams.itemByName('jointangle_2').expression = '180-angle'
                allParams.itemByName('ypos_2').expression = '%f*10' %pointgeom.y
                allParams.itemByName('xpos_2').expression = '%f*10' %pointgeom.x
                allParams.itemByName('jointdepth_2').expression = 'depth'
                # Joint 4
                allParams.itemByName('ypos_3').expression = '%f*10' %pointgeom.y
                allParams.itemByName('jointangle_3').expression = '(180+angle)'
                allParams.itemByName('xpos_3').expression = '%f*10' %pointgeom.x
                allParams.itemByName('jointdepth_3').expression = 'depth'
                allParams.itemByName('ypos_3').expression = '%f*-10' %pointgeom.y

            # Combines joints and body
            target = rootComp.bRepBodies.item(0)

            tool = adsk.core.ObjectCollection.create()

            allComp = design.allComponents

            # Cycles through all components (other than the root component)
            for k in range(0, allComp.count):
                # Cycles through all bodies in each component
                for j in range (0,allComp.item(k).bRepBodies.count):
                    # Adds each body to the tool body collection
                    tool.add(allComp.item(k).bRepBodies.item(j))

            # Removes the target body from the tool body collection
            tool.removeByItem(target)

            #Sets the combine command
            combine = design.activeComponent.features.combineFeatures

            # Creates the input for the combine feature
            combineInput = combine.createInput(target,tool)

            # Combines all bodies
            design.activeComponent.features.combineFeatures.add(combineInput)

        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def exportstl(app, ui):
    try:

        # get active design        
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        design.timeline.moveToEnd
        # get root component in this design
        rootComp = design.rootComponent
        
        # create a single exportManager instance
        exportMgr = design.exportManager

        # Gets local time
        localtime = time.localtime(time.time())

        # Set styles of file dialog.
        fileDlg = ui.createFileDialog()
        fileDlg.isMultiSelectEnabled = False
        fileDlg.title = 'Fusion File Dialog'
        fileDlg.filter = '*.*'
            
        # Set styles of file dialog.
        folderDlg = ui.createFolderDialog()
        folderDlg.title = 'Please select stl export folder' 
        
        # Show folder dialog
        dlgResult = folderDlg.showDialog()
        if dlgResult == adsk.core.DialogResults.DialogOK:
            format(folderDlg.folder)

        if dlgResult != adsk.core.DialogResults.DialogOK:
            stlfile = _filelocation +'/export/' + str(localtime.tm_hour) + str(localtime.tm_min) + str(localtime.tm_sec) + '_' + _filein.selectedItem.name
            ui.messageBox('An invalid folder was selected. A file will be created within the add-in directory.')
        else: 
            # Sets export location and name
            stlfile = folderDlg.folder + '/' + str(localtime.tm_hour) + str(localtime.tm_min) + str(localtime.tm_sec) + '_' + _filein.selectedItem.name

        # export the root component to printer utility
        stlRootOptions = exportMgr.createSTLExportOptions(rootComp,stlfile)
        
        # export the root component to a specified file            
        stlRootOptions.sendToPrintUtility = False
        
        # Exports stl file
        exporttest = exportMgr.execute(stlRootOptions)

        # Checks if export succeeded - if yes say where, if not warn user
        if exporttest == True:
            ui.messageBox('The file has been exported to ' + stlfile + '.stl')
        
        else:
            ui.messageBox('The export failed. Please try manually exporting your file.')
    
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))	

# Stop function for the code. Removes all buttons
def stop(context):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        # Clean up the UI.
        cmdDef = ui.commandDefinitions.itemById('MicroButtonid')
        if cmdDef:
            cmdDef.deleteMe()
            
        addinsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        cntrl = addinsPanel.controls.itemById('MicroButtonid')
        if cntrl:
            cntrl.deleteMe()

        addinsPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        cntrl = addinsPanel.controls.itemById('MicroButtonid')
        if cntrl:
            cntrl.deleteMe()

        workSpace = ui.workspaces.itemById('FusionSolidEnvironment')
        tbPanels = workSpace.toolbarPanels
        cntrl = tbPanels.itemById('MicroPanel')
        if cntrl:
            cntrl.deleteMe()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))	