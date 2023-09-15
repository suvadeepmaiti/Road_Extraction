import matplotlib.pyplot as plt
from PIL import Image
import os
import wx
from src import *
import warnings
warnings.filterwarnings("ignore")


#-------------------------------------------------------------------------------------------
class DoodleWindow(wx.Window):

	def __init__(self, parent, ID):
		wx.Window.__init__(self, parent, ID, style=wx.NO_FULL_REPAINT_ON_RESIZE)
		self.SetBackgroundColour("WHITE")
		self.filename=[]
		self.thickness = 10
		self.drawRegion = False
		self.RegionSet = False
		self.fgselect = False
		self.OpenCV = True
		self.SetColour("Cyan")
		self.pos_foreground = []
		self.pos = wx.Point(0,0)
		self.Regionpos1 = wx.Point(0,0)
		self.Regionpos2 = wx.Point(0,0)

		self.InitBuffer()

		self.SetCursor(wx.StockCursor(wx.CURSOR_PENCIL))

		self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
		self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
		self.Bind(wx.EVT_MOTION, self.OnMotion)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_IDLE, self.OnIdle)
		self.Bind(wx.EVT_PAINT, self.OnPaint)

	def InitBuffer(self):
		size = self.GetClientSize()
		self.buffer = wx.EmptyBitmap(max(1,size.width), max(1,size.height))
		dc = wx.BufferedDC(None, self.buffer)
		dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
		dc.Clear()
		self.reInitBuffer = False

	def SetDrawRegion(self, tf):
		self.drawRegion=tf

	def setfgselect(self, tf):
		self.fgselect = tf

	def SetRegionSet(self, tf):
		self.RegionSet = tf

	def SetColour(self, colour):
		self.colour = colour
		self.pen = wx.Pen(self.colour, self.thickness, wx.SOLID)

	def SetFilename(self, fn):
		self.filename = fn
		self.Refresh()

	def GetFilename(self):
		return self.filename

	def SetLinesData(self, lines):
		self.InitBuffer()
		self.Refresh()

	def ClearGroundData(self):
		self.pos_foreground = []
		self.pos_background = []

	def GetNonroadData(self):
		return self.pos_foreground

	def OnLeftDown(self, event):
		self.pos = event.GetPosition()
		if self.drawRegion:
			self.Regionpos1 = self.pos
		self.CaptureMouse()

	def OnLeftUp(self, event):
		if self.HasCapture():
			self.ReleaseMouse()

	def OnMotion(self, event):
		if event.Dragging() and event.LeftIsDown():
			pos = event.GetPosition()
			if self.drawRegion:
				self.fgselect = True
				if self.colour=='Cyan':
					self.pos_foreground.append((self.pos.x, self.pos.y, pos.x, pos.y))
				self.Regionpos2 = pos
				self.pos = pos
				self.Refresh()
				
	def OnSize(self, event):
		self.reInitBuffer = True

	def OnIdle(self, event):
		if self.reInitBuffer:
			self.InitBuffer()
			self.Refresh(False)

	def OnPaint(self, event):
		self.InitBuffer()
		dc = wx.BufferedPaintDC(self, self.buffer)
		if not self.filename==[]:
			img = wx.Image(self.filename)
			# img = img.Scale(200, 200, quality=wx.IMAGE_QUALITY_BOX_AVERAGE)
			dc.DrawBitmap(img.ConvertToBitmap(), 0, 0, True)

			if self.fgselect:
				dc.SetPen(self.pen)
				coords = (self.pos.x, self.pos.y,self.Regionpos2.x, self.Regionpos2.y)
				dc.DrawLine(*coords)

			im = Image.open(self.filename)
			self.Regionpos1 = wx.Point(1,1)
			self.Regionpos2 = wx.Point(im.size[0]-1,im.size[1]-1)

#-------------------------------------------------------------------------------------------
class ControlPanel(wx.Panel):

	def __init__(self, parent, ID, doodle):
		wx.Panel.__init__(self, parent, ID, style=wx.RAISED_BORDER)
		self.doodle = doodle

		self.sizer2 = wx.BoxSizer(wx.VERTICAL)
		self.buttons = []
		self.buttons.append(wx.Button(self, -1, "Open"))
		self.buttons.append(wx.Button(self, -1, "Mark non-road"))
		self.buttons.append(wx.Button(self, -1, "Run"))
		for i in range(0, 3):
			self.sizer2.Add(self.buttons[i], 1, wx.EXPAND)
		# self.buttons[3].SetValue(True)

		self.Bind(wx.EVT_BUTTON, self.OnOpen, self.buttons[0])
		self.Bind(wx.EVT_BUTTON, self.OnSetForeground, self.buttons[1])
		self.Bind(wx.EVT_BUTTON, self.OnRun, self.buttons[2])
		
		box = wx.BoxSizer(wx.VERTICAL)
		box.Add(self.sizer2, 0, wx.ALL)
		self.SetSizer(box)
		self.SetAutoLayout(True)
		box.Fit(self)

	def OnOpen(self, event):
		dlg = wx.FileDialog(self, "Open image file...", os.getcwd()+"/images",
							style=wx.FD_OPEN,
							wildcard = "Image files (*.png;*.jpeg;*.jpg)|*.png;*.jpeg;*.jpg")
		if dlg.ShowModal() == wx.ID_OK:
			self.filename = dlg.GetPath()
			self.doodle.SetFilename(self.filename)
			self.doodle.SetLinesData([])
			self.doodle.ClearGroundData()
			self.doodle.SetRegionSet(False)
			self.doodle.setfgselect(False)
		dlg.Destroy()

	def OnSetForeground(self, event):
		self.doodle.SetDrawRegion(True)
		self.doodle.SetColour('Cyan')

	def OnRun(self, event):
		fn=self.doodle.GetFilename()
		if fn==[]:
			wx.MessageBox("You should open a image file before you run the GrabCut algorithm!", "oops!", style=wx.OK|wx.ICON_EXCLAMATION)
		else:
			pos_fore = self.doodle.GetNonroadData()
			clustered_image = run_roadId(fname=fn, fg=pos_fore)
			identified_roads = longest_component_identification(clustered_image)
			filtered_roads = morphological_operations(identified_roads, 3,2,2,1)
			final_image = remove_nonroad_areas(filtered_roads,5)
			plt.imshow(final_image, cmap='gray')
			plt.show()

#-------------------------------------------------------------------------------------------
class GrabFrame(wx.Frame):
	def __init__(self, parent):
		wx.Frame.__init__(self, parent, -1, "Road Extraction", size=(638,512),
							style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

		self.doodle = DoodleWindow(self, -1)				#build a doodle window object
		cPanel = ControlPanel(self, -1, self.doodle)	#build a control panel object

		#set the layout of the two objects above
		box = wx.BoxSizer(wx.HORIZONTAL)	
		box.Add(cPanel, 0, wx.EXPAND)
		box.Add(self.doodle, 1, wx.EXPAND)

		self.SetSizer(box)
		self.Centre()

#-------------------------------------------------------------------------------------------
class GrabApp(wx.App):

	def OnInit(self):
		frame = GrabFrame(None)
		frame.Show(True)
		return True

#-------------------------------------------------------------------------------------------
if __name__ == '__main__':
	app = GrabApp()
	app.MainLoop()

    # OnRun() method has all the methods called when 'Run' button is clicked.

    