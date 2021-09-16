import wx
from diffpy.pdfgui.gui.setspinsdialog import DialogSetSpins
from diffpy.pdfgui.gui.maginstructionsdialog import DialogInstructions
from matplotlib.figure import Figure
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import numpy.linalg as la
import os
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import proj3d
from matplotlib import pyplot as plt
import numpy as np
import matplotlib as mpl
from diffpy.pdfgui.gui import magpanelutils
from itertools import repeat
mpl.interactive(False)
mpl.use('WXAgg')
mpl.rcParams["toolbar"] = "toolmanager"


class CanvasFrame(wx.Frame):

    def __init__(self, X, elems, revdmap, magconfigure, nonmag=None, cif="", basis=np.eye(3), size=(900, 700)):
        if len(X) == 0:
            wx.MessageBox("No atoms inside of the structure are magnetic!",
                          "Error", wx.OK | wx.ICON_INFORMATION)
            magconfigure.firstViewerLaunch = True
            return
        wx.Frame.__init__(self, parent=magconfigure, size=(900, 700))
        self.panel = CanvasPanel(self, X, elems, revdmap,
                                 magconfigure, nonmag, cif, basis)
        self.parent = magconfigure
        self.isFullscreen = False
        self.panel.connect()
        self.Show(True)
        self.Bind(wx.EVT_CHAR_HOOK, self.onFullscreen)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        magconfigure.firstViewerLaunch = False
        self.SetFocus()

    def onClose(self, event):
        self.panel.on_close(event)
        self.Destroy()

    def onFullscreen(self, event):
        if event.GetKeyCode() == 70:  # sets the letter "f" to toggle fullscreen
            if self.isFullscreen is True:
                self.ShowFullScreen(False)
                self.isFullscreen = False
            else:
                self.ShowFullScreen(True)
                self.isFullscreen = True


class CanvasPanel(wx.Panel):
    def __init__(self, parent, X, elems, revdmap, magconfigure, nonmag=None, cif="", basis=np.eye(3), ):
        """
        Attributes:

            self.X         : (ndarray, (n,9)) copy of the X array imput into the class
                              cols :3 are x,y,z coords
                              cols 3 is 1 if changed or 0 if nothing has been done
                              cols 4:7 is vector cords (default (0,0,0)
                              cols 7 is the magnitude (default 1)
                              cols 8 is the unique index / label (int)
            self.mag	   : (ndarray, n)
            self.nonmag    : (ndarray, (m,3)) copy of input other array
            self.l         : (int) length scale of arrows
            self.s         : (int) size scale of atoms
            self.clicked   : (list) keeps track of indices that are clicked during
                             any given iteration
            self.fig       : (mpl figure object)
            self.ax        : (mpl axes object)
            self.plotted   : (list) saves the indices of atoms with associated
                             vectors / arrows
            self.quiver    : (list, (m)) mpl quiver objects with one per coordinate
            self.plot      : (mpl scatter object) magnetic coords dots
            self.fixed     : (mpl scatter object) non-magnetic coords dots
            self.tog       : (bool) True if the non-magnetic atoms are toggled
            self.grid      : (bool) True if the plot's grid is visible
            self.blue      : (ndarray, (4,)) values associated to a shade of blue
            self.red       : (ndarray, (4,)) values associated to a shade of red
            self.fc        : (ndarray, (n,4)) array of color values per coordinate
            self.centroid  : (ndarray, (3,)) centroid of the structure
            self.axscalefactor
                           : (ndarray, (3,)) max coordinate distance from centroid
                             along each axis.  Used for axes scaling to ensure centroid
                             is centered and all points are in equally scaled axes
            self.zoom      : (float) zoom in / out factor
            self.showgrid  : (bool) is the grid displayed
            self.showticks : (bool) are the ticks displayed
            self.full      : (bool) is command to fullscreen in effect
        """
        wx.Panel.__init__(self, parent)

        self.btnInfo = wx.Button(self, wx.ID_ANY, "Information")
        self.btnInfo.Bind(wx.EVT_BUTTON, self.onInstructions)

        self.btn1 = wx.Button(self, wx.ID_ANY, "Done")
        self.btn1.Bind(wx.EVT_BUTTON, self.destroy)

        self.magconfigure = magconfigure
        if X is None:
            raise ValueError("Must an assign X matrix")
        if cif is None:
            cif = ""
        if nonmag is None:
            nonmag = []
        if basis is None:
            basis = np.eye(3)
        self.visible = False
        self.basis = np.array(basis)
        self.nonmag = nonmag
        self.clicked = []                      # to contain points receiving a vector
        self.l = 4                            # default length of arrows
        self.s = 50                             # default size of point
        self.revdmap = revdmap
        self.elems = elems
        self.X = np.zeros((len(X[:, 0]), 9))
        self.X[:, :3] = X[:, :3]  # X matrix containing coordinates and vectors
        self.X[:, 7] = 1   # 7 is magnitudes
        self.n = len(self.X[:, 8])
        self.X[:, 8] = np.arange(self.n)
        self.fig = plt.figure(figsize=(8., 6.))  # set and save figure object
        #self.window = self.fig.canvas.manager.window
        self.ax = self.fig.add_subplot(111, projection='3d')  # make 3d
        self.plotted = []
        self.quiver = []
        self.showgrid = True
        self.showticks = False
        self.isfull = False
        self.props = dict(
            zip(list(range(self.n)), [np.array([[0, 0, 0]]) for i in range(self.n)]))
        self.saves = {}
        self.getProps()
        self.instructionsOpen = False

        #scatter the structure data
        if len(self.X) == 0:  # check if there are any coordinates
            raise ValueError("no selected indeces")

        # plot all X values
        self.plot = self.ax.scatter(self.X[:, 0], self.X[:, 1], self.X[:, 2],
                                    picker=True, s=self.s, facecolors=["C0"]*self.n,
                                    edgecolors=["C0"]*self.n)

        # plot all non-magnetic coordinates if any
        if len(self.nonmag) != 0:
            self.tog = False
            self.fixed = self.ax.scatter(self.nonmag[:, 0], self.nonmag[:, 1], self.nonmag[:, 2],
                                         s=self.s/4, facecolors="gray", edgecolors="gray")

        self.set_plot_params(cif)  # set color, axes, labels, title
        self.arrowscale = self.axscalefactor/self.l
        self.plot_text()  # instructions string
        self.setlegend()  # plot legend

        # initialize functions called upon events
        #self.fig.canvas.mpl_connect(
        #'close_event', self.on_close)  # D, escape, enter
        #self.fig.canvas.mpl_connect(
        #'pick_event', self.on_click)  # click on plotted point
        #self.fig.canvas.mpl_connect(
        #'key_release_event', self.on_key_press)  # zoom / scale
        #plt.ion()
        #plt.show()

        self.canvas = FigureCanvas(self, -1, self.fig)
        self.__do_layout()

        #sets the default grid scale
        self.xtickDefault = self.ax.get_xticks()
        self.ytickDefault = self.ax.get_yticks()
        self.ztickDefault = self.ax.get_zticks()

        #Checks if this is the first time magviewer launches. If not, it will use imported X from magconfigure
        if self.magconfigure.firstViewerLaunch is False:
            self.X[:, 4:8] = X[:, 4:8]
            self.redraw_arrows()

    def __do_layout(self):
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()
        self.toolbar.update()
        sizerMain = wx.BoxSizer(wx.VERTICAL)
        sizerMain.Add(self.toolbar, 0, wx.LEFT | wx.TOP)
        #sizerCanvas = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, ""), wx.VERTICAL)
        sizerMain.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        sizer_4 = wx.StaticBoxSizer(wx.StaticBox(
            self, wx.ID_ANY, ""), wx.HORIZONTAL)
        sizer_4.Add(2, 1, 1)
        sizer_4.Add(self.btnInfo, 0, wx.ALL | wx.ALIGN_RIGHT, 10)
        sizer_4.Add(self.btn1, 0, wx.ALL | wx.ALIGN_RIGHT, 10)
        #sizerMain.Add(sizerCanvas, 5, wx.EXPAND | wx.ALL, 20)
        sizerMain.Add(sizer_4, 0, wx.EXPAND, 0)
        self.SetSizer(sizerMain)
        sizerMain.Fit(self)
        self.Layout()

    def connect(self):
        self.fig.canvas.mpl_connect(
            'close_event', self.on_close)  # D, escape, enter
        self.fig.canvas.mpl_connect(
            'pick_event', self.on_click)  # click on plotted point
        self.fig.canvas.mpl_connect(
            'key_release_event', self.on_key_press)  # zoom / scale

    def destroy(self, event):
        #self.setIsVisible(False)
        self.on_close(event)
        frame = self.GetParent()
        frame.Close()
        plt.close()
        self.toolbar.Destroy()
        self.Destroy()

    def onInstructions(self, event):
        dlg = DialogInstructions(self)
        dlg.ShowModal()
        dlg.Destroy()
        self.instructionsOpen = True
        return

    def setlegend(self):
        """
        build and plot a custom legend on the figure to label
        the different scatterplot colors
        """
        dotsize = 8  # size of dot in legend

        # build legend and include non-magnetic atoms if any
        legend_elements = [mpl.lines.Line2D([0], [0],
                           lw=0, marker='o', color=self.blue,
                           label='Can be Assigned',
                           markerfacecolor=self.blue,
                           markersize=dotsize),
                           mpl.lines.Line2D([0], [0],
                           lw=0, marker='o', color=self.red,
                           label='Selected or\nAssigned',
                           markerfacecolor=self.red,
                           markersize=dotsize)]
        if len(self.nonmag) != 0:  # if non-magnetic atoms in the structure, add gray to legend
            legend_elements += [mpl.lines.Line2D([0], [0],
                                lw=0, marker='o', color='gray',
                                label='Non-Magnetic', markerfacecolor='gray',
                                markersize=dotsize)]

        # plot legend on axes
        self.ax.legend(handles=legend_elements, fontsize='x-small')

    def plot_text(self):
        """ sets the text on the bottom center of the plot
        telling user how to access instructions """

        # text instructions on plot GUI
        self.ax.text2D(0.5, -0.05, s="Press i to view control instructions", horizontalalignment='center',
                       transform=self.ax.transAxes, fontweight='bold')

    def set_plot_params(self, cif):
        """ sets plot parameters such as:
        colors for selected / non-selected
        plot and window titles
        removes axis ticks
        label axes x,y,z
        center plot around centroid and fit axes to cover all of the structure
        """
        # set colors
        self.blue = np.array([0.12156863, 0.4666667, 0.70588235, 1.])
        self.red = np.array([1, 0, 0, 1])
        tmp = self.plot.get_facecolors()
        print("facecolors:")
        if self.n > 1:
            self.fc = np.vstack((tmp, [0.12156863, 0.4666667, 0.70588235, 1.]))
        elif self.n == 1:
            self.fc = tmp
        print(self.fc)

        # graph cosmetics
        title = "\n\n"+str(cif)
        #self.fig.canvas.set_window_title("MagPlotSpin")
        #self.fig.suptitle(title, fontweight='bold')

        # save all axes ticks
        self.update_ticks()

        # label axes in bold
        self.ax.set_xlabel("X", fontweight='bold')
        self.ax.set_ylabel("Y", fontweight='bold')
        self.ax.set_zlabel("Z", fontweight='bold')

        #### build bounding box

        box = np.array([[0, 0, 0],
                        [0, 0, 1],
                        [0, 1, 1],
                        [1, 1, 1],
                        [1, 1, 0],
                        [0, 1, 0],
                        [1, 1, 0],
                        [1, 0, 0],
                        [0, 0, 0],
                        [0, 1, 0],
                        [0, 1, 1],
                        [1, 1, 1],
                        [1, 0, 1],
                        [1, 0, 0],
                        [1, 0, 1],
                        [0, 0, 1]])

        self.bbox = box @ self.basis
        self.showbox = False
        # get coordinate furthest from centroid and scale axes accordingly, centering the plot
        self.centroid = np.mean(self.X[:, :3], axis=0)
        if len(self.nonmag) != 0:
            self.centroid = np.mean(np.concatenate(
                [self.X[:, :3], self.nonmag], axis=0), axis=0)
        self.axscalefactor = np.max(np.abs(self.bbox - self.centroid))
        self.zoom = 1.1
        self.ax.grid(b=self.showgrid)
        self.axes_lim()

    def axes_lim(self):
        # scale axes
        self.ax.set_xlim3d(self.centroid[0] - self.zoom*self.axscalefactor,
                           self.centroid[0] + self.zoom*self.axscalefactor)
        self.ax.set_ylim3d(self.centroid[1] - self.zoom*self.axscalefactor,
                           self.centroid[1] + self.zoom*self.axscalefactor)
        self.ax.set_zlim3d(self.centroid[2] - self.zoom*self.axscalefactor,
                           self.centroid[2] + self.zoom*self.axscalefactor)

    def getProps(self):
        for i in range(len(self.magconfigure.structure.magnetic_atoms)):
            if self.magconfigure.structure.magnetic_atoms[i][0] == 1:
                label = self.magconfigure.structure.magnetic_atoms[i][1]
                self.props[i - 1] = self.magconfigure.structure.magStructure.species[label].kvecs

    def on_close(self, event=[]):
        """save basis and prop vecs on close"""

        count = 0
        for i in range(len(self.magconfigure.structure.magnetic_atoms)):
            if self.magconfigure.structure.magnetic_atoms[i][0] == 1:
                label = self.magconfigure.structure.magnetic_atoms[i][1]
                self.magconfigure.structure.magStructure.species[label].basisvecs = np.array([
                                                                                             self.X[:, 4:7][count]])
                self.magconfigure.structure.magStructure.species[label].kvecs = np.array(
                    self.props[count])
                count += 1
        self.magconfigure.Xarr = self.X
        self.magconfigure.refresh()
        self.magconfigure.mainFrame.needsSave()
        plt.close()

    def enter(self):
        """
        Function called when enter is pressed
            Upon enter, if any points are selected, vector assignement GUI
            is opened and the input data is loaded into the magview viewer
        """
        self.save = {}
        dlg = DialogSetSpins(self)
        dlg.ShowModal()
        dlg.Destroy()

        if self.clicked and 'spin vector' in self.save:

            vector = self.save['spin vector']
            mag = self.save['magnitude']
            usecrys = self.save['crystal coords checked']
            prop = self.save['prop vec']

            # normalize and set vector
            if vector.size != 1:
                if not np.allclose(vector, np.zeros_like(vector)):
                    norm = la.norm(vector)
                    if usecrys:
                        vector = vector[0]*self.basis[0] + vector[1] * \
                            self.basis[1] + vector[2]*self.basis[2]

                    norm = la.norm(vector)
                    self.X[np.array(self.clicked), 4:7] = vector / \
                        norm * np.sign(mag)
                    self.X[np.array(self.clicked), 3] = 1
                    self.X[np.array(self.clicked), 7] = np.abs(mag)
                    for i in self.X[np.array(self.clicked), 8]:
                        self.props[i] = prop
                else:
                    self.fc[np.array(self.clicked), :] = self.blue

        # reset colors and replot
        self.plot._facecolor3d = self.fc
        self.plot._edgecolor3d = self.fc
        self.clicked = []
        self.redraw_arrows()
        self.plotted = (self.X[:, 3] == 1).nonzero()
        self.fig.canvas.draw_idle()
        #self.redraw_scatter()

    def update_ticks(self):
        self.xticks = self.ax.get_xticks()
        self.yticks = self.ax.get_yticks()
        self.zticks = self.ax.get_zticks()

    def on_key_press(self, event):
        """
        Keyboard helper function that sends a keyboard touch to the
        appropriate action
        """
        print("EVENT")
        # and (len(self.clicked) != 0): # proceed to save and continue to vector assignemnt
        if (event.key == "enter") and (len(self.clicked) != 0):
            self.enter()
            return
        elif (event.key == "escape"):  # end program
            self.destroy(event)

        else:
            if (event.key == "right") and (len(self.plotted) != 0) and (self.axscalefactor/self.l < self.arrowscale*3):  # grow arrow
                self.l = 0.9*self.l
                self.redraw_arrows()
            elif (event.key == "left") and (len(self.plotted) != 0) and (self.axscalefactor/self.l) > self.arrowscale/3:  # shrink arrow
                self.l = 10*self.l/9
                self.redraw_arrows()
            elif event.key == "down" and self.s > 3:  # shrink size of point
                self.s = 0.9*self.s
                self.redraw_scatter()
            elif event.key == "up" and self.s < 1600:  # grow size of point
                self.s = 10*self.s/9
                self.redraw_scatter()
            elif event.key == "i":  # show instructions
                if self.instructionsOpen is True:
                    self.instructionsOpen = False
                else:
                    self.onInstructions(event)
            elif event.key == "ctrl+-" and self.zoom < 2.5:  # zoom out of structure
                self.zoom = 10*self.zoom/9
                self.axes_lim()
                self.update_ticks()
            elif event.key == "ctrl+=" and self.zoom > 1/2.5:  # zoom into structure
                self.zoom = 9*self.zoom/10
                self.axes_lim()
                self.update_ticks()
            elif event.key == "g":
                self.showgrid = bool(1 - self.showgrid)
                self.ax.grid(b=self.showgrid)
            elif event.key == "n":
                self.showticks = bool(1 - self.showticks)
                if self.showticks:
                    self.showticks = True
                    self.ax.set_xticks(self.xticks)
                    self.ax.set_yticks(self.yticks)
                    self.ax.set_zticks(self.zticks)
                else:
                    self.showticks = False
                    self.ax.set_xticks(self.xtickDefault)
                    self.ax.set_yticks(self.ytickDefault)
                    self.ax.set_zticks(self.ztickDefault)
                self.axes_lim()
            elif event.key == "b":
                self.showbox = bool(1-self.showbox)
                if self.showbox:
                    self.bboxplot = self.ax.plot(
                        self.bbox[:, 0], self.bbox[:, 1], self.bbox[:, 2], color="gray", linestyle="--")
                else:
                    lines = self.bboxplot.pop(0)
                    lines.remove()

            elif (event.key == "t") and (len(self.nonmag) != 0):  # toggle non-magnetic atoms
                self.tog = bool(1 - self.tog)
                if self.tog:
                    self.fixed.remove()
                else:
                    self.fixed = self.ax.scatter(self.nonmag[:, 0], self.nonmag[:, 1],
                                                 self.nonmag[:, 2], s=self.s/3,
                                                 facecolors="gray", edgecolors="gray")
                self.redraw_scatter()

        if event.key in {"right", "b", "f", "c", "left", "n", "g", "t",
                         "down", "up", "ctrl+-", "ctrl+=", "enter"}:
            # update canvas
            self.fig.canvas.draw_idle()

    def redraw_arrows(self):
        """
        Remove and Replot arrows with updated info
        """
        if len(self.quiver) != 0:  # check if there are arrows to remove
            for i in range(len(self.quiver)):
                self.quiver[i].remove()
        self.quiver = []
        for count, row in enumerate(self.X):  # plot each arrow individually
            self.quiver += [self.ax.quiver(row[0], row[1], row[2], row[4], row[5], row[6],
                                           length=2*self.axscalefactor /
                                           self.l*self.X[count, 7],
                                           color="black", pivot="middle", arrow_length_ratio=0.3)]

    def redraw_scatter(self):
        """
        Remove and Replot dots with updated info
        """
        self.plot.remove()  # remove magnetic atoms
        if (len(self.nonmag) != 0) and (self.tog == False):  # check if there non-magnetics to remove
            self.fixed.remove()
            self.fixed = self.ax.scatter(self.nonmag[:, 0], self.nonmag[:, 1], self.nonmag[:, 2],
                                         s=self.s/3, facecolors="gray", edgecolors="gray")
        # replot magnetics
        self.plot = self.ax.scatter(self.X[:, 0], self.X[:, 1], self.X[:, 2],
                                    picker=True, s=self.s, facecolors=self.fc,
                                    edgecolors=self.fc)

    def distance(self, point, event):
        assert point.shape == (3,)
        x2, y2, _ = proj3d.proj_transform(
            point[0], point[1], point[2], plt.gca().get_proj())
        x3, y3 = self.ax.transData.transform((x2, y2))
        return np.sqrt((x3 - event.mouseevent.x)**2 + (y3 - event.mouseevent.y)**2)

    def getClosestPoint(self, event):
        distances = [self.distance(self.X[i, 0:3], event)
                     for i in range(self.X.shape[0])]
        return np.argmin(distances)

    def on_click(self, event):
        """
        When artist (dot) is clicked, the appropriate action is taken:
            left click: selected
            right click: remove
        """
        # indeces in X matrix that were clicked on
        ind = self.getClosestPoint(event)
        #check if any are already assigned (fixed)
        fixed = True if np.sum(self.X[ind, 3]) > 0 else False
        new_fc = self.fc.copy()

        if str(event.mouseevent.button) == "MouseButton.LEFT" and not fixed:

            # add to clicked if not already in it and change color to red
            if ind not in self.clicked:
                self.clicked += [ind]
                self.fc[ind, :] = self.red
                new_fc[ind, :] = ([1, 0, 0, 1])
            # otherwise remove it from clicked and change color to blue
            else:
                self.clicked.remove(ind)
                self.fc[ind, :] = self.blue
                new_fc[ind, :] = ([0.12156863, 0.4666667, 0.70588235, 1.])
            # update plot colors
            self.plot._facecolor3d = new_fc
            self.plot._edgecolor3d = new_fc

        elif str(event.mouseevent.button) == "MouseButton.RIGHT" and fixed:

            #set vector data to zero and update
            self.X[np.array(ind), 3:7] = np.zeros(4)
            self.redraw_arrows()
            #reset colors to blue
            self.fc[np.array(ind), :] = self.blue
            #remove each from clicked and update colors in plot
            for i in ind:
                if i in self.clicked:
                    self.clicked.remove(i)
            self.plot._facecolor3d = self.fc
            self.plot._edgecolor3d = self.fc
            # update plotted
            self.plotted = (self.X[:, 3] == 1).nonzero()
        self.fig.canvas.draw_idle()
        self.redraw_scatter()


"""
# remove matplotlib toolbar for further plots
mpl.rcParams['toolbar'] = 'None'
mpl.rcParams['keymap.fullscreen'] = 'None'
mpl.rcParams['keymap.quit'] = 'None'
mpl.rcParams['keymap.xscale'] = 'None'
mpl.rcParams['keymap.yscale'] = 'None'
mpl.rcParams['keymap.xscale'] = 'None'
mpl.rcParams['keymap.yscale'] = 'None'
"""
